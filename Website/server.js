// server.js
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');


const app = express();
const PORT = 3000;

app.use(express.json());
// Serve static files
app.use(express.static('public'));

// Connect to SQLite database
const db = new sqlite3.Database('./clothes.db', (err) => {
  if (err) {
    console.error('Error opening database:', err);
  } else {
    console.log('Connected to SQLite database');
  }
});

// API endpoint to get all clothes, ordered by ID descending (newest first)
app.get('/api/clothes', (req, res) => {
    db.all('SELECT * FROM clothes WHERE seen != 1 ORDER BY "cIndex" DESC', [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});
app.get("/api/clothes/kill", (req, res) => {
  db.all('UPDATE clothes SET seen = 1', [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
})

app.post('/api/clothes/index', (req, res) => {
  if (!req.body || !req.body.brand) {
    return res.status(400).json({ error: "Missing brand" });
  }

  const brand = `${req.body.brand.toLowerCase()}`;

  // Step 1: get 
  db.get(
    `SELECT cIndex FROM clothes
     WHERE seen != 1
     ORDER BY cIndex DESC
     LIMIT 1`,
    (err, row) => {
      if (err) {
        return res.status(500).json({ error: err.message });
      }

      if (!row) {
        return res.status(404).json({ error: "No match found" });
      }

      const targetIndex = row.cIndex;

      // Step 2: count how many seen=1 items are above it
      db.get(
        `SELECT cIndex FROM clothes
         WHERE seen != 1 AND
         LOWER(brand) == ?
         ORDER BY cIndex DESC
         LIMIT 1`,
        [brand],
        (err2, result) => {
          if (err2) {
            return res.status(500).json({ error: err2.message });
          }
          let index = 0
          if(result){
            index = targetIndex - result.cIndex
          }
          
          res.json({
            index: index
          });
        }
      );
    }
  );
});

// Serve the main page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  db.close((err) => {
    if (err) {
      console.error(err.message);
    }
    console.log('Database connection closed');
    process.exit(0);
  });
});

/* 
 * public/index.html
 * Place this file in a 'public' folder in the same directory as server.js
 */
