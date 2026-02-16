# AI Study Assistant - Developer Documentation

## Architecture Overview

This project implements a sophisticated AI Study Assistant using multiple software design patterns to create a maintainable, extensible, and well-structured application.

## Design Patterns Implemented

### 1. Singleton Pattern
**File:** [src/patterns/singleton.py](src/patterns/singleton.py)

**Purpose:** Ensures single instance of configuration management across the application.

**Implementation:**
```python
config = ConfigManager()  # Always returns the same instance
```

**Benefits:**
- Centralized configuration management
- Consistent settings across all components
- Easy to modify configuration at runtime

### 2. Strategy Pattern
**File:** [src/strategies/learning_strategies.py](src/strategies/learning_strategies.py)

**Purpose:** Allows dynamic switching between different teaching approaches.

**Strategies Implemented:**
- `SocraticStrategy`: Guides through questioning
- `HintBasedStrategy`: Provides progressive hints
- `ConceptualStrategy`: Explains underlying concepts
- `ProblemDecompositionStrategy`: Breaks down problems into steps

**Usage:**
```python
strategy = SocraticStrategy()
context = StrategyContext(strategy)
context.set_strategy(HintBasedStrategy())  # Switch dynamically
```

**Benefits:**
- Easy to add new teaching strategies
- Runtime strategy switching
- Separation of concerns

### 3. Factory Pattern
**File:** [src/patterns/factory.py](src/patterns/factory.py)

**Purpose:** Creates appropriate response handlers based on question type.

**Question Types Detected:**
- CONCEPTUAL: "What is...?"
- PROBLEM_SOLVING: Math, coding problems
- HOW_TO: "How do I...?"
- WHY: "Why does...?"
- COMPARISON: "What's the difference...?"

**Usage:**
```python
strategy, q_type = ResponseHandlerFactory.create_response_handler(question)
```

**Benefits:**
- Automatic question type detection
- Appropriate strategy selection
- Extensible for new question types

### 4. Observer Pattern
**File:** [src/patterns/observer.py](src/patterns/observer.py)

**Purpose:** Tracks and logs student learning activities.

**Observers Implemented:**
- `ProgressLogger`: Logs to JSON file
- `ConsoleProgressTracker`: Prints to console
- `AnalyticsTracker`: Tracks session statistics

**Usage:**
```python
tracker = StudentProgressTracker()
tracker.attach(ProgressLogger())
tracker.attach(AnalyticsTracker())
tracker.log_question(question, q_type, strategy)
```

**Benefits:**
- Decoupled progress tracking
- Easy to add new tracking mechanisms
- Real-time analytics

### 5. Chain of Responsibility
**File:** [src/patterns/chain_of_responsibility.py](src/patterns/chain_of_responsibility.py)

**Purpose:** Routes questions through a chain of specialized handlers.

**Handler Chain:**
1. `GreetingHandler`: Handles greetings
2. `HelpCommandHandler`: Handles help requests
3. `DirectAnswerDetector`: Redirects direct answer requests
4. `HintRequestHandler`: Processes hint requests
5. `LearningQuestionHandler`: Processes with AI

**Usage:**
```python
chain = create_question_handler_chain()
result = chain.handle(question, context)
```

**Benefits:**
- Separation of concerns
- Easy to add new handlers
- Order-dependent processing

## Core Components

### Study Assistant Service
**File:** [src/services/study_assistant.py](src/services/study_assistant.py)

The main orchestrator that combines all patterns:

```python
assistant = StudyAssistant()
result = assistant.process_question(question)
```

**Process Flow:**
1. Chain of Responsibility handles special cases
2. Factory detects question type
3. Strategy generates appropriate prompt
4. OLLAMA generates AI response
5. Observer tracks progress
6. Result returned with metadata

### OLLAMA Service
**File:** [src/services/ollama_service.py](src/services/ollama_service.py)

Handles communication with OLLAMA API:

```python
ollama = OllamaService()
response = ollama.generate_response(prompt, system_message)
```

**Features:**
- Connection status checking
- Model listing
- Error handling
- Timeout management

## Configuration

### Environment Variables (.env)
```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi3:mini
LOG_LEVEL=INFO
MAX_CONTEXT_LENGTH=2048
TEMPERATURE=0.7
```

### Modifying Configuration
```python
from src.patterns.singleton import config

# Get value
model = config.get('ollama.model')

# Set value
config.set('ollama.model', 'llama3.2:1b')
```

## Extending the System

### Adding a New Learning Strategy

1. Create strategy class in [src/strategies/learning_strategies.py](src/strategies/learning_strategies.py):

```python
class MyNewStrategy(LearningStrategy):
    def generate_response(self, question: str, context: Dict[str, Any]) -> str:
        # Your implementation
        return prompt
    
    def get_strategy_name(self) -> str:
        return "My New Strategy"
```

2. Add to Factory mapping in [src/patterns/factory.py](src/patterns/factory.py):

```python
strategy_map = {
    QuestionType.MY_TYPE: MyNewStrategy(),
    # ... existing mappings
}
```

### Adding a New Question Type

1. Add to `QuestionType` enum in [src/patterns/factory.py](src/patterns/factory.py):

```python
class QuestionType(Enum):
    MY_NEW_TYPE = "my_type"
```

2. Update detection logic:

```python
def detect_question_type(question: str) -> QuestionType:
    if 'my_keyword' in question.lower():
        return QuestionType.MY_NEW_TYPE
```

### Adding a New Observer

1. Create observer class in [src/patterns/observer.py](src/patterns/observer.py):

```python
class MyObserver(Observer):
    def update(self, event: Dict[str, Any]):
        # Your implementation
        pass
```

2. Attach to tracker:

```python
tracker = StudentProgressTracker()
tracker.attach(MyObserver())
```

### Adding a New Handler in Chain

1. Create handler in [src/patterns/chain_of_responsibility.py](src/patterns/chain_of_responsibility.py):

```python
class MyHandler(QuestionHandler):
    def handle(self, question: str, context: Dict[str, Any]):
        if self._should_handle(question):
            return {'handled': True, 'response': '...'}
        return self._pass_to_next(question, context)
```

2. Add to chain:

```python
def create_question_handler_chain():
    my_handler = MyHandler()
    # ... other handlers
    my_handler.set_next(next_handler)
    return my_handler
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Manual Testing

```bash
# Run demo
python demo.py

# Test specific components
python -c "from src.patterns.singleton import ConfigManager; print(ConfigManager().get_all())"
```

## Performance Optimization for Core i3

### Model Selection
- **Recommended:** `phi3:mini` (3.8GB) - Best balance
- **Lightweight:** `llama3.2:1b` (1.3GB) - Faster, less capable
- **Avoid:** `llama3:8b`, `mistral` - Too heavy for i3

### Configuration Tuning

For faster responses on low-end hardware:

```python
# In .env
MAX_CONTEXT_LENGTH=1024  # Reduce from 2048
TEMPERATURE=0.5           # Lower = more deterministic, faster
```

### Memory Management

```python
# Limit conversation history
MAX_HISTORY = 10  # Keep only last 10 messages

# In session_context
history = history[-MAX_HISTORY:]
```

## Logging and Debugging

### Enable Debug Logging

```python
# In .env
LOG_LEVEL=DEBUG
```

### Log Locations
- Application logs: `data/app.log`
- Progress logs: `data/progress_log.json`

### Viewing Logs

```python
# Tail application log
tail -f data/app.log

# View progress JSON
cat data/progress_log.json | jq .
```

## Common Development Tasks

### Changing OLLAMA Model

```python
# In .env
OLLAMA_MODEL=llama3.2:1b

# Or at runtime
from src.patterns.singleton import config
config.set('ollama.model', 'llama3.2:1b')
```

### Adjusting Learning Behavior

Modify system message in [src/services/study_assistant.py](src/services/study_assistant.py):

```python
self.system_message = """Your custom system message..."""
```

### Customizing UI

Edit [src/ui/streamlit_app.py](src/ui/streamlit_app.py):

```python
# Change theme
st.set_page_config(theme="dark")

# Modify CSS
st.markdown("""<style>...</style>""")
```

## API Reference

### StudyAssistant

```python
assistant = StudyAssistant()

# Process question
result = assistant.process_question(question: str) -> Dict

# Request hint
hint_result = assistant.request_hint() -> Dict

# Get statistics
stats = assistant.get_session_stats() -> Dict

# Reset session
assistant.reset_session()

# Check OLLAMA
status = assistant.check_ollama_status() -> Dict
```

### Response Structure

```python
{
    'response': str,  # The generated response
    'metadata': {
        'question_type': str,
        'strategy': str,
        'hint_count': int,
        'handler': str,
        'timestamp': str
    }
}
```

## Troubleshooting

### OLLAMA Connection Issues

```python
# Check if OLLAMA is running
ollama = OllamaService()
if not ollama.is_available():
    print("Start OLLAMA service")
```

### Import Errors

```bash
# Ensure PYTHONPATH includes src/
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Model Not Found

```bash
# Pull the model
ollama pull phi3:mini

# Verify
ollama list
```

## Best Practices

1. **Always use design patterns** when extending functionality
2. **Log important events** using the Observer pattern
3. **Test new handlers** in the chain before deployment
4. **Keep strategies focused** on single teaching approach
5. **Document new question types** in the Factory
6. **Monitor performance** on target hardware (i3 laptop)
7. **Version control .env.example** but not .env

## Resources

- OLLAMA Documentation: https://github.com/ollama/ollama
- Streamlit Documentation: https://docs.streamlit.io
- Design Patterns: https://refactoring.guru/design-patterns

## License

Development code - For educational purposes
