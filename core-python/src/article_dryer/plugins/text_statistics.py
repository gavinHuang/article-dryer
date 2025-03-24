import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from ..types import Plugin, ContentData, OutputHandler
from ..lib.word_list_loader import WordListLoader

@dataclass
class VocabularyProfile:
    ngsl: int = 0      # New General Service List words (basic)
    awl: int = 0       # Academic Word List words (academic)
    technical: int = 0  # Technical/specialized vocabulary
    other: int = 0     # Other words

class TextStatisticsPlugin(Plugin):
    name = 'text-statistics'
    
    def __init__(self):
        self.average_wpm = 250  # Average adult reading speed
        self.word_list_loader = None
        
        # Technical patterns (common suffixes and patterns for technical terms)
        self.technical_patterns = [
            re.compile(r'[a-z]+ology\b', re.I),    # Words ending in "ology"
            re.compile(r'[a-z]+ization\b', re.I),  # Words ending in "ization"
            re.compile(r'[a-z]+icism\b', re.I),    # Words ending in "icism"
            re.compile(r'[a-z]+istic\b', re.I),    # Words ending in "istic"
            re.compile(r'[a-z]+esis\b', re.I),     # Words ending in "esis"
            re.compile(r'[a-z]+itis\b', re.I),     # Words ending in "itis"
            re.compile(r'[a-z]+omy\b', re.I),      # Words ending in "omy"
            re.compile(r'\b[a-z]+lyze\b', re.I),   # Words ending in "lyze"
            re.compile(r'\b[a-z]{3,}[^aeiou]{2}[a-z]{2,}\b', re.I)  # Words with consonant clusters
        ]

    def configure(self, options: Dict[str, Any]) -> None:
        if 'averageWPM' in options:
            self.average_wpm = options['averageWPM']

    async def process(self, data: ContentData, output_handler: Optional[OutputHandler] = None) -> ContentData:
        content = data.content
        
        # Basic statistics
        words = [
            word.lower().replace(r'[^a-z\'-]', '') 
            for word in re.split(r'\s+', content)
            if word
        ]
        
        word_count = len(words)
        paragraph_count = len([p for p in re.split(r'\n\n+', content) if p.strip()])
        sentence_count = len([s for s in re.split(r'[.!?]+\s', content) if s.strip()])
        
        # Calculate reading time
        reading_time_minutes = ceil(word_count / self.average_wpm)
        
        # Analyze vocabulary levels
        vocab_profile = await self.analyze_vocabulary_profile(words)
        
        # Calculate Gunning Fog Index (readability)
        complex_words = len([word for word in words if self.is_complex_word(word)])
        gunning_fog = 0.4 * ((word_count / sentence_count) + 100 * (complex_words / word_count))
        
        # Calculate average word length
        avg_word_length = sum(len(word) for word in words) / word_count

        statistics = {
            'wordCount': word_count,
            'paragraphCount': paragraph_count,
            'sentenceCount': sentence_count,
            'readingTimeMinutes': reading_time_minutes,
            'averageWordLength': f"{avg_word_length:.1f}",
            'wordsPerSentence': f"{(word_count / sentence_count):.1f}",
            'readabilityScore': f"{gunning_fog:.1f}",
            'vocabularyProfile': {
                'basic': {
                    'count': vocab_profile.ngsl,
                    'percentage': f"{(vocab_profile.ngsl / word_count * 100):.1f}"
                },
                'academic': {
                    'count': vocab_profile.awl,
                    'percentage': f"{(vocab_profile.awl / word_count * 100):.1f}"
                },
                'technical': {
                    'count': vocab_profile.technical,
                    'percentage': f"{(vocab_profile.technical / word_count * 100):.1f}"
                },
                'other': {
                    'count': vocab_profile.other,
                    'percentage': f"{(vocab_profile.other / word_count * 100):.1f}"
                }
            }
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
                'textStatistics': statistics
            }
        )

    async def analyze_vocabulary_profile(self, words: List[str]) -> VocabularyProfile:
        if not self.word_list_loader:
            self.word_list_loader = await WordListLoader.get_instance()
            
        word_lists = await self.word_list_loader.load_word_lists()
        profile = VocabularyProfile()

        for word in words:
            if word in word_lists.cefr['a1'] or word in word_lists.cefr['a2']:
                profile.ngsl += 1
            elif word in word_lists.cefr['b1'] or word in word_lists.cefr['b2']:
                profile.awl += 1
            elif self.is_technical_word(word):
                profile.technical += 1
            else:
                profile.other += 1

        return profile

    def is_technical_word(self, word: str) -> bool:
        return any(pattern.search(word) for pattern in self.technical_patterns)

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
