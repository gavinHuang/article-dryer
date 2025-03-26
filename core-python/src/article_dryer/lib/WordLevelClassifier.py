import os
import re
import json
import logging
import aiofiles
from typing import Dict, List, Any, Set, Optional

from .WordProcessor import WordProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WordLevelClassifier:
    """
    A class for classifying words according to their CEFR level (A1-C2),
    using loaded vocabularies and optional LLM fallback for unknown words.
    """
    
    def __init__(self, word_processor: WordProcessor, word_map: Dict[str, Dict], cefr_sets: Dict[str, Set[str]], data_dir: str):
        """
        Initialize the classifier with word processor and vocabulary data
        
        Args:
            word_processor: An instance of WordProcessor for normalizing/processing words
            word_map: A map of words to their level information
            cefr_sets: Sets of words categorized by CEFR level
            data_dir: Path to the data directory containing CEFR definitions
        """
        self.word_processor = word_processor
        self.word_map = word_map
        self.cefr_sets = cefr_sets
        self.data_dir = data_dir

    async def get_word_level(self, word: str) -> Dict[str, Any]:
        """Get the CEFR level and information for a word"""
        # Normalize the word first
        normalized_word = self.word_processor.normalize_word(word)
        
        # First check the word itself
        if normalized_word in self.word_map:
            return self.word_map[normalized_word]
            
        # Try the lemmatized form (most accurate for analysis)
        lemma_form = self.word_processor.process_word(normalized_word, "lemma")
        if lemma_form in self.word_map:
            return self.word_map[lemma_form]
            
        # Try the stemmed form
        stem_form = self.word_processor.process_word(normalized_word, "stem")
        if stem_form in self.word_map:
            return self.word_map[stem_form]
        
        # Try the tokenized form
        token_form = self.word_processor.process_word(normalized_word, "token")
        if token_form in self.word_map:
            return self.word_map[token_form]
                
        # If still no match is found, return unknown
        return {
            "word": word,
            "level": "unknown",
            "needs_llm_classification": True
        }
    
    async def classify_unknown_words_with_llm(self, unknown_words: List[str], llm_client) -> Dict[str, Dict]:
        """
        Use LLM to classify words that don't exist in our vocabularies
        Returns a dictionary mapping words to their classifications
        """
        if not unknown_words:
            return {}
            
        # Load CEFR definitions
        cefr_definitions = await self.load_cefr_definitions()
        
        # Get examples for each level
        example_words = await self.get_level_examples()
        
        # Process words in batches of 10 to avoid context length issues
        results = {}
        batch_size = 10
        for i in range(0, len(unknown_words), batch_size):
            batch = unknown_words[i:i+batch_size]
            batch_results = await self._classify_word_batch(batch, cefr_definitions, example_words, llm_client)
            results.update(batch_results)
            
        # Update the word_map with the newly classified words
        for word, data in results.items():
            level = data.get("level", "unknown").lower()
            if level in self.cefr_sets:
                # Add to CEFR set and word map
                self.cefr_sets[level].add(word.lower())
                self.word_map[word.lower()] = data
                
                # Also add processed forms
                lemma = self.word_processor.process_word(word, "lemma")
                stem = self.word_processor.process_word(word, "stem")
                if lemma != word.lower():
                    self.word_map[lemma] = data
                if stem != word.lower() and stem != lemma:
                    self.word_map[stem] = data
                
        return results
        
    async def _classify_word_batch(
        self, 
        words: List[str], 
        cefr_definitions: str, 
        examples: Dict[str, List[str]],
        llm_client
    ) -> Dict[str, Dict]:
        """Classify a batch of words using the LLM"""
        # Format examples
        example_text = "\n".join([
            f"{level.upper()} examples: {', '.join(examples[level])}"
            for level in ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']
        ])
        
        # Create the prompt
        prompt = f"""
{cefr_definitions}

{example_text}

For each of the following words, determine the most appropriate CEFR level (A1, A2, B1, B2, C1, or C2) based on:
1. Word frequency in everyday language
2. Complexity of the word
3. When students typically learn this word

Words to classify:
{", ".join(words)}

For each word, provide the level and a brief explanation in this JSON format:
{{
  "word1": {{"level": "A1", "explanation": "Basic everyday word"}},
  "word2": {{"level": "C2", "explanation": "Advanced academic vocabulary"}}
}}
"""

        try:
            # Call the LLM
            response = await llm_client.generate_text(prompt)
            
            # Extract JSON from response
            match = re.search(r'({.*})', response.replace('\n', ''))
            if match:
                json_str = match.group(1)
                result = json.loads(json_str)
                
                # Validate and format the result
                formatted_results = {}
                for word, data in result.items():
                    if word.lower() in [w.lower() for w in words]:
                        level = data.get("level", "").lower()
                        if level in ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']:
                            formatted_results[word.lower()] = {
                                "word": word.lower(),
                                "level": data.get("level", "").upper(),
                                "explanation": data.get("explanation", ""),
                                "source": "llm"
                            }
                        else:
                            # Default to C1 if level not recognized
                            formatted_results[word.lower()] = {
                                "word": word.lower(),
                                "level": "C1",
                                "explanation": "Level not recognized, defaulting to C1",
                                "source": "llm"
                            }
                
                return formatted_results
            else:
                logger.error(f"Couldn't extract JSON from LLM response: {response}")
                return {word.lower(): {"word": word.lower(), "level": "C1", "source": "default"} for word in words}
        
        except Exception as e:
            logger.error(f"Error using LLM to classify words: {e}")
            # Default to C1 for all words in case of error
            return {word.lower(): {"word": word.lower(), "level": "C1", "source": "default"} for word in words}

    async def load_cefr_definitions(self) -> str:
        """Load CEFR definitions from file"""
        cefr_path = os.path.join(self.data_dir, 'CEFR.txt')
        if os.path.exists(cefr_path):
            async with aiofiles.open(cefr_path, 'r') as f:
                return await f.read()
        else:
            # Fallback definitions if file doesn't exist
            return """
CEFR Levels:
A1: Beginner - Basic everyday words
A2: Elementary - Simple common words
B1: Intermediate - Common words in many contexts
B2: Upper-Intermediate - More specific vocabulary
C1: Advanced - Specialized academic/professional words
C2: Proficiency - Rare and nuanced words
"""

    async def get_level_examples(self) -> Dict[str, List[str]]:
        """Get example words for each CEFR level"""
        examples = {level: [] for level in ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']}
        
        # Use words from our existing vocabulary as examples
        for level, words in self.cefr_sets.items():
            if level == 'unknown':
                continue
                
            # Get up to 5 examples for each level
            examples[level] = list(words)[:5] if len(words) >= 5 else list(words)
            
        # If any level has no examples, use these fallbacks
        fallbacks = {
            'a1': ['hello', 'water', 'book', 'house', 'car'],
            'a2': ['weather', 'hobby', 'family', 'shopping', 'weekend'],
            'b1': ['advantage', 'culture', 'solution', 'experience', 'celebrate'],
            'b2': ['consideration', 'assumption', 'perspective', 'controversy', 'volume'],
            'c1': ['implementation', 'phenomenon', 'subsequent', 'unprecedented', 'innovative'],
            'c2': ['paradigm', 'juxtaposition', 'nuance', 'ambivalence', 'meticulous']
        }
        
        for level, words in examples.items():
            if len(words) < 5:
                examples[level] = fallbacks[level]
                
        return examples