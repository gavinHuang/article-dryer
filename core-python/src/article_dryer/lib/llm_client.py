from typing import Optional, Callable, Union, Dict, Any, Awaitable
import re
import asyncio
from openai import OpenAI, APIError
from .stream_processor import StreamProcessor
from ..types import OutputHandler

class LLMClient:
    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None,
                 max_tokens: int = 1000, stream: bool = False):
        if not api_key or not api_key.startswith('sk-'):
            raise ValueError('Invalid API key format. OpenAI API keys should start with "sk-"')

        self.config = {
            'api_key': api_key,
            'model': model,
            'base_url': base_url,
            'max_tokens': max_tokens,
            'stream': stream
        }

        self.client = OpenAI(
            api_key=self.config['api_key'],
            base_url=self.config['base_url']
        )

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
            if error.status == 401:
                raise ValueError('Authentication failed: Invalid API key')
            elif error.status == 429:
                raise ValueError('Rate limit exceeded: Too many requests')
            elif error.status == 404:
                raise ValueError(f"Model '{self.config['model']}' not found")
            raise ValueError(f'API Error: {str(error)}')
        
        except Exception as error:
            if 'ENOTFOUND' in str(error):
                raise ConnectionError(
                    f"Network error: Unable to connect to LLM API. Check your internet connection "
                    f"and API endpoint ({self.config['base_url'] or 'default OpenAI endpoint'})"
                )
            raise
