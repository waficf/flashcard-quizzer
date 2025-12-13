"""
Quiz strategies implementing the Strategy pattern
Three modes: Sequential, Random, and Adaptive
"""

from abc import ABC, abstractmethod
import random
from typing import List, Dict, Any, Optional


class QuizStrategy(ABC):
    """Abstract base class for quiz strategies"""
    
    @abstractmethod
    def get_card_order(self, cards: List[Dict[str, Any]]) -> List[int]:
        """
        Get the order in which cards should be presented
        
        Args:
            cards: List of flashcards
            
        Returns:
            List of card indices in the order they should be presented
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return the name of this strategy"""
        pass


class SequentialStrategy(QuizStrategy):
    """Sequential quiz strategy: presents cards in order 1,2,3"""
    
    def get_strategy_name(self) -> str:
        return "Sequential"
    
    def get_card_order(self, cards: List[Dict[str, Any]]) -> List[int]:
        """Return cards in sequential order (1,2,3,...)"""
        return list(range(len(cards)))


class RandomStrategy(QuizStrategy):
    """Random quiz strategy: shuffles the order of cards"""
    
    def get_strategy_name(self) -> str:
        return "Random"
    
    def get_card_order(self, cards: List[Dict[str, Any]]) -> List[int]:
        """Return cards in shuffled order"""
        indices = list(range(len(cards)))
        random.shuffle(indices)
        return indices


class AdaptiveStrategy(QuizStrategy):
    """Adaptive quiz strategy: prioritizes cards that users get wrong"""
    
    def get_strategy_name(self) -> str:
        return "Adaptive"
    
    def get_card_order(self, cards: List[Dict[str, Any]]) -> List[int]:
        """Return cards ordered by difficulty (most wrong answers first)"""
        
        # Calculate difficulty score for each card
        card_difficulty = []
        for i, card in enumerate(cards):
            total_attempts = card.get("total_attempts", 0)
            correct_attempts = card.get("correct_attempts", 0)
            
            if total_attempts == 0:
                # New cards get medium priority
                difficulty_score = 0.5
            else:
                # Cards with lower success rate are more difficult
                success_rate = correct_attempts / total_attempts
                difficulty_score = 1 - success_rate  # Higher score = more difficult
            
            card_difficulty.append((i, difficulty_score))
        
        # Sort by difficulty score (highest first = most wrong answers first)
        card_difficulty.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the indices
        return [card_index for card_index, _ in card_difficulty]


class QuizEngine:
    """Quiz engine that uses different strategies to present flashcards"""
    
    def __init__(self, strategy: QuizStrategy):
        """
        Initialize quiz engine with a strategy
        
        Args:
            strategy: The quiz strategy to use
        """
        self.strategy = strategy
        self.cards = []
        self.card_order = []
        self.current_position = 0
        self.session_stats = {
            "correct": 0,
            "total": 0,
            "strategy_used": ""
        }
    
    def load_cards(self, cards: List[Dict[str, Any]]) -> None:
        """
        Load flashcards and determine presentation order
        
        Args:
            cards: List of flashcard dictionaries
        """
        self.cards = cards.copy()
        self.card_order = self.strategy.get_card_order(self.cards)
        self.current_position = 0
        self.session_stats["strategy_used"] = self.strategy.get_strategy_name()
        self.session_stats["total_cards"] = len(self.cards)
    
    def get_next_card(self) -> Optional[Dict[str, Any]]:
        """
        Get the next card according to the current strategy
        
        Returns:
            Next flashcard or None if quiz is finished
        """
        if self.current_position >= len(self.card_order):
            return None
        
        card_index = self.card_order[self.current_position]
        return self.cards[card_index]
    
    def answer_card(self, is_correct: bool) -> None:
        """
        Record the answer for the current card and move to next
        
        Args:
            is_correct: Whether the answer was correct
        """
        if self.current_position < len(self.card_order):
            card_index = self.card_order[self.current_position]
            card = self.cards[card_index]
            
            # Update card statistics
            card["total_attempts"] = card.get("total_attempts", 0) + 1
            if is_correct:
                card["correct_attempts"] = card.get("correct_attempts", 0) + 1
                self.session_stats["correct"] += 1
            
            # Update session statistics
            self.session_stats["total"] += 1
            
            # Move to next card
            self.current_position += 1
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get current quiz progress
        
        Returns:
            Dictionary with progress information
        """
        total_cards = len(self.card_order)
        completed = self.current_position
        
        return {
            "completed": completed,
            "total": total_cards,
            "remaining": total_cards - completed,
            "progress_percentage": (completed / total_cards * 100) if total_cards > 0 else 0,
            "current_accuracy": (self.session_stats["correct"] / self.session_stats["total"] * 100) if self.session_stats["total"] > 0 else 0
        }
    
    def is_finished(self) -> bool:
        """
        Check if the quiz is finished
        
        Returns:
            True if all cards have been presented
        """
        return self.current_position >= len(self.card_order)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of the quiz session
        
        Returns:
            Dictionary with session statistics
        """
        total = self.session_stats["total"]
        correct = self.session_stats["correct"]
        
        return {
            "strategy_used": self.session_stats["strategy_used"],
            "total_cards": len(self.card_order),
            "cards_completed": total,
            "correct_answers": correct,
            "incorrect_answers": total - correct,
            "accuracy_percentage": (correct / total * 100) if total > 0 else 0,
            "finished": self.is_finished()
        }
    
    def reset(self) -> None:
        """Reset the quiz to start over with the same cards and strategy"""
        self.current_position = 0
        self.session_stats["correct"] = 0
        self.session_stats["total"] = 0
        # Regenerate card order (important for random strategy)
        if self.cards:
            self.card_order = self.strategy.get_card_order(self.cards)
    
    def change_strategy(self, new_strategy: QuizStrategy) -> None:
        """
        Change the quiz strategy and reset
        
        Args:
            new_strategy: New strategy to use
        """
        self.strategy = new_strategy
        if self.cards:
            self.load_cards(self.cards)


# Factory function to create strategies
def create_strategy(strategy_name: str) -> QuizStrategy:
    """
    Factory function to create quiz strategies
    
    Args:
        strategy_name: Name of the strategy ('sequential', 'random', 'adaptive')
        
    Returns:
        Quiz strategy instance
        
    Raises:
        ValueError: If strategy name is not recognized
    """
    strategy_name = strategy_name.lower()
    
    if strategy_name == "sequential":
        return SequentialStrategy()
    elif strategy_name == "random":
        return RandomStrategy()
    elif strategy_name == "adaptive":
        return AdaptiveStrategy()
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}. Available: sequential, random, adaptive")