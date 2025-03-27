import sys
import os
import unittest
import asyncio

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from article_dryer.lib.WordProcessor import WordProcessor

class TestWordProcessor(unittest.TestCase):
    """Test cases for the WordProcessor class"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.word_processor = WordProcessor()

    def test_normalize_word(self):
        """Test word normalization functionality"""
        test_cases = [
            # Format: (input, expected_output)
            # Basic normalization
            ("Hello", "hello"),
            ("WORLD", "world"),
            
            # Contractions
            ("don't", "do not"),
            ("isn't", "is not"),
            ("he's", "he is"),
            ("we've", "we have"),
            ("wouldn't", "would not"),
            ("she'll", "she will"),
            
            # Possessives
            ("teacher's", "teacher"),
            ("children's", "children"),
            ("boss'", "boss"),
            
            # Compound/hyphenated words
            ("self-contained", "self contained"),
            ("semi-automatic", "semi automatic"),
            ("hello-world", "hello world"),
            
            # Punctuation removal
            ("Hello!", "hello"),
            ("world?", "world"),
            
            # Inflected forms - plurals to singular
            ("cats", "cat"),
            ("boxes", "box"),
            ("children", "child"),
            ("mice", "mouse"),
            ("women", "woman"),
            
            # Inflected forms - verb tenses to base form
            ("running", "run"),
            ("walked", "walk"),
            ("ate", "eat"),
            ("is", "be"),
            ("was", "be"),
            
            # Comparatives & superlatives
            ("better", "good"),
            ("best", "good"),
            ("happier", "happy"),
            ("happiest", "happy"),
            
            # Abbreviations & acronyms
            ("dr.", "doctor"),
            ("Mr.", "mister"),
            ("NASA", "national aeronautics and space administration"),
            
            # Slang & informal language
            ("wanna", "want to"),
            ("dunno", "do not know"),
            ("lemme", "let me"),
            ("u", "you"),
            
            # Edge cases
            ("", ""),  # Empty string test
            (None, ""),  # None test
            ("123", "123"),  # Numbers
        ]

        for input_word, expected in test_cases:
            result = self.word_processor.normalize_word(input_word)
            self.assertEqual(result, expected, f"Failed to normalize '{input_word}' correctly. Got '{result}', expected '{expected}'")

    def test_normalize_words(self):
        """Test batch normalization of multiple words"""
        input_words = ["running", "better", "mice", "don't", "teacher's"]
        expected_normalized = ["run", "good", "mouse", "do not", "teacher"]
        
        results = self.word_processor.normalize_words(input_words)
        self.assertEqual(results, expected_normalized)
        
        # Test with empty list
        self.assertEqual(self.word_processor.normalize_words([]), [])
        
        # Test with invalid inputs
        self.assertEqual(self.word_processor.normalize_words([None, "", 123]), [])

    def test_extract_words(self):
        """Test extracting words from text"""
        test_text = "Hello, world! This is a sample text with some numbers like 123 and punctuation."
        expected_words = ["Hello", "world", "This", "is", "a", "sample", "text", "with", "some", 
                         "numbers", "like", "and", "punctuation"]
        
        results = self.word_processor.extract_words(test_text)
        self.assertEqual(results, expected_words)
        
        # Test with empty text
        self.assertEqual(self.word_processor.extract_words(""), [])
        
        # Test with only punctuation
        self.assertEqual(self.word_processor.extract_words("!@#$%^&*()"), [])

if __name__ == '__main__':
    unittest.main()