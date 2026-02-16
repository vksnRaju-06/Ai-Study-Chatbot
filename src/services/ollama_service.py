"""
OLLAMA Service Integration
Handles communication with OLLAMA for AI responses
"""

import requests
from typing import Dict, Any, Optional
import logging
from src.patterns.singleton import config

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with OLLAMA API"""
    
    def __init__(self):
        self.host = config.get('ollama.host')
        self.model = config.get('ollama.model')
        self.timeout = config.get('ollama.timeout', 60)
        self.temperature = config.get('app.temperature', 0.7)
        self.max_context = config.get('app.max_context_length', 2048)
    
    def is_available(self) -> bool:
        """Check if OLLAMA is running and accessible"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"OLLAMA not available: {e}")
            return False
    
    def list_models(self) -> list:
        """List available models in OLLAMA"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def generate_response(self, prompt: str, system_message: Optional[str] = None) -> str:
        """
        Generate response from OLLAMA
        
        Args:
            prompt: The user's prompt
            system_message: Optional system message to set context
            
        Returns:
            Generated response text
        """
        try:
            # Prepare the request
            url = f"{self.host}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_ctx": self.max_context,
                }
            }
            
            if system_message:
                payload["system"] = system_message
            
            # Make the request
            logger.debug(f"Sending request to OLLAMA: {self.model}")
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '').strip()
            else:
                logger.error(f"OLLAMA returned status {response.status_code}")
                return self._get_error_message(response.status_code)
        
        except requests.exceptions.Timeout:
            logger.error("OLLAMA request timed out")
            return "⏱️ The response took too long. Try asking a simpler question or breaking it into parts."
        
        except requests.exceptions.RequestException as e:
            logger.error(f"OLLAMA request failed: {e}")
            return f"❌ Error connecting to AI service: {str(e)}"
    
    def _get_error_message(self, status_code: int) -> str:
        """Get user-friendly error message"""
        if status_code == 404:
            return f"❌ Model '{self.model}' not found. Please run: ollama pull {self.model}"
        elif status_code == 500:
            return "❌ OLLAMA server error. Please check if OLLAMA is running properly."
        else:
            return f"❌ Unexpected error (status {status_code}). Please check OLLAMA."
    
    def chat(self, messages: list, system_message: Optional[str] = None) -> str:
        """
        Chat completion with conversation history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_message: Optional system message
            
        Returns:
            Generated response text
        """
        try:
            url = f"{self.host}/api/chat"
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_ctx": self.max_context,
                }
            }
            
            if system_message:
                payload["messages"].insert(0, {
                    "role": "system",
                    "content": system_message
                })
            
            logger.debug(f"Sending chat request to OLLAMA")
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('message', {}).get('content', '').strip()
            else:
                return self._get_error_message(response.status_code)
        
        except requests.exceptions.Timeout:
            return "⏱️ The response took too long. Try a simpler question."
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Chat request failed: {e}")
            return f"❌ Error: {str(e)}"
