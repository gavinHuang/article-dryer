Article Dryer CLI Example

This example demonstrates using the article-dryer core library to summarize articles from URLs.

Setup:
1. Create a .env file in this directory with your OpenAI API key:
   OPENAI_API_KEY=your_api_key_here

Optional environment variables:
- OPENAI_MODEL: The model to use (default: gpt-4)
- OPENAI_API_BASE_URL: Custom API endpoint (default: https://api.openai.com/v1/chat/completions)

Usage:
npm run example:summarize
