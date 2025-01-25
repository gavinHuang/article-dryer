const express = require('express');
const router = express.Router();
const { processText } = require('../controllers/dryController');

router.post('/', async (req, res) => {
  try {
    const { text } = req.body;
    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
    }

    const processedContent = await processText(text);
    res.json({ processedContent });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: error.message || 'Internal server error' });
  }
});

module.exports = router;