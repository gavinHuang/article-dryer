import { Pipeline, JinaReaderPlugin, SummarizerPlugin, PluginOutput } from '../src';
import * as readline from 'readline';
import * as dotenv from 'dotenv';
import { promises as fs } from 'fs';
import * as path from 'path';

// Load environment variables from .env file
dotenv.config();

function validateEnvironment() {
  const requiredEnvVars = ['OPENAI_API_KEY'];
  const missing = requiredEnvVars.filter(v => !process.env[v]);
  
  if (missing.length > 0) {
    console.error('\x1b[31mError: Missing required environment variables:\x1b[0m');
    console.error(missing.map(v => `  - ${v}`).join('\n'));
    console.error('\nPlease create a .env file with the following variables:');
    console.error('OPENAI_API_KEY=your_api_key_here');
    process.exit(1);
  }

  // Validate API key format
  const apiKey = process.env.OPENAI_API_KEY?.trim();
  if (!apiKey?.startsWith('sk-')) {
    console.error('\x1b[31mError: Invalid OpenAI API key format\x1b[0m');
    console.error('The API key should:');
    console.error('1. Start with "sk-"');
    console.error('2. Not include quotes or extra whitespace');
    console.error('3. Be copied exactly as shown in your OpenAI dashboard');
    process.exit(1);
  }
}

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

async function main() {
  try {
    // Validate environment variables first
    validateEnvironment();

    // Configure pipeline with plugins
    const pipeline = new Pipeline()
      .addPlugin(new JinaReaderPlugin({ skipImages: true }))
      .addPlugin(new SummarizerPlugin({
        apiKey: process.env.OPENAI_API_KEY,
        model: process.env.OPENAI_MODEL || 'gpt-4',
        baseURL: process.env.OPENAI_API_BASE_URL,
        stream: true,
        maxTokens: 1000
      }))
      .setOutputHandler(async (output: PluginOutput) => {
        if (output.type === 'error') {
          console.error('\x1b[31m%s\x1b[0m', output.content);
        } else if (output.type === 'text') {
          process.stdout.write(output.content);
        } else {
          console.log('\x1b[36m%s\x1b[0m', JSON.stringify(output.content, null, 2));
        }
      });

    // Get URL input
    const url = await new Promise<string>((resolve) => {
      rl.question('\nEnter article URL: ', resolve);
    });

    if (!url.trim()) {
      throw new Error('URL is required');
    }

    try {
      new URL(url); // Validate URL format
    } catch {
      throw new Error('Invalid URL format. URL must start with http:// or https://');
    }

    // Process the URL
    console.log('\nProcessing URL:', url, '\n');
    const result = await pipeline.process(url);

    // Show final summary
    if (result.metadata.summary) {
      console.log('\n\x1b[32mFinal Summary:\x1b[0m\n');
      console.log(result.metadata.summary);
    } else {
      console.log('\n\x1b[33mNo summary generated\x1b[0m');
    }

  } catch (error) {
    console.error('\n\x1b[31mError:\x1b[0m', error instanceof Error ? error.message : String(error));
    if (error instanceof Error && error.message.includes('Unauthorized')) {
      console.error('\nPlease check that your OPENAI_API_KEY is valid and has sufficient permissions.');
    }
  } finally {
    rl.close();
  }
}

// Create a README to help users get started
const readme = `Article Dryer CLI Example

This example demonstrates using the article-dryer core library to summarize articles from URLs.

Setup:
1. Create a .env file in this directory with your OpenAI API key:
   OPENAI_API_KEY=your_api_key_here

Optional environment variables:
- OPENAI_MODEL: The model to use (default: gpt-4)
- OPENAI_API_BASE_URL: Custom API endpoint (default: https://api.openai.com/v1/chat/completions)

Usage:
npm run example:summarize
`;

// Write README if it doesn't exist
fs.access(path.join(__dirname, 'README.md'))
  .catch(() => fs.writeFile(path.join(__dirname, 'README.md'), readme))
  .then(() => main());