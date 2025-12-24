const XLSX = require('xlsx');
const fs = require('fs');
const { exec } = require('child_process');

// 1. Load the file
// cellDates: true forces the library to convert Excel Serial numbers (44567) 
// into actual JavaScript Date objects immediately.
const workbook = XLSX.readFile('invoice_by_client/invoice_mars_client.xlsx', { cellDates: true });

// 2. Get the first sheet name
const firstSheetName = workbook.SheetNames[0];
const worksheet = workbook.Sheets[firstSheetName];

// 3. Convert to CSV
// This function handles the date objects and turns them into readable strings
const csvContent = XLSX.utils.sheet_to_csv(worksheet, {
   facture_date: 'yyyy-mm-dd' // Force specific date format (optional)
});

// 4. Write to file
fs.writeFileSync('output.csv', csvContent);

console.log('Conversion complete! Check output.csv');

// TODO the command node read-file-2-db.js output.csv qlik_invoice_raw
// exec(`node read-file-2-db.js output.csv qlik_invoice_raw`, (error, stdout, stderr) => {
//     if (error) {
//         console.error(`Error executing command: ${error.message}`);
//         return;
//     }
//     if (stderr) {
//         console.error(`stderr: ${stderr}`);
//         return;
//     }
//     console.log(`stdout: ${stdout}`);
// });