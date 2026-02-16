"""
Chain of Responsibility Pattern for Question Handling
Routes questions through a chain of handlers
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class QuestionHandler(ABC):
    """Abstract handler in the chain"""
    
    def __init__(self):
        self._next_handler: Optional['QuestionHandler'] = None
    
    def set_next(self, handler: 'QuestionHandler') -> 'QuestionHandler':
        """Set the next handler in the chain"""
        self._next_handler = handler
        return handler
    
    @abstractmethod
    def handle(self, question: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle the question or pass to next handler
        Returns None if can't handle, Dict with response if handled
        """
        pass
    
    def _pass_to_next(self, question: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Pass to next handler if exists"""
        if self._next_handler:
            return self._next_handler.handle(question, context)
        return None


class DirectAnswerDetector(QuestionHandler):
    """
    Detects if student is asking for direct answers
    Redirects them to think critically
    """
    
    DIRECT_ANSWER_KEYWORDS = [
        'give me the answer',
        'what is the answer',
        'just tell me',
        'i give up',
        'show me the solution',
        'solve it for me',
    ]
    
    def handle(self, question: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect and handle direct answer requests"""
        question_lower = question.lower()
        
        # Check if asking for direct answer
        if any(keyword in question_lower for keyword in self.DIRECT_ANSWER_KEYWORDS):
            return {
                'handled': True,
                'response': self._generate_encouragement(),
                'requires_ai': False,
                'handler': 'DirectAnswerDetector'
            }
        
        return self._pass_to_next(question, context)
    
    def _generate_encouragement(self) -> str:
        """Generate encouraging response"""
        return """I understand you're struggling, but giving you the direct answer won't help you learn! 🎓

Instead, let me help you work through this step by step. Learning happens when you engage with the material.

Would you like me to:
1. Break down the problem into smaller steps?
2. Give you a hint to point you in the right direction?
3. Explain the underlying concept with a different example?

You've got this! 💪"""


class GreetingHandler(QuestionHandler):
    """Handles greetings and small talk"""
    
    GREETINGS = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
    
    def handle(self, question: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle greetings"""
        question_lower = question.lower().strip()
        
        if any(question_lower.startswith(greeting) for greeting in self.GREETINGS):
            return {
                'handled': True,
                'response': """Hello! I'm your AI Study Assistant! 👋

I'm here to help you LEARN, not just get answers. I'll guide you through:
- Understanding concepts deeply
- Breaking down complex problems
- Thinking critically about questions

What would you like to learn about today?""",
                'requires_ai': False,
                'handler': 'GreetingHandler'
            }
        
        return self._pass_to_next(question, context)


class HelpCommandHandler(QuestionHandler):
    """Handles help requests"""
    
    def handle(self, question: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle help commands"""
        question_lower = question.lower().strip()
        
        if question_lower in ['help', '/help', 'how does this work', 'what can you do']:
            return {
                'handled': True,
                'response': """**How I Help You Learn:**

🧠 **Socratic Method**: I ask guiding questions to help you think critically
💡 **Hints**: I provide progressive hints (type "hint" to get one)
📚 **Concept Explanation**: I explain underlying principles
🔍 **Problem Decomposition**: I help break complex problems into steps

**Tips:**
- Ask your question naturally
- If stuck, ask for a "hint"
- I won't give direct answers - that's the point!
- The more you engage, the more you learn

**Example Questions:**
- "I don't understand how photosynthesis works"
- "Can you help me with quadratic equations?"
- "Why does this Python code give an error?"

What would you like to learn?""",
                'requires_ai': False,
                'handler': 'HelpCommandHandler'
            }
        
        return self._pass_to_next(question, context)


class HintRequestHandler(QuestionHandler):
    """Handles explicit hint requests"""
    
    def handle(self, question: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle hint requests"""
        question_lower = question.lower().strip()
        
        if question_lower in ['hint', 'give me a hint', 'i need a hint', 'show hint']:
            # Mark that this is a hint request
            context['request_hint'] = True
            context['hint_count'] = context.get('hint_count', 0)
            
            if context['hint_count'] >= 3:
                return {
                    'handled': True,
                    'response': """You've used all 3 hints! At this point, let's try a different approach.

Would you like me to:
1. Explain the underlying concept?
2. Show you a similar but different example?
3. Break down the problem-solving approach?

Sometimes stepping back helps more than another hint!""",
                    'requires_ai': False,
                    'handler': 'HintRequestHandler'
                }
            
            # Pass to AI with hint request flag
            return self._pass_to_next(question, context)
        
        return self._pass_to_next(question, context)


class LearningQuestionHandler(QuestionHandler):
    """
    Final handler - processes learning questions with AI
    This should be the last in the chain
    """
    
    def handle(self, question: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle learning questions - requires AI processing"""
        return {
            'handled': True,
            'response': None,  # Will be filled by AI service
            'requires_ai': True,
            'handler': 'LearningQuestionHandler'
        }


def create_question_handler_chain() -> QuestionHandler:
    """
    Factory function to create the complete handler chain
    Order matters - more specific handlers come first
    """
    greeting = GreetingHandler()
    help_cmd = HelpCommandHandler()
    direct_answer = DirectAnswerDetector()
    hint_request = HintRequestHandler()
    learning = LearningQuestionHandler()
    
    # Chain them together
    greeting.set_next(help_cmd).set_next(direct_answer).set_next(hint_request).set_next(learning)
    
    return greeting
