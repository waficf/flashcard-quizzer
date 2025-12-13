"""
Flashcard data loader module with user-friendly error handling
Handles loading and validating flashcard data from various sources
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from .validator import FlashcardValidator, ValidationError


class DataLoadError(Exception):
    """Custom exception for data loading errors"""
    pass


class FlashcardDataLoader:
    """Loads and validates flashcard data from various sources"""
    
    def __init__(self):
        self.validator = FlashcardValidator()
    
    def load_from_json_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Load flashcards from a JSON file
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of validated flashcard data
            
        Raises:
            DataLoadError: If loading or validation fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DataLoadError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise DataLoadError(f"Path is not a file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise DataLoadError(f"Invalid JSON format in {file_path}: {e}")
        except Exception as e:
            raise DataLoadError(f"Error reading file {file_path}: {e}")
        
        try:
            return self.validator.validate_json_data(data)
        except ValidationError as e:
            raise DataLoadError(f"Validation failed for {file_path}: {e}")
    
    def load_from_json_string(self, json_string: str) -> List[Dict[str, Any]]:
        """
        Load flashcards from a JSON string
        
        Args:
            json_string: JSON string containing flashcard data
            
        Returns:
            List of validated flashcard data
            
        Raises:
            DataLoadError: If loading or validation fails
        """
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise DataLoadError(f"Invalid JSON format: {e}")
        
        try:
            return self.validator.validate_json_data(data)
        except ValidationError as e:
            raise DataLoadError(f"Validation failed: {e}")
    
    def load_from_dict(self, data: Union[List[Dict], Dict]) -> List[Dict[str, Any]]:
        """
        Load flashcards from a dictionary or list
        
        Args:
            data: Raw flashcard data
            
        Returns:
            List of validated flashcard data
            
        Raises:
            DataLoadError: If validation fails
        """
        try:
            return self.validator.validate_json_data(data)
        except ValidationError as e:
            raise DataLoadError(f"Validation failed: {e}")
    
    def save_to_json_file(self, flashcards: List[Dict[str, Any]], 
                         file_path: Union[str, Path], 
                         format_type: str = "simple") -> None:
        """
        Save flashcards to a JSON file
        
        Args:
            flashcards: List of flashcard data
            file_path: Path where to save the file
            format_type: "simple" for list format, "wrapper" for object format
            
        Raises:
            DataLoadError: If saving fails
        """
        file_path = Path(file_path)
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format_type == "simple":
            data = flashcards
        elif format_type == "wrapper":
            data = {"flashcards": flashcards}
        else:
            raise DataLoadError(f"Invalid format type: {format_type}. Must be 'simple' or 'wrapper'")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise DataLoadError(f"Error writing file {file_path}: {e}")
    
    def detect_json_format(self, data: Union[List[Dict], Dict]) -> str:
        """
        Detect the format of JSON data
        
        Args:
            data: Raw JSON data
            
        Returns:
            "simple" for list format, "wrapper" for object format
            
        Raises:
            DataLoadError: If format cannot be determined
        """
        if isinstance(data, list):
            return "simple"
        elif isinstance(data, dict) and "flashcards" in data:
            return "wrapper"
        else:
            raise DataLoadError("Cannot determine JSON format")
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get information about a flashcard file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
            
        Raises:
            DataLoadError: If file cannot be analyzed
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DataLoadError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise DataLoadError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise DataLoadError(f"Error reading file: {e}")
        
        try:
            format_type = self.detect_json_format(data)
            flashcards = self.validator.validate_json_data(data)
            
            # Analyze flashcard statistics
            categories = set()
            difficulties = set()
            total_cards = len(flashcards)
            
            for card in flashcards:
                categories.add(card.get("category", "general"))
                difficulties.add(card.get("difficulty", "medium"))
            
            return {
                "file_path": str(file_path),
                "format": format_type,
                "total_cards": total_cards,
                "categories": sorted(list(categories)),
                "difficulties": sorted(list(difficulties)),
                "file_size": file_path.stat().st_size,
                "valid": True
            }
        
        except (ValidationError, DataLoadError) as e:
            return {
                "file_path": str(file_path),
                "format": "unknown",
                "total_cards": 0,
                "categories": [],
                "difficulties": [],
                "file_size": file_path.stat().st_size,
                "valid": False,
                "error": str(e)
            }
    
    def batch_load_files(self, file_paths: List[Union[str, Path]]) -> Dict[str, Any]:
        """
        Load multiple flashcard files
        
        Args:
            file_paths: List of file paths to load
            
        Returns:
            Dictionary with loaded data and any errors
        """
        results = {
            "successful": [],
            "failed": [],
            "total_cards": 0
        }
        
        for file_path in file_paths:
            try:
                flashcards = self.load_from_json_file(file_path)
                results["successful"].append({
                    "file_path": str(file_path),
                    "cards": flashcards,
                    "count": len(flashcards)
                })
                results["total_cards"] += len(flashcards)
            except DataLoadError as e:
                results["failed"].append({
                    "file_path": str(file_path),
                    "error": str(e)
                })
        
        return results
    
    def convert_format(self, input_file: Union[str, Path], 
                      output_file: Union[str, Path], 
                      target_format: str) -> None:
        """
        Convert flashcard file from one format to another
        
        Args:
            input_file: Source file path
            output_file: Destination file path  
            target_format: "simple" or "wrapper"
            
        Raises:
            DataLoadError: If conversion fails
        """
        flashcards = self.load_from_json_file(input_file)
        self.save_to_json_file(flashcards, output_file, target_format)
    
    def merge_files(self, file_paths: List[Union[str, Path]], 
                   output_file: Union[str, Path], 
                   output_format: str = "simple") -> Dict[str, Any]:
        """
        Merge multiple flashcard files into one
        
        Args:
            file_paths: List of input file paths
            output_file: Output file path
            output_format: Format for the output file
            
        Returns:
            Dictionary with merge results
            
        Raises:
            DataLoadError: If merge fails
        """
        batch_results = self.batch_load_files(file_paths)
        
        if batch_results["failed"]:
            raise DataLoadError(f"Failed to load {len(batch_results['failed'])} files")
        
        # Combine all flashcards
        all_flashcards = []
        for result in batch_results["successful"]:
            all_flashcards.extend(result["cards"])
        
        # Save merged file
        self.save_to_json_file(all_flashcards, output_file, output_format)
        
        return {
            "input_files": len(file_paths),
            "total_cards": len(all_flashcards),
            "output_file": str(output_file),
            "output_format": output_format
        }
    
    def handle_load_error(self, error: Exception, file_path: str) -> Dict[str, Any]:
        """
        Convert file loading errors into user-friendly messages
        
        Args:
            error: The exception that occurred
            file_path: Path to the file that caused the error
            
        Returns:
            Dictionary with error information and friendly message
        """
        error_info = {
            "success": False,
            "file_path": file_path,
            "error_type": type(error).__name__,
            "technical_error": str(error),
            "user_message": "",
            "suggestions": []
        }
        
        if isinstance(error, FileNotFoundError):
            error_info["user_message"] = f"The file '{file_path}' could not be found."
            error_info["suggestions"] = [
                "Check if the file path is correct",
                "Make sure the file exists in the specified location",
                "Verify you have permission to access the file"
            ]
        
        elif isinstance(error, PermissionError):
            error_info["user_message"] = f"You don't have permission to access the file '{file_path}'."
            error_info["suggestions"] = [
                "Check file permissions",
                "Make sure the file is not being used by another program",
                "Try running as administrator if necessary"
            ]
        
        elif isinstance(error, json.JSONDecodeError):
            line_info = f" (line {error.lineno}, column {error.colno})" if hasattr(error, 'lineno') else ""
            error_info["user_message"] = f"The file '{file_path}' contains invalid JSON format{line_info}."
            error_info["suggestions"] = [
                "Check for missing commas, brackets, or quotes",
                "Use a JSON validator to identify the specific issue",
                "Make sure the file is properly formatted JSON",
                "Check for trailing commas which are not allowed in JSON"
            ]
        
        elif isinstance(error, ValidationError):
            error_info["user_message"] = f"The flashcard data in '{file_path}' has validation errors."
            error_info["suggestions"] = self._get_validation_suggestions(str(error))
        
        elif isinstance(error, DataLoadError):
            if "Invalid JSON format" in str(error):
                error_info["user_message"] = f"The file '{file_path}' is not in a valid JSON format."
                error_info["suggestions"] = [
                    "Make sure the file contains valid JSON",
                    "Check for syntax errors like missing quotes or brackets",
                    "Verify the file is not corrupted"
                ]
            elif "flashcards" in str(error):
                error_info["user_message"] = f"The file '{file_path}' doesn't have the expected flashcard structure."
                error_info["suggestions"] = [
                    "For wrapper format: file should contain a 'flashcards' field with an array",
                    "For simple format: file should be an array of flashcard objects",
                    "Each flashcard should have 'front' and 'back' fields"
                ]
            else:
                error_info["user_message"] = f"There was a problem loading the file '{file_path}'."
                error_info["suggestions"] = ["Check the file format and try again"]
        
        else:
            error_info["user_message"] = f"An unexpected error occurred while loading '{file_path}'."
            error_info["suggestions"] = [
                "Check if the file is corrupted",
                "Try opening the file in a text editor to verify its contents",
                "Contact support if the problem persists"
            ]
        
        return error_info
    
    def _get_validation_suggestions(self, error_message: str) -> list:
        """Get specific suggestions based on validation error message"""
        suggestions = []
        
        if "front" in error_message and "required" in error_message:
            suggestions.extend([
                "Each flashcard must have a 'front' field (the question)",
                "Make sure the 'front' field is not empty"
            ])
        
        if "back" in error_message and "required" in error_message:
            suggestions.extend([
                "Each flashcard must have a 'back' field (the answer)",
                "Make sure the 'back' field is not empty"
            ])
        
        if "must be a string" in error_message:
            suggestions.append("Text fields should be enclosed in quotes")
        
        if "difficulty" in error_message:
            suggestions.append("Difficulty must be one of: 'easy', 'medium', 'hard'")
        
        if "category" in error_message and "pattern" in error_message:
            suggestions.append("Category names can only contain letters, numbers, spaces, hyphens, and underscores")
        
        if "must be at least" in error_message:
            suggestions.append("Fields cannot be empty - add some content")
        
        if "must be at most" in error_message:
            suggestions.append("Content is too long - please shorten it")
        
        if not suggestions:
            suggestions = [
                "Check that all required fields are present",
                "Verify field values match the expected format"
            ]
        
        return suggestions
    
    def format_friendly_message(self, error_info: Dict[str, Any]) -> str:
        """
        Format error information into a user-friendly message
        
        Args:
            error_info: Error information dictionary
            
        Returns:
            Formatted error message string
        """
        message = f"❌ {error_info['user_message']}\n"
        
        if error_info['suggestions']:
            message += "\n💡 Suggestions:\n"
            for i, suggestion in enumerate(error_info['suggestions'], 1):
                message += f"   {i}. {suggestion}\n"
        
        return message
    
    def safe_load_from_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Safely load flashcards with user-friendly error handling
        
        Args:
            file_path: Path to the flashcard file
            
        Returns:
            Dictionary with success status and data or error info
        """
        try:
            flashcards = self.load_from_json_file(file_path)
            return {
                "success": True,
                "data": flashcards,
                "message": f"✅ Successfully loaded {len(flashcards)} flashcard(s) from '{file_path}'"
            }
        except Exception as error:
            error_info = self.handle_load_error(error, str(file_path))
            return {
                "success": False,
                "error_info": error_info,
                "message": self.format_friendly_message(error_info)
            }
    
    def safe_save_to_file(self, flashcards: List[Dict[str, Any]], 
                         file_path: Union[str, Path], 
                         format_type: str = "simple") -> Dict[str, Any]:
        """
        Safely save flashcards with user-friendly error handling
        
        Args:
            flashcards: List of flashcard data
            file_path: Path where to save the file
            format_type: Format type ("simple" or "wrapper")
            
        Returns:
            Dictionary with success status and message
        """
        try:
            self.save_to_json_file(flashcards, file_path, format_type)
            return {
                "success": True,
                "message": f"✅ Successfully saved {len(flashcards)} flashcard(s) to '{file_path}'"
            }
        except Exception as error:
            return {
                "success": False,
                "message": f"❌ Failed to save file '{file_path}': {str(error)}",
                "suggestions": [
                    "Check if you have write permission to the directory",
                    "Make sure the directory exists",
                    "Verify there's enough disk space"
                ]
            }