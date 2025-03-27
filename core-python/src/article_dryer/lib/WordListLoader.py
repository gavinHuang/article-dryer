import os
import json
import csv
import logging
import traceback  # Add traceback import
import aiofiles
from typing import Dict, Set, List, Any

from .WordProcessor import WordProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WordLists:
    """Data structure to hold vocabulary information"""
    def __init__(self):
        self.word_map = {}  # Maps processed words to their original data
        self.cefr = {
            'a1': set(),
            'a2': set(),
            'b1': set(),
            'b2': set(),
            'c1': set(),
            'c2': set(),
            'unknown': set()
        }

class WordListLoader:
    """
    Class responsible for loading vocabulary from various sources:
    - Oxford 5000 vocabulary (primary)
    - EPV-deduped vocabulary (secondary)
    - User-defined words file (tertiary, including LLM-classified words)
    
    This class handles file loading and vocabulary management.
    """
    
    _instance = None
    
    def __init__(self):
        if WordListLoader._instance is not None:
            raise Exception("Use get_instance() instead")
        self.word_lists = None
        self.data_dir = os.path.join(os.path.dirname(__file__), '../data')
        self.word_processor = WordProcessor()
        self.initialized = False
        self.user_words_file = "user_defined_words.json"
        
    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = WordListLoader()
            await cls._instance.initialize()
        return cls._instance

    async def initialize(self):
        """Initialize the WordListLoader"""
        if self.initialized:
            return
        
        logger.info('Initializing WordListLoader...')
        self.initialized = True

    async def load_word_file(self, filename: str) -> List[Dict[str, Any]]:
        """Load a JSON word list file"""
        try:
            file_path = os.path.join(self.data_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as error:
            logger.error(f'Failed to load {filename}: {error}')
            raise error

    async def load_word_lists(self) -> WordLists:
        """Load both Oxford and EPV word lists and create a combined vocabulary"""
        if self.word_lists:
            return self.word_lists

        try:
            word_lists = WordLists()
            
            # Load the Oxford 5000 word list first (main source)
            await self.load_oxford_words(word_lists)
            
            # Load EPV as a secondary source
            await self.load_epv_words(word_lists)
            
            # Load user-defined words as a tertiary source
            await self.load_user_words(word_lists)
            
            self.word_lists = word_lists
            return self.word_lists
        except Exception as error:
            logger.error(f'Failed to load word lists: {error}')
            return self.get_fallback_lists()

    async def load_oxford_words(self, word_lists: WordLists):
        """Load words from the Oxford 5000 vocabulary"""
        try:
            oxford_file_path = os.path.join(self.data_dir, 'oxford-5000.json')
            if not os.path.exists(oxford_file_path):
                logger.warning("Oxford file not found, skipping Oxford vocabulary")
                return
                
            logger.info("Loading Oxford vocabulary...")
            oxford_data = await self.load_word_file('oxford-5000.json')
            
            # Process all words in the oxford data
            for entry in oxford_data:
                # Extract the word and its data from the nested structure
                word_value = None
                if isinstance(entry, dict) and 'value' in entry:
                    word_value = entry.get('value', {})
                    word = word_value.get('word', '')
                    level = word_value.get('level', '').lower()
                elif isinstance(entry, dict) and 'word' in entry:
                    word = entry.get('word', '')
                    level = entry.get('level', '').lower()
                    word_value = entry
                else:
                    continue
                
                # Skip empty words or invalid levels
                if not word or level not in word_lists.cefr:
                    continue
                
                # Add to CEFR sets
                word_lists.cefr[level].add(word.lower())
                
                # Add multiple word forms to the word map
                await self.add_word_forms_to_map(word, word_value, word_lists)
            
            logger.info(f"Loaded {sum(len(s) for s in word_lists.cefr.values())} words from Oxford vocabulary")
            
        except Exception as error:
            logger.error(f'Failed to load Oxford words: {error}')
            raise error

    async def load_epv_words(self, word_lists: WordLists):
        """Load words from the EPV vocabulary as a secondary source"""
        try:
            epv_file_path = os.path.join(self.data_dir, 'epv-deduped.csv')
            if not os.path.exists(epv_file_path):
                logger.warning("EPV file not found, skipping EPV vocabulary")
                return
                
            logger.info("Loading EPV vocabulary...")
            count = 0
            
            with open(epv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) >= 2:
                        word = row[0].strip().lower()
                        level = row[1].strip().lower()
                        
                        # Skip if level is not valid or word already exists in the main vocabulary
                        if level not in word_lists.cefr:
                            continue
                        
                        # Don't override existing entries from Oxford
                        if await self.word_exists_in_any_form(word, word_lists):
                            continue
                            
                        # Create a simpler word_value for EPV words
                        word_value = {
                            "word": word,
                            "level": level.upper(),
                            "source": "epv"
                        }
                        
                        # Add to CEFR sets
                        word_lists.cefr[level].add(word.lower())
                        
                        # Add multiple word forms to the word map
                        await self.add_word_forms_to_map(word, word_value, word_lists)
                        count += 1
            
            logger.info(f"Added {count} additional words from EPV vocabulary")
            
        except Exception as error:
            logger.error(f'Failed to load EPV words: {error}')
            # Don't raise an error here, as Oxford is our primary source

    async def load_user_words(self, word_lists: WordLists):
        """Load words from the user-defined words file"""
        try:
            user_words_file_path = os.path.join(self.data_dir, self.user_words_file)
            if not os.path.exists(user_words_file_path):
                logger.warning("User-defined words file not found, skipping user-defined vocabulary")
                return
                
            logger.info("Loading user-defined vocabulary...")
            user_data = await self.load_word_file(self.user_words_file)
            
            # Process all words in the user data
            for entry in user_data:
                # Extract the word and its data from the nested structure
                word_value = None
                if isinstance(entry, dict) and 'value' in entry:
                    word_value = entry.get('value', {})
                    word = word_value.get('word', '')
                    level = word_value.get('level', '').lower()
                elif isinstance(entry, dict) and 'word' in entry:
                    word = entry.get('word', '')
                    level = entry.get('level', '').lower()
                    word_value = entry
                else:
                    continue
                
                # Skip empty words or invalid levels
                if not word or level not in word_lists.cefr:
                    continue
                
                # Add to CEFR sets
                word_lists.cefr[level].add(word.lower())
                
                # Add multiple word forms to the word map
                await self.add_word_forms_to_map(word, word_value, word_lists)
            
            logger.info(f"Loaded {sum(len(s) for s in word_lists.cefr.values())} words from user-defined vocabulary")
            
        except Exception as error:
            logger.error(f'Failed to load user-defined words: {error}')
            # Don't raise an error here, as Oxford is our primary source

    async def word_exists_in_any_form(self, word: str, word_lists: WordLists) -> bool:
        """Check if a word already exists in the word map in its normalized form"""
        # Check base form
        if word.lower() in word_lists.word_map:
            return True
            
        # Check normalized form (which handles contractions, possessives, inflections, etc.)
        normalized_form = self.word_processor.normalize_word(word)
        if normalized_form in word_lists.word_map:
            return True
            
        # Check normalized form without spaces
        normalized_no_spaces = normalized_form.replace(" ", "")
        for vocab_word in word_lists.word_map.keys():
            if vocab_word.replace(" ", "") == normalized_no_spaces:
                return True
            
        return False

    async def add_word_forms_to_map(self, word: str, word_value: Dict, word_lists: WordLists) -> None:
        """Add the normalized form of a word to the word map"""
        word_lower = word.lower()
        
        # Add original form
        word_lists.word_map[word_lower] = word_value
        
        # Add normalized form
        normalized_form = self.word_processor.normalize_word(word)
        if normalized_form and normalized_form != word_lower:
            word_lists.word_map[normalized_form] = word_value

    async def save_words_to_user_file(self, words_data: Dict[str, Dict]) -> bool:
        """
        Save words data to the user-defined words file.
        This is used to store word classifications from the LLM.
        
        Args:
            words_data: Dictionary mapping words to their classification data
                        {"word": {"word": "word", "level": "A1", "explanation": "...", "source": "llm"}}
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            user_words_file_path = os.path.join(self.data_dir, self.user_words_file)
            existing_data = []
            
            # Load existing data if file exists
            if os.path.exists(user_words_file_path):
                try:
                    with open(user_words_file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in {self.user_words_file}, starting with empty file")
                    existing_data = []
            
            # Convert existing data to a dictionary for easy lookup
            existing_dict = {}
            for entry in existing_data:
                if isinstance(entry, dict) and "word" in entry:
                    existing_dict[entry["word"].lower()] = entry
            
            # Update with new data
            for word, data in words_data.items():
                existing_dict[word.lower()] = data
            
            # Convert back to list format
            updated_data = list(existing_dict.values())
            
            # Write back to file with proper indentation
            async with aiofiles.open(user_words_file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(updated_data, indent=2))
            
            logger.info(f"Saved {len(words_data)} words to user-defined words file")
            return True
            
        except Exception as e:
            logger.error(f"Error saving words to user file: {str(e)}")
            traceback.print_exc()
            return False

    def get_fallback_lists(self) -> WordLists:
        """Create a minimal fallback vocabulary if loading fails"""
        fallback = WordLists()
        
        # Create a basic fallback dictionary
        basic_words = {
            'hello': {'word': 'hello', 'level': 'A1'},
            'world': {'word': 'world', 'level': 'A1'},
            'simple': {'word': 'simple', 'level': 'A2'},
            'basic': {'word': 'basic', 'level': 'A2'},
            'intermediate': {'word': 'intermediate', 'level': 'B1'},
            'progress': {'word': 'progress', 'level': 'B1'},
            'advanced': {'word': 'advanced', 'level': 'B2'},
            'complex': {'word': 'complex', 'level': 'B2'},
            'proficient': {'word': 'proficient', 'level': 'C1'},
            'master': {'word': 'master', 'level': 'C1'},
            'expert': {'word': 'expert', 'level': 'C2'},
            'fluent': {'word': 'fluent', 'level': 'C2'}
        }
        
        # Add to word map
        fallback.word_map = basic_words
        
        # Also populate CEFR sets for backward compatibility
        for word, data in basic_words.items():
            level = data['level'].lower()
            fallback.cefr[level].add(word)
            
        return fallback

    def get_data_dir(self) -> str:
        """Return the data directory path"""
        return self.data_dir