import os
import json
import csv
import logging
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

    async def word_exists_in_any_form(self, word: str, word_lists: WordLists) -> bool:
        """Check if a word already exists in the word map in any form"""
        # Check base form
        if word.lower() in word_lists.word_map:
            return True
            
        # Check lemmatized form
        lemma_form = self.word_processor.process_word(word, "lemma")
        if lemma_form in word_lists.word_map:
            return True
            
        # Check stem form
        stem_form = self.word_processor.process_word(word, "stem") 
        if stem_form in word_lists.word_map:
            return True
            
        # Check token form
        token_form = self.word_processor.process_word(word, "token")
        if token_form in word_lists.word_map:
            return True
            
        return False

    async def add_word_forms_to_map(self, word: str, word_value: Dict, word_lists: WordLists) -> None:
        """Add various forms of a word to the word map"""
        word_lower = word.lower()
        
        # Add original form
        word_lists.word_map[word_lower] = word_value
        
        # Add lemmatized form
        lemma_form = self.word_processor.process_word(word, "lemma")
        if lemma_form and lemma_form != word_lower:
            word_lists.word_map[lemma_form] = word_value
        
        # Add stemmed form
        stem_form = self.word_processor.process_word(word, "stem")
        if stem_form and stem_form != word_lower and stem_form != lemma_form:
            word_lists.word_map[stem_form] = word_value
        
        # Add tokenized form
        token_form = self.word_processor.process_word(word, "token")
        if token_form and token_form != word_lower and token_form != lemma_form and token_form != stem_form:
            word_lists.word_map[token_form] = word_value

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