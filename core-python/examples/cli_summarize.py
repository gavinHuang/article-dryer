from dotenv import load_dotenv
import os
from urllib.parse import urlparse
import sys
from typing import Any, Dict
import asyncio
from pathlib import Path

# Update imports to use local module path
sys.path.append(str(Path(__file__).parent.parent))
from article_dryer.pipeline import Pipeline
from article_dryer.plugins.jina_reader import JinaReaderPlugin
from article_dryer.plugins.summarizer import SummarizerPlugin
from article_dryer.plugins.text_statistics import TextStatisticsPlugin
from article_dryer.plugins.word_level_analyzer import WordLevelAnalyzerPlugin
from article_dryer.lib.llm_client import LLMClient

# Load environment variables
load_dotenv()

def validate_environment():
    required_env_vars = ['OPENAI_API_KEY']
    missing = [v for v in required_env_vars if not os.getenv(v)]
    
    if missing:
        print('\033[31mError: Missing required environment variables:\033[0m')
        print('\n'.join(f'  - {v}' for v in missing))
        print('\nPlease create a .env file with the following variables:')
        print('OPENAI_API_KEY=your_api_key_here')
        sys.exit(1)

    # Validate API key format
    api_key = os.getenv('OPENAI_API_KEY', '').strip()
    if not api_key.startswith('sk-'):
        print('\033[31mError: Invalid OpenAI API key format\033[0m')
        print('The API key should:')
        print('1. Start with "sk-"')
        print('2. Not include quotes or extra whitespace')
        print('3. Be copied exactly as shown in your OpenAI dashboard')
        sys.exit(1)

async def output_handler(output: Dict[str, Any]):
    if output['type'] == 'error':
        print(f'\033[31m{output["content"]}\033[0m')
    elif output['type'] == 'text':
        print(output['content'], end='')
    else:
        import json
        print(f'\033[36m{json.dumps(output["content"], indent=2)}\033[0m')

async def main():
    try:
        # Validate environment variables first
        validate_environment()

        # Create plugins with proper initialization
        jina_plugin = JinaReaderPlugin(skip_images=True)
        text_stats_plugin = TextStatisticsPlugin()
        
        # Create LLM client with SSL verification disabled and timeout
        # llm_client = LLMClient(verify_ssl=False)
        
        # Create and initialize WordLevelAnalyzerPlugin with the LLM client
        word_level_plugin = WordLevelAnalyzerPlugin()
        await word_level_plugin.initialize(context={})
        
        # Create summarizer plugin with correct configuration
        # Don't include the LLM client directly in the config dictionary
        summarizer_plugin = SummarizerPlugin(config={
            'stream': True,
            'max_tokens': 1000
        })
        # Set the LLM client separately if needed
        # summarizer_plugin.llm_client = llm_client

        # Configure pipeline with plugins
        pipeline = Pipeline()
        pipeline.add_plugin(jina_plugin)
        pipeline.add_plugin(text_stats_plugin)
        pipeline.add_plugin(word_level_plugin)
        pipeline.add_plugin(summarizer_plugin)
        pipeline.set_output_handler(output_handler)

        # Get URL input
        url = input('\nEnter article URL: ').strip()

        if not url:
            raise ValueError('URL is required')

        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError()
        except:
            raise ValueError('Invalid URL format. URL must start with http:// or https://')

        # Process the URL
        print(f'\nProcessing URL: {url}\n')
        result = await pipeline.process(url)

        # Show final summary
        if result.metadata.get('summary'):
            print('\n\033[32mFinal Summary:\033[0m\n')
            print(result.metadata['summary'])
        else:
            print('\n\033[33mNo summary generated\033[0m')

    except Exception as error:
        print(f'\n\033[31mError:\033[0m {str(error)}')
        if 'Unauthorized' in str(error):
            print('\nPlease check that your OPENAI_API_KEY is valid and has sufficient permissions.')

if __name__ == '__main__':
    # Create README if it doesn't exist
    readme_content = '''Article Dryer CLI Example

This example demonstrates using the article-dryer core library to summarize articles from URLs.

Setup:
1. Create a .env file in this directory with your OpenAI API key:
   OPENAI_API_KEY=your_api_key_here

Optional environment variables:
- OPENAI_MODEL: The model to use (default: gpt-4)
- OPENAI_API_BASE_URL: Custom API endpoint (default: https://api.openai.com/v1/chat/completions)

Usage:
python cli_summarize.py
'''
    
    readme_path = Path(__file__).parent / 'README.md'
    if not readme_path.exists():
        readme_path.write_text(readme_content)
    
    # Run the main function
    asyncio.run(main())
