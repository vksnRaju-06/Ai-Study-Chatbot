"""
Example usage and testing script
Demonstrates how to use the Study Assistant programmatically
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.study_assistant import StudyAssistant
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demo_basic_usage():
    """Demonstrate basic usage"""
    print("=" * 60)
    print("AI STUDY ASSISTANT - DEMO")
    print("=" * 60)
    
    # Create assistant
    assistant = StudyAssistant()
    
    # Check OLLAMA status
    print("\n1. Checking OLLAMA Status...")
    status = assistant.check_ollama_status()
    print(f"   {status['message']}")
    
    if not status['available']:
        print("\n⚠️  OLLAMA is not available. Please start OLLAMA and try again.")
        return
    
    # Example questions
    questions = [
        "Hello!",
        "What is photosynthesis?",
        "Can you solve 2x + 5 = 15 for me?",
        "hint",
    ]
    
    print("\n2. Processing Questions...")
    for i, question in enumerate(questions, 1):
        print(f"\n--- Question {i} ---")
        print(f"Student: {question}")
        
        result = assistant.process_question(question)
        
        print(f"\nAssistant: {result['response']}")
        print(f"\nMetadata:")
        print(f"  - Strategy: {result['metadata'].get('strategy', 'N/A')}")
        print(f"  - Question Type: {result['metadata'].get('question_type', 'N/A')}")
        print(f"  - Handler: {result['metadata'].get('handler', 'N/A')}")
        print(f"  - Hint Count: {result['metadata'].get('hint_count', 0)}")
    
    # Show session stats
    print("\n" + "=" * 60)
    print("SESSION STATISTICS")
    print("=" * 60)
    stats = assistant.get_session_stats()
    print(f"Total Questions: {stats['total_questions']}")
    print(f"Hints Requested: {stats['hints_requested']}")
    print(f"\nQuestions by Type:")
    for q_type, count in stats['questions_by_type'].items():
        print(f"  - {q_type}: {count}")
    print(f"\nStrategies Used:")
    for strategy, count in stats['strategies_used'].items():
        print(f"  - {strategy}: {count}")


def demo_design_patterns():
    """Demonstrate design patterns in action"""
    print("\n" + "=" * 60)
    print("DESIGN PATTERNS DEMONSTRATION")
    print("=" * 60)
    
    # Singleton Pattern
    print("\n1. SINGLETON PATTERN (ConfigManager)")
    from src.patterns.singleton import ConfigManager
    config1 = ConfigManager()
    config2 = ConfigManager()
    print(f"   Same instance? {config1 is config2}")
    print(f"   OLLAMA Model: {config1.get('ollama.model')}")
    
    # Strategy Pattern
    print("\n2. STRATEGY PATTERN (Learning Strategies)")
    from src.strategies.learning_strategies import (
        SocraticStrategy, HintBasedStrategy, StrategyContext
    )
    
    context = StrategyContext(SocraticStrategy())
    print(f"   Current Strategy: {context.get_current_strategy_name()}")
    
    context.set_strategy(HintBasedStrategy())
    print(f"   Changed to: {context.get_current_strategy_name()}")
    
    # Factory Pattern
    print("\n3. FACTORY PATTERN (Response Handler Factory)")
    from src.patterns.factory import ResponseHandlerFactory
    
    questions = [
        ("What is gravity?", "Should detect CONCEPTUAL"),
        ("Solve x + 5 = 10", "Should detect PROBLEM_SOLVING"),
        ("Why does ice float?", "Should detect WHY"),
    ]
    
    for question, expected in questions:
        strategy, q_type = ResponseHandlerFactory.create_response_handler(question)
        print(f"   '{question}'")
        print(f"   -> Type: {q_type.value}, Strategy: {strategy.get_strategy_name()}")
    
    # Observer Pattern
    print("\n4. OBSERVER PATTERN (Progress Tracking)")
    from src.patterns.observer import StudentProgressTracker, AnalyticsTracker
    
    tracker = StudentProgressTracker()
    analytics = AnalyticsTracker()
    tracker.attach(analytics)
    
    tracker.log_question("Test question", "conceptual", "Socratic Method")
    tracker.log_hint_request("Test question", 1)
    
    stats = analytics.get_stats()
    print(f"   Questions tracked: {stats['total_questions']}")
    print(f"   Hints requested: {stats['hints_requested']}")
    
    # Chain of Responsibility
    print("\n5. CHAIN OF RESPONSIBILITY (Question Handler Chain)")
    from src.patterns.chain_of_responsibility import create_question_handler_chain
    
    chain = create_question_handler_chain()
    
    test_cases = [
        "Hello",
        "help",
        "give me the answer",
        "What is Python?"
    ]
    
    for test in test_cases:
        result = chain.handle(test, {})
        print(f"   '{test}' -> Handler: {result['handler']}, Requires AI: {result['requires_ai']}")


if __name__ == "__main__":
    print("\nChoose demo mode:")
    print("1. Basic Usage Demo")
    print("2. Design Patterns Demo")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice in ['1', '3']:
        demo_basic_usage()
    
    if choice in ['2', '3']:
        demo_design_patterns()
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)
