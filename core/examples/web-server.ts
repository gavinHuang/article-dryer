/// <reference types="express" />
import express, { Request, Response } from 'express';
import { Pipeline, JinaReaderPlugin, SummarizerPlugin } from '../src';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const app = express();
app.use(express.json());

// Validate environment
function validateEnvironment() {
  if (!process.env.OPENAI_API_KEY?.trim()) {
    console.error('\x1b[31mError: OPENAI_API_KEY environment variable is required\x1b[0m');
    process.exit(1);
  }
}

// Create a reusable pipeline factory
function createPipeline(res: Response) {
  return new Pipeline()
    .addPlugin(new JinaReaderPlugin({ skipImages: true }))
    .addPlugin(new SummarizerPlugin({
      apiKey: process.env.OPENAI_API_KEY!,
      model: process.env.OPENAI_MODEL || 'gpt-4',
      stream: true,
      maxTokens: 1000
    }))
    .bindToWeb(res, {
      onChunk: async (chunk) => {
        res.write(`data: ${JSON.stringify({ content: chunk })}\n\n`);
      },
      onError: async (error) => {
        res.write(`data: ${JSON.stringify({ error: error.message })}\n\n`);
      },
      onComplete: async () => {
        res.write('data: [DONE]\n\n');
        res.end();
      }
    });
}

interface SummarizeRequest {
  url: string;
}

app.post('/summarize', async (req: Request<{}, {}, SummarizeRequest>, res: Response) => {
  const { url } = req.body;

  if (!url) {
    res.status(400).json({ error: 'URL is required' });
    return;
  }

  try {
    // Validate URL format
    new URL(url);

    // Set headers for SSE
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    // Create and run pipeline
    const pipeline = createPipeline(res);
    await pipeline.processWebRequest({
      body: url,
      method: 'POST',
      headers: {}
    });
  } catch (error) {
    if (!res.headersSent) {
      res.status(500).json({ 
        error: error instanceof Error ? error.message : 'Failed to process URL' 
      });
    }
  }
});

app.get('/health', (_: Request, res: Response) => {
  res.json({ status: 'ok' });
});

// Start server
const PORT = process.env.PORT || 3000;

validateEnvironment();
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log('\nAvailable endpoints:');
  console.log('POST /summarize - Summarize article from URL');
  console.log('GET  /health   - Health check\n');
});