const { Sequelize } = require('sequelize');
require('dotenv').config();

const db_user = process.env.DB_USER;
const db_pwd = process.env.DB_PWD;
const db_dhost = process.env.DB_DHOST || 'localhost';
const db_name = process.env.DB_NAME || 'default_db';
const db_port = process.env.DB_PORT || 5432; // Default PostgreSQL port


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
  });
}

module.exports = { connectDB };
