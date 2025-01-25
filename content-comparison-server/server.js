const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
// Load environment variables from .env file
dotenv.config();
const dryRoutes = require('./routes/dryRoutes');

// Create Express app
const app = express();
const port = process.env.PORT || 5000;
// console.log('All Environment Variables:', process.env);

// Middleware
app.use(cors()); // Enable CORS
app.use(express.json()); // Parse JSON request bodies

// Routes
app.use('/api/dry', dryRoutes);

// Health check endpoint
app.get('/', (req, res) => {
  res.send('Article Dryer API is running!');
});

// Start the server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});