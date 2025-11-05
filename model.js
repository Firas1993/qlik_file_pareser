const { DataTypes } = require('sequelize');

/**
 * Check if a table exists in the database
 */
async function tableExists(sequelize, tableName) {
  try {
    const query = `
      SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = :tableName
      );
    `;
    const [results] = await sequelize.query(query, {
      replacements: { tableName },
      type: sequelize.QueryTypes.SELECT
    });
    return results.exists;
  } catch (error) {
    console.error(`❌ Error checking if table exists: ${error.message}`);
    return false;
  }
}

/**
 * Get existing columns from a table
 */
async function getExistingColumns(sequelize, tableName) {
  try {
    const query = `
      SELECT column_name 
      FROM information_schema.columns 
      WHERE table_schema = 'public' 
      AND table_name = :tableName;
    `;
    const results = await sequelize.query(query, {
      replacements: { tableName },
      type: sequelize.QueryTypes.SELECT
    });
    return results.map(row => row.column_name);
  } catch (error) {
    console.error(`❌ Error getting existing columns: ${error.message}`);
    return [];
  }
}

/**
 * Add missing columns to an existing table
 */
async function addMissingColumns(sequelize, tableName, missingColumns) {
  try {
    for (const column of missingColumns) {
      const query = `ALTER TABLE "${tableName}" ADD COLUMN "${column}" VARCHAR;`;
      await sequelize.query(query);
      console.log(`✅ Added column "${column}" to table "${tableName}"`);
    }
  } catch (error) {
    console.error(`❌ Error adding missing columns: ${error.message}`);
    throw error;
  }
}

/**
 * Create a Sequelize model dynamically based on provided columns.
 * All columns are created as VARCHAR and allowNull: true.
 * Enhanced version that handles existing tables and missing columns.
 */
async function createOrUpdateDynamicModel(sequelize, tableName, columns) {
  try {
    console.log(`🔍 Checking if table "${tableName}" exists...`);
    const exists = await tableExists(sequelize, tableName);
    
    if (exists) {
      console.log(`📋 Table "${tableName}" already exists. Checking columns...`);
      const existingColumns = await getExistingColumns(sequelize, tableName);
      console.log(`📋 Existing columns: ${existingColumns.join(', ')}`);
      
      const missingColumns = columns.filter(col => !existingColumns.includes(col));
      
      if (missingColumns.length > 0) {
        console.log(`➕ Missing columns found: ${missingColumns.join(', ')}`);
        await addMissingColumns(sequelize, tableName, missingColumns);
        console.log(`✅ Added ${missingColumns.length} missing columns to table "${tableName}"`);
      } else {
        console.log(`✅ All required columns already exist in table "${tableName}"`);
      }
    } else {
      console.log(`📋 Table "${tableName}" does not exist. Will create new table.`);
    }

    // Create the Sequelize model definition
    const modelDefinition = {};
    for (const column of columns) {
      modelDefinition[column] = {
        type: DataTypes.STRING,
        allowNull: true,
      };
    }
    console.log(`📋 Model definition prepared for table "${tableName}" with columns: ${columns.join(', ')}`);
    const DynamicModel = sequelize.define(tableName, modelDefinition, {
      tableName,
      timestamps: false,
      id:false,
    });
    if(!columns.includes('id')){
      DynamicModel.removeAttribute('id');
    }
    // Sync the model (creates table if it doesn't exist)
    await DynamicModel.sync({});
    
    if (!exists) {
      console.log(`✅ Created new table "${tableName}" with columns: ${columns.join(', ')}`);
    }
    
    return DynamicModel;
  } catch (error) {
    console.error(`❌ Error in createOrUpdateDynamicModel: ${error.message}`);
    throw error;
  }
}

/**
 * Legacy function for backward compatibility
 * Create a Sequelize model dynamically based on provided columns.
 * All columns are created as VARCHAR and allowNull: true.
 */
async function createDynamicModel(sequelize, tableName, columns) {
  const modelDefinition = {};

  for (const column of columns) {
    modelDefinition[column] = {
      type: DataTypes.STRING,
      allowNull: true,
    };
  }

  const DynamicModel = sequelize.define(tableName, modelDefinition, {
    tableName,
    timestamps: false,
  });

  await DynamicModel.sync(); // Creates table if not exist
  return DynamicModel;
}

module.exports = { 
  createDynamicModel, 
  createOrUpdateDynamicModel,
  tableExists,
  getExistingColumns,
  addMissingColumns
};
