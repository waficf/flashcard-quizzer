"""
Quiz modes with Factory Pattern for mode selection
Abstract base class QuizMode with concrete implementations
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .quiz_strategies import QuizEngine, QuizStrategy, create_strategy


class QuizMode(ABC):
    """Abstract base class for quiz modes"""
    
    def __init__(self, name: str, description: str):
        """
        Initialize quiz mode
        
        Args:
            name: Name of the quiz mode
            description: Description of what this mode does
        """
        self.name = name
        self.description = description
        self.quiz_engine: Optional[QuizEngine] = None
    
    @abstractmethod
    def setup_quiz(self, flashcards: List[Dict[str, Any]], **kwargs) -> bool:
        """
        Setup the quiz with given flashcards
        
        Args:
            flashcards: List of flashcard data
            **kwargs: Additional configuration options
            
        Returns:
            True if setup successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_configuration_options(self) -> Dict[str, Any]:
        """
        Get available configuration options for this mode
        
        Returns:
            Dictionary of configuration options with their descriptions
        """
        pass
    
    def get_mode_info(self) -> Dict[str, str]:
        """Get basic information about this mode"""
        return {
            "name": self.name,
            "description": self.description
        }
    
    def get_quiz_engine(self) -> Optional[QuizEngine]:
        """Get the current quiz engine instance"""
        return self.quiz_engine


class StudyMode(QuizMode):
    """Standard study mode with configurable strategy"""
    
    def __init__(self):
        super().__init__(
            name="Study Mode",
            description="Standard flashcard study session with different strategies"
        )
    
    def get_configuration_options(self) -> Dict[str, Any]:
        return {
            "strategy": {
                "description": "How cards are presented",
                "options": ["sequential", "random", "adaptive"],
                "default": "random"
            },
            "max_cards": {
                "description": "Maximum number of cards to study (0 for all)",
                "type": "integer",
                "default": 0,
                "min": 0
            }
        }
    
    def setup_quiz(self, flashcards: List[Dict[str, Any]], **kwargs) -> bool:
        """Setup study mode quiz"""
        try:
            strategy_name = kwargs.get("strategy", "random")
            max_cards = kwargs.get("max_cards", 0)
            
            # Limit cards if specified
            cards_to_use = flashcards
            if max_cards > 0 and max_cards < len(flashcards):
                cards_to_use = flashcards[:max_cards]
            
            # Create quiz engine with selected strategy
            strategy = create_strategy(strategy_name)
            self.quiz_engine = QuizEngine(strategy)
            self.quiz_engine.load_cards(cards_to_use)
            
            return True
        except Exception:
            return False


class PracticeMode(QuizMode):
    """Practice mode focusing on difficult cards"""
    
    def __init__(self):
        super().__init__(
            name="Practice Mode",
            description="Focus on cards you find difficult (uses adaptive strategy)"
        )
    
    def get_configuration_options(self) -> Dict[str, Any]:
        return {
            "difficulty_threshold": {
                "description": "Success rate below which cards are considered difficult (0.0-1.0)",
                "type": "float",
                "default": 0.6,
                "min": 0.0,
                "max": 1.0
            },
            "max_cards": {
                "description": "Maximum number of cards to practice (0 for all difficult cards)",
                "type": "integer", 
                "default": 20,
                "min": 0
            }
        }
    
    def setup_quiz(self, flashcards: List[Dict[str, Any]], **kwargs) -> bool:
        """Setup practice mode quiz"""
        try:
            difficulty_threshold = kwargs.get("difficulty_threshold", 0.6)
            max_cards = kwargs.get("max_cards", 20)
            
            # Filter cards that need practice
            difficult_cards = []
            for card in flashcards:
                total_attempts = card.get("total_attempts", 0)
                correct_attempts = card.get("correct_attempts", 0)
                
                if total_attempts == 0:
                    # New cards are included
                    difficult_cards.append(card)
                else:
                    success_rate = correct_attempts / total_attempts
                    if success_rate < difficulty_threshold:
                        difficult_cards.append(card)
            
            if not difficult_cards:
                # No difficult cards found, use all cards
                difficult_cards = flashcards
            
            # Limit cards if specified
            if max_cards > 0 and max_cards < len(difficult_cards):
                difficult_cards = difficult_cards[:max_cards]
            
            # Use adaptive strategy for practice
            strategy = create_strategy("adaptive")
            self.quiz_engine = QuizEngine(strategy)
            self.quiz_engine.load_cards(difficult_cards)
            
            return True
        except Exception:
            return False


class QuickReviewMode(QuizMode):
    """Quick review mode for fast sessions"""
    
    def __init__(self):
        super().__init__(
            name="Quick Review",
            description="Quick review session with limited time or cards"
        )
    
    def get_configuration_options(self) -> Dict[str, Any]:
        return {
            "card_limit": {
                "description": "Number of cards to review",
                "type": "integer",
                "default": 10,
                "min": 1,
                "max": 50
            },
            "strategy": {
                "description": "How cards are selected",
                "options": ["random", "sequential", "adaptive"],
                "default": "random"
            }
        }
    
    def setup_quiz(self, flashcards: List[Dict[str, Any]], **kwargs) -> bool:
        """Setup quick review quiz"""
        try:
            card_limit = kwargs.get("card_limit", 10)
            strategy_name = kwargs.get("strategy", "random")
            
            # Limit cards for quick review
            cards_to_use = flashcards[:min(card_limit, len(flashcards))]
            
            # Create quiz engine
            strategy = create_strategy(strategy_name)
            self.quiz_engine = QuizEngine(strategy)
            self.quiz_engine.load_cards(cards_to_use)
            
            return True
        except Exception:
            return False


class CategoryFocusMode(QuizMode):
    """Mode that focuses on specific categories"""
    
    def __init__(self):
        super().__init__(
            name="Category Focus",
            description="Study cards from specific categories only"
        )
    
    def get_configuration_options(self) -> Dict[str, Any]:
        return {
            "categories": {
                "description": "Categories to focus on (comma-separated)",
                "type": "string",
                "default": "general"
            },
            "strategy": {
                "description": "How cards are presented",
                "options": ["sequential", "random", "adaptive"],
                "default": "random"
            },
            "max_cards": {
                "description": "Maximum cards per category (0 for all)",
                "type": "integer",
                "default": 0,
                "min": 0
            }
        }
    
    def setup_quiz(self, flashcards: List[Dict[str, Any]], **kwargs) -> bool:
        """Setup category focus quiz"""
        try:
            categories_str = kwargs.get("categories", "general")
            strategy_name = kwargs.get("strategy", "random")
            max_cards_per_category = kwargs.get("max_cards", 0)
            
            # Parse categories
            target_categories = [cat.strip().lower() for cat in categories_str.split(",")]
            
            # Filter cards by categories
            filtered_cards = []
            for card in flashcards:
                card_category = card.get("category", "general").lower()
                if card_category in target_categories:
                    filtered_cards.append(card)
            
            if not filtered_cards:
                # No cards found in specified categories
                return False
            
            # Limit cards if specified
            if max_cards_per_category > 0:
                filtered_cards = filtered_cards[:max_cards_per_category]
            
            # Create quiz engine
            strategy = create_strategy(strategy_name)
            self.quiz_engine = QuizEngine(strategy)
            self.quiz_engine.load_cards(filtered_cards)
            
            return True
        except Exception:
            return False


class QuizModeFactory:
    """Factory class for creating quiz modes"""
    
    _modes = {
        "study": StudyMode,
        "practice": PracticeMode,
        "quick": QuickReviewMode,
        "category": CategoryFocusMode
    }
    
    @classmethod
    def create_mode(cls, mode_name: str) -> Optional[QuizMode]:
        """
        Create a quiz mode instance
        
        Args:
            mode_name: Name of the mode to create
            
        Returns:
            QuizMode instance or None if mode not found
        """
        mode_name = mode_name.lower().strip()
        
        if mode_name in cls._modes:
            return cls._modes[mode_name]()
        return None
    
    @classmethod
    def get_available_modes(cls) -> Dict[str, Dict[str, str]]:
        """
        Get information about all available modes
        
        Returns:
            Dictionary mapping mode names to their information
        """
        modes_info = {}
        for name, mode_class in cls._modes.items():
            mode_instance = mode_class()
            modes_info[name] = mode_instance.get_mode_info()
        return modes_info
    
    @classmethod
    def get_mode_names(cls) -> List[str]:
        """Get list of available mode names"""
        return list(cls._modes.keys())


def display_available_modes() -> str:
    """
    Create a formatted string showing available quiz modes
    
    Returns:
        Formatted string describing all available modes
    """
    modes_info = QuizModeFactory.get_available_modes()
    
    output = "Available Quiz Modes:\n"
    output += "=" * 40 + "\n"
    
    for mode_key, mode_info in modes_info.items():
        output += f"{mode_key.upper()}: {mode_info['name']}\n"
        output += f"  {mode_info['description']}\n\n"
    
    return output