"""
Flashcard data validation module
Supports both simple list and wrapper object JSON formats
"""

import re
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class FieldType(Enum):
    """Supported field types for validation"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"


@dataclass
class ValidationRule:
    """Defines validation rules for a field"""
    field_name: str
    field_type: FieldType
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None


class FlashcardValidator:
    """Validates flashcard data against defined schema"""
    
    def __init__(self):
        self.schema = self._define_schema()
    
    def _define_schema(self) -> List[ValidationRule]:
        """Define the flashcard data schema"""
        return [
            ValidationRule(
                field_name="front",
                field_type=FieldType.STRING,
                required=True,
                min_length=1,
                max_length=1000
            ),
            ValidationRule(
                field_name="back",
                field_type=FieldType.STRING,
                required=True,
                min_length=1,
                max_length=500
            ),
            ValidationRule(
                field_name="category",
                field_type=FieldType.STRING,
                required=False,
                min_length=1,
                max_length=50,
                pattern=r'^[a-zA-Z0-9_\-\s]+$'
            ),
            ValidationRule(
                field_name="difficulty",
                field_type=FieldType.STRING,
                required=False,
                allowed_values=["easy", "medium", "hard"]
            ),
            ValidationRule(
                field_name="tags",
                field_type=FieldType.LIST,
                required=False
            ),
            ValidationRule(
                field_name="correct_attempts",
                field_type=FieldType.INTEGER,
                required=False,
                min_value=0
            ),
            ValidationRule(
                field_name="total_attempts",
                field_type=FieldType.INTEGER,
                required=False,
                min_value=0
            )
        ]
    
    def validate_json_data(self, data: Union[List[Dict], Dict]) -> List[Dict[str, Any]]:
        """
        Validate JSON data in either simple list or wrapper object format
        
        Args:
            data: Either a list of flashcards or wrapper object with 'flashcards' key
            
        Returns:
            List of validated flashcard data
            
        Raises:
            ValidationError: If validation fails
        """
        flashcard_list = self._extract_flashcard_list(data)
        return self.validate_flashcard_set(flashcard_list)
    
    def _extract_flashcard_list(self, data: Union[List[Dict], Dict]) -> List[Dict[str, Any]]:
        """
        Extract flashcard list from either format
        
        Args:
            data: Raw data from JSON
            
        Returns:
            List of flashcard dictionaries
            
        Raises:
            ValidationError: If data format is invalid
        """
        if isinstance(data, list):
            # Simple list format: [{"front": "...", "back": "..."}, ...]
            return data
        elif isinstance(data, dict):
            # Wrapper object format: {"flashcards": [...]}
            if "flashcards" in data:
                flashcards = data["flashcards"]
                if not isinstance(flashcards, list):
                    raise ValidationError("'flashcards' field must be a list")
                return flashcards
            else:
                raise ValidationError("Wrapper object must contain 'flashcards' field")
        else:
            raise ValidationError("Data must be either a list or an object with 'flashcards' field")
    
    def validate_flashcard(self, flashcard_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single flashcard
        
        Args:
            flashcard_data: Dictionary containing flashcard data
            
        Returns:
            Cleaned and validated flashcard data
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(flashcard_data, dict):
            raise ValidationError("Flashcard data must be a dictionary")
        
        validated_data = {}
        errors = []
        
        for rule in self.schema:
            field_name = rule.field_name
            field_value = flashcard_data.get(field_name)
            
            try:
                validated_value = self._validate_field(field_value, rule)
                if validated_value is not None:
                    validated_data[field_name] = validated_value
            except ValidationError as e:
                errors.append(f"{field_name}: {str(e)}")
        
        if errors:
            raise ValidationError(f"Validation failed: {'; '.join(errors)}")
        
        # Set defaults for optional fields
        validated_data.setdefault("category", "general")
        validated_data.setdefault("difficulty", "medium")
        validated_data.setdefault("tags", [])
        validated_data.setdefault("correct_attempts", 0)
        validated_data.setdefault("total_attempts", 0)
        
        return validated_data
    
    def validate_flashcard_set(self, flashcard_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate a list of flashcards
        
        Args:
            flashcard_list: List of flashcard dictionaries
            
        Returns:
            List of validated flashcard data
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(flashcard_list, list):
            raise ValidationError("Flashcard data must be a list")
        
        if not flashcard_list:
            raise ValidationError("Flashcard list cannot be empty")
        
        validated_cards = []
        errors = []
        
        for i, flashcard_data in enumerate(flashcard_list):
            try:
                validated_card = self.validate_flashcard(flashcard_data)
                validated_cards.append(validated_card)
            except ValidationError as e:
                errors.append(f"Card {i + 1}: {str(e)}")
        
        if errors:
            raise ValidationError(f"Validation failed for {len(errors)} cards:\n" + "\n".join(errors))
        
        return validated_cards
    
    def _validate_field(self, value: Any, rule: ValidationRule) -> Any:
        """
        Validate a single field
        
        Args:
            value: The field value to validate
            rule: The validation rule to apply
            
        Returns:
            The validated value
            
        Raises:
            ValidationError: If validation fails
        """
        # Handle required fields
        if value is None or (isinstance(value, str) and value.strip() == ""):
            if rule.required:
                raise ValidationError(f"Field is required")
            return None
        
        # Type validation
        if rule.field_type == FieldType.STRING:
            if not isinstance(value, str):
                raise ValidationError(f"Must be a string")
            value = value.strip()
            
            # Length validation
            if rule.min_length is not None and len(value) < rule.min_length:
                raise ValidationError(f"Must be at least {rule.min_length} characters")
            if rule.max_length is not None and len(value) > rule.max_length:
                raise ValidationError(f"Must be at most {rule.max_length} characters")
            
            # Pattern validation
            if rule.pattern and not re.match(rule.pattern, value):
                raise ValidationError(f"Does not match required pattern")
        
        elif rule.field_type == FieldType.INTEGER:
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise ValidationError(f"Must be an integer")
            
            if rule.min_value is not None and value < rule.min_value:
                raise ValidationError(f"Must be at least {rule.min_value}")
            if rule.max_value is not None and value > rule.max_value:
                raise ValidationError(f"Must be at most {rule.max_value}")
        
        elif rule.field_type == FieldType.FLOAT:
            try:
                value = float(value)
            except (ValueError, TypeError):
                raise ValidationError(f"Must be a number")
            
            if rule.min_value is not None and value < rule.min_value:
                raise ValidationError(f"Must be at least {rule.min_value}")
            if rule.max_value is not None and value > rule.max_value:
                raise ValidationError(f"Must be at most {rule.max_value}")
        
        elif rule.field_type == FieldType.BOOLEAN:
            if isinstance(value, str):
                value = value.lower()
                if value in ('true', '1', 'yes', 'on'):
                    value = True
                elif value in ('false', '0', 'no', 'off'):
                    value = False
                else:
                    raise ValidationError(f"Must be a boolean value")
            elif not isinstance(value, bool):
                raise ValidationError(f"Must be a boolean value")
        
        elif rule.field_type == FieldType.LIST:
            if not isinstance(value, list):
                # Try to convert string to list (comma-separated)
                if isinstance(value, str):
                    value = [item.strip() for item in value.split(',') if item.strip()]
                else:
                    raise ValidationError(f"Must be a list")
        
        # Allowed values validation
        if rule.allowed_values is not None:
            if value not in rule.allowed_values:
                raise ValidationError(f"Must be one of: {', '.join(map(str, rule.allowed_values))}")
        
        return value
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about the validation schema"""
        schema_info = {}
        for rule in self.schema:
            field_info = {
                "type": rule.field_type.value,
                "required": rule.required
            }
            
            if rule.min_length is not None:
                field_info["min_length"] = rule.min_length
            if rule.max_length is not None:
                field_info["max_length"] = rule.max_length
            if rule.min_value is not None:
                field_info["min_value"] = rule.min_value
            if rule.max_value is not None:
                field_info["max_value"] = rule.max_value
            if rule.pattern is not None:
                field_info["pattern"] = rule.pattern
            if rule.allowed_values is not None:
                field_info["allowed_values"] = rule.allowed_values
            
            schema_info[rule.field_name] = field_info
        
        return schema_info