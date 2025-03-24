import os
import json
import requests
from typing import Dict, Set, List
from transformers import pipeline
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

class WordLists:
    def __init__(self):
        self.cefr = {
            'a1': set(),
            'a2': set(),
            'b1': set(),
            'b2': set(),
            'c1': set(),
            'c2': set()
        }

class WordListLoader:
    _instance = None
    
    def __init__(self):
        if WordListLoader._instance is not None:
            raise Exception("Use getInstance() instead")
        self.word_lists = None
        self.data_dir = os.path.join(os.path.dirname(__file__), '../data')
        self.tokenizer = None
        self.stemmer = PorterStemmer()
        self.initialized = False
        
    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = WordListLoader()
            await cls._instance.initialize()
        return cls._instance

    async def initialize(self):
        if self.initialized:
            return
        print('Initializing NLP components...')
        await self.init_nlp()
        print('Ensuring word list file exists...')
        await self.ensure_word_list_file()
        self.initialized = True

    async def init_nlp(self):
        try:
            print('Loading tokenizer...')
            self.tokenizer = pipeline('token-classification', 'Xenova/bert-base-uncased')
            nltk.download('punkt')
        except Exception as error:
            print('Error initializing NLP:', error)
            raise error

    async def ensure_word_list_file(self):
        oxford_file_path = os.path.join(self.data_dir, 'oxford-5000.json')
        if not os.path.exists(oxford_file_path):
            print('Downloading Oxford 5000 word list...')
            await self.download_oxford_list()

    async def download_oxford_list(self):
        url = 'https://raw.githubusercontent.com/tyypgzl/Oxford-5000-words/refs/heads/main/full-word.json'
        response = requests.get(url)
        os.makedirs(self.data_dir, exist_ok=True)
        with open(os.path.join(self.data_dir, 'oxford-5000.json'), 'w') as f:
            json.dump(response.json(), f, indent=2)

    async def load_word_lists(self) -> WordLists:
        if self.word_lists:
            return self.word_lists

        try:
            cefr_words = await self.load_word_file('oxford-5000.json')
            word_lists = WordLists()
            word_lists.cefr = {
                'a1': set(await self.process_words(cefr_words['a1'])),
                'a2': set(await self.process_words(cefr_words['a2'])),
                'b1': set(await self.process_words(cefr_words['b1'])),
                'b2': set(await self.process_words(cefr_words['b2'])),
                'c1': set(await self.process_words(cefr_words['c1'])),
                'c2': set(await self.process_words(cefr_words['c2']))
            }
            self.word_lists = word_lists
            return self.word_lists
        except Exception as error:
            print('Failed to load local word lists, attempting internet fetch:', error)
            try:
                cefr_words = await self.fetch_cefr()
                self.word_lists = WordLists()
                self.word_lists.cefr = cefr_words
                await self.save_to_cache(self.word_lists)
                return self.word_lists
            except Exception as fetch_error:
                print('Failed to fetch word lists from internet:', fetch_error)
                return self.get_fallback_lists()

    async def load_word_file(self, filename: str):
        try:
            file_path = os.path.join(self.data_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as error:
            print(f'Failed to load {filename}:', error)
            raise error

    async def save_to_cache(self, lists: WordLists):
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(os.path.join(self.data_dir, 'oxford-5000.json'), 'w') as f:
                json.dump({
                    'a1': list(lists.cefr['a1']),
                    'a2': list(lists.cefr['a2']),
                    'b1': list(lists.cefr['b1']),
                    'b2': list(lists.cefr['b2']),
                    'c1': list(lists.cefr['c1']),
                    'c2': list(lists.cefr['c2'])
                }, f, indent=2)
        except Exception as error:
            print('Failed to cache word lists:', error)

    async def fetch_cefr(self):
        oxford_file_path = os.path.join(self.data_dir, 'oxford-5000.json')
        with open(oxford_file_path, 'r', encoding='utf-8') as f:
            words = json.load(f)
        
        word_by_level = {
            'a1': set(), 'a2': set(), 'b1': set(),
            'b2': set(), 'c1': set(), 'c2': set()
        }

        for word_obj in words:
            level = word_obj['level'].lower()
            if level in word_by_level:
                processed_words = await self.process_words([word_obj['word']])
                word_by_level[level].update(processed_words)

        return word_by_level

    async def process_words(self, words: List[str]) -> List[str]:
        processed = set()
        
        for word in words:
            if not word or not isinstance(word, str):
                continue
            
            try:
                tokens = await self.tokenizer(word, skip_special_tokens=True)
                tokenized = word_tokenize(word)
                stemmed = [self.stemmer.stem(token.lower()) for token in tokenized]
                
                processed.add(stemmed[0])  # Add stemmed version
                processed.add(word.lower())  # Add original version
            except Exception as error:
                print(f'Error processing word: {word}', error)
                processed.add(word.lower())

        return list(processed)

    def get_fallback_lists(self) -> WordLists:
        fallback = WordLists()
        fallback.cefr = {
            'a1': {'hello', 'world'},
            'a2': {'simple', 'basic'},
            'b1': {'intermediate', 'progress'},
            'b2': {'advanced', 'complex'},
            'c1': {'proficient', 'master'},
            'c2': {'expert', 'fluent'}
        }
        return fallback
