import fetch from 'node-fetch';
import { Readable } from 'stream';

async function testWebServer() {
  const url = process.argv[2] || 'https://example.com/article';
  console.log('\nTesting web server with URL:', url);

  try {
    const response = await fetch('http://localhost:3000/summarize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Convert response to readable stream
    const stream = Readable.from(response.body);
    const decoder = new TextDecoder();
    let buffer = '';

    // Process chunks as they arrive
    for await (const chunk of stream) {
      buffer += decoder.decode(chunk, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || ''; // Keep the last incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            console.log('\nProcessing complete!');
            return;
          }

          try {
            const parsed = JSON.parse(data);
            if (parsed.error) {
              console.error('\x1b[31mError:\x1b[0m', parsed.error);
            } else if (parsed.content) {
              process.stdout.write(parsed.content);
            }
          } catch (e) {
            console.error('Failed to parse server response:', e);
          }
        }
      }
    }

    // Process any remaining data in buffer
    if (buffer.startsWith('data: ')) {
      const data = buffer.slice(6);
      if (data !== '[DONE]') {
        try {
          const parsed = JSON.parse(data);
          if (parsed.error) {
            console.error('\x1b[31mError:\x1b[0m', parsed.error);
          } else if (parsed.content) {
            process.stdout.write(parsed.content);
          }
        } catch (e) {
          console.error('Failed to parse server response:', e);
        }
      }
    }

  } catch (error) {
    console.error('\x1b[31mError:\x1b[0m', error instanceof Error ? error.message : String(error));
  }
}

// Run the test if this file is executed directly
if (require.main === module) {
  if (process.argv.length < 3) {
    console.log('\nUsage: ts-node test-web-server.ts <url>');
    console.log('Example: ts-node test-web-server.ts https://example.com/article\n');
    process.exit(1);
  }
  testWebServer();
}