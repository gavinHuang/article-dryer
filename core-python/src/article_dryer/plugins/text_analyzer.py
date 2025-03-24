import re
from typing import Dict, Any, Optional
from ..types import Plugin, ContentData, OutputHandler

class TextAnalyzerPlugin(Plugin):
    name = "text-analyzer"
    
    def __init__(self):
        self.word_count_threshold = 150

    def configure(self, options: Dict[str, Any]) -> None:
        self.word_count_threshold = options.get('wordCountThreshold', 150)

    def count_words(self, text: str) -> int:
        # Split on whitespace and remove empty strings
        words = [word for word in re.split(r'\s+', text) if word]
        return len(words)

    def count_sentences(self, text: str) -> int:
        # Split on common sentence endings
        sentences = re.split(r'[.!?]+', text)
        # Filter out empty strings
        return len([s for s in sentences if s.strip()])

    async def process(self, data: ContentData, output_handler: Optional[OutputHandler] = None) -> ContentData:
        text = data.content
        word_count = self.count_words(text)
        sentence_count = self.count_sentences(text)

        metrics = {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'meets_threshold': word_count >= self.word_count_threshold
        }

        if output_handler:
            await output_handler({
                'type': 'metrics',
                'content': metrics
            })

        return ContentData(
            content=data.content,
            metadata={
                **data.metadata,
                'analysis': metrics
            }
        )
