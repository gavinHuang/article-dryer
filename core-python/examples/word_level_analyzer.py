#!/usr/bin/env python3
"""
Word Level Analyzer Example

This script demonstrates how to use the TextLevelAnalyzerPlugin to analyze text for CEFR levels.
It uses the WordListLoader to load and combine the Oxford 5000 and EPV vocabularies.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.article_dryer.types import Document
from src.article_dryer.plugins.TextLevelAnalyzerPlugin import TextLevelAnalyzerPlugin
from src.article_dryer.lib.WordListLoader import WordListLoader

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def analyze_text(text, skip_llm=False):
    """Analyze text using the TextLevelAnalyzerPlugin"""
    # Initialize the plugin
    plugin = TextLevelAnalyzerPlugin()
    await plugin.initialize({"skip_llm": skip_llm})
    
    # Create a document
    document = Document(text=text)
    
    # Process the document
    result = await plugin.process(document, {})
    
    return result

async def load_sample_text(file_path=None):
    """Load text from a file or use a default sample"""
    default_text = """
    The implementation of artificial intelligence in modern society has led to unprecedented transformations across various sectors. While some argue that AI brings substantial advantages, others remain skeptical about its ethical implications.

    When we talk about AI, we need to understand the paradigm shift it represents. Many people are worried about AI taking their jobs, but this concern is often exaggerated. 

    Water and food are basic human needs. Everyone likes to eat good food and drink clean water. The weather has been quite nice today, and I've enjoyed my walk in the park.

    The juxtaposition of cutting-edge technology with traditional methods creates an interesting dynamic. This phenomenon requires careful consideration by policymakers.
    """
    
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            logger.info(f"Using default sample text instead")
            return default_text
    
    return default_text

def print_analysis(analysis_result):
    """Print the analysis results in a readable format"""
    # Extract analysis metadata
    analysis = analysis_result.metadata.get("word_level_analysis", {})
    word_levels = analysis.get("word_levels", {})
    level_counts = analysis.get("level_counts", {})
    level_percentages = analysis.get("level_percentages", {})
    total_words = analysis.get("total_words", 0)
    
    print("\n" + "="*50)
    print("WORD LEVEL ANALYSIS RESULTS")
    print("="*50)
    
    # Print statistics
    print(f"\nTotal words analyzed: {total_words}")
    print("\nWord level distribution:")
    print("-"*30)
    
    # Order levels from A1 to C2
    ordered_levels = ["a1", "a2", "b1", "b2", "c1", "c2", "unknown"]
    
    for level in ordered_levels:
        if level in level_counts:
            count = level_counts.get(level, 0)
            percentage = level_percentages.get(level, 0)
            print(f"{level.upper()}: {count} words ({percentage:.1f}%)")
    
    # Print some example words for each level
    print("\nExample words by level:")
    print("-"*30)
    
    level_examples = {}
    for word, info in word_levels.items():
        level = info.get("level", "UNKNOWN").lower()
        if level not in level_examples:
            level_examples[level] = []
        
        # Only keep up to 5 examples per level
        if len(level_examples[level]) < 5:
            source = info.get("source", "")
            if source:
                level_examples[level].append(f"{word} ({source})")
            else:
                level_examples[level].append(word)
    
    # Print in order
    for level in ordered_levels:
        if level in level_examples and level_examples[level]:
            print(f"{level.upper()}: {', '.join(level_examples[level])}")
    
    print("\n")
    print("="*50)
    print("COLOR-CODED TEXT SNIPPET")
    print("="*50)
    print("\nNote: In a proper HTML renderer, the text would be color-coded by CEFR level.")
    print("A1 (Green), A2 (Light Green), B1 (Yellow), B2 (Orange), C1 (Red), C2 (Purple), Unknown (Gray)\n")
    
    # Print a snippet of the highlighted text (without HTML rendering)
    print(analysis_result.text[:500] + ("..." if len(analysis_result.text) > 500 else ""))
    
    print("\n" + "="*50)

async def main():
    """Main function that runs the word level analyzer"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Analyze text for CEFR word levels")
    parser.add_argument("--file", "-f", help="Path to a text file to analyze")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM processing for unknown words")
    args = parser.parse_args()
    
    # Load text from file or use default sample
    text = await load_sample_text(args.file)
    
    # Run the analysis
    logger.info("Running word level analysis...")
    result = await analyze_text(text, skip_llm=args.no_llm)
    
    # Print the results
    print_analysis(result)
    
    return 0

if __name__ == "__main__":
    asyncio.run(main())