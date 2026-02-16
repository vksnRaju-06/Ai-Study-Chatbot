"""
Factory Pattern for Creating Response Handlers
Dynamically creates appropriate handlers based on question type
"""

from typing import Dict, Any
from enum import Enum
from src.strategies.learning_strategies import (
    LearningStrategy,
    SocraticStrategy,
    HintBasedStrategy,
    ConceptualStrategy,
    ProblemDecompositionStrategy
)


class QuestionType(Enum):
    """Types of questions students might ask"""
    CONCEPTUAL = "conceptual"          # "What is...?", "Explain..."
    PROBLEM_SOLVING = "problem"        # Math, coding problems
    HOW_TO = "how_to"                  # "How do I...?"
    WHY = "why"                        # "Why does...?"
    COMPARISON = "comparison"          # "What's the difference...?"
    GENERAL = "general"                # Default


class ResponseHandlerFactory:
    """
    Factory for creating appropriate response handlers
    Implements Factory Pattern
    """
    
    @staticmethod
    def detect_question_type(question: str) -> QuestionType:
        """
        Detect the type of question being asked
        Uses simple keyword matching (can be enhanced with NLP)
        """
        question_lower = question.lower()
        
        # Conceptual questions
        if any(word in question_lower for word in ['what is', 'define', 'explain', 'describe']):
            return QuestionType.CONCEPTUAL
        
        # Why questions
        if question_lower.startswith('why') or 'why does' in question_lower or 'why is' in question_lower:
            return QuestionType.WHY
        
        # How-to questions
        if any(word in question_lower for word in ['how do i', 'how to', 'how can i', 'steps to']):
            return QuestionType.HOW_TO
        
        # Comparison questions
        if any(word in question_lower for word in ['difference between', 'compare', 'versus', 'vs']):
            return QuestionType.COMPARISON
        
        # Problem-solving (look for numbers, equations, code keywords)
        if any(indicator in question_lower for indicator in 
               ['solve', 'calculate', 'compute', 'find the', 'answer', '=', '+', '-', '*', '/']):
            return QuestionType.PROBLEM_SOLVING
        
        return QuestionType.GENERAL
    
    @staticmethod
    def create_strategy(question_type: QuestionType, context: Dict[str, Any]) -> LearningStrategy:
        """
        Create appropriate learning strategy based on question type
        Factory Method
        """
        # Check if user requested hints
        if context.get('request_hint', False):
            return HintBasedStrategy()
        
        # Map question types to strategies
        strategy_map = {
            QuestionType.CONCEPTUAL: ConceptualStrategy(),
            QuestionType.WHY: SocraticStrategy(),
            QuestionType.HOW_TO: ProblemDecompositionStrategy(),
            QuestionType.COMPARISON: ConceptualStrategy(),
            QuestionType.PROBLEM_SOLVING: ProblemDecompositionStrategy(),
            QuestionType.GENERAL: SocraticStrategy(),
        }
        
        return strategy_map.get(question_type, SocraticStrategy())
    
    @staticmethod
    def create_response_handler(question: str, context: Dict[str, Any] = None) -> tuple[LearningStrategy, QuestionType]:
        """
        Main factory method - detects question type and creates appropriate strategy
        Returns tuple of (strategy, question_type) for tracking
        """
        if context is None:
            context = {}
        
        question_type = ResponseHandlerFactory.detect_question_type(question)
        strategy = ResponseHandlerFactory.create_strategy(question_type, context)
        
        return strategy, question_type


class ResponseMetadata:
    """Data class for response metadata"""
    
    def __init__(self, question_type: QuestionType, strategy_name: str, 
                 timestamp: str, hint_count: int = 0):
        self.question_type = question_type
        self.strategy_name = strategy_name
        self.timestamp = timestamp
        self.hint_count = hint_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'question_type': self.question_type.value,
            'strategy_name': self.strategy_name,
            'timestamp': self.timestamp,
            'hint_count': self.hint_count
        }
