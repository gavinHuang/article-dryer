import re
import nltk
import logging
import tiktoken
from typing import List, Literal, Dict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type for processing type
ProcessingType = Literal["token", "stem", "lemma"]

class WordProcessor:
    """
    A class for processing and normalizing words including:
    - Word lemmatization
    - Stemming
    - Tokenization
    - Normalization (contractions, possessives, compound words)
    """
    
    def __init__(self):
        """Initialize the WordProcessor with necessary NLP tools"""
        self.stemmer = nltk.stem.PorterStemmer()
        self.lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()
        self.encoding = tiktoken.get_encoding("cl100k_base")  # Using OpenAI's tokenizer
        self.contractions_map = self._create_contractions_map()
        self._ensure_nltk_data()
        
    def _ensure_nltk_data(self):
        """Ensure required NLTK data is downloaded"""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/wordnet')
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            logger.info('Downloading required NLTK data...')
            nltk.download('punkt')
            nltk.download('wordnet')
            nltk.download('averaged_perceptron_tagger')

    def _create_contractions_map(self) -> Dict[str, str]:
        """Create a map of English contractions to their expanded forms"""
        return {
            # Common contractions
            "aren't": "are not",
            "can't": "cannot",
            "couldn't": "could not",
            "didn't": "did not",
            "doesn't": "does not",
            "don't": "do not",
            "hadn't": "had not",
            "hasn't": "has not",
            "haven't": "have not",
            "he'd": "he would",
            "he'll": "he will",
            "he's": "he is",
            "i'd": "i would",
            "i'll": "i will",
            "i'm": "i am",
            "i've": "i have",
            "isn't": "is not",
            "it's": "it is",
            "let's": "let us",
            "mightn't": "might not",
            "mustn't": "must not",
            "shan't": "shall not",
            "she'd": "she would",
            "she'll": "she will",
            "she's": "she is",
            "shouldn't": "should not",
            "that's": "that is",
            "there's": "there is",
            "they'd": "they would",
            "they'll": "they will",
            "they're": "they are",
            "they've": "they have",
            "we'd": "we would",
            "we're": "we are",
            "we've": "we have",
            "weren't": "were not",
            "what'll": "what will",
            "what're": "what are",
            "what's": "what is",
            "what've": "what have",
            "where's": "where is",
            "who'd": "who would",
            "who'll": "who will",
            "who're": "who are",
            "who's": "who is",
            "who've": "who have",
            "won't": "will not",
            "wouldn't": "would not",
            "you'd": "you would",
            "you'll": "you will",
            "you're": "you are",
            "you've": "you have",
            # Possessives - map to the non-possessive form
            "teacher's": "teacher",
            "girl's": "girl",
            "boy's": "boy",
            "dog's": "dog",
            "cat's": "cat",
            "children's": "children",
            "men's": "men",
            "women's": "women",
            "people's": "people",
        }

    def normalize_word(self, word: str) -> str:
        """
        Normalize a word by:
        1. Converting to lowercase
        2. Expanding contractions
        3. Handling possessives
        4. Handling compound/hyphenated words
        5. Removing non-alphabetic characters
        """
        if not word or not isinstance(word, str):
            return ""
        
        # Convert to lowercase
        word = word.lower().strip()
        
        # Expand contractions
        if word in self.contractions_map:
            word = self.contractions_map[word]
            
        # Handle general possessives (e.g., teacher's -> teacher)
        if word.endswith("'s"):
            word = word[:-2]
            
        # Handle compound/hyphenated words (convert to space-separated)
        word = word.replace('-', ' ')
        
        # Remove any remaining punctuation and special characters
        word = re.sub(r'[^\w\s]', '', word)
        
        return word.strip()

    def process_word(self, word: str, process_type: ProcessingType = "lemma") -> str:
        """
        Process a single word using the specified processing type:
        - lemma: convert to base form using lemmatization (default, best for analysis)
        - stem: apply stemming
        - token: tokenize with tiktoken
        """
        if not word or not isinstance(word, str):
            return ""
        
        word = word.lower().strip()
        
        try:
            if process_type == "lemma":
                # Get the word's part of speech for better lemmatization
                pos_tag = nltk.pos_tag([word])[0][1]
                pos = 'n'  # Default to noun
                
                # Convert Penn Treebank tag to WordNet tag
                if pos_tag.startswith('J'):
                    pos = 'a'  # Adjective
                elif pos_tag.startswith('V'):
                    pos = 'v'  # Verb
                elif pos_tag.startswith('R'):
                    pos = 'r'  # Adverb
                    
                # Lemmatize with appropriate POS
                return self.lemmatizer.lemmatize(word, pos)
                
            elif process_type == "stem":
                # Apply stemming
                return self.stemmer.stem(word)
                
            else:  # Default to tokenization
                # Use tiktoken for tokenization
                token_ids = self.encoding.encode(word)
                
                # For tokenization, we'll return the first token
                if token_ids:
                    return self.encoding.decode([token_ids[0]]).strip()
                else:
                    return word
                
        except Exception as error:
            logger.error(f'Error processing word: {word} - {error}')
            return word

    def process_words(self, words: List[str], process_type: ProcessingType = "lemma") -> List[str]:
        """Process multiple words using the specified processing type"""
        processed = []
        for word in words:
            if not word or not isinstance(word, str):
                continue
                
            try:
                # Normalize and preprocess the word first
                normalized_word = self.normalize_word(word)
                processed_word = self.process_word(normalized_word, process_type)
                processed.append(processed_word)
            except Exception as error:
                logger.error(f'Error processing word: {word} - {error}')
                processed.append(word.lower())
                
        return processed
        
    def extract_words(self, text: str) -> List[str]:
        """Extract individual words from text, filtering out punctuation and numbers"""
        # Split text into words using regex
        # This will match words containing letters, apostrophes but exclude pure numbers
        words = re.findall(r'\b(?![0-9]+\b)[a-zA-Z\'-]+\b', text)
        return [word for word in words if word]