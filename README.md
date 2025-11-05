# Qlik File Parser API

A Node.js application that parses CSV and Excel files and saves the data to a PostgreSQL database. The application supports both CLI usage and HTTP API endpoints for frontend integration.

## Features

- ✅ Parse CSV and Excel (.xlsx) files
- ✅ Clean and validate data
- ✅ Dynamic table creation based on file headers
- ✅ Batch processing with unique batch IDs
- ✅ Error handling and fault logging
- ✅ CLI interface
- ✅ RESTful API endpoints
- ✅ File upload support
- ✅ Frontend web interface

## Installation

1. Clone the repository
2. Install dependencies:
```bash
npm install
```

3. Configure environment variables in `.env` file:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
APP_PORT=3000
UPLOAD_DIR=./uploads
```

## Usage

### CLI Mode (Original)

```bash
node read-file-2-db.js <file_path> <table_name>
```

Example:
```bash
node read-file-2-db.js ./data/sales.csv sales_data
node read-file-2-db.js ./data/products.xlsx product_catalog
```

### API Server Mode (New)

1. Start the server:
```bash
npm start
# or
node server.js
```

2. Access the web interface at: `http://localhost:3000`

3. API will be available at: `http://localhost:3000/api`

## API Endpoints

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "OK",
  "timestamp": "2025-10-20T10:00:00.000Z",
  "service": "Qlik File Parser API"
}
```

### GET /api/info
Get API information and available endpoints

**Response:**
```json
{
  "name": "Qlik File Parser API",
  "version": "2.0.1",
  "description": "API for parsing CSV and Excel files and saving to database",
  "endpoints": { ... },
  "supportedFormats": [".csv", ".xlsx"],
  "maxFileSize": "200MB"
}
```

### POST /api/upload
Upload and process a file

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body:
  - `file`: File to upload (CSV or Excel)
  - `tableName`: Target database table name

**Response:**
```json
{
  "success": true,
  "message": "File processed successfully",
  "data": {
    "processedRows": 1250,
    "faultyRows": 5,
    "tableName": "sales_data",
    "batchid": "202510201430",
    "columnNames": ["id", "name", "amount", "date"],
    "originalFileName": "sales.csv",
    "fileSize": 102400,
    "faultFilePath": "./fault_sales_data_202510201430.json"
  }
}
```

### POST /api/process
Process a file by file path (for server-side files)

**Request:**
```json
{
  "filePath": "/path/to/file.csv",
  "tableName": "target_table"
}
```

**Response:**
```json
{
  "success": true,
  "message": "File processed successfully",
  "data": {
    "processedRows": 1250,
    "faultyRows": 5,
    "tableName": "target_table",
    "batchid": "202510201430",
    "columnNames": ["id", "name", "amount"],
    "faultFilePath": "./fault_target_table_202510201430.json"
  }
}
```

## Frontend Integration

### Using the Web Interface
Visit `http://localhost:3000` to use the built-in web interface for uploading and processing files.

### Using JavaScript Fetch API

```javascript
// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('tableName', 'my_table');

const response = await fetch('http://localhost:3000/api/upload', {
  method: 'POST',
  body: formData
});

const result = await response.json();
```

### Using cURL

```bash
# Upload file
curl -X POST http://localhost:3000/api/upload \
  -F "file=@./data/sample.csv" \
  -F "tableName=sample_data"

# Process file by path
curl -X POST http://localhost:3000/api/process \
  -H "Content-Type: application/json" \
  -d '{"filePath": "./data/sample.csv", "tableName": "sample_data"}'
```

## File Format Support

### CSV Files (.csv)
- Headers in first row
- Comma-separated values
- UTF-8 encoding recommended

### Excel Files (.xlsx)
- First worksheet is processed
- Headers in first row
- .xlsx format (Excel 2007+)

## Data Processing

### Header Cleaning
- Removes % symbols
- Removes leading dashes
- Converts to lowercase
- Trims whitespace

### Batch ID Generation
- Format: YYYYMMDDHHMM
- Generated based on 5-minute intervals
- Used for tracking and data lineage

### Error Handling
- Invalid headers are logged as faults
- Faulty rows saved to JSON file
- Database errors are captured and returned

## Database Schema

Tables are created dynamically based on file headers:
- All columns are created as TEXT type
- `batchid` column is automatically added
- Primary key is auto-generated if not present

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | Required |
| `DB_USER` | Database user | Required |
| `DB_PASSWORD` | Database password | Required |
| `APP_PORT` | API server port | 3000 |
| `UPLOAD_DIR` | File upload directory | ./uploads |

## Error Codes

| Status | Description |
|--------|-------------|
| 200 | Success |
| 400 | Bad Request (missing parameters, invalid file) |
| 404 | File not found |
| 500 | Internal Server Error (database, processing errors) |

## Security Notes

- File uploads are limited to 200MB
- Only CSV and Excel files are accepted
- CORS is enabled for all origins (configure for production)
- Uploaded files are automatically cleaned up after processing

## Development

### Scripts
```bash
npm start     # Start the server
npm run dev   # Start in development mode
```

### Project Structure
```
├── server.js                 # Express API server
├── fileProcessorService.js   # File processing service
├── read-file-2-db.js        # Original CLI script
├── db.js                    # Database connection
├── model.js                 # Sequelize models
├── public/
│   └── index.html           # Web interface
├── uploads/                 # File upload directory
└── .env                     # Environment configuration
```

## License

ISC License - See package.json for details.