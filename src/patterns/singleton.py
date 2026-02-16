"""
Singleton Pattern for Configuration Management
Ensures single instance of configuration across the application
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv


class ConfigManager:
    """Singleton configuration manager"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize configuration from environment and files"""
        # Load environment variables
        load_dotenv()
        
        # Set default configuration
        self._config = {
            'ollama': {
                'host': os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
                'model': os.getenv('OLLAMA_MODEL', 'phi3:mini'),
                'timeout': int(os.getenv('OLLAMA_TIMEOUT', '120')),
            },
            'app': {
                'log_level': os.getenv('LOG_LEVEL', 'INFO'),
                'max_context_length': int(os.getenv('MAX_CONTEXT_LENGTH', '2048')),
                'temperature': float(os.getenv('TEMPERATURE', '0.7')),
            },
            'supabase': {
                'url': os.getenv('SUPABASE_URL', 'your_supabase_project_url'),
                'key': os.getenv('SUPABASE_KEY', 'your_supabase_anon_key'),
                'enabled': os.getenv('SUPABASE_ENABLED', 'false'),
            },
            'database': {
                'path': os.getenv('DB_PATH', 'data/student_progress.db'),
            },
            'ui': {
                'theme': os.getenv('UI_THEME', 'light'),
                'max_history': 50,
            },
            'learning': {
                'max_hints': 3,
                'enable_progress_tracking': True,
                'socratic_question_limit': 5,
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value by dot notation key"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()


# Global config instance
config = ConfigManager()
