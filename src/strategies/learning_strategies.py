"""
Strategy Pattern for Different Learning Approaches
Allows switching between different teaching strategies dynamically
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class LearningStrategy(ABC):
    """Abstract base class for learning strategies"""
    
    @abstractmethod
    def generate_response(self, question: str, context: Dict[str, Any]) -> str:
        """Generate a response based on the strategy"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return the strategy name"""
        pass


class SocraticStrategy(LearningStrategy):
    """
    Socratic Method: Guide students through questioning
    Encourages critical thinking by asking guiding questions
    """
    
    def generate_response(self, question: str, context: Dict[str, Any]) -> str:
        """Generate Socratic questions to guide learning"""
        prompt = f"""You are a Socratic tutor. A student asked: "{question}"

Instead of providing the answer, ask 2-3 guiding questions that will help the student:
1. Think critically about the problem
2. Break down the concept into smaller parts
3. Discover the answer themselves

Be encouraging and supportive. Focus on understanding, not just the answer.

Your response:"""
        return prompt
    
    def get_strategy_name(self) -> str:
        return "Socratic Method"


class HintBasedStrategy(LearningStrategy):
    """
    Hint-Based Learning: Provide progressive hints
    Gives incremental clues without revealing the full answer
    """
    
    def generate_response(self, question: str, context: Dict[str, Any]) -> str:
        """Generate hints without giving away the answer"""
        hint_level = context.get('hint_count', 0) + 1
        
        prompt = f"""You are a helpful tutor providing hints. A student asked: "{question}"

This is hint level {hint_level} of 3. Provide a {['gentle', 'moderate', 'stronger'][min(hint_level-1, 2)]} hint that:
1. Points the student in the right direction
2. Does NOT give the complete answer
3. Encourages them to think about specific aspects
4. Builds on previous hints if this isn't the first hint

Be supportive and explain WHY this hint matters.

Your hint:"""
        return prompt
    
    def get_strategy_name(self) -> str:
        return "Hint-Based Learning"


class ConceptualStrategy(LearningStrategy):
    """
    Conceptual Explanation: Break down concepts
    Explains underlying principles without solving the specific problem
    """
    
    def generate_response(self, question: str, context: Dict[str, Any]) -> str:
        """Explain concepts without solving the problem"""
        prompt = f"""You are a concept-focused tutor. A student asked: "{question}"

Instead of solving their specific problem:
1. Explain the underlying concepts and principles involved
2. Provide a similar but DIFFERENT example to illustrate the concept
3. Help them understand the "why" behind the topic
4. Do NOT solve their specific question

Be clear and thorough in explaining the concepts.

Your explanation:"""
        return prompt
    
    def get_strategy_name(self) -> str:
        return "Conceptual Understanding"


class ProblemDecompositionStrategy(LearningStrategy):
    """
    Problem Decomposition: Break complex problems into steps
    Teaches students how to approach problem-solving systematically
    """
    
    def generate_response(self, question: str, context: Dict[str, Any]) -> str:
        """Help break down the problem into manageable steps"""
        prompt = f"""You are a tutor focused on problem-solving methodology. A student asked: "{question}"

Help them by:
1. Breaking down the problem into smaller, manageable steps
2. Explaining what they should consider for EACH step
3. NOT solving any step, but showing them the approach
4. Teaching them the problem-solving process

Focus on the methodology, not the answer.

Your guidance:"""
        return prompt
    
    def get_strategy_name(self) -> str:
        return "Problem Decomposition"


class StrategyContext:
    """
    Context class that uses a strategy
    Allows dynamic switching between strategies
    """
    
    def __init__(self, strategy: LearningStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: LearningStrategy):
        """Change the learning strategy"""
        self._strategy = strategy
    
    def execute_strategy(self, question: str, context: Dict[str, Any]) -> str:
        """Execute the current strategy"""
        return self._strategy.generate_response(question, context)
    
    def get_current_strategy_name(self) -> str:
        """Get the name of current strategy"""
        return self._strategy.get_strategy_name()
