#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const xlsx = require('xlsx');

const { connectDB } = require('./db');
const { createOrUpdateDynamicModel } = require('./model');

const filePath = process.argv[2];
let tableName = process.argv[3] 
// throw error if tableName is not provided
if (!tableName) {
  console.error('❌ Table name is required. Using default: "dynamic_table"');
  
    process.exit(1);
  }

  if (!filePath ) {
  console.error('❌ Usage: node read-file-to-db.js <file_path> <db_name> [table_name]');
  process.exit(1);
}

console.log(`📂 File: ${filePath}`);
console.log(`📄 Table: ${tableName}`);

const ext = path.extname(filePath).toLowerCase();
console.log(`📂 File extension: ${ext}`);
function cleanHeader(header) {
  if (!header) return 'undefined';
  return header.replace(/%/g, '').replace(/^[-]+/, '').trim().toLowerCase();
}

async function readCSV(filePath) {
  return new Promise((resolve, reject) => {
    const rows = [];
    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (row) => rows.push(row))
      .on('end', () => resolve(rows))
      .on('error', reject);
  });
}

function readXLSX(filePath) {
  const workbook = xlsx.readFile(filePath);
  const sheet = workbook.Sheets[workbook.SheetNames[0]];
  return xlsx.utils.sheet_to_json(sheet);
}

function cleanData(rawRows,batchid) {
  const cleaned = [];
  const faults = [];
let i = 0;
  for (const row of rawRows) {
    const newRow = {};
    let hasUndefined = false;

    for (const key in row) {
      const cleanedKey = cleanHeader(key)
      if (cleanedKey === 'undefined') {
        hasUndefined = true;
        break;
      }
      newRow[cleanedKey] = row[key];
      newRow.batchid = batchid; // Add batchid to each row
    }
    if(i=0) console.log("final header is ", Object.keys(newRow))
      i++
    if (hasUndefined) {
      faults.push(row);
    } else {
      cleaned.push(newRow);
    }
  }

  return { cleaned, faults };
}
function getBatchId(periodicity_minutes = 5) {
  const now = new Date();

  // Truncate to the start of the hour
  const startOfHour = new Date(now);
  startOfHour.setMinutes(0, 0, 0);

  // How many 5-min blocks have passed since the start of the hour
  const minutes = now.getMinutes();
  const block = Math.floor(minutes / periodicity_minutes);

  // Add the block * periodicity to the hour start
  const result = new Date(startOfHour.getTime() + block * periodicity_minutes * 60000);

  // Format as YYYYMMDDHHMM
  const pad = (n) => String(n).padStart(2, "0");
  const batchid =
    result.getFullYear() +
    pad(result.getMonth() + 1) +
    pad(result.getDate()) +
    pad(result.getHours()) +
    pad(result.getMinutes());

  return batchid;
}
const batchid = getBatchId();

console.log(`📊 Start Main code`);
(async () => {
  try {
    const rawData = ext === '.csv' ? await readCSV(filePath)
                  : ext === '.xlsx' ? readXLSX(filePath)
                  : null;
    console.log(`📊 Read ${rawData.length} rows from file.`);
    if (!rawData || rawData.length === 0) {
      console.error('❌ No data found in file.');
      return;
    }
    console.log(`📊 Raw data: ${JSON.stringify(rawData[0])}`);
    const { cleaned, faults } = cleanData(rawData, batchid);
    console.log(`✅ Cleaned rows: ${cleaned.length}, ⚠️ Faulty: ${faults.length}`);

    console.log('connect to db')
    const sequelize = await connectDB();
    // drop table if exist 
    // Test simple query
    // try{
    // const query = `DROP TABLE IF EXSIT ${tableName}`; 
    // const [results, metadata] = await sequelize.query(query);

    // console.log('Query Results:', results);
    // console.log('Metadata:', metadata);

    // }catch(e){
    //   console.error('error during dropping table')
    // }
    console.log('🔌 Connected to DB');

    const columnNames = Object.keys(cleaned[0]);
    const DataModel = await createOrUpdateDynamicModel(sequelize, tableName, columnNames);
    console.log(`📋 Model ready for table "${tableName}" with columns: ${columnNames.join(', ')}`);
    // bulk create by 500 rows at a  time 
    console.log(`📦 Inserting ${cleaned.length} rows into "${tableName}" in chunks of 500`);
    for (let i = 0; i < cleaned.length; i += 500) {

      console.log(`📦 Processing chunk ${Math.ceil(i / 500) + 1} of ${Math.ceil(cleaned.length / 500)}`);
      const chunk = cleaned.slice(i, i + 500);
      console.log(`📦 Inserting chunk ${Math.ceil(i / 500) + 1} of ${Math.ceil(cleaned.length / 500)}`);
      await DataModel.bulkCreate(chunk);
    }
    //await DataModel.bulkCreate(cleaned);
    console.log(`📥 Inserted ${cleaned.length} rows into "${tableName}"`);

    if (faults.length > 0) {
      fs.writeFileSync('json_file_fault.json', JSON.stringify(faults, null, 2));
      console.log('⚠️ Faulty rows saved to json_file_fault.json');
    }

    await sequelize.close();
    console.log('✅ Database connection closed.');
  } catch (err) {
    console.error('❌ Error 161:', err);
  }
})();
