from typing import Optional, Callable, Union, Dict, Any, Awaitable
import re
import asyncio
import os
import traceback  # Add traceback import
import ssl
import certifi
from openai import OpenAI, APIError
from dotenv import load_dotenv
from .stream_processor import StreamProcessor
from ..types import OutputHandler

# Load environment variables from .env file
load_dotenv()

class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o", base_url: Optional[str] = None,
                 max_tokens: int = 1000, stream: bool = False, verify_ssl: bool = True):
        # Try to load API key from multiple possible environment variables
        if api_key is None:
            api_key = os.getenv('API_KEY') or os.getenv('OPENAI_API_KEY')
            
        if not api_key:
            raise ValueError('API key is required. Please provide it or set the API_KEY or OPENAI_API_KEY environment variable.')

        self.config = {
            'api_key': api_key,
            'model': model,
            'base_url': base_url,
            'max_tokens': max_tokens,
            'stream': stream,
            'verify_ssl': verify_ssl
        }

        # Configure OpenAI client with appropriate SSL verification settings
        client_params = {
            'api_key': self.config['api_key'],
            'base_url': self.config['base_url']
        }
        
        # Add SSL verification options
        # if not verify_ssl:
        #     # Create a custom SSL context that doesn't verify certificates
        #     ssl_context = ssl.create_default_context()
        #     ssl_context.check_hostname = False
        #     ssl_context.verify_mode = ssl.CERT_NONE
        #     client_params['http_client'] = {
        #         'ssl_context': ssl_context
        #     }
        
        self.client = OpenAI(**client_params)

    async def generate_response(
        self, 
        content: str, 
        system_prompt: str = "You are a helpful assistant that summarizes text concisely.",
        output_handler: Optional[OutputHandler] = None
    ) -> str:
        try:
            params = {
                'model': self.config['model'],
                'messages': [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ],
                'max_tokens': self.config['max_tokens'],
                'stream': self.config['stream']
            }

            if self.config['stream']:
                async with StreamProcessor(output_handler) as stream_processor:
                    stream_response = self.client.chat.completions.create(**params)
                    full_response = ''
                    
                    for chunk in stream_response:
                        content = chunk.choices[0].delta.content or ''
                        if content:
                            await stream_processor.write(content)
                            full_response += content
                    
                    return full_response
            else:
                completion = self.client.chat.completions.create(**params)
                return completion.choices[0].message.content or ''

        except APIError as error:
            traceback.print_exc()  # Print detailed stack trace
            if error.status == 401:
                raise ValueError('Authentication failed: Invalid API key')
            elif error.status == 429:
                raise ValueError('Rate limit exceeded: Too many requests')
            elif error.status == 404:
                raise ValueError(f"Model '{self.config['model']}' not found")
            raise ValueError(f'API Error: {str(error)}')
        
        except Exception as error:
            traceback.print_exc()  # Print detailed stack trace
            if 'ENOTFOUND' in str(error):
                raise ConnectionError(
                    f"Network error: Unable to connect to LLM API. Check your internet connection "
                    f"and API endpoint ({self.config['base_url'] or 'default OpenAI endpoint'})"
                )
            raise
