"""
Observer Pattern for Progress Tracking
Monitors and logs student learning activities
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Observer(ABC):
    """Abstract observer interface"""
    
    @abstractmethod
    def update(self, event: Dict[str, Any]):
        """Receive update from subject"""
        pass


class ProgressLogger(Observer):
    """Logs student progress to file"""
    
    def __init__(self, log_path: str = "data/progress_log.json"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize log file if doesn't exist
        if not self.log_path.exists():
            self.log_path.write_text("[]")
    
    def update(self, event: Dict[str, Any]):
        """Log the event"""
        # Read existing logs
        try:
            with open(self.log_path, 'r') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logs = []
        
        # Add new event
        logs.append(event)
        
        # Write back
        with open(self.log_path, 'w') as f:
            json.dump(logs, f, indent=2)


class ConsoleProgressTracker(Observer):
    """Prints progress updates to console"""
    
    def update(self, event: Dict[str, Any]):
        """Print event to console"""
        event_type = event.get('type', 'unknown')
        timestamp = event.get('timestamp', 'N/A')
        print(f"[{timestamp}] {event_type.upper()}: {event.get('summary', 'No details')}")


class AnalyticsTracker(Observer):
    """Tracks analytics for student learning patterns"""
    
    def __init__(self):
        self.session_stats = {
            'total_questions': 0,
            'questions_by_type': {},
            'strategies_used': {},
            'hints_requested': 0,
            'session_start': datetime.now().isoformat()
        }
    
    def update(self, event: Dict[str, Any]):
        """Update analytics based on event"""
        if event.get('type') == 'question_asked':
            self.session_stats['total_questions'] += 1
            
            # Track question types
            q_type = event.get('question_type', 'unknown')
            self.session_stats['questions_by_type'][q_type] = \
                self.session_stats['questions_by_type'].get(q_type, 0) + 1
            
            # Track strategies
            strategy = event.get('strategy', 'unknown')
            self.session_stats['strategies_used'][strategy] = \
                self.session_stats['strategies_used'].get(strategy, 0) + 1
        
        elif event.get('type') == 'hint_requested':
            self.session_stats['hints_requested'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        return self.session_stats.copy()


class SupabaseObserver(Observer):
    """
    Observer that stores events in Supabase
    Gracefully falls back to local storage if Supabase unavailable
    """
    
    def __init__(self, session_id: Optional[str] = None):
        try:
            from src.services.supabase_service import SupabaseService
            self.supabase = SupabaseService()
            self.session_id = session_id
            logger.info("SupabaseObserver initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize SupabaseObserver: {e}")
            self.supabase = None
            self.session_id = None
    
    def set_session_id(self, session_id: str):
        """Set the session ID for tracking"""
        self.session_id = session_id
    
    def update(self, event: Dict[str, Any]):
        """Store event in Supabase"""
        if not self.supabase or not self.supabase.is_available():
            logger.debug("Supabase not available, skipping storage")
            return
        
        if not self.session_id:
            logger.warning("No session_id set for SupabaseObserver")
            return
        
        try:
            event_type = event.get('type', 'unknown')
            
            # Store different event types appropriately
            if event_type == 'question_asked':
                self.supabase.log_question(self.session_id, {
                    'question': event.get('question', ''),
                    'question_type': event.get('question_type', 'unknown'),
                    'strategy': event.get('strategy', ''),
                })
            
            elif event_type == 'hint_requested':
                self.supabase.log_progress_event(
                    self.session_id,
                    'hint_requested',
                    {
                        'question': event.get('question', ''),
                        'hint_number': event.get('hint_number', 0)
                    }
                )
            
            else:
                # Store other events as progress events
                self.supabase.log_progress_event(
                    self.session_id,
                    event_type,
                    event
                )
        
        except Exception as e:
            logger.error(f"Failed to store event in Supabase: {e}")


class StudentProgressTracker:
    """
    Subject in Observer pattern
    Manages observers and notifies them of events
    """
    
    def __init__(self):
        self._observers: List[Observer] = []
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def attach(self, observer: Observer):
        """Add an observer"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer):
        """Remove an observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event: Dict[str, Any]):
        """Notify all observers of an event"""
        # Add session info and timestamp
        event['session_id'] = self._session_id
        event['timestamp'] = datetime.now().isoformat()
        
        # Notify all observers
        for observer in self._observers:
            observer.update(event)
    
    def log_question(self, question: str, question_type: str, strategy: str):
        """Log when a question is asked"""
        self.notify({
            'type': 'question_asked',
            'question': question,
            'question_type': question_type,
            'strategy': strategy,
            'summary': f'Question: {question[:50]}...'
        })
    
    def log_hint_request(self, question: str, hint_number: int):
        """Log when a hint is requested"""
        self.notify({
            'type': 'hint_requested',
            'question': question,
            'hint_number': hint_number,
            'summary': f'Hint {hint_number} requested'
        })
    
    def log_strategy_change(self, old_strategy: str, new_strategy: str):
        """Log when learning strategy changes"""
        self.notify({
            'type': 'strategy_changed',
            'old_strategy': old_strategy,
            'new_strategy': new_strategy,
            'summary': f'Changed from {old_strategy} to {new_strategy}'
        })
