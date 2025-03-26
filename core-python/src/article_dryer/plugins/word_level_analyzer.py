from typing import Dict, Any, List, Optional, Tuple
import re
from ..types import ContentData, OutputData, OutputHandler
from ..lib.word_list_loader import WordListLoader

class WordLevelAnalyzerPlugin:
    name = "word-level-analyzer"
    
    def __init__(self):
        self.options = {
            "outputFormat": "inline",  # Options: inline, json, html
            "includeCounts": True,
            "includePercentages": True,
            "includeFullData": False,  # Whether to include full Oxford data
        }
        
    def configure(self, options: Dict[str, Any]) -> None:
        self.options.update(options)
        
    async def process(self, data: ContentData, output_handler: Optional[OutputHandler] = None) -> ContentData:
        """
        Process the content and analyze word levels based on CEFR.
        
        Args:
            data: ContentData object containing the text to analyze
            output_handler: Optional handler for additional output
            
        Returns:
            ContentData with the processed content and word level metadata
        """
        if not data.content or not isinstance(data.content, str):
            return data
            
        # Get word level analysis
        word_data = await self._analyze_word_levels(data.content)
        
        # Extract simple word-level pairs for backward compatibility
        word_levels = [(item["word"], item["level"].lower()) for item in word_data]
        
        # Prepare output based on format
        if self.options["outputFormat"] == "inline":
            result = await self._format_inline(word_levels)
        elif self.options["outputFormat"] == "html":
            result = await self._format_html(word_levels)
        else:  # Default to JSON structure in the content
            result = data.content
            
        # Calculate statistics
        level_stats = self._calculate_statistics(word_levels)
        
        # Update metadata with word level information
        if self.options["includeFullData"]:
            data.metadata["wordLevels"] = {
                "words": word_data,
                "statistics": level_stats
            }
        else:
            data.metadata["wordLevels"] = {
                "words": [{"word": word, "level": level} for word, level in word_levels],
                "statistics": level_stats
            }
        
        # If we're using inline format, update the content
        if self.options["outputFormat"] == "inline":
            data.content = result
        
        # Send detailed output if a handler is provided
        if output_handler:
            await output_handler(OutputData(
                type="word-level-analysis",
                content={
                    "wordLevels": word_data if self.options["includeFullData"] else word_levels,
                    "statistics": level_stats,
                    "formattedText": result if self.options["outputFormat"] != "json" else None
                }
            ))
            
        return data
    
    async def _analyze_word_levels(self, text: str) -> List[Dict[str, Any]]:
        """
        Analyze the CEFR level and other properties of each word in the text.
        
        Args:
            text: The input text to analyze
            
        Returns:
            List of dictionaries with word data including CEFR level
        """
        # Get the word list loader instance
        loader = await WordListLoader.get_instance()
        
        # Tokenize the text while preserving the original words
        tokens = re.findall(r'\b[\w\']+\b|[^\w\s]', text)
        
        # Create a list to store word data
        word_data = []
        
        for token in tokens:
            # Skip non-word tokens
            if not re.match(r'^[a-zA-Z]', token):
                continue
                
            # Get all data for this word
            word_info = await loader.get_word_level(token)
            
            # Prepare the result object with the original token
            result = {
                "word": token,
                "level": word_info.get("level", "unknown").lower()
            }
            
            # Include additional information if available
            if self.options["includeFullData"]:
                for key, value in word_info.items():
                    if key not in result:
                        result[key] = value
            
            word_data.append(result)
        
        return word_data
    
    async def _format_inline(self, word_levels: List[Tuple[str, str]]) -> str:
        """Format the word levels as inline text with annotations."""
        result = ""
        for word, level in word_levels:
            result += f"{word} [{level.upper()}] "
        return result.strip()
    
    async def _format_html(self, word_levels: List[Tuple[str, str]]) -> str:
        """Format the word levels as HTML with color-coded spans."""
        level_colors = {
            'a1': '#28a745',  # Green
            'a2': '#5cb85c',  # Light green
            'b1': '#ffc107',  # Yellow
            'b2': '#fd7e14',  # Orange
            'c1': '#dc3545',  # Red
            'c2': '#9c27b0',  # Purple
            'unknown': '#6c757d'  # Gray
        }
        
        html = ""
        for word, level in word_levels:
            color = level_colors.get(level, '#6c757d')
            html += f'<span title="{level.upper()}" style="color: {color}; font-weight: {500 if level in ["c1", "c2"] else "normal"}">{word}</span> '
        
        return html.strip()
    
    def _calculate_statistics(self, word_levels: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Calculate statistics about word levels."""
        # Count words by level
        level_counts = {'a1': 0, 'a2': 0, 'b1': 0, 'b2': 0, 'c1': 0, 'c2': 0, 'unknown': 0}
        for _, level in word_levels:
            level_counts[level] += 1
        
        total_words = len(word_levels)
        
        # Calculate percentages
        level_percentages = {}
        for level, count in level_counts.items():
            level_percentages[level] = (count / total_words) * 100 if total_words > 0 else 0
        
        # Group by difficulty
        elementary = level_counts['a1'] + level_counts['a2']
        intermediate = level_counts['b1'] + level_counts['b2']
        advanced = level_counts['c1'] + level_counts['c2']
        
        return {
            "counts": level_counts,
            "percentages": level_percentages,
            "totalWords": total_words,
            "groupedCounts": {
                "elementary": elementary,
                "intermediate": intermediate,
                "advanced": advanced,
                "unknown": level_counts['unknown']
            },
            "groupedPercentages": {
                "elementary": (elementary / total_words) * 100 if total_words > 0 else 0,
                "intermediate": (intermediate / total_words) * 100 if total_words > 0 else 0,
                "advanced": (advanced / total_words) * 100 if total_words > 0 else 0,
                "unknown": (level_counts['unknown'] / total_words) * 100 if total_words > 0 else 0
            }
        }