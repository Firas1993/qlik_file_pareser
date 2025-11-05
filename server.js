const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const FileProcessorService = require('./fileProcessorService');

const app = express();
const port = process.env.APP_PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// CORS middleware for frontend integration
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  
  if (req.method === 'OPTIONS') {
    res.sendStatus(200);
  } else {
    next();
  }
});

// IP Logging Middleware - Log every request with IP and details
app.use((req, res, next) => {
  const clientIP = req.headers['x-forwarded-for'] || 
                   req.headers['x-real-ip'] || 
                   req.connection.remoteAddress || 
                   req.socket.remoteAddress || 
                   (req.connection.socket ? req.connection.socket.remoteAddress : null) ||
                   req.ip;

  const timestamp = new Date().toISOString();
  const userAgent = req.headers['user-agent'] || 'Unknown';
  const method = req.method;
  const url = req.url;
  const referer = req.headers['referer'] || 'Direct';
  
  // Clean IP (remove IPv6 wrapper if present)
  const cleanIP = clientIP ? clientIP.replace(/^::ffff:/, '') : 'Unknown';
  
  // Log format: [TIMESTAMP] IP | METHOD URL | User-Agent | Referer
  console.log(`🔍 [${timestamp}] IP: ${cleanIP} | ${method} ${url} | UA: ${userAgent.substring(0, 100)} | Ref: ${referer}`);
  
  // Also log to file if LOG_FILE is set in .env
  if (process.env.LOG_FILE) {
    const logEntry = `[${timestamp}] IP: ${cleanIP} | ${method} ${url} | UA: ${userAgent} | Ref: ${referer}\n`;
    
    // Create logs directory if it doesn't exist
    const logDir = path.dirname(process.env.LOG_FILE);
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }
    
    // Append to log file
    fs.appendFile(process.env.LOG_FILE, logEntry, (err) => {
      if (err) console.error('❌ Error writing to log file:', err.message);
    });
  }
  
  next();
});

// Create uploads directory if it doesn't exist
const uploadsDir = process.env.UPLOAD_DIR || './uploads';
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    // Always use the same filename to ensure only one file exists
    const ext = path.extname(file.originalname);
    cb(null, `uploaded_file${ext}`);
  }
});

const fileFilter = (req, file, cb) => {
  const allowedMimes = [
    'text/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ];
  
  const allowedExtensions = ['.csv', '.xlsx', '.xls'];
  const fileExtension = path.extname(file.originalname).toLowerCase();
  
  if (allowedMimes.includes(file.mimetype) || allowedExtensions.includes(fileExtension)) {
    cb(null, true);
  } else {
    cb(new Error('Invalid file type. Only CSV and Excel files are allowed.'), false);
  }
};

const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: {
    fileSize: 50 * 1024 * 1024 // 50MB limit
  }
});

// Initialize service
const fileProcessor = new FileProcessorService();

// Routes

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    service: 'Qlik File Parser API'
  });
});

// Get API information
app.get('/api/info', (req, res) => {
  res.json({
    name: 'Qlik File Parser API',
    version: '2.0.1',
    description: 'API for parsing CSV and Excel files and saving to database',
    endpoints: {
      'POST /api/upload': 'Upload and process file',
      'POST /api/process': 'Process file by path',
      'GET /health': 'Health check',
      'GET /api/info': 'API information'
    },
    supportedFormats: ['.csv', '.xlsx'],
    maxFileSize: '50MB'
  });
});

// Upload and process file endpoint
app.post('/api/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No file uploaded'
      });
    }

    const { tableName } = req.body;
    
    if (!tableName) {
      return res.status(400).json({
        success: false,
        error: 'Table name is required'
      });
    }

    console.log(`📤 Processing uploaded file: ${req.file.originalname}`);
    console.log(`📁 Saved to: ${req.file.path}`);
    console.log(`🏷️ Table name: ${tableName}`);

    const result = await fileProcessor.processFile(req.file.path, tableName);

    // Store metadata about the file for later use
    const metadataPath = path.join(uploadsDir, 'file_metadata.json');
    const metadata = {
      originalFileName: req.file.originalname,
      uploadedPath: req.file.path,
      originalTableName: tableName,
      uploadTime: new Date().toISOString(),
      fileSize: req.file.size,
      lastProcessedTable: tableName
    };
    fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));

    // DON'T delete the file - keep it for potential re-processing
    res.json({
      success: true,
      message: 'File processed successfully',
      data: {
        ...result,
        originalFileName: req.file.originalname,
        fileSize: req.file.size,
        uploadedFilePath: req.file.path,
        originalTableName: tableName
      }
    });

  } catch (error) {
    console.error('❌ Upload processing error:', error.message);
    
    res.status(500).json({
      success: false,
      error: error.message,
      uploadedFilePath: req.file ? req.file.path : null
    });
  }
});

// Re-process uploaded file with same table name
app.post('/api/reprocess', async (req, res) => {
  try {
    // Look for the uploaded file (hardcoded name pattern)
    const possibleFiles = [
      path.join(uploadsDir, 'uploaded_file.csv'),
      path.join(uploadsDir, 'uploaded_file.xlsx'),
      path.join(uploadsDir, 'uploaded_file.xls')
    ];

    let filePath = null;
    for (const file of possibleFiles) {
      if (fs.existsSync(file)) {
        filePath = file;
        break;
      }
    }

    if (!filePath) {
      return res.status(404).json({
        success: false,
        error: 'No uploaded file found. Please upload a file first.'
      });
    }

    // Load metadata to get original table name
    const metadataPath = path.join(uploadsDir, 'file_metadata.json');
    let tableName = 'default_table'; // fallback

    if (fs.existsSync(metadataPath)) {
      try {
        const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
        tableName = metadata.originalTableName || metadata.lastProcessedTable || 'default_table';
      } catch (error) {
        console.error('Error reading metadata:', error.message);
      }
    }

    console.log(`🔄 Re-processing uploaded file: ${filePath}`);
    console.log(`🏷️ Using table name: ${tableName}`);

    const result = await fileProcessor.processFile(filePath, tableName);

    // Update metadata with last processed time
    if (fs.existsSync(metadataPath)) {
      try {
        const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
        metadata.lastProcessTime = new Date().toISOString();
        fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));
      } catch (error) {
        console.error('Error updating metadata:', error.message);
      }
    }

    res.json({
      success: true,
      message: 'File re-processed successfully',
      data: result
    });

  } catch (error) {
    console.error('❌ Re-process error:', error.message);
    
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({
        success: false,
        error: 'File too large. Maximum size is 50MB.'
      });
    }
  }

  console.error('❌ Unhandled error:', error);
  res.status(500).json({
    success: false,
    error: error.message || 'Internal server error'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found'
  });
});

// Start server
app.listen(port, () => {
  console.log(`🚀 Qlik File Parser API running on port ${port}`);
  console.log(`📋 API Info: http://localhost:${port}/api/info`);
  console.log(`💚 Health Check: http://localhost:${port}/health`);
  console.log(`📤 Upload Endpoint: POST http://localhost:${port}/api/upload`);
  console.log(`🔄 Re-process Endpoint: POST http://localhost:${port}/api/reprocess`);
});

module.exports = app;