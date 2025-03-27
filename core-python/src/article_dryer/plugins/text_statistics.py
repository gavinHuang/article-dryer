import re
import math  # Adding math for ceil function
from typing import Dict, Any, List, Optional
from ..types import Plugin, ContentData, OutputHandler

class TextStatisticsPlugin(Plugin):
    name = 'text-statistics'
    
    def __init__(self):
        self.average_wpm = 250  # Average adult reading speed
        self.word_count_threshold = 150 

    def configure(self, options: Dict[str, Any]) -> None:
        if 'averageWPM' in options:
            self.average_wpm = options['averageWPM']
        self.word_count_threshold = options.get('wordCountThreshold', self.word_count_threshold)

    async def process(self, data: ContentData, output_handler: Optional[OutputHandler] = None) -> ContentData:
        content = data.content
        
        word_count = self.count_words(content)
        sentence_count = self.count_sentences(content)
        paragraph_count = len([p for p in re.split(r'\n\n+', content) if p.strip()])
        
        meets_threshold = word_count >= self.word_count_threshold
        
        # Calculate reading time
        reading_time_minutes = math.ceil(word_count / self.average_wpm)
        
        # Process words for analysis
        words = [
            word.lower().replace(r'[^a-z\'-]', '') 
            for word in re.split(r'\s+', content)
            if word
        ]
        
        # Calculate Gunning Fog Index (readability)
        complex_words = len([word for word in words if self.is_complex_word(word)])
        gunning_fog = 0.4 * ((word_count / sentence_count) + 100 * (complex_words / word_count)) if sentence_count > 0 and word_count > 0 else 0
        
        # Calculate average word length
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0

        statistics = {
            'wordCount': word_count,
            'paragraphCount': paragraph_count,
            'sentenceCount': sentence_count,
            'meetsThreshold': meets_threshold,  # Added from TextAnalyzerPlugin
            'readingTimeMinutes': reading_time_minutes,
            'averageWordLength': f"{avg_word_length:.1f}",
            'wordsPerSentence': f"{(word_count / sentence_count):.1f}" if sentence_count > 0 else "0.0",
            'readabilityScore': f"{gunning_fog:.1f}"
        }


        if output_handler:
            await output_handler({
                'type': 'json',
                'content': {
                    'statistics': statistics,
                    'message': f"Analysis complete: {word_count} words, Reading level: {statistics['readabilityScore']} (Gunning Fog Index)"
                }
            })
        
        return ContentData(
            content=data.content,
            metadata={
                **data.metadata,
                'statistics': statistics,
            }
        )

    def is_complex_word(self, word: str) -> bool:
        return self.count_syllables(word) >= 3

    def count_syllables(self, word: str) -> int:
        word = word.lower()
        if len(word) <= 3:
            return 1
        
        # Remove common word endings
        word = re.sub(r'(?:[^laeiouy]es|ed|[^laeiouy]e)$', '', word)
        word = re.sub(r'^y', '', word)
        
        # Count vowel groups
        matches = re.findall(r'[aeiouy]{1,2}', word)
        return len(matches) if matches else 1

    def count_words(self, text: str) -> int:
        # Simple word counting method from TextAnalyzerPlugin
        words = [word for word in re.split(r'\s+', text) if word]
        return len(words)

    def count_sentences(self, text: str) -> int:
        # Simple sentence counting method from TextAnalyzerPlugin
        sentences = re.split(r'[.!?]+', text)
        # Filter out empty strings
        return len([s for s in sentences if s.strip()])
