import sys
import os
import unittest
import asyncio
from unittest.mock import patch, MagicMock, mock_open

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from article_dryer.lib.WordLevelClassifier import WordLevelClassifier
from article_dryer.lib.WordProcessor import WordProcessor

class TestWordLevelClassifier(unittest.TestCase):
    """Test cases for the WordLevelClassifier class"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.word_processor = WordProcessor()
        
        # Create a mock word_map
        self.word_map = {
            'hello': {'word': 'hello', 'level': 'A1'},
            'world': {'word': 'world', 'level': 'A1'},
            'interesting': {'word': 'interesting', 'level': 'B1'},
            'complex': {'word': 'complex', 'level': 'B2'},
            'paradigm': {'word': 'paradigm', 'level': 'C2'},
            'run': {'word': 'run', 'level': 'A1'},
            'good': {'word': 'good', 'level': 'A1'}
        }
        
        # Create a mock cefr dictionary
        self.cefr = {
            'a1': {'hello', 'world', 'run', 'good'},
            'a2': {'book', 'table'},
            'b1': {'interesting', 'ability'},
            'b2': {'complex', 'assumption'},
            'c1': {'implementation', 'subsequent'},
            'c2': {'paradigm', 'nuance'},
            'unknown': set()
        }
        
        self.data_dir = '/mock/path'
        self.classifier = WordLevelClassifier(
            self.word_processor, 
            self.word_map, 
            self.cefr,
            self.data_dir
        )
        self.loop = asyncio.get_event_loop()

    def test_get_word_level(self):
        """Test retrieving the level of a word"""
        # Test exact match
        result = self.loop.run_until_complete(self.classifier.get_word_level('hello'))
        self.assertEqual(result['level'], 'A1')
        
        # Test case insensitivity
        result = self.loop.run_until_complete(self.classifier.get_word_level('Hello'))
        self.assertEqual(result['level'], 'A1')
        
        # Test lemmatized form
        result = self.loop.run_until_complete(self.classifier.get_word_level('running'))
        self.assertEqual(result['level'], 'A1')  # should match 'run'
        
        # Test word that doesn't exist
        result = self.loop.run_until_complete(self.classifier.get_word_level('xylophone'))
        self.assertEqual(result['level'], 'unknown')
        self.assertTrue(result.get('needs_llm_classification', False))

    @patch('builtins.open', new_callable=mock_open, read_data="CEFR definitions text")
    def test_load_cefr_definitions(self, mock_file):
        """Test loading CEFR definitions"""
        definitions = self.loop.run_until_complete(self.classifier.load_cefr_definitions())
        self.assertEqual(definitions, "CEFR definitions text")

    @patch.object(WordLevelClassifier, 'load_cefr_definitions')
    def test_get_level_examples(self, mock_load_defs):
        """Test getting level examples"""
        # Set up the test
        mock_load_defs.return_value = "Mock definitions"
        
        examples = self.loop.run_until_complete(self.classifier.get_level_examples())
        
        # Check structure
        self.assertIsInstance(examples, dict)
        for level in ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']:
            self.assertIn(level, examples)
            self.assertIsInstance(examples[level], list)
            self.assertTrue(len(examples[level]) > 0)
        
    @patch.object(WordLevelClassifier, 'load_cefr_definitions')
    @patch.object(WordLevelClassifier, 'get_level_examples')
    async def test_classify_unknown_words_with_llm(self, mock_examples, mock_defs):
        """Test classifying unknown words with LLM"""
        # Setup mocks
        mock_defs.return_value = "CEFR mock definitions"
        mock_examples.return_value = {
            'a1': ['hello', 'world'],
            'a2': ['book', 'table'],
            'b1': ['interesting', 'ability'],
            'b2': ['complex', 'assumption'],
            'c1': ['implementation', 'subsequent'],
            'c2': ['paradigm', 'nuance']
        }
        
        # Mock LLM client
        mock_llm = MagicMock()
        mock_llm.generate_text = MagicMock(return_value='{"xylophone": {"level": "B2", "explanation": "Musical instrument vocabulary"}}')
        
        # Run the test
        unknown_words = ['xylophone']
        result = await self.classifier.classify_unknown_words_with_llm(unknown_words, mock_llm)
        
        # Check result
        self.assertIn('xylophone', result)
        self.assertEqual(result['xylophone']['level'], 'B2')
        
        # Verify LLM was called with proper prompt
        mock_llm.generate_text.assert_called_once()
        prompt = mock_llm.generate_text.call_args[0][0]
        self.assertIn('xylophone', prompt)
        self.assertIn('CEFR', prompt)

    @patch.object(WordLevelClassifier, '_classify_word_batch')
    async def test_classify_unknown_words_batching(self, mock_batch):
        """Test that words are properly batched for LLM classification"""
        # Setup a mock for _classify_word_batch that returns different results for each batch
        batch1_result = {'word1': {'level': 'A2'}, 'word2': {'level': 'B1'}}
        batch2_result = {'word3': {'level': 'C1'}}
        
        mock_batch.side_effect = [batch1_result, batch2_result]
        
        # Test with multiple words to trigger batching
        unknown_words = ['word1', 'word2', 'word3']
        mock_llm = MagicMock()
        
        result = await self.classifier.classify_unknown_words_with_llm(unknown_words, mock_llm)
        
        # Check results were combined correctly
        self.assertEqual(len(result), 3)
        self.assertEqual(result['word1']['level'], 'A2')
        self.assertEqual(result['word2']['level'], 'B1')
        self.assertEqual(result['word3']['level'], 'C1')
        
        # Check that _classify_word_batch was called twice (once for each batch)
        self.assertEqual(mock_batch.call_count, 2)

if __name__ == '__main__':
    unittest.main()