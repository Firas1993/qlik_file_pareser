const { Sequelize } = require('sequelize');
require('dotenv').config();

const db_user = process.env.DB_USER;
const db_pwd = process.env.DB_PASSWORD;
const db_dhost = process.env.DB_HOST ;
const db_name = process.env.DB_NAME;
const db_port = process.env.DB_PORT || 5432; // Default PostgreSQL port

if (!db_user || !db_pwd || !db_dhost || !db_name) {
  console.error('❌ Missing required database environment variables.');
  process.exit(1);
}

console.log(`🔍 Connecting to:`);
console.log(`- DB:      ${db_name}`);
console.log(`- Host:    ${db_dhost}`);
console.log(`- Port:    ${db_port}`);
console.log(`- User:    ${db_user}`);
function connectDB(dbName) {
  return new Sequelize(
    db_name,
    db_user,
    db_pwd,
    {
      host: db_dhost,
      dialect: 'postgres', // or 'mysql'
      logging: false, // Disable logging; default: console.log
      port: db_port,
      // logging: console.log
  });
}

module.exports = { connectDB };
