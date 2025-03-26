import sys
import os
import unittest
import asyncio
from unittest.mock import patch, MagicMock, mock_open

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from article_dryer.lib.WordListLoader import WordListLoader, WordLists

class TestWordListLoader(unittest.TestCase):
    """Test cases for the WordListLoader class"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Reset the singleton instance before each test
        WordListLoader._instance = None
        self.loop = asyncio.get_event_loop()

    @patch('os.path.exists')
    @patch('json.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_oxford_words(self, mock_file, mock_json_load, mock_exists):
        """Test loading Oxford word list"""
        # Mock the file existence check
        mock_exists.return_value = True
        
        # Mock the JSON data that would be loaded
        mock_json_load.return_value = [
            {'word': 'hello', 'level': 'A1'},
            {'word': 'world', 'level': 'A1'},
            {'word': 'complex', 'level': 'B2'},
            {'word': 'ambivalence', 'level': 'C2'}
        ]
        
        # Run the test
        word_loader = self.loop.run_until_complete(WordListLoader.get_instance())
        word_lists = WordLists()
        self.loop.run_until_complete(word_loader.load_oxford_words(word_lists))
        
        # Verify results
        self.assertIn('hello', word_lists.cefr['a1'])
        self.assertIn('world', word_lists.cefr['a1'])
        self.assertIn('complex', word_lists.cefr['b2'])
        self.assertIn('ambivalence', word_lists.cefr['c2'])
        
        # Check the word_map
        self.assertIn('hello', word_lists.word_map)
        self.assertIn('world', word_lists.word_map)
        self.assertEqual(word_lists.word_map['hello']['level'], 'A1')
        
    @patch('os.path.exists')
    @patch('csv.reader')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_epv_words(self, mock_file, mock_csv_reader, mock_exists):
        """Test loading EPV word list"""
        # Mock the file existence check
        mock_exists.return_value = True
        
        # Mock the CSV data
        mock_csv_reader.return_value = [
            ['unique', 'b1'],
            ['rare', 'c1'],
            ['hello', 'a1']  # This one should be skipped if it already exists in Oxford
        ]
        
        # Run the test
        word_loader = self.loop.run_until_complete(WordListLoader.get_instance())
        word_lists = WordLists()
        
        # Add a word to simulate that it came from Oxford
        word_lists.word_map['hello'] = {'word': 'hello', 'level': 'A1', 'source': 'oxford'}
        word_lists.cefr['a1'].add('hello')
        
        # Run the EPV loading
        self.loop.run_until_complete(word_loader.load_epv_words(word_lists))
        
        # Verify results - 'hello' should remain with original data
        self.assertIn('unique', word_lists.cefr['b1'])
        self.assertIn('rare', word_lists.cefr['c1'])
        self.assertEqual(word_lists.word_map['hello'].get('source'), 'oxford')
        self.assertEqual(word_lists.word_map['unique'].get('source'), 'epv')

    @patch.object(WordListLoader, 'load_oxford_words')
    @patch.object(WordListLoader, 'load_epv_words')
    def test_load_word_lists(self, mock_load_epv, mock_load_oxford):
        """Test the main load_word_lists method"""
        word_loader = self.loop.run_until_complete(WordListLoader.get_instance())
        
        # Run the method
        word_lists = self.loop.run_until_complete(word_loader.load_word_lists())
        
        # Verify both loaders were called
        mock_load_oxford.assert_called_once()
        mock_load_epv.assert_called_once()
        
        # Verify we got a WordLists instance back
        self.assertIsInstance(word_lists, WordLists)

    def test_word_exists_in_any_form(self):
        """Test checking if a word exists in any form"""
        word_loader = self.loop.run_until_complete(WordListLoader.get_instance())
        word_lists = WordLists()
        
        # Add some test words
        word_lists.word_map = {
            'run': {'word': 'run', 'level': 'A1'},
            'good': {'word': 'good', 'level': 'A1'},
        }
        
        # Test exact match
        result = self.loop.run_until_complete(word_loader.word_exists_in_any_form('run', word_lists))
        self.assertTrue(result)
        
        # Test case insensitivity
        result = self.loop.run_until_complete(word_loader.word_exists_in_any_form('RUN', word_lists))
        self.assertTrue(result)
        
        # Test lemma form
        result = self.loop.run_until_complete(word_loader.word_exists_in_any_form('running', word_lists))
        self.assertTrue(result)
        
        # Test word that doesn't exist in any form
        result = self.loop.run_until_complete(word_loader.word_exists_in_any_form('xylophone', word_lists))
        self.assertFalse(result)

    def test_add_word_forms_to_map(self):
        """Test adding word forms to the map"""
        word_loader = self.loop.run_until_complete(WordListLoader.get_instance())
        word_lists = WordLists()
        
        word = 'running'
        word_value = {'word': 'running', 'level': 'A2'}
        
        # Add word forms
        self.loop.run_until_complete(word_loader.add_word_forms_to_map(word, word_value, word_lists))
        
        # Verify original form was added
        self.assertIn('running', word_lists.word_map)
        
        # Verify lemmatized form was added
        self.assertIn('run', word_lists.word_map)
        
        # Verify stem form was added if different
        stem_form = word_loader.word_processor.process_word(word, "stem")
        if stem_form != 'running' and stem_form != 'run':
            self.assertIn(stem_form, word_lists.word_map)

    def test_get_fallback_lists(self):
        """Test fallback vocabulary creation"""
        word_loader = self.loop.run_until_complete(WordListLoader.get_instance())
        
        fallback = word_loader.get_fallback_lists()
        
        # Check basic structure
        self.assertIsInstance(fallback, WordLists)
        self.assertIn('hello', fallback.word_map)
        self.assertIn('hello', fallback.cefr['a1'])
        self.assertIn('complex', fallback.cefr['b2'])
        
        # Verify fallback levels are correct
        self.assertEqual(fallback.word_map['hello']['level'], 'A1')
        self.assertEqual(fallback.word_map['complex']['level'], 'B2')

    def test_get_data_dir(self):
        """Test getting data directory path"""
        word_loader = self.loop.run_until_complete(WordListLoader.get_instance())
        
        data_dir = word_loader.get_data_dir()
        
        # Verify it ends with the correct path segment
        self.assertTrue(data_dir.endswith('data'))

if __name__ == '__main__':
    unittest.main()