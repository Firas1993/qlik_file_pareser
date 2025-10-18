#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const xlsx = require('xlsx');

const filePath = process.argv[2];

if (!filePath) {
  console.error('❌ Please provide a file path. Example: node read-file.js data.csv');
  process.exit(1);
}

console.log(`📂 Reading file: ${filePath}`);

if (!fs.existsSync(filePath)) {
  console.error(`❌ File not found: ${filePath}`);
  process.exit(1);
}

const ext = path.extname(filePath).toLowerCase();
console.log(`📄 Detected file type: ${ext}`);

function cleanHeader(header) {
  if (!header) return 'undefined';
  let cleaned = header.replace(/%/g, '').replace(/^[-]+/, '');
  return cleaned;
}

function cleanData(headers, data) {
  const cleanedRows = [];
  const faultErrors = [];

  console.log(`🧪 Cleaning ${data.length} rows...`);

  data.forEach((row, index) => {
    const cleanedRow = {};
    let hasUndefined = false;

    Object.entries(row).forEach(([originalKey, value]) => {
      const cleanedKey = cleanHeader(originalKey);
      if (cleanedKey.toLowerCase() === 'undefined') {
        hasUndefined = true;
        console.log(`🚫 Row ${index + 1} skipped: header "${originalKey}" is undefined`);
        return;
      }
      cleanedRow[cleanedKey] = value;
    });

    if (hasUndefined) {
      faultErrors.push(row);
    } else {
      cleanedRows.push(cleanedRow);
    }
  });

  return { cleanedRows, faultErrors };
}

async function readCSV(filePath) {
  console.log('📊 Reading CSV file...');
  return new Promise((resolve, reject) => {
    const rows = [];
    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (row) => {
        console.log('📥 CSV Row:', row);
        rows.push(row);
      })
      .on('end', () => {
        console.log('✅ CSV reading finished');
        resolve(rows);
      })
      .on('error', (err) => {
        console.error('❌ CSV parse error:', err.message);
        reject(err);
      });
  });
}

function readXLSX(filePath) {
  console.log('📊 Reading XLSX file...');
  const workbook = xlsx.readFile(filePath);
  //
  const sheetName = workbook.SheetNames[0];
  console.log(`📄 Using sheet: ${sheetName}`);
  const sheetData = xlsx.utils.sheet_to_json(workbook.Sheets[sheetName]);
  console.log('✅ XLSX reading finished');
  return sheetData;
}

(async function main() {
  try {
    let rawData = [];

    if (ext === '.csv') {
      rawData = await readCSV(filePath);
    } else if (ext === '.xlsx') {
      rawData = await readXLSX(filePath);
    } else {
      console.error('❌ Unsupported file type');
      return;
    }

    console.log(`🔍 Total raw rows: ${rawData.length}`);

    const { cleanedRows, faultErrors } = cleanData(Object.keys(rawData[0] || {}), rawData);

    fs.writeFileSync('json_file_confirmer.json', JSON.stringify(cleanedRows, null, 2));
    fs.writeFileSync('json_file_fault.json', JSON.stringify(faultErrors, null, 2));

    console.log(`✅ Cleaned rows saved to json_file_confirmer.json (${cleanedRows.length} rows)`);
    console.log(`⚠️ Faulty rows saved to json_file_fault.json (${faultErrors.length} rows)`);
  } catch (err) {
    console.error('❌ Error:', err.message);
  }
})();
