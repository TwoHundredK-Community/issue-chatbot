require('dotenv').config();
const sql = require('mssql');

const config = {
  user: process.env.DB_USER,
  password: process.env.DB_PASS,
  database: process.env.DB_NAME,
  server: process.env.DB_SERVER,
  options: {
    encrypt: process.env.DB_ENCRYPT === 'true',
    trustServerCertificate: false
  }
};

const poolPromise = new sql.ConnectionPool(config)
  .connect()
  .then(pool => pool)
  .catch(err => console.error('SQL DB connection failed', err));

module.exports = { sql, poolPromise };