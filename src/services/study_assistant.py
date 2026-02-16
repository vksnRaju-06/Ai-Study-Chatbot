"""
Study Assistant Core Service
Orchestrates all components using design patterns
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from src.services.ollama_service import OllamaService
from src.services.supabase_service import SupabaseService
from src.patterns.factory import ResponseHandlerFactory
from src.patterns.chain_of_responsibility import create_question_handler_chain
from src.patterns.observer import (
    StudentProgressTracker,
    ProgressLogger,
    ConsoleProgressTracker,
    AnalyticsTracker,
    SupabaseObserver
)
from src.strategies.learning_strategies import StrategyContext

logger = logging.getLogger(__name__)


class StudyAssistant:
    """
    Main study assistant orchestrator
    Combines all design patterns and services
    """
    
    def __init__(self):
        # Initialize services
        self.ollama = OllamaService()
        self.supabase = SupabaseService()
        
        # Initialize chain of responsibility
        self.handler_chain = create_question_handler_chain()
        
        # Initialize progress tracking (Observer pattern)
        self.progress_tracker = StudentProgressTracker()
        self.progress_logger = ProgressLogger()
        self.console_tracker = ConsoleProgressTracker()
        self.analytics_tracker = AnalyticsTracker()
        
        # Attach observers
        self.progress_tracker.attach(self.progress_logger)
        self.progress_tracker.attach(self.console_tracker)
        self.progress_tracker.attach(self.analytics_tracker)
        
        # Attach Supabase observer if available
        self.supabase_observer = None
        if self.supabase.is_available():
            # Create a session in Supabase
            session_id = self.supabase.create_session()
            if session_id:
                self.supabase_observer = SupabaseObserver(session_id)
                self.progress_tracker.attach(self.supabase_observer)
                logger.info(f"Supabase session created: {session_id}")
            else:
                logger.warning("Failed to create Supabase session")
        
        # Session context
        self.session_context = {
            'last_question': None,
            'hint_count': 0,
            'conversation_history': [],
            'session_id': self.supabase_observer.session_id if self.supabase_observer else None
        }
        
        # System message for AI
        self.system_message = """You are an educational AI assistant focused on helping students LEARN, not just get answers.

Core principles:
1. NEVER provide direct answers to homework or test questions
2. Guide students through Socratic questioning
3. Provide hints that lead to understanding, not solutions
4. Encourage critical thinking and problem-solving skills
5. Be supportive and encouraging
6. Explain concepts, but don't solve specific problems for them

Remember: The goal is LEARNING, not just completing assignments."""
    
    def check_ollama_status(self) -> Dict[str, Any]:
        """Check if OLLAMA is available"""
        available = self.ollama.is_available()
        
        status = {
            'available': available,
            'host': self.ollama.host,
            'model': self.ollama.model,
        }
        
        if available:
            status['models'] = self.ollama.list_models()
            status['message'] = f"✅ Connected to OLLAMA ({self.ollama.model})"
        else:
            status['models'] = []
            status['message'] = """❌ OLLAMA not available!

Please ensure:
1. OLLAMA is installed and running
2. Run: ollama pull phi3:mini
3. OLLAMA service is accessible at http://localhost:11434"""
        
        return status
    
    def check_supabase_status(self) -> Dict[str, Any]:
        """Check if Supabase is available and connected"""
        if not self.supabase.is_available():
            return {
                'available': False,
                'message': 'Supabase is disabled or not configured',
                'session_id': None
            }
        
        test_result = self.supabase.test_connection()
        
        return {
            'available': test_result.get('connected', False),
            'message': test_result.get('message', ''),
            'session_id': self.session_context.get('session_id'),
            'error': test_result.get('error')
        }
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """
        Process a student question through the complete pipeline
        
        Returns:
            Dict with 'response', 'metadata', and other info
        """
        logger.info(f"Processing question: {question}")
        
        # Update context
        context = self.session_context.copy()
        
        # Step 1: Chain of Responsibility - handle special cases
        handler_result = self.handler_chain.handle(question, context)
        
        # If handled without AI (greetings, help, etc.)
        if not handler_result.get('requires_ai', False):
            return {
                'response': handler_result['response'],
                'metadata': {
                    'handler': handler_result['handler'],
                    'requires_ai': False,
                    'timestamp': datetime.now().isoformat()
                }
            }
        
        # Step 2: Factory Pattern - detect question type and create strategy
        strategy, question_type = ResponseHandlerFactory.create_response_handler(
            question, context
        )
        
        # Step 3: Strategy Pattern - generate appropriate prompt
        strategy_context = StrategyContext(strategy)
        prompt = strategy_context.execute_strategy(question, context)
        
        # Step 4: Get AI response
        ai_response = self.ollama.generate_response(prompt, self.system_message)
        
        # Step 5: Observer Pattern - track progress
        self.progress_tracker.log_question(
            question,
            question_type.value,
            strategy.get_strategy_name()
        )
        
        # Update session context
        self.session_context['last_question'] = question
        if context.get('request_hint'):
            self.session_context['hint_count'] += 1
            self.progress_tracker.log_hint_request(
                question,
                self.session_context['hint_count']
            )
        
        # Add to conversation history
        self.session_context['conversation_history'].append({
            'question': question,
            'response': ai_response,
            'strategy': strategy.get_strategy_name(),
            'timestamp': datetime.now().isoformat()
        })
        
        # Save to Supabase if available
        if self.supabase.is_available() and self.session_context.get('session_id'):
            self.supabase.save_conversation(
                self.session_context['session_id'],
                'user',
                question,
                {'question_type': question_type.value}
            )
            self.supabase.save_conversation(
                self.session_context['session_id'],
                'assistant',
                ai_response,
                {
                    'strategy': strategy.get_strategy_name(),
                    'hint_count': self.session_context['hint_count']
                }
            )
        
        # Prepare response
        result = {
            'response': ai_response,
            'metadata': {
                'question_type': question_type.value,
                'strategy': strategy.get_strategy_name(),
                'hint_count': self.session_context['hint_count'],
                'handler': handler_result['handler'],
                'timestamp': datetime.now().isoformat()
            }
        }
        
        return result
    
    def request_hint(self) -> Dict[str, Any]:
        """Request a hint for the last question"""
        if not self.session_context.get('last_question'):
            return {
                'response': "Please ask a question first, then I can provide hints!",
                'metadata': {'error': 'no_previous_question'}
            }
        
        # Update context to request hint
        self.session_context['request_hint'] = True
        
        # Process as hint request
        return self.process_question(self.session_context['last_question'])
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        return self.analytics_tracker.get_stats()
    
    def reset_session(self):
        """Reset the learning session"""
        # End current Supabase session if exists
        if self.supabase.is_available() and self.session_context.get('session_id'):
            stats = self.get_session_stats()
            self.supabase.end_session(self.session_context['session_id'], stats)
        
        # Create new Supabase session
        new_session_id = None
        if self.supabase.is_available():
            new_session_id = self.supabase.create_session()
            if new_session_id and self.supabase_observer:
                self.supabase_observer.set_session_id(new_session_id)
        
        self.session_context = {
            'last_question': None,
            'hint_count': 0,
            'conversation_history': [],
            'session_id': new_session_id
        }
        logger.info("Session reset")
