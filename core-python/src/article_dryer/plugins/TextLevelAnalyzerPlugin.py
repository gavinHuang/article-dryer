import re
import asyncio
import logging
from typing import Dict, List, Any, Set, Optional, Tuple
from collections import Counter

from ..types import Plugin, PluginContext, Document
from ..lib.WordProcessor import WordProcessor
from ..lib.WordListLoader import WordListLoader
from ..lib.WordLevelClassifier import WordLevelClassifier
from ..lib.LLMClient import LLMClient

logger = logging.getLogger(__name__)

class TextLevelAnalyzerPlugin(Plugin):
    """
    Plugin that analyzes text for CEFR vocabulary levels.
    This plugin categorizes words based on their CEFR level using:
    1. Oxford 5000 vocabulary
    2. EPV vocabulary as a fallback
    3. LLM as a final fallback for unknown words
    """

    def __init__(self):
        self.name = "text_level_analyzer"
        self.word_processor = None
        self.word_list_loader = None
        self.word_level_classifier = None
        self.llm_client = None
        self.skip_llm = False

    async def initialize(self, context: PluginContext) -> bool:
        """Initialize the plugin with word lists and LLM client"""
        try:
            # Initialize word processor
            self.word_processor = WordProcessor()
            
            # Initialize word list loader
            self.word_list_loader = await WordListLoader.get_instance()
            
            # Load word lists
            word_lists = await self.word_list_loader.load_word_lists()
            
            # Initialize LLM client
            if "llm" in context and context["llm"]:
                self.llm_client = context["llm"]
            else:
                self.llm_client = LLMClient()
                await self.llm_client.initialize({})
            
            # Check if we should skip LLM processing
            if "skip_llm" in context:
                self.skip_llm = context["skip_llm"]
            
            # Initialize word level classifier
            self.word_level_classifier = WordLevelClassifier(
                self.word_processor,
                word_lists.word_map,
                word_lists.cefr,
                self.word_list_loader.get_data_dir()
            )
                
            return True
        except Exception as e:
            logger.error(f"Failed to initialize TextLevelAnalyzerPlugin: {e}")
            return False

    async def process(self, document: Document, context: PluginContext) -> Document:
        """Process document text to classify word levels"""
        if not document or not document.text:
            return document
            
        # Create a copy of the document
        result = document.clone()
        
        # Extract clean words from text
        text = document.text
        all_words = self.word_processor.extract_words(text)
        
        if not all_words:
            logger.warning("No words found in the text to analyze")
            return result
            
        # Analyze word levels
        word_levels = await self.analyze_word_levels(all_words)
        
        # Calculate statistics
        level_counts = Counter([info['level'].lower() for info in word_levels.values()])
        total_words = len(all_words)
        level_percentages = {level: count / total_words * 100 for level, count in level_counts.items()}
        
        # Add metadata to the document
        result.metadata["word_level_analysis"] = {
            "word_levels": word_levels,
            "level_counts": dict(level_counts),
            "level_percentages": level_percentages,
            "total_words": total_words,
            "unknown_words": level_counts.get("unknown", 0),
        }
        
        # Create a text with word levels highlighted for visualization
        highlighted_text = await self.create_highlighted_text(text, word_levels)
        result.metadata["word_level_highlighted"] = highlighted_text
        
        return result
    
    async def analyze_word_levels(self, words: List[str]) -> Dict[str, Dict[str, Any]]:
        """Analyze the CEFR level of each word"""
        result = {}
        unknown_words = []
        
        # First pass: check all words against the word list
        for word in words:
            word_lower = word.lower()
            if word_lower in result:
                continue  # Skip duplicates
                
            # Get word level info
            word_info = await self.word_level_classifier.get_word_level(word_lower)
            
            # If level is unknown and we should use LLM, add to unknown list
            if word_info.get("level", "").lower() == "unknown" and not self.skip_llm:
                unknown_words.append(word_lower)
                
            result[word_lower] = word_info
            
        # Second pass: classify unknown words with LLM if needed
        if unknown_words and not self.skip_llm:
            logger.info(f"Classifying {len(unknown_words)} unknown words with LLM")
            llm_results = await self.word_level_classifier.classify_unknown_words_with_llm(
                unknown_words, self.llm_client
            )
            
            # Update results with LLM classifications
            for word, info in llm_results.items():
                if word in result:
                    result[word] = info
        
        return result
    
    async def create_highlighted_text(self, text: str, word_levels: Dict[str, Dict[str, Any]]) -> str:
        """Create a version of the text with words color-coded by level"""
        # Define color mappings for each CEFR level
        color_map = {
            "a1": "#28a745",  # Green for A1
            "a2": "#5cb85c",  # Light Green for A2
            "b1": "#ffc107",  # Yellow for B1
            "b2": "#fd7e14",  # Orange for B2
            "c1": "#dc3545",  # Red for C1
            "c2": "#9c27b0",  # Purple for C2
            "unknown": "#6c757d"  # Gray for unknown
        }
        
        # Create HTML version with colored spans
        highlighted_text = text
        
        # Sort words by length (longest first) to avoid substring replacement issues
        sorted_words = sorted(word_levels.keys(), key=len, reverse=True)
        
        for word in sorted_words:
            level = word_levels[word].get("level", "unknown").lower()
            if level not in color_map:
                level = "unknown"
                
            color = color_map[level]
            
            # Replace whole words only using regex (with word boundaries)
            pattern = r'\b' + re.escape(word) + r'\b'
            replacement = f'<span style="color:{color}" title="{level.upper()}">{word}</span>'
            highlighted_text = re.sub(pattern, replacement, highlighted_text, flags=re.IGNORECASE)
        
        return highlighted_text