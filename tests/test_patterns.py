"""
Unit tests for design patterns
Run with: pytest tests/test_patterns.py -v
"""

import pytest
from src.patterns.singleton import ConfigManager
from src.patterns.factory import ResponseHandlerFactory, QuestionType
from src.strategies.learning_strategies import (
    SocraticStrategy, HintBasedStrategy, ConceptualStrategy, StrategyContext
)
from src.patterns.observer import (
    StudentProgressTracker, AnalyticsTracker, ProgressLogger
)
from src.patterns.chain_of_responsibility import create_question_handler_chain


class TestSingletonPattern:
    """Test Singleton Pattern implementation"""
    
    def test_singleton_same_instance(self):
        """Test that ConfigManager returns same instance"""
        config1 = ConfigManager()
        config2 = ConfigManager()
        assert config1 is config2
    
    def test_config_get_set(self):
        """Test configuration get/set"""
        config = ConfigManager()
        config.set('test.value', 'test123')
        assert config.get('test.value') == 'test123'
    
    def test_config_default_value(self):
        """Test default value when key doesn't exist"""
        config = ConfigManager()
        value = config.get('nonexistent.key', 'default')
        assert value == 'default'


class TestStrategyPattern:
    """Test Strategy Pattern implementation"""
    
    def test_strategy_switching(self):
        """Test dynamic strategy switching"""
        socratic = SocraticStrategy()
        hint = HintBasedStrategy()
        
        context = StrategyContext(socratic)
        assert context.get_current_strategy_name() == "Socratic Method"
        
        context.set_strategy(hint)
        assert context.get_current_strategy_name() == "Hint-Based Learning"
    
    def test_socratic_strategy_response(self):
        """Test Socratic strategy generates questions"""
        strategy = SocraticStrategy()
        response = strategy.generate_response("What is Python?", {})
        
        assert "question" in response.lower()
        assert "student" in response.lower()
    
    def test_hint_strategy_with_context(self):
        """Test hint strategy uses context"""
        strategy = HintBasedStrategy()
        context = {'hint_count': 2}
        
        response = strategy.generate_response("Solve x+5=10", context)
        assert "hint" in response.lower()


class TestFactoryPattern:
    """Test Factory Pattern implementation"""
    
    def test_question_type_detection_conceptual(self):
        """Test detection of conceptual questions"""
        q_type = ResponseHandlerFactory.detect_question_type("What is gravity?")
        assert q_type == QuestionType.CONCEPTUAL
    
    def test_question_type_detection_problem(self):
        """Test detection of problem-solving questions"""
        q_type = ResponseHandlerFactory.detect_question_type("Solve 2x + 5 = 15")
        assert q_type == QuestionType.PROBLEM_SOLVING
    
    def test_question_type_detection_why(self):
        """Test detection of why questions"""
        q_type = ResponseHandlerFactory.detect_question_type("Why does ice float?")
        assert q_type == QuestionType.WHY
    
    def test_factory_creates_correct_strategy(self):
        """Test factory creates appropriate strategy for question type"""
        strategy, q_type = ResponseHandlerFactory.create_response_handler(
            "What is photosynthesis?"
        )
        
        assert q_type == QuestionType.CONCEPTUAL
        assert isinstance(strategy, ConceptualStrategy)
    
    def test_factory_hint_request(self):
        """Test factory handles hint requests"""
        strategy, _ = ResponseHandlerFactory.create_response_handler(
            "Help me understand",
            {'request_hint': True}
        )
        
        assert isinstance(strategy, HintBasedStrategy)


class TestObserverPattern:
    """Test Observer Pattern implementation"""
    
    def test_observer_attachment(self):
        """Test attaching observers"""
        tracker = StudentProgressTracker()
        analytics = AnalyticsTracker()
        
        tracker.attach(analytics)
        assert analytics in tracker._observers
    
    def test_observer_detachment(self):
        """Test detaching observers"""
        tracker = StudentProgressTracker()
        analytics = AnalyticsTracker()
        
        tracker.attach(analytics)
        tracker.detach(analytics)
        assert analytics not in tracker._observers
    
    def test_observer_notification(self):
        """Test observers receive notifications"""
        tracker = StudentProgressTracker()
        analytics = AnalyticsTracker()
        
        tracker.attach(analytics)
        tracker.log_question("Test question", "conceptual", "Socratic Method")
        
        stats = analytics.get_stats()
        assert stats['total_questions'] == 1
        assert stats['questions_by_type']['conceptual'] == 1
    
    def test_multiple_observers(self):
        """Test multiple observers work together"""
        tracker = StudentProgressTracker()
        analytics1 = AnalyticsTracker()
        analytics2 = AnalyticsTracker()
        
        tracker.attach(analytics1)
        tracker.attach(analytics2)
        
        tracker.log_question("Test", "why", "Socratic Method")
        
        assert analytics1.get_stats()['total_questions'] == 1
        assert analytics2.get_stats()['total_questions'] == 1
    
    def test_hint_tracking(self):
        """Test hint request tracking"""
        tracker = StudentProgressTracker()
        analytics = AnalyticsTracker()
        
        tracker.attach(analytics)
        tracker.log_hint_request("Question", 1)
        tracker.log_hint_request("Question", 2)
        
        stats = analytics.get_stats()
        assert stats['hints_requested'] == 2


class TestChainOfResponsibility:
    """Test Chain of Responsibility Pattern"""
    
    def test_greeting_handler(self):
        """Test greeting handler catches greetings"""
        chain = create_question_handler_chain()
        result = chain.handle("Hello", {})
        
        assert result['handled'] is True
        assert result['handler'] == 'GreetingHandler'
        assert result['requires_ai'] is False
    
    def test_help_handler(self):
        """Test help handler catches help commands"""
        chain = create_question_handler_chain()
        result = chain.handle("help", {})
        
        assert result['handled'] is True
        assert result['handler'] == 'HelpCommandHandler'
        assert "Socratic Method" in result['response']
    
    def test_direct_answer_detector(self):
        """Test direct answer detector catches requests"""
        chain = create_question_handler_chain()
        result = chain.handle("give me the answer", {})
        
        assert result['handled'] is True
        assert result['handler'] == 'DirectAnswerDetector'
        assert "learn" in result['response'].lower()
    
    def test_hint_request_handler(self):
        """Test hint request handler"""
        chain = create_question_handler_chain()
        context = {'hint_count': 0}
        result = chain.handle("hint", context)
        
        assert result['handled'] is True
        assert context['request_hint'] is True
    
    def test_hint_limit(self):
        """Test hint limit enforcement"""
        chain = create_question_handler_chain()
        context = {'hint_count': 3}
        result = chain.handle("hint", context)
        
        assert "all 3 hints" in result['response'].lower()
    
    def test_learning_question_fallthrough(self):
        """Test regular questions fall through to learning handler"""
        chain = create_question_handler_chain()
        result = chain.handle("What is photosynthesis?", {})
        
        assert result['handled'] is True
        assert result['handler'] == 'LearningQuestionHandler'
        assert result['requires_ai'] is True
    
    def test_chain_order_matters(self):
        """Test that handler order affects results"""
        # "hello" should be caught by GreetingHandler, not reach LearningHandler
        chain = create_question_handler_chain()
        result = chain.handle("hello", {})
        
        assert result['handler'] == 'GreetingHandler'
        assert result['requires_ai'] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
