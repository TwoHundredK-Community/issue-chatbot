const sql = require('mssql');
const express = require('express');
const bodyParser = require('body-parser');
const { Sequelize, DataTypes } = require('sequelize');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 4000;

// Middleware
app.use(bodyParser.json());

// Azure SQL connection
const sequelize = new Sequelize(
  process.env.DB_NAME,
  process.env.DB_USER,
  process.env.DB_PASS,
  {
    host: process.env.DB_SERVER,
    dialect: 'mssql',
    dialectOptions: {
      encrypt: process.env.DB_ENCRYPT === 'true',
      options: {
        requestTimeout: 30000, // 30 seconds
      },
    },
  }
);

// Define a model for logging requests
const Log = sequelize.define('Log', {
  ip: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  content: {
    type: DataTypes.TEXT,
    allowNull: false,
  },
  createdAt: {
    type: DataTypes.DATE,
    defaultValue: Sequelize.NOW,
  },
});

// Sync database
sequelize.sync();

// Rate limiter middleware
const limiter = rateLimit({
  windowMs: 24 * 60 * 60 * 1000, // 24 hours
  max: 3, // Limit each IP to 3 requests per windowMs
  message: 'Usage limit exceeded. Please try again after 24 hours.',
  keyGenerator: (req) => req.ip,
});

// Apply rate limiter to all routes
app.use(limiter);

app.post('/log', async (req, res) => {
  const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
  const content = req.body.message;

  try {
    const pool = await poolPromise;

    // Count requests today
    const { recordset } = await pool.request()
      .input('ip', sql.NVarChar, ip)
      .query(`
        SELECT COUNT(*) as count 
        FROM logs 
        WHERE ip_address = @ip AND DATEDIFF(DAY, request_time, GETDATE()) = 0
      `);

    const count = recordset[0].count;

    if (count >= 3) {
      return res.status(429).json({ message: 'Usage limit reached. Try again in 24 hours.' });
    }

    await pool.request()
      .input('ip', sql.NVarChar, ip)
      .input('content', sql.NVarChar, content)
      .query('INSERT INTO logs (ip_address, request_content) VALUES (@ip, @content)');

    res.json({ message: 'Logged successfully' });
  } catch (err) {
    console.error(err);
    res.status(500).send('Internal server error');
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});