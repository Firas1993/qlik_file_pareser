const { connectDB } = require('./db');
require('dotenv').config();
const async = require("async");

const CONCURRENCY_LIMIT = 200;

/**
 * Execute SQL queries from qlik_invoice_view_delta table in batches
 * Handles failures and returns them with invoice_line_id
 */
class QlikDeltaExecutor {
  constructor() {
    this.sequelize = connectDB();
    this.failedQueries = [];
  }

  /**
   * Fetch all SQL queries from qlik_invoice_view_delta table
   * @returns {Promise<Array>} Array of objects with invoice_line_id and mdm_sql
   */
  async fetchDeltaQueries() {
    try {
      console.log('📥 Fetching SQL queries from qlik_invoice_view_delta table...');
      
      const [results] = await this.sequelize.query(`
        SELECT invoice_line_id, mdm_invoice_id, mdm_sql 
        FROM qlik_invoice_view_delta 
        WHERE mdm_sql IS NOT NULL AND mdm_sql != ''
        ORDER BY invoice_line_id
      `);

      console.log(`✅ Found ${results.length} SQL queries to execute`);
      return results;
    } catch (error) {
      console.error('❌ Error fetching delta queries:', error.message);
      throw error;
    }
  }

  /**
   * Execute a single SQL query
   * @param {Object} queryData - Object containing invoice_line_id and mdm_sql
   * @returns {Promise<Object>} Result object with success status
   */
  async executeSingleQuery(queryData) {
    const { invoice_line_id, mdm_sql } = queryData;
    
    try {
      // Execute the SQL query
      await this.sequelize.query(mdm_sql);
      
      return {
        invoice_line_id,
        success: true,
        error: null
      };
    } catch (error) {
      console.warn(`⚠️  Query failed for invoice_line_id ${invoice_line_id}:`, error.message);
      
      return {
        invoice_line_id,
        success: false,
        error: error.message,
        mdm_sql
      };
    }
  }

  /**
   * Execute all queries using async.eachOfLimit for controlled concurrency
   * @param {Array} allQueries - All queries to execute
   */
  async executeAllQueries(allQueries) {
    console.log(`� Starting execution of ${allQueries.length} queries with concurrency limit of ${CONCURRENCY_LIMIT}...`);
    
    let processedCount = 0;
    let successCount = 0;
    const totalQueries = allQueries.length;

    return new Promise((resolve, reject) => {
      async.eachOfLimit(allQueries, CONCURRENCY_LIMIT, (queryData, index, callback) => {
        // Execute the query and handle the callback properly
        this.executeSingleQuery(queryData)
          .then(result => {
          
          // Collect failed queries
          if (!result.success) {
            this.failedQueries.push(result);
          } else {
            successCount++;
          }
          
          processedCount++;
          
          // Log progress every 100 processed queries or at completion
          if (processedCount % 100 === 0 || processedCount === totalQueries) {
            const progress = ((processedCount / totalQueries) * 100).toFixed(1);
            console.log(`� Progress: ${processedCount}/${totalQueries} (${progress}%) - Success: ${successCount}, Failed: ${this.failedQueries.length}`);
          }
          
          // Call callback with no parameters to indicate success
          callback();
        })
        .catch(error => {
          // This should not happen as executeSingleQuery handles its own errors
          console.error(`❌ Unexpected error processing query ${index}:`, error.message);
          // Call callback with error to indicate failure
          callback(error);
        });
      }, (error) => {
        if (error) {
          reject(error);
        } else {
          console.log(`✅ All queries processed: ${successCount} successful, ${this.failedQueries.length} failed`);
          resolve();
        }
      });
    });
  }

  /**
   * Main execution function
   */
  async execute() {
    const startTime = Date.now();
    
    try {
      console.log('🔧 Connecting to database...');
      await this.sequelize.authenticate();
      console.log('✅ Database connection established');

      // Fetch all queries
      const allQueries = await this.fetchDeltaQueries();

      if (allQueries.length === 0) {
        console.log('ℹ️  No queries found to execute');
        return;
      }
        // print total query to run
      console.log(`📊 Total queries to run: ${allQueries.length}`);
       // Print number of queries with null mdm_invoice_id
       const nullMdmInvoiceIdCount = allQueries.filter(query => !query.mdm_invoice_id).length;
      console.log(`📊 Queries with null mdm_invoice_id: ${nullMdmInvoiceIdCount}`);

      // Execute all queries in batches
      await this.executeAllQueries(allQueries);

      // Report results
      const executionTime = ((Date.now() - startTime) / 1000).toFixed(2);
      const successCount = allQueries.length - this.failedQueries.length;
      
      console.log('\n📋 EXECUTION SUMMARY');
      console.log('===================');
      console.log(`⏱️  Total execution time: ${executionTime}s`);
      console.log(`📊 Total queries processed: ${allQueries.length}`);
      console.log(`✅ Successful executions: ${successCount}`);
      console.log(`❌ Failed executions: ${this.failedQueries.length}`);
      
      if (this.failedQueries.length > 0) {
        console.log('\n🚫 FAILED QUERIES:');
        console.log('==================');
        this.failedQueries.forEach((failure, index) => {
          console.log(`${index + 1}. Invoice Line ID: ${failure.invoice_line_id}`);
          console.log(`   Error: ${failure.error}`);
          console.log(`   SQL: ${failure.mdm_sql.substring(0, 100)}...`);
          console.log('');
        });
        
        // Optionally save failed queries to a JSON file for further analysis
        const fs = require('fs');
        const failuresFile = `failed_queries_${new Date().toISOString().split('T')[0]}.json`;
        fs.writeFileSync(failuresFile, JSON.stringify(this.failedQueries, null, 2));
        console.log(`💾 Failed queries saved to: ${failuresFile}`);
      }

    } catch (error) {
      console.error('❌ Execution failed:', error.message);
      console.error(error.stack);
      process.exit(1);
    } finally {
      // Close database connection
      await this.sequelize.close();
      console.log('🔌 Database connection closed');
    }
  }

  /**
   * Get failed queries (useful for programmatic access)
   * @returns {Array} Array of failed query objects
   */
  getFailedQueries() {
    return this.failedQueries;
  }
}

// CLI execution
if (require.main === module) {
  const executor = new QlikDeltaExecutor();
  
  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\n🛑 Received interrupt signal, shutting down gracefully...');
    await executor.sequelize.close();
    process.exit(0);
  });
  
  // Execute the main function
  executor.execute()
    .then(() => {
      console.log('🎉 Execution completed successfully');
      process.exit(0);
    })
    .catch((error) => {
      console.error('💥 Execution failed:', error.message);
      process.exit(1);
    });
}

module.exports = QlikDeltaExecutor;