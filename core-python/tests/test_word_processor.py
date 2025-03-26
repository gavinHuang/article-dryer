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
            ("Hello", "hello"),
            ("WORLD", "world"),
            ("don't", "do not"),
            ("isn't", "is not"),
            ("teacher's", "teacher"),
            ("self-contained", "self contained"),
            ("Hello!", "hello"),
            ("semi-automatic", "semi automatic"),
            ("", ""),  # Empty string test
            (None, ""),  # None test
            ("123", "123"),  # Numbers
            ("hello-world", "hello world")
        ]

        for input_word, expected in test_cases:
            result = self.word_processor.normalize_word(input_word)
            self.assertEqual(result, expected, f"Failed to normalize '{input_word}' correctly")

    def test_process_word(self):
        """Test word processing with different types"""
        # Test lemmatization
        lemma_cases = [
            ("running", "run"),
            ("better", "good"),
            ("mice", "mouse"),
            ("stories", "story"),
            ("is", "be")
        ]
        for input_word, expected in lemma_cases:
            result = self.word_processor.process_word(input_word, "lemma")
            self.assertEqual(result, expected, f"Failed to lemmatize '{input_word}' correctly")

        # Test stemming
        stem_cases = [
            ("running", "run"),
            ("easily", "easili"),
            ("better", "better"),
            ("stories", "stori"),
        ]
        for input_word, expected in stem_cases:
            result = self.word_processor.process_word(input_word, "stem")
            self.assertEqual(result, expected, f"Failed to stem '{input_word}' correctly")

        # Test tokenization (harder to test precisely due to the tokenizer implementation)
        # Instead, check that we get a result for common words
        token_inputs = ["hello", "world", "testing"]
        for input_word in token_inputs:
            result = self.word_processor.process_word(input_word, "token")
            self.assertIsNotNone(result)
            self.assertTrue(len(result) > 0)

    def test_process_words(self):
        """Test batch processing of multiple words"""
        input_words = ["running", "better", "mice", "stories"]
        expected_lemmas = ["run", "good", "mouse", "story"]
        
        results = self.word_processor.process_words(input_words, "lemma")
        self.assertEqual(results, expected_lemmas)

    def test_extract_words(self):
        """Test extracting words from text"""
        test_text = "Hello, world! This is a sample text with some numbers like 123 and punctuation."
        expected_words = ["hello", "world", "this", "is", "a", "sample", "text", "with", "some", 
                         "numbers", "like", "123", "and", "punctuation"]
        
        results = self.word_processor.extract_words(test_text)
        self.assertEqual(results, expected_words)
        
        # Test with empty text
        self.assertEqual(self.word_processor.extract_words(""), [])
        
        # Test with only punctuation
        self.assertEqual(self.word_processor.extract_words("!@#$%^&*()"), [])

if __name__ == '__main__':
    unittest.main()