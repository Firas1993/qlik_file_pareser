const XLSX = require('xlsx');
const fs = require('fs');
const { exec } = require('child_process');

// 1. Load the file path from CLI and validate
const inputPath = process.argv[2];
if (!inputPath) {
   console.error('Usage: node xl_2_csv.js <input-xlsx-path>');
   process.exit(1);
}
if (!fs.existsSync(inputPath)) {
   console.error(`Error: file does not exist: ${inputPath}`);
   process.exit(2);
}
const stat = fs.statSync(inputPath);
if (!stat.isFile()) {
   console.error(`Error: path is not a file: ${inputPath}`);
   process.exit(3);
}
// cellDates: true forces the library to convert Excel Serial numbers into Date objects.
const workbook = XLSX.readFile(inputPath, { cellDates: true });

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