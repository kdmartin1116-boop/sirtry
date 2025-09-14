import express from 'express';
import sqlite3 from 'sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Connect to SQLite database
const dbPath = path.resolve(__dirname, 'app_database.db');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error connecting to database:', err.message);
    } else {
        console.log('Connected to the SQLite database.');
    }
});

// Middleware to parse JSON bodies
app.use(express.json());

// Serve static files from the React app's build output
app.use(express.static(path.join(__dirname, 'dist')));

// API routes (will be added later)
app.get('/api/test', (req, res) => {
    res.json({ message: 'API is working!' });
});

// For any other request, serve the index.html from the dist folder
// This should be the last route handler
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'dist', 'src', 'index.html'));
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

// Close the database connection when the server is closed
process.on('SIGINT', () => {
    db.close((err) => {
        if (err) {
            console.error(err.message);
        }
        console.log('Closed the database connection.');
    });
});