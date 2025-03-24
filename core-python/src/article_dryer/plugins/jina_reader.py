import re
import aiohttp
from typing import Dict, Any, Optional
from ..types import Plugin, ContentData, OutputHandler

class JinaReaderPlugin(Plugin):
    name = "jina-reader"
    
    def __init__(self, skip_images: bool = True):
        self.skip_images = skip_images
        self.base_url = "https://r.jina.ai"

    def configure(self, options: Dict[str, Any]) -> None:
        self.skip_images = options.get('skipImages', True)

    async def process(self, data: ContentData, output_handler: Optional[OutputHandler] = None) -> ContentData:
        url = data.content.strip()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/{url}") as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch content: {response.status}")
                content = await response.text()

        if self.skip_images:
            # Remove markdown images
            content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
            # Remove HTML images
            content = re.sub(r'<img[^>]*>', '', content)

        return ContentData(
            content=content,
            metadata={
                **data.metadata,
                'source_url': url,
                'content_type': 'markdown'
            }
        )
