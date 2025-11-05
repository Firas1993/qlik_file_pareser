const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const xlsx = require('xlsx');

const { connectDB } = require('./db');
const { createOrUpdateDynamicModel } = require('./model');

class FileProcessorService {
  constructor() {
    this.sequelize = null;
  }

  cleanHeader(header) {
    if (!header) return 'undefined';
    return header.replace(/%/g, '').replace(/^[-]+/, '').trim().toLowerCase();
  }

  async readCSV(filePath) {
    return new Promise((resolve, reject) => {
      const rows = [];
      fs.createReadStream(filePath)
        .pipe(csv())
        .on('data', (row) => rows.push(row))
        .on('end', () => resolve(rows))
        .on('error', reject);
    });
  }

  readXLSX(filePath) {
    const workbook = xlsx.readFile(filePath);
    const sheet = workbook.Sheets[workbook.SheetNames[0]];
    return xlsx.utils.sheet_to_json(sheet);
  }

  cleanData(rawRows, batchid) {
    const cleaned = [];
    const faults = [];
    let i = 0;

    for (const row of rawRows) {
      const newRow = {};
      let hasUndefined = false;

      for (const key in row) {
        const cleanedKey = this.cleanHeader(key);
        if (cleanedKey === 'undefined') {
          hasUndefined = true;
          break;
        }
        newRow[cleanedKey] = row[key];
        newRow.batchid = batchid;
      }

      if (i === 0) console.log("Final header is:", Object.keys(newRow));
      i++;

      if (hasUndefined) {
        faults.push(row);
      } else {
        cleaned.push(newRow);
      }
    }

    return { cleaned, faults };
  }

  getBatchId(periodicity_minutes = 5) {
    const now = new Date();
    const startOfHour = new Date(now);
    startOfHour.setMinutes(0, 0, 0);

    const minutes = now.getMinutes();
    const block = Math.floor(minutes / periodicity_minutes);

    const result = new Date(startOfHour.getTime() + block * periodicity_minutes * 60000);

    const pad = (n) => String(n).padStart(2, "0");
    const batchid =
      result.getFullYear() +
      pad(result.getMonth() + 1) +
      pad(result.getDate()) +
      pad(result.getHours()) +
      pad(result.getMinutes());

    return batchid;
  }

  async processFile(filePath, tableName) {
    try {
      console.log(`📂 Processing file: ${filePath}`);
      console.log(`📄 Target table: ${tableName}`);

      const ext = path.extname(filePath).toLowerCase();
      console.log(`📂 File extension: ${ext}`);

      if (!['.csv', '.xlsx'].includes(ext)) {
        throw new Error(`Unsupported file format: ${ext}. Only .csv and .xlsx are supported.`);
      }

      const rawData = ext === '.csv' ? await this.readCSV(filePath) : this.readXLSX(filePath);
      console.log(`📊 Read ${rawData.length} rows from file.`);

      if (!rawData || rawData.length === 0) {
        throw new Error('No data found in file.');
      }

      const batchid = this.getBatchId();
      const { cleaned, faults } = this.cleanData(rawData, batchid);
      console.log(`✅ Cleaned rows: ${cleaned.length}, ⚠️ Faulty: ${faults.length}`);

      // Connect to database
      this.sequelize = await connectDB();
      console.log('🔌 Connected to DB');

      const columnNames = Object.keys(cleaned[0]);
      const DataModel = await createOrUpdateDynamicModel(this.sequelize, tableName, columnNames);
      console.log(`📋 Model ready for table "${tableName}" with columns: ${columnNames.join(', ')}`);

      // Bulk insert in chunks
      console.log(`📦 Inserting ${cleaned.length} rows into "${tableName}" in chunks of 500`);
      for (let i = 0; i < cleaned.length; i += 500) {
        console.log(`📦 Processing chunk ${Math.ceil(i / 500) + 1} of ${Math.ceil(cleaned.length / 500)}`);
        const chunk = cleaned.slice(i, i + 500);
        await DataModel.bulkCreate(chunk, { 
          ignoreDuplicates: true,
          returning: true
        });
      }

      console.log(`📥 Inserted ${cleaned.length} rows into "${tableName}"`);

      // Save faulty rows if any
      let faultFilePath = null;
      if (faults.length > 0) {
        faultFilePath = path.join(process.cwd(), `fault_${tableName}_${batchid}.json`);
        fs.writeFileSync(faultFilePath, JSON.stringify(faults, null, 2));
        console.log(`⚠️ Faulty rows saved to ${faultFilePath}`);
      }

      await this.sequelize.close();
      console.log('✅ Database connection closed.');

      return {
        success: true,
        processedRows: cleaned.length,
        faultyRows: faults.length,
        tableName,
        batchid,
        faultFilePath,
        columnNames
      };

    } catch (error) {
      if (this.sequelize) {
        await this.sequelize.close();
      }
      console.error('❌ Error:', error.message);
      throw error;
    }
  }
}

module.exports = FileProcessorService;