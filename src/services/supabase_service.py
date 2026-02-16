"""
Supabase Backend Service
Handles all database operations using Supabase PostgreSQL
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from supabase import create_client, Client
from src.patterns.singleton import config

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service for interacting with Supabase backend"""
    
    def __init__(self):
        self.enabled = config.get('supabase.enabled', 'false').lower() == 'true'
        
        if self.enabled:
            try:
                url = config.get('supabase.url')
                key = config.get('supabase.key')
                
                if not url or not key or url == 'your_supabase_project_url':
                    logger.warning("Supabase credentials not configured, disabling Supabase")
                    self.enabled = False
                    self.client = None
                else:
                    self.client: Client = create_client(url, key)
                    logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase: {e}")
                self.enabled = False
                self.client = None
        else:
            self.client = None
            logger.info("Supabase is disabled in configuration")
    
    def is_available(self) -> bool:
        """Check if Supabase is available"""
        return self.enabled and self.client is not None
    
    # ==================== Session Management ====================
    
    def create_session(self, user_id: str = "anonymous") -> Optional[str]:
        """
        Create a new learning session
        Returns session_id or None if failed
        """
        if not self.is_available():
            return None
        
        try:
            session_data = {
                'user_id': user_id,
                'started_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            result = self.client.table('sessions').insert(session_data).execute()
            
            if result.data:
                session_id = result.data[0]['id']
                logger.info(f"Created session: {session_id}")
                return session_id
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return None
    
    def end_session(self, session_id: str, stats: Dict[str, Any]) -> bool:
        """End a learning session with final statistics"""
        if not self.is_available():
            return False
        
        try:
            update_data = {
                'ended_at': datetime.now().isoformat(),
                'status': 'completed',
                'total_questions': stats.get('total_questions', 0),
                'total_hints': stats.get('hints_requested', 0),
                'session_stats': stats
            }
            
            self.client.table('sessions').update(update_data).eq('id', session_id).execute()
            logger.info(f"Ended session: {session_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            return False
    
    # ==================== Question Logging ====================
    
    def log_question(self, session_id: str, question_data: Dict[str, Any]) -> bool:
        """
        Log a student question with metadata
        
        Args:
            session_id: The session ID
            question_data: Dict containing question, type, strategy, etc.
        """
        if not self.is_available():
            return False
        
        try:
            data = {
                'session_id': session_id,
                'question_text': question_data.get('question', ''),
                'question_type': question_data.get('question_type', 'unknown'),
                'strategy_used': question_data.get('strategy', ''),
                'timestamp': datetime.now().isoformat(),
                'metadata': question_data
            }
            
            self.client.table('questions').insert(data).execute()
            logger.debug(f"Logged question for session {session_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to log question: {e}")
            return False
    
    # ==================== Conversation History ====================
    
    def save_conversation(self, session_id: str, role: str, content: str, 
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save a conversation message (user or assistant)
        
        Args:
            session_id: The session ID
            role: 'user' or 'assistant'
            content: The message content
            metadata: Optional metadata about the message
        """
        if not self.is_available():
            return False
        
        try:
            data = {
                'session_id': session_id,
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            self.client.table('conversations').insert(data).execute()
            return True
        
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return False
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a session
        
        Args:
            session_id: The session ID
            limit: Maximum number of messages to retrieve
        """
        if not self.is_available():
            return []
        
        try:
            result = self.client.table('conversations')\
                .select('*')\
                .eq('session_id', session_id)\
                .order('timestamp', desc=False)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
        
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    # ==================== Progress Tracking ====================
    
    def log_progress_event(self, session_id: str, event_type: str, 
                          event_data: Dict[str, Any]) -> bool:
        """
        Log a progress tracking event
        
        Args:
            session_id: The session ID
            event_type: Type of event (question_asked, hint_requested, etc.)
            event_data: Event details
        """
        if not self.is_available():
            return False
        
        try:
            data = {
                'session_id': session_id,
                'event_type': event_type,
                'event_data': event_data,
                'timestamp': datetime.now().isoformat()
            }
            
            self.client.table('progress_events').insert(data).execute()
            return True
        
        except Exception as e:
            logger.error(f"Failed to log progress event: {e}")
            return False
    
    # ==================== Analytics ====================
    
    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific session"""
        if not self.is_available():
            return None
        
        try:
            # Get session data
            session = self.client.table('sessions')\
                .select('*')\
                .eq('id', session_id)\
                .single()\
                .execute()
            
            if not session.data:
                return None
            
            # Get question count by type
            questions = self.client.table('questions')\
                .select('question_type')\
                .eq('session_id', session_id)\
                .execute()
            
            # Get hint count
            hints = self.client.table('progress_events')\
                .select('event_type')\
                .eq('session_id', session_id)\
                .eq('event_type', 'hint_requested')\
                .execute()
            
            question_types = {}
            if questions.data:
                for q in questions.data:
                    q_type = q['question_type']
                    question_types[q_type] = question_types.get(q_type, 0) + 1
            
            return {
                'session_id': session_id,
                'total_questions': len(questions.data) if questions.data else 0,
                'hints_requested': len(hints.data) if hints.data else 0,
                'questions_by_type': question_types,
                'started_at': session.data.get('started_at'),
                'status': session.data.get('status')
            }
        
        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return None
    
    def get_user_analytics(self, user_id: str = "anonymous") -> Dict[str, Any]:
        """Get analytics for a user across all sessions"""
        if not self.is_available():
            return {}
        
        try:
            sessions = self.client.table('sessions')\
                .select('*')\
                .eq('user_id', user_id)\
                .execute()
            
            if not sessions.data:
                return {
                    'total_sessions': 0,
                    'total_questions': 0,
                    'total_hints': 0
                }
            
            total_questions = sum(s.get('total_questions', 0) for s in sessions.data)
            total_hints = sum(s.get('total_hints', 0) for s in sessions.data)
            
            return {
                'user_id': user_id,
                'total_sessions': len(sessions.data),
                'total_questions': total_questions,
                'total_hints': total_hints,
                'sessions': sessions.data
            }
        
        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            return {}
    
    # ==================== Hint Management ====================
    
    def log_hint(self, session_id: str, question: str, hint_number: int, 
                hint_content: str) -> bool:
        """Log a hint provided to the student"""
        if not self.is_available():
            return False
        
        try:
            data = {
                'session_id': session_id,
                'question': question,
                'hint_number': hint_number,
                'hint_content': hint_content,
                'timestamp': datetime.now().isoformat()
            }
            
            self.client.table('hints').insert(data).execute()
            return True
        
        except Exception as e:
            logger.error(f"Failed to log hint: {e}")
            return False
    
    # ==================== Utility Methods ====================
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the Supabase connection"""
        if not self.is_available():
            return {
                'connected': False,
                'error': 'Supabase is disabled or not configured'
            }
        
        try:
            # Try to select from sessions table
            result = self.client.table('sessions').select('id').limit(1).execute()
            
            return {
                'connected': True,
                'message': 'Successfully connected to Supabase',
                'tables_accessible': True
            }
        
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'message': 'Connection failed or tables not set up'
            }
