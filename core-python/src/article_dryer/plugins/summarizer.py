from typing import Dict, Any, Optional
from datetime import datetime
from ..types import Plugin, ContentData, OutputHandler
from ..lib.llm_client import LLMClient

class SummarizerPlugin(Plugin):
    name = 'summarizer'
    
    def __init__(self, config: Dict[str, Any]):
        if not config.get('api_key'):
            raise ValueError('API key is required for SummarizerPlugin. Set OPENAI_API_KEY environment variable.')
        
        try:
            self.llm_client = LLMClient(
                api_key=config['api_key'],
                model=config.get('model', 'gpt-4'),
                base_url=config.get('base_url'),
                max_tokens=config.get('max_tokens', 1000),
                stream=config.get('stream', True)
            )
        except Exception as error:
            raise RuntimeError(f'Failed to initialize LLM client: {str(error)}')

    async def process(self, data: ContentData, output_handler: Optional[OutputHandler] = None) -> ContentData:
        system_prompt = """Understand the meaning of this paragraph, rewrite it into a shorter version with keywords. 
        Return with markdown format like this:
        # Shortened
        Shortened text...
        # Keywords
        - keyword1
        - keyword2"""

        try:
            if output_handler:
                await output_handler({
                    'type': 'text',
                    'content': 'Generating summary...\n'
                })

            summary = await self.llm_client.generate_response(
                data.content,
                system_prompt,
                output_handler=output_handler  # Pass the output_handler directly
            )

            return ContentData(
                content=data.content,
                metadata={
                    **data.metadata,
                    'summary': summary,
                    'processedAt': datetime.now().isoformat()
                }
            )
            
        except Exception as error:
            error_message = str(error)
            is_auth_error = any(msg in error_message.lower() 
                              for msg in ['unauthorized', 'invalid api key'])
            
            if output_handler:
                await output_handler({
                    'type': 'error',
                    'content': ('Authentication failed: Please check your OpenAI API key (OPENAI_API_KEY)'
                              if is_auth_error else f'Summarization failed: {error_message}')
                })
            raise
