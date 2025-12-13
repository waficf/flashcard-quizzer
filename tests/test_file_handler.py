"""
Test suite for FlashcardDataLoader
Tests loading functionality, error handling, and validation
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

# Add parent directory to path to import utils
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.file_handler import FlashcardDataLoader, DataLoadError
from utils.validator import ValidationError


class TestFlashcardDataLoader(unittest.TestCase):
    """Test cases for FlashcardDataLoader class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loader = FlashcardDataLoader()
        
        # Valid flashcard data - simple format
        self.valid_simple_data = [
            {
                "front": "What is the capital of France?",
                "back": "Paris",
                "category": "geography"
            },
            {
                "front": "What is 2 + 2?", 
                "back": "4",
                "category": "math"
            }
        ]
        
        # Valid flashcard data - wrapper format
        self.valid_wrapper_data = {
            "flashcards": [
                {
                    "front": "Who wrote Romeo and Juliet?",
                    "back": "William Shakespeare",
                    "category": "literature"
                },
                {
                    "front": "What is H2O?",
                    "back": "Water",
                    "category": "science"
                }
            ]
        }
        
        # Invalid data - missing back field
        self.invalid_missing_back = [
            {
                "front": "What is the capital of Spain?",
                "category": "geography"
                # Missing "back" field
            }
        ]
        
        # Invalid data - missing front field
        self.invalid_missing_front = [
            {
                "back": "Madrid",
                "category": "geography"
                # Missing "front" field
            }
        ]
        
        # Invalid JSON syntax
        self.invalid_json = '{"front": "test", "back": "test",}'  # trailing comma
    
    def test_load_valid_simple_format(self):
        """Test loading valid flashcards in simple list format"""
        # Create temporary file with valid data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_simple_data, f)
            temp_file = f.name
        
        try:
            # Test loading
            flashcards = self.loader.load_from_json_file(temp_file)
            
            # Assertions
            self.assertEqual(len(flashcards), 2)
            self.assertEqual(flashcards[0]['front'], "What is the capital of France?")
            self.assertEqual(flashcards[0]['back'], "Paris")
            self.assertEqual(flashcards[1]['front'], "What is 2 + 2?")
            self.assertEqual(flashcards[1]['back'], "4")
            
        finally:
            os.unlink(temp_file)
    
    def test_load_valid_wrapper_format(self):
        """Test loading valid flashcards in wrapper object format"""
        # Create temporary file with valid wrapper data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_wrapper_data, f)
            temp_file = f.name
        
        try:
            # Test loading
            flashcards = self.loader.load_from_json_file(temp_file)
            
            # Assertions
            self.assertEqual(len(flashcards), 2)
            self.assertEqual(flashcards[0]['front'], "Who wrote Romeo and Juliet?")
            self.assertEqual(flashcards[0]['back'], "William Shakespeare")
            
        finally:
            os.unlink(temp_file)
    
    def test_load_nonexistent_file(self):
        """Test loading from a file that doesn't exist"""
        nonexistent_file = "/tmp/nonexistent_flashcards.json"
        
        with self.assertRaises(DataLoadError) as context:
            self.loader.load_from_json_file(nonexistent_file)
        
        self.assertIn("File not found", str(context.exception))
    
    def test_load_invalid_json_syntax(self):
        """Test loading file with invalid JSON syntax"""
        # Create temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(self.invalid_json)
            temp_file = f.name
        
        try:
            with self.assertRaises(DataLoadError) as context:
                self.loader.load_from_json_file(temp_file)
            
            self.assertIn("Invalid JSON format", str(context.exception))
            
        finally:
            os.unlink(temp_file)
    
    def test_load_missing_back_field(self):
        """Test that cards without 'back' field are rejected"""
        # Create temporary file with missing back field
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.invalid_missing_back, f)
            temp_file = f.name
        
        try:
            with self.assertRaises(DataLoadError) as context:
                self.loader.load_from_json_file(temp_file)
            
            self.assertIn("Validation failed", str(context.exception))
            self.assertIn("back", str(context.exception))
            
        finally:
            os.unlink(temp_file)
    
    def test_load_missing_front_field(self):
        """Test that cards without 'front' field are rejected"""
        # Create temporary file with missing front field
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.invalid_missing_front, f)
            temp_file = f.name
        
        try:
            with self.assertRaises(DataLoadError) as context:
                self.loader.load_from_json_file(temp_file)
            
            self.assertIn("Validation failed", str(context.exception))
            self.assertIn("front", str(context.exception))
            
        finally:
            os.unlink(temp_file)
    
    def test_load_from_json_string_valid(self):
        """Test loading from valid JSON string"""
        json_string = json.dumps(self.valid_simple_data)
        
        flashcards = self.loader.load_from_json_string(json_string)
        
        self.assertEqual(len(flashcards), 2)
        self.assertEqual(flashcards[0]['front'], "What is the capital of France?")
    
    def test_load_from_json_string_invalid(self):
        """Test loading from invalid JSON string"""
        with self.assertRaises(DataLoadError) as context:
            self.loader.load_from_json_string(self.invalid_json)
        
        self.assertIn("Invalid JSON format", str(context.exception))
    
    def test_load_from_dict_valid(self):
        """Test loading from valid dictionary"""
        flashcards = self.loader.load_from_dict(self.valid_simple_data)
        
        self.assertEqual(len(flashcards), 2)
        self.assertEqual(flashcards[0]['back'], "Paris")
    
    def test_detect_json_format_simple(self):
        """Test detecting simple list format"""
        format_type = self.loader.detect_json_format(self.valid_simple_data)
        self.assertEqual(format_type, "simple")
    
    def test_detect_json_format_wrapper(self):
        """Test detecting wrapper object format"""
        format_type = self.loader.detect_json_format(self.valid_wrapper_data)
        self.assertEqual(format_type, "wrapper")
    
    def test_detect_json_format_invalid(self):
        """Test detecting invalid format"""
        invalid_data = {"wrong_key": []}
        
        with self.assertRaises(DataLoadError) as context:
            self.loader.detect_json_format(invalid_data)
        
        self.assertIn("Cannot determine JSON format", str(context.exception))
    
    def test_safe_load_from_file_success(self):
        """Test safe loading method with successful load"""
        # Create temporary file with valid data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_simple_data, f)
            temp_file = f.name
        
        try:
            result = self.loader.safe_load_from_file(temp_file)
            
            # Check success response
            self.assertTrue(result["success"])
            self.assertEqual(len(result["data"]), 2)
            self.assertIn("Successfully loaded", result["message"])
            
        finally:
            os.unlink(temp_file)
    
    def test_safe_load_from_file_failure(self):
        """Test safe loading method with failed load"""
        nonexistent_file = "/tmp/nonexistent.json"
        
        result = self.loader.safe_load_from_file(nonexistent_file)
        
        # Check failure response
        self.assertFalse(result["success"])
        self.assertIn("error_info", result)
        self.assertIn("File not found", result["message"])
    
    def test_save_to_json_file_simple(self):
        """Test saving flashcards to file in simple format"""
        flashcard_data = [
            {"front": "Test question", "back": "Test answer", "category": "test"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            # Save file
            self.loader.save_to_json_file(flashcard_data, temp_file, "simple")
            
            # Read back and verify
            with open(temp_file, 'r') as f:
                saved_data = json.load(f)
            
            self.assertEqual(saved_data, flashcard_data)
            
        finally:
            os.unlink(temp_file)
    
    def test_save_to_json_file_wrapper(self):
        """Test saving flashcards to file in wrapper format"""
        flashcard_data = [
            {"front": "Test question", "back": "Test answer", "category": "test"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            # Save file
            self.loader.save_to_json_file(flashcard_data, temp_file, "wrapper")
            
            # Read back and verify
            with open(temp_file, 'r') as f:
                saved_data = json.load(f)
            
            expected_data = {"flashcards": flashcard_data}
            self.assertEqual(saved_data, expected_data)
            
        finally:
            os.unlink(temp_file)
    
    def test_get_file_info_valid(self):
        """Test getting file information for valid file"""
        # Create temporary file with valid data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_simple_data, f)
            temp_file = f.name
        
        try:
            info = self.loader.get_file_info(temp_file)
            
            # Check file info
            self.assertTrue(info["valid"])
            self.assertEqual(info["format"], "simple")
            self.assertEqual(info["total_cards"], 2)
            self.assertIn("geography", info["categories"])
            self.assertIn("math", info["categories"])
            
        finally:
            os.unlink(temp_file)
    
    def test_get_file_info_invalid(self):
        """Test getting file information for invalid file"""
        # Create temporary file with invalid data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.invalid_missing_back, f)
            temp_file = f.name
        
        try:
            info = self.loader.get_file_info(temp_file)
            
            # Check file info for invalid file
            self.assertFalse(info["valid"])
            self.assertIn("error", info)
            self.assertEqual(info["total_cards"], 0)
            
        finally:
            os.unlink(temp_file)
    
    def test_error_handling_user_friendly_messages(self):
        """Test that error messages are user-friendly"""
        # Test file not found error
        result = self.loader.safe_load_from_file("/nonexistent/path.json")
        
        error_info = result["error_info"]
        self.assertIn("could not be found", error_info["user_message"])
        self.assertGreater(len(error_info["suggestions"]), 0)
    
    def test_batch_load_files_mixed_results(self):
        """Test batch loading with some successful and some failed files"""
        # Create one valid file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_simple_data, f)
            valid_file = f.name
        
        # Create one invalid file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(self.invalid_json)
            invalid_file = f.name
        
        try:
            # Test batch loading
            results = self.loader.batch_load_files([valid_file, invalid_file, "/nonexistent.json"])
            
            # Check results
            self.assertEqual(len(results["successful"]), 1)
            self.assertEqual(len(results["failed"]), 2)
            self.assertEqual(results["total_cards"], 2)
            
        finally:
            os.unlink(valid_file)
            os.unlink(invalid_file)


if __name__ == '__main__':
    unittest.main()