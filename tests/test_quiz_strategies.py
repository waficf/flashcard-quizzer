"""
Test suite for Quiz Strategies and Factory Pattern
Tests factory returns correct classes and adaptive strategy prioritizes incorrect questions
"""

import unittest
import random
import os
import sys

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.quiz_strategies import (
    QuizStrategy,
    SequentialStrategy, 
    RandomStrategy,
    AdaptiveStrategy,
    QuizEngine,
    create_strategy
)


class TestQuizStrategyFactory(unittest.TestCase):
    """Test cases for quiz strategy factory pattern"""
    
    def test_create_sequential_strategy(self):
        """Test factory returns correct SequentialStrategy class"""
        strategy = create_strategy("sequential")
        
        self.assertIsInstance(strategy, SequentialStrategy)
        self.assertEqual(strategy.get_strategy_name(), "Sequential")
    
    def test_create_random_strategy(self):
        """Test factory returns correct RandomStrategy class"""
        strategy = create_strategy("random")
        
        self.assertIsInstance(strategy, RandomStrategy)
        self.assertEqual(strategy.get_strategy_name(), "Random")
    
    def test_create_adaptive_strategy(self):
        """Test factory returns correct AdaptiveStrategy class"""
        strategy = create_strategy("adaptive")
        
        self.assertIsInstance(strategy, AdaptiveStrategy)
        self.assertEqual(strategy.get_strategy_name(), "Adaptive")
    
    def test_create_strategy_case_insensitive(self):
        """Test factory works with different cases"""
        strategies = [
            ("SEQUENTIAL", SequentialStrategy),
            ("Random", RandomStrategy),
            ("ADAPTIVE", AdaptiveStrategy),
            ("sequential", SequentialStrategy)
        ]
        
        for name, expected_class in strategies:
            strategy = create_strategy(name)
            self.assertIsInstance(strategy, expected_class)
    
    def test_create_invalid_strategy(self):
        """Test factory raises error for invalid strategy name"""
        with self.assertRaises(ValueError) as context:
            create_strategy("invalid_strategy")
        
        self.assertIn("Unknown strategy", str(context.exception))
        self.assertIn("Available: sequential, random, adaptive", str(context.exception))


class TestSequentialStrategy(unittest.TestCase):
    """Test cases for SequentialStrategy"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.strategy = SequentialStrategy()
        self.sample_cards = [
            {"front": "Question 1", "back": "Answer 1", "category": "test"},
            {"front": "Question 2", "back": "Answer 2", "category": "test"},
            {"front": "Question 3", "back": "Answer 3", "category": "test"},
            {"front": "Question 4", "back": "Answer 4", "category": "test"}
        ]
    
    def test_sequential_order(self):
        """Test that sequential strategy returns cards in order 1,2,3,4"""
        card_order = self.strategy.get_card_order(self.sample_cards)
        
        expected_order = [0, 1, 2, 3]  # Indices in sequential order
        self.assertEqual(card_order, expected_order)
    
    def test_sequential_with_different_lengths(self):
        """Test sequential strategy with different card list lengths"""
        # Test with 2 cards
        two_cards = self.sample_cards[:2]
        order = self.strategy.get_card_order(two_cards)
        self.assertEqual(order, [0, 1])
        
        # Test with 1 card
        one_card = self.sample_cards[:1]
        order = self.strategy.get_card_order(one_card)
        self.assertEqual(order, [0])
        
        # Test with empty list
        empty_cards = []
        order = self.strategy.get_card_order(empty_cards)
        self.assertEqual(order, [])


class TestRandomStrategy(unittest.TestCase):
    """Test cases for RandomStrategy"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.strategy = RandomStrategy()
        self.sample_cards = [
            {"front": "Question 1", "back": "Answer 1", "category": "test"},
            {"front": "Question 2", "back": "Answer 2", "category": "test"},
            {"front": "Question 3", "back": "Answer 3", "category": "test"},
            {"front": "Question 4", "back": "Answer 4", "category": "test"}
        ]
    
    def test_random_contains_all_indices(self):
        """Test that random strategy includes all card indices"""
        card_order = self.strategy.get_card_order(self.sample_cards)
        
        self.assertEqual(len(card_order), len(self.sample_cards))
        self.assertEqual(set(card_order), {0, 1, 2, 3})
    
    def test_random_is_shuffled(self):
        """Test that random strategy actually shuffles (with multiple attempts)"""
        # Set seed for reproducible test
        random.seed(42)
        
        sequential_order = [0, 1, 2, 3]
        shuffled_count = 0
        
        # Try multiple times to ensure shuffling happens
        for _ in range(10):
            card_order = self.strategy.get_card_order(self.sample_cards)
            if card_order != sequential_order:
                shuffled_count += 1
        
        # At least some should be shuffled
        self.assertGreater(shuffled_count, 0, "Random strategy should shuffle cards")


class TestAdaptiveStrategy(unittest.TestCase):
    """Test cases for AdaptiveStrategy - prioritizes cards with more incorrect answers"""
    
    def setUp(self):
        """Set up test fixtures with cards having different success rates"""
        self.strategy = AdaptiveStrategy()
        
        # Create cards with different performance stats
        self.sample_cards = [
            {
                "front": "Easy Question", 
                "back": "Easy Answer",
                "category": "test",
                "total_attempts": 10,
                "correct_attempts": 9  # 90% success rate
            },
            {
                "front": "Hard Question", 
                "back": "Hard Answer",
                "category": "test",
                "total_attempts": 10,
                "correct_attempts": 2  # 20% success rate - should be prioritized
            },
            {
                "front": "Medium Question", 
                "back": "Medium Answer",
                "category": "test",
                "total_attempts": 10,
                "correct_attempts": 6  # 60% success rate
            },
            {
                "front": "New Question", 
                "back": "New Answer",
                "category": "test",
                "total_attempts": 0,
                "correct_attempts": 0  # New card - medium priority
            }
        ]
    
    def test_adaptive_prioritizes_incorrect_questions(self):
        """Test that adaptive strategy puts cards with more wrong answers first"""
        card_order = self.strategy.get_card_order(self.sample_cards)
        
        # Get the cards in the order they would be presented
        ordered_cards = [self.sample_cards[i] for i in card_order]
        
        # The hardest question (20% success) should come first
        self.assertEqual(ordered_cards[0]["front"], "Hard Question")
        
        # The easiest question (90% success) should come last
        self.assertEqual(ordered_cards[-1]["front"], "Easy Question")
    
    def test_adaptive_difficulty_calculation(self):
        """Test that difficulty scores are calculated correctly"""
        card_order = self.strategy.get_card_order(self.sample_cards)
        
        # Check that indices correspond to expected difficulty order
        # Index 1 = Hard Question (lowest success rate) should be first
        # Index 0 = Easy Question (highest success rate) should be last
        self.assertEqual(card_order[0], 1)  # Hard Question first
        self.assertEqual(card_order[-1], 0)  # Easy Question last
    
    def test_adaptive_with_new_cards(self):
        """Test adaptive strategy handling of cards with no attempts"""
        new_cards = [
            {"front": "New Q1", "back": "New A1", "total_attempts": 0, "correct_attempts": 0},
            {"front": "New Q2", "back": "New A2", "total_attempts": 0, "correct_attempts": 0}
        ]
        
        card_order = self.strategy.get_card_order(new_cards)
        
        # Should still return all card indices
        self.assertEqual(len(card_order), 2)
        self.assertEqual(set(card_order), {0, 1})
    
    def test_adaptive_repeats_incorrect_questions(self):
        """Test that adaptive strategy focuses on cards the user gets wrong"""
        # Cards with very poor performance should be prioritized
        poor_performance_cards = [
            {
                "front": "Very Hard Q1",
                "back": "Answer 1", 
                "total_attempts": 20,
                "correct_attempts": 1  # 5% success - very difficult
            },
            {
                "front": "Very Hard Q2",
                "back": "Answer 2",
                "total_attempts": 15, 
                "correct_attempts": 2  # 13% success - difficult
            },
            {
                "front": "Easy Q1",
                "back": "Answer 3",
                "total_attempts": 10,
                "correct_attempts": 10  # 100% success - easy
            }
        ]
        
        card_order = self.strategy.get_card_order(poor_performance_cards)
        
        # The cards with worst performance should come first
        first_card = poor_performance_cards[card_order[0]]
        last_card = poor_performance_cards[card_order[-1]]
        
        # First card should have lower success rate than last card
        first_success_rate = first_card["correct_attempts"] / first_card["total_attempts"]
        last_success_rate = last_card["correct_attempts"] / last_card["total_attempts"]
        
        self.assertLess(first_success_rate, last_success_rate, 
                       "Adaptive strategy should prioritize cards with lower success rates")


class TestQuizEngine(unittest.TestCase):
    """Test cases for QuizEngine integration with strategies"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_cards = [
            {
                "front": "Question 1",
                "back": "Answer 1", 
                "category": "test",
                "total_attempts": 0,
                "correct_attempts": 0
            },
            {
                "front": "Question 2",
                "back": "Answer 2",
                "category": "test", 
                "total_attempts": 0,
                "correct_attempts": 0
            }
        ]
    
    def test_quiz_engine_with_sequential_strategy(self):
        """Test QuizEngine works with SequentialStrategy"""
        strategy = SequentialStrategy()
        engine = QuizEngine(strategy)
        engine.load_cards(self.sample_cards)
        
        # Get cards in order
        first_card = engine.get_next_card()
        self.assertEqual(first_card["front"], "Question 1")
        
        engine.answer_card(True)
        
        second_card = engine.get_next_card()
        self.assertEqual(second_card["front"], "Question 2")
    
    def test_quiz_engine_tracks_performance(self):
        """Test that QuizEngine updates card performance stats"""
        strategy = SequentialStrategy()
        engine = QuizEngine(strategy)
        engine.load_cards(self.sample_cards)
        
        # Answer first card correctly
        first_card = engine.get_next_card()
        engine.answer_card(True)
        
        # Check that stats were updated
        self.assertEqual(first_card["total_attempts"], 1)
        self.assertEqual(first_card["correct_attempts"], 1)
        
        # Answer second card incorrectly
        second_card = engine.get_next_card()
        engine.answer_card(False)
        
        # Check that stats were updated
        self.assertEqual(second_card["total_attempts"], 1)
        self.assertEqual(second_card["correct_attempts"], 0)
    
    def test_quiz_engine_progress_tracking(self):
        """Test QuizEngine progress tracking"""
        strategy = SequentialStrategy()
        engine = QuizEngine(strategy)
        engine.load_cards(self.sample_cards)
        
        # Initial progress
        progress = engine.get_progress()
        self.assertEqual(progress["completed"], 0)
        self.assertEqual(progress["total"], 2)
        
        # After answering one card
        engine.get_next_card()
        engine.answer_card(True)
        
        progress = engine.get_progress()
        self.assertEqual(progress["completed"], 1)
        self.assertEqual(progress["current_accuracy"], 100.0)
    
    def test_quiz_engine_session_summary(self):
        """Test QuizEngine session summary"""
        strategy = AdaptiveStrategy()
        engine = QuizEngine(strategy)
        engine.load_cards(self.sample_cards)
        
        # Complete quiz
        engine.get_next_card()
        engine.answer_card(True)
        engine.get_next_card() 
        engine.answer_card(False)
        
        summary = engine.get_session_summary()
        
        self.assertEqual(summary["strategy_used"], "Adaptive")
        self.assertEqual(summary["total_cards"], 2)
        self.assertEqual(summary["correct_answers"], 1)
        self.assertEqual(summary["incorrect_answers"], 1)
        self.assertEqual(summary["accuracy_percentage"], 50.0)
    
    def test_adaptive_strategy_in_quiz_engine(self):
        """Test that AdaptiveStrategy works correctly in QuizEngine"""
        # Create cards with different performance levels
        cards_with_stats = [
            {
                "front": "Easy Question",
                "back": "Easy Answer",
                "total_attempts": 10,
                "correct_attempts": 9
            },
            {
                "front": "Hard Question", 
                "back": "Hard Answer",
                "total_attempts": 10,
                "correct_attempts": 2
            }
        ]
        
        strategy = AdaptiveStrategy()
        engine = QuizEngine(strategy)
        engine.load_cards(cards_with_stats)
        
        # First card should be the hard one (more wrong answers)
        first_card = engine.get_next_card()
        self.assertEqual(first_card["front"], "Hard Question")


if __name__ == '__main__':
    unittest.main()