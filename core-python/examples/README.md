# Article Dryer Python Examples

This directory contains example scripts showing how to use the Article Dryer Python library.

## CLI Summarizer Example

A command-line tool that summarizes articles from URLs.

### Setup

1. Create a .env file in this directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

### Optional Environment Variables

- `OPENAI_MODEL`: The model to use (default: gpt-4)
- `OPENAI_API_BASE_URL`: Custom API endpoint (default: https://api.openai.com/v1/chat/completions)

### Usage

```bash
python cli_summarize.py
```
