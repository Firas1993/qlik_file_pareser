const { connectDB } = require('./db');
require('dotenv').config();
const async = require("async");

const CONCURRENCY_LIMIT = 500;

/**
 * Execute SQL queries from qlik_invoice_view_delta table in batches
 * Handles failures and returns them with invoice_line_id
 */
class QlikDeltaExecutor {
  /**
   * @param {Object} [options]
   * @param {boolean} [options.safeDelete=true] - whether to run safeDeleteChangedInvoiceRows
   */
  constructor(options = {}) {
    this.sequelize = connectDB();
    this.failedQueries = [];
    this.safeDelete = (typeof options.safeDelete === 'boolean') ? options.safeDelete : true;
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
   * Refresh materialized view
   * @returns {Promise<boolean>} True if successful, otherwise throws error
   */
  async refreshMaterializedView() {
    try {
      console.log('🔄 Refreshing materialized view qlik_invoice_view_filtered...');
      await this.sequelize.query(`REFRESH MATERIALIZED VIEW qlik_invoice_view_filtered;`);
      console.log('✅ Materialized view refreshed successfully');
      return true;
    } catch (error) {
      console.error('❌ Error refreshing materialized view:', error.message);
      throw error;
    }
  }

  /*
    * Safely delete changed invoice rows from mdm_invoice_qlik table
    * by marking them as deleted in mdm_invoice_line_to_remove_qlik table
    * @returns {Promise<boolean>} True if successful, otherwise throws error
  */
  async safeDeleteChangedInvoiceRows() {
    try {
      // the row to be deleted from mdm_invoice_qlik is all rows in mdm_invoice_line_to_remove_qlik
      const [results] = await this.sequelize.query(`
        SELECT mdm_invoice_id
        FROM mdm_invoice_line_to_remove_qlik
      `);
      console.log('📥 Fetching rows to be deleted from mdm_invoice_qlik...  result ::');
      console.log(results);
      // set deleted_at to now for all rows in mdm_invoice_line_to_remove_qlik
      console.log(`✅ Found ${results.length} rows to be deleted from mdm_invoice_qlik`);
      if (results.length === 0) {
        console.log('ℹ️  No rows to delete');
        return true;
      }

      await this.sequelize.query(`
        UPDATE mdm_invoice_qlik
        SET deleted_at = NOW()
        WHERE mdm_invoice_id IN (${results.map(id => `'${id.mdm_invoice_id}'`).join(',')})
      `);
      console.log(`✅ Marked ${results.length} rows as deleted in mdm_invoice_line_to_remove_qlik`);
      return true;
    } catch (error) {
      console.error('❌ Error fetching rows to be deleted:', error.message);
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

      // Conditionally perform safe delete of changed invoice rows
      if (this.safeDelete) {
        await this.safeDeleteChangedInvoiceRows();
      } else {
        console.log('ℹ️  safeDeleteChangedInvoiceRows is disabled by configuration');
      }
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
  // CLI mode flag: default 0 (run full execution). If 1 -> show counts only.
  const modeFlag = parseInt(process.argv[2] ?? '0', 10) || 0;
  // CLI safe-delete flag: default 1 (enabled). Pass 0 to disable safe delete.
  const safeDeleteFlag = parseInt(process.argv[3] ?? '1', 10) || 0;
  const executor = new QlikDeltaExecutor({ safeDelete: Boolean(safeDeleteFlag) });

  // Handle graceful shutdown
  const processEvent = {
    SIGINT: 'SIGINT', // Ctrl+C
    SIGTERM: 'SIGTERM' // Termination signal
  }

  process.on(processEvent.SIGINT, async () => {
    console.log('\n🛑 Received interrupt signal, shutting down gracefully...');
    try {
      await executor.sequelize.close();
    } catch (e) {
      // ignore
    }
    process.exit(0);
  });

  // If modeFlag is 1, only show counts and grouped counts, then exit
  if (modeFlag === 1) {
    (async () => {
      try {
        console.log('🔎 Running in counts-only mode (mode=1)...');
        await executor.sequelize.authenticate();
        console.log('✅ Database connection established');

        const [totalRows] = await executor.sequelize.query(`SELECT COUNT(*) as count FROM qlik_invoice_view_delta;`);
        const totalCount = (Array.isArray(totalRows) && totalRows[0]) ? totalRows[0].count : (totalRows.count || 0);
        console.log(`📊 qlik_invoice_view_delta row count: ${totalCount}`);

        const [groupRows] = await executor.sequelize.query(
          `SELECT client_yonka_entity as yonka_entity, COUNT(*) as count FROM qlik_invoice_view_delta GROUP BY client_yonka_entity ORDER BY yonka_entity;`
        );

        console.log('\n📊 qlik_invoice_view_delta counts grouped by yonka_entity:');
        console.log('===============================================');
        if (Array.isArray(groupRows) && groupRows.length > 0) {
          groupRows.forEach(r => console.log(`- ${r.yonka_entity || 'NULL'}: ${r.count}`));
        } else {
          console.log('No rows returned for grouping.');
        }

        await executor.sequelize.close();
        console.log('🔌 Database connection closed');
        process.exit(0);
      } catch (err) {
        console.error('❌ Failed to fetch counts:', err.message);
        try { await executor.sequelize.close(); } catch(e){}
        process.exit(1);
      }
    })();
    return;
  }

  // Execute the main function (default behavior)
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