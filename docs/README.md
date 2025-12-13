# Flashcard Quizzer

A powerful, flexible flashcard quiz application with multiple study modes, intelligent adaptive learning, and comprehensive data validation. Built with Python using object-oriented design patterns including Strategy and Factory patterns.

## 🌟 Features

### Quiz Modes
- **Study Mode**: Standard flashcard study sessions with configurable strategies
- **Practice Mode**: Focus on difficult cards you've gotten wrong
- **Quick Review**: Fast sessions with limited cards for quick studying
- **Category Focus**: Study specific categories of flashcards only

### Quiz Strategies
- **Sequential**: Present cards in order (1, 2, 3...)
- **Random**: Shuffle cards for varied presentation
- **Adaptive**: Prioritize cards you get wrong most often (intelligent learning)

### Data Management
- **Multiple JSON Formats**: Support for simple list and wrapper object formats
- **Robust Validation**: Comprehensive data validation with user-friendly error messages
- **Performance Tracking**: Automatic tracking of correct/incorrect attempts per card
- **Statistics**: Detailed statistics by category and difficulty

### User Interface
- **Command Line Interface**: Full argparse-based CLI with colored output
- **Graceful Exit**: Handle CTRL+C and 'exit' commands gracefully
- **Progress Tracking**: Real-time progress and accuracy display
- **Error Handling**: User-friendly error messages with helpful suggestions

## 📁 Project Structure

```
flashcard-quizzer/
├── main.py                 # Main entry point
├── cli.py                  # Command line interface
├── utils/                  # Core utilities package
│   ├── __init__.py        # Package initialization
│   ├── validator.py       # Data validation logic
│   ├── file_handler.py    # File loading and error handling
│   ├── quiz_strategies.py # Quiz strategies implementation
│   └── quiz_modes.py      # Quiz modes and factory pattern
├── tests/                 # Test suite
│   ├── test_file_handler.py
│   └── test_quiz_strategies.py
├── data/                  # Sample data files
├── docs/                  # Documentation
├── claude/               # Claude-specific files
└── README.md            # This file
```

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd flashcard-quizzer
   ```

2. **Set up Python environment** (Python 3.7+ required):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies** (if any):
   ```bash
   pip install -r requirements.txt  # If requirements file exists
   ```

## 📋 Flashcard File Formats

### Simple List Format
```json
[
  {
    "front": "What is the capital of France?",
    "back": "Paris",
    "category": "geography",
    "difficulty": "easy",
    "tags": ["europe", "capitals"],
    "correct_attempts": 8,
    "total_attempts": 10
  },
  {
    "front": "What is 2 + 2?",
    "back": "4",
    "category": "math",
    "difficulty": "easy"
  }
]
```

### Wrapper Object Format
```json
{
  "flashcards": [
    {
      "front": "Who wrote Romeo and Juliet?",
      "back": "William Shakespeare",
      "category": "literature",
      "difficulty": "medium"
    }
  ]
}
```

### Required Fields
- **`front`**: The question (string, 1-1000 characters)
- **`back`**: The answer (string, 1-500 characters)

### Optional Fields
- **`category`**: Category name (default: "general")
- **`difficulty`**: "easy", "medium", or "hard" (default: "medium")
- **`tags`**: Array of tags for organization
- **`correct_attempts`**: Number of correct answers (auto-tracked)
- **`total_attempts`**: Total number of attempts (auto-tracked)

## 🎯 Usage

### Basic Usage

```bash
# Show help
python main.py --help

# Start a quiz with a flashcard file
python main.py -f data/cards.json -m study

# Quick review with 10 random cards
python main.py -f cards.json -m quick --max-cards 10

# Practice mode focusing on difficult cards
python main.py -f cards.json -m practice --difficulty-threshold 0.6

# Study specific categories
python main.py -f cards.json -m category --categories "math,science"

# View statistics for a file
python main.py --stats data/cards.json
```

### Command Line Options

```
Required:
  -f, --file FILE        Path to flashcard JSON file

Quiz Options:
  -m, --mode MODE        Quiz mode: study, practice, quick, category
  --strategy STRATEGY    Quiz strategy: sequential, random, adaptive (default: random)
  --max-cards N          Maximum number of cards to quiz (0 for all)
  --categories CATS      Categories to focus on (comma-separated, for category mode)
  --difficulty-threshold FLOAT  Difficulty threshold for practice mode (0.0-1.0, default: 0.6)

Other:
  --stats               Show statistics for the flashcard file
  --help                Show help message
```

### Interactive Quiz

During a quiz session:
- **Answer questions**: Type your answer and press Enter
- **Skip cards**: Type 'skip' to skip a card
- **Exit gracefully**: Type 'exit' or press CTRL+C
- **View progress**: Progress and accuracy shown for each card

### Color Coding
- 🟢 **Green**: Correct answers
- 🔴 **Red**: Incorrect answers  
- 🔵 **Blue**: Information messages
- 🟡 **Yellow**: Warnings

## 📊 Quiz Modes Explained

### Study Mode
Standard study session with configurable options:
```bash
python main.py -f cards.json -m study --strategy adaptive --max-cards 20
```

### Practice Mode
Focuses on cards you find difficult:
```bash
python main.py -f cards.json -m practice --difficulty-threshold 0.5
```
- Only shows cards with success rate below threshold
- Uses adaptive strategy to prioritize worst-performing cards

### Quick Review
Fast sessions for time-constrained studying:
```bash
python main.py -f cards.json -m quick --max-cards 5 --strategy random
```

### Category Focus
Study specific subject areas:
```bash
python main.py -f cards.json -m category --categories "math,physics,chemistry"
```

## 🧠 Quiz Strategies Explained

### Sequential Strategy
- Presents cards in the exact order they appear in the file
- Predictable and systematic
- Good for first-time learning

### Random Strategy  
- Shuffles cards for varied presentation
- Prevents memorization of card order
- Good for general review

### Adaptive Strategy (Intelligent Learning)
- **Prioritizes cards you get wrong most often**
- Calculates difficulty based on `correct_attempts / total_attempts`
- Cards with lower success rates appear first
- Helps focus study time on weak areas
- **Most effective for learning improvement**

## 📈 Statistics and Progress Tracking

### Individual Card Tracking
Each card automatically tracks:
- Total number of attempts
- Number of correct answers
- Success rate percentage

### Session Statistics
- Real-time accuracy percentage
- Cards completed vs. total cards
- Final session summary with performance breakdown

### File Statistics
```bash
python main.py --stats data/cards.json
```
Shows:
- Total cards and quiz attempts
- Overall accuracy across all sessions
- Breakdown by category and difficulty level

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python -m pytest tests/test_file_handler.py
python -m pytest tests/test_quiz_strategies.py

# Run tests with verbose output
python -m pytest tests/ -v
```

### Test Coverage
- **File Handler**: Data loading, validation, error handling
- **Quiz Strategies**: Factory pattern, adaptive learning logic
- **Validation**: Field validation, format detection
- **Error Handling**: User-friendly error messages

## 🏗️ Architecture

### Design Patterns Used

**Strategy Pattern**:
- `QuizStrategy` interface with concrete implementations
- Allows switching between different card presentation algorithms
- Easy to add new strategies without modifying existing code

**Factory Pattern**:
- `QuizModeFactory` creates appropriate quiz modes
- `create_strategy()` function creates quiz strategies
- Centralizes object creation logic

**Template Method Pattern**:
- `QuizMode` abstract base class defines quiz setup workflow
- Concrete modes implement specific configuration logic

### Key Components

**Data Layer**:
- `FlashcardValidator`: Robust data validation with detailed error reporting
- `FlashcardDataLoader`: File loading with multiple format support and error handling

**Quiz Engine**:
- `QuizEngine`: Core quiz management and progress tracking
- `QuizStrategy`: Pluggable algorithms for card presentation
- `QuizMode`: High-level quiz configuration and setup

**User Interface**:
- `FlashcardCLI`: Full-featured command line interface
- Colored output and graceful error handling
- Comprehensive argument parsing with argparse

## 🤝 Contributing

### Adding New Quiz Strategies
1. Create a new class inheriting from `QuizStrategy`
2. Implement `get_card_order()` and `get_strategy_name()` methods
3. Add the strategy to the factory function `create_strategy()`

### Adding New Quiz Modes  
1. Create a new class inheriting from `QuizMode`
2. Implement `setup_quiz()` and `get_configuration_options()` methods
3. Register the mode in `QuizModeFactory._modes`

### Adding New File Formats
1. Extend `FlashcardDataLoader` with new format detection
2. Add validation rules in `FlashcardValidator` if needed
3. Update documentation and tests

## 🐛 Error Handling

The application provides user-friendly error messages for common issues:

### File Errors
- **File not found**: Clear message with path verification steps
- **Permission errors**: Instructions for fixing file permissions
- **Invalid JSON**: Specific syntax error location when possible

### Validation Errors
- **Missing required fields**: Explains which fields are needed
- **Invalid field values**: Specific guidance on correct formats
- **Format detection**: Helpful suggestions for file structure

### Runtime Errors
- **Empty card sets**: Suggestions for adding cards or changing filters
- **Configuration errors**: Clear explanations of valid options

## 📄 License

[Add your license information here]

## 🙋 Support

For questions, bug reports, or feature requests:
- Check existing issues in the repository
- Create a new issue with detailed description
- Include example files and error messages when reporting bugs

---

**Happy Learning!** 🎓✨