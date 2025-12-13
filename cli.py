#!/usr/bin/env python3
"""
Command Line Interface for Flashcard Quizzer
Supports argparse flags: -f (file), -m (mode), --stats
Features colored output and graceful exit handling
"""

import argparse
import signal
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_colored(text: str, color: str = Colors.WHITE) -> None:
    """Print text with color"""
    print(f"{color}{text}{Colors.END}")


def print_correct(text: str) -> None:
    """Print text in green for correct answers"""
    print_colored(f"✓ {text}", Colors.GREEN)


def print_incorrect(text: str) -> None:
    """Print text in red for incorrect answers"""
    print_colored(f"✗ {text}", Colors.RED)


def print_info(text: str) -> None:
    """Print info text in blue"""
    print_colored(text, Colors.BLUE)


def print_warning(text: str) -> None:
    """Print warning text in yellow"""
    print_colored(f"⚠ {text}", Colors.YELLOW)


def print_header(text: str) -> None:
    """Print header text in bold"""
    print_colored(f"\n{text}", Colors.BOLD + Colors.CYAN)


def signal_handler(signum, frame):
    """Handle CTRL+C gracefully"""
    print_colored("\n\n👋 Thanks for using Flashcard Quizzer! Goodbye!", Colors.CYAN)
    sys.exit(0)


class FlashcardCLI:
    """Command Line Interface for Flashcard Quizzer"""
    
    def __init__(self):
        """Initialize CLI"""
        # Set up graceful exit on CTRL+C
        signal.signal(signal.SIGINT, signal_handler)
        
        # Import here to avoid circular imports
        from utils import (
            FlashcardDataLoader, QuizModeFactory, 
            display_available_modes
        )
        
        self.loader = FlashcardDataLoader()
        self.quiz_factory = QuizModeFactory
        self.flashcards = []
        self.quiz_mode = None
        self.quiz_engine = None
        
    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser"""
        parser = argparse.ArgumentParser(
            description="Flashcard Quizzer - Study with flashcards using different modes and strategies",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s -f data/cards.json -m study
  %(prog)s --file cards.json --mode practice
  %(prog)s --stats data/cards.json
  %(prog)s -f cards.json -m quick --max-cards 10
            """
        )
        
        # File argument
        parser.add_argument(
            '-f', '--file',
            type=str,
            required=False,
            help='Path to flashcard JSON file'
        )
        
        # Mode argument
        parser.add_argument(
            '-m', '--mode',
            type=str,
            choices=['study', 'practice', 'quick', 'category'],
            help='Quiz mode (study, practice, quick, category)'
        )
        
        # Stats flag
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show statistics for the flashcard file'
        )
        
        # Mode-specific arguments
        parser.add_argument(
            '--strategy',
            type=str,
            choices=['sequential', 'random', 'adaptive'],
            default='random',
            help='Quiz strategy (default: random)'
        )
        
        parser.add_argument(
            '--max-cards',
            type=int,
            default=0,
            help='Maximum number of cards to quiz (0 for all)'
        )
        
        parser.add_argument(
            '--categories',
            type=str,
            help='Categories to focus on (comma-separated, for category mode)'
        )
        
        parser.add_argument(
            '--difficulty-threshold',
            type=float,
            default=0.6,
            help='Difficulty threshold for practice mode (0.0-1.0, default: 0.6)'
        )
        
        return parser
    
    def load_flashcards(self, file_path: str) -> bool:
        """Load flashcards from file"""
        if not file_path:
            print_warning("No file specified. Use -f or --file to specify a flashcard file.")
            return False
        
        file_path = Path(file_path)
        if not file_path.exists():
            print_incorrect(f"File not found: {file_path}")
            return False
        
        print_info(f"Loading flashcards from: {file_path}")
        
        # Use safe loading with error handling
        result = self.loader.safe_load_from_file(file_path)
        
        if result["success"]:
            self.flashcards = result["data"]
            print_correct(result["message"])
            return True
        else:
            print_incorrect("Failed to load flashcards:")
            print(result["message"])
            return False
    
    def show_stats(self, file_path: str) -> None:
        """Show statistics for flashcard file"""
        if not self.load_flashcards(file_path):
            return
        
        print_header("📊 FLASHCARD STATISTICS")
        
        total_cards = len(self.flashcards)
        categories = {}
        difficulties = {}
        total_attempts = 0
        total_correct = 0
        
        for card in self.flashcards:
            # Category stats
            category = card.get('category', 'general')
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
            
            # Difficulty stats
            difficulty = card.get('difficulty', 'medium')
            if difficulty not in difficulties:
                difficulties[difficulty] = 0
            difficulties[difficulty] += 1
            
            # Performance stats
            card_attempts = card.get('total_attempts', 0)
            card_correct = card.get('correct_attempts', 0)
            total_attempts += card_attempts
            total_correct += card_correct
        
        # Display stats
        print(f"Total Cards: {total_cards}")
        print(f"Total Quiz Attempts: {total_attempts}")
        
        if total_attempts > 0:
            accuracy = (total_correct / total_attempts) * 100
            print_correct(f"Overall Accuracy: {accuracy:.1f}% ({total_correct}/{total_attempts})")
        else:
            print_info("No quiz attempts recorded yet")
        
        print("\n📁 Categories:")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count} cards")
        
        print("\n🎯 Difficulty Levels:")
        for difficulty, count in sorted(difficulties.items()):
            print(f"  {difficulty}: {count} cards")
    
    def setup_quiz_mode(self, args) -> bool:
        """Setup quiz mode based on arguments"""
        if not args.mode:
            print_warning("No mode specified. Use -m or --mode to choose a quiz mode.")
            self.show_available_modes()
            return False
        
        # Create quiz mode
        self.quiz_mode = self.quiz_factory.create_mode(args.mode)
        if not self.quiz_mode:
            print_incorrect(f"Invalid mode: {args.mode}")
            self.show_available_modes()
            return False
        
        # Prepare mode-specific configuration
        config = {
            'strategy': args.strategy,
            'max_cards': args.max_cards
        }
        
        if args.mode == 'practice':
            config['difficulty_threshold'] = args.difficulty_threshold
            
        elif args.mode == 'quick':
            config['card_limit'] = args.max_cards if args.max_cards > 0 else 10
            
        elif args.mode == 'category':
            if not args.categories:
                print_warning("Category mode requires --categories argument")
                return False
            config['categories'] = args.categories
        
        # Setup quiz
        if not self.quiz_mode.setup_quiz(self.flashcards, **config):
            print_incorrect("Failed to setup quiz mode")
            return False
        
        self.quiz_engine = self.quiz_mode.get_quiz_engine()
        return True
    
    def show_available_modes(self) -> None:
        """Show available quiz modes"""
        print_header("Available Quiz Modes")
        
        modes_info = self.quiz_factory.get_available_modes()
        for mode_key, mode_info in modes_info.items():
            print_colored(f"{mode_key.upper()}: {mode_info['name']}", Colors.CYAN)
            print(f"  {mode_info['description']}")
        
        print_info("\nUse -m or --mode followed by the mode name (e.g., -m study)")
    
    def run_quiz(self) -> None:
        """Run the interactive quiz"""
        if not self.quiz_engine:
            print_incorrect("Quiz not properly initialized")
            return
        
        print_header(f"🎯 STARTING QUIZ - {self.quiz_mode.name}")
        print_info("Type 'exit' to quit the quiz at any time")
        print_info("Press CTRL+C for graceful exit\n")
        
        try:
            while not self.quiz_engine.is_finished():
                card = self.quiz_engine.get_next_card()
                if not card:
                    break
                
                # Show progress
                progress = self.quiz_engine.get_progress()
                print_colored(
                    f"Card {progress['completed'] + 1}/{progress['total']} "
                    f"(Accuracy: {progress['current_accuracy']:.1f}%)",
                    Colors.PURPLE
                )
                
                # Show question
                print_colored(f"\n❓ {card['front']}", Colors.BOLD + Colors.WHITE)
                
                # Get user answer
                user_answer = input(f"{Colors.CYAN}Your answer: {Colors.END}").strip()
                
                # Check for exit
                if user_answer.lower() == 'exit':
                    print_colored("Quiz ended by user", Colors.YELLOW)
                    break
                
                # Check answer
                correct_answer = card['back']
                is_correct = user_answer.lower() == correct_answer.lower()
                
                # Record answer
                self.quiz_engine.answer_card(is_correct)
                
                # Show result
                if is_correct:
                    print_correct("Correct!")
                else:
                    print_incorrect(f"Incorrect. The answer is: {correct_answer}")
                
                print()  # Blank line for readability
            
            # Show final summary
            self.show_quiz_summary()
            
        except KeyboardInterrupt:
            # This should be caught by signal handler, but just in case
            signal_handler(None, None)
    
    def show_quiz_summary(self) -> None:
        """Show quiz session summary"""
        if not self.quiz_engine:
            return
        
        summary = self.quiz_engine.get_session_summary()
        
        print_header("📋 QUIZ SUMMARY")
        print(f"Mode: {summary['strategy_used']}")
        print(f"Cards Completed: {summary['cards_completed']}/{summary['total_cards']}")
        print_correct(f"Correct Answers: {summary['correct_answers']}")
        print_incorrect(f"Incorrect Answers: {summary['incorrect_answers']}")
        
        accuracy = summary['accuracy_percentage']
        if accuracy >= 80:
            print_correct(f"Final Accuracy: {accuracy:.1f}% - Excellent! 🌟")
        elif accuracy >= 60:
            print_colored(f"Final Accuracy: {accuracy:.1f}% - Good job! 👍", Colors.YELLOW)
        else:
            print_colored(f"Final Accuracy: {accuracy:.1f}% - Keep practicing! 📚", Colors.RED)
    
    def run(self) -> None:
        """Main CLI entry point"""
        parser = self.create_parser()
        
        # If no arguments provided, show help
        if len(sys.argv) == 1:
            parser.print_help()
            return
        
        args = parser.parse_args()
        
        # Handle stats mode
        if args.stats:
            if not args.file:
                print_warning("--stats requires a file. Use -f or --file to specify the flashcard file.")
                return
            self.show_stats(args.file)
            return
        
        # Load flashcards
        if not self.load_flashcards(args.file):
            return
        
        # Setup and run quiz
        if self.setup_quiz_mode(args):
            self.run_quiz()


def main():
    """Main entry point"""
    try:
        cli = FlashcardCLI()
        cli.run()
    except Exception as e:
        print_incorrect(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()