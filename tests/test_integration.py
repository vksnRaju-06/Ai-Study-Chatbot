"""
Integration tests for Study Assistant
Run with: pytest tests/test_integration.py -v
"""

import pytest
from unittest.mock import Mock, patch
from src.services.study_assistant import StudyAssistant
from src.services.ollama_service import OllamaService


class TestStudyAssistantIntegration:
    """Integration tests for the complete system"""
    
    @pytest.fixture
    def assistant(self):
        """Create a study assistant instance"""
        return StudyAssistant()
    
    def test_assistant_initialization(self, assistant):
        """Test that assistant initializes correctly"""
        assert assistant.ollama is not None
        assert assistant.handler_chain is not None
        assert assistant.progress_tracker is not None
        assert len(assistant.session_context['conversation_history']) == 0
    
    @patch('src.services.ollama_service.requests.get')
    def test_ollama_status_check(self, mock_get, assistant):
        """Test OLLAMA status checking"""
        # Mock successful response
        mock_get.return_value.status_code = 200
        
        status = assistant.check_ollama_status()
        
        assert 'available' in status
        assert 'host' in status
        assert 'model' in status
    
    def test_greeting_handling(self, assistant):
        """Test greeting is handled without AI"""
        result = assistant.process_question("Hello")
        
        assert 'response' in result
        assert 'metadata' in result
        assert result['metadata']['requires_ai'] is False
        assert "Study Assistant" in result['response']
    
    def test_help_command_handling(self, assistant):
        """Test help command"""
        result = assistant.process_question("help")
        
        assert result['metadata']['requires_ai'] is False
        assert "Socratic Method" in result['response']
        assert "Hints" in result['response']
    
    def test_direct_answer_prevention(self, assistant):
        """Test that direct answer requests are redirected"""
        result = assistant.process_question("give me the answer")
        
        assert result['metadata']['requires_ai'] is False
        assert "learn" in result['response'].lower()
    
    @patch.object(OllamaService, 'generate_response')
    def test_question_processing_with_ai(self, mock_generate, assistant):
        """Test question processing that requires AI"""
        mock_generate.return_value = "This is a test response"
        
        result = assistant.process_question("What is Python?")
        
        assert 'response' in result
        assert 'metadata' in result
        assert 'question_type' in result['metadata']
        assert 'strategy' in result['metadata']
    
    @patch.object(OllamaService, 'generate_response')
    def test_hint_request_flow(self, mock_generate, assistant):
        """Test requesting hints"""
        mock_generate.return_value = "Here's a hint..."
        
        # First ask a question
        assistant.process_question("Solve x + 5 = 10")
        
        # Then request a hint
        result = assistant.request_hint()
        
        assert result['metadata']['hint_count'] >= 1
    
    def test_hint_without_question(self, assistant):
        """Test hint request without previous question"""
        result = assistant.request_hint()
        
        assert 'error' in result['metadata']
        assert "ask a question first" in result['response'].lower()
    
    @patch.object(OllamaService, 'generate_response')
    def test_session_statistics(self, mock_generate, assistant):
        """Test session statistics tracking"""
        mock_generate.return_value = "Response"
        
        # Ask multiple questions
        assistant.process_question("What is gravity?")
        assistant.process_question("How does it work?")
        
        stats = assistant.get_session_stats()
        
        assert stats['total_questions'] == 2
        assert 'questions_by_type' in stats
        assert 'strategies_used' in stats
    
    def test_session_reset(self, assistant):
        """Test session reset functionality"""
        # Add some session data
        assistant.session_context['last_question'] = "Test"
        assistant.session_context['hint_count'] = 2
        
        # Reset
        assistant.reset_session()
        
        assert assistant.session_context['last_question'] is None
        assert assistant.session_context['hint_count'] == 0
        assert len(assistant.session_context['conversation_history']) == 0
    
    @patch.object(OllamaService, 'generate_response')
    def test_conversation_history(self, mock_generate, assistant):
        """Test conversation history is maintained"""
        mock_generate.return_value = "Response"
        
        assistant.process_question("Question 1")
        assistant.process_question("Question 2")
        
        history = assistant.session_context['conversation_history']
        
        assert len(history) == 2
        assert history[0]['question'] == "Question 1"
        assert history[1]['question'] == "Question 2"
    
    @patch.object(OllamaService, 'generate_response')
    def test_different_question_types(self, mock_generate, assistant):
        """Test different question types are handled correctly"""
        mock_generate.return_value = "Response"
        
        questions = [
            ("What is photosynthesis?", "conceptual"),
            ("Why does ice float?", "why"),
            ("Solve x + 5 = 10", "problem"),
        ]
        
        for question, expected_type in questions:
            result = assistant.process_question(question)
            # Just verify processing works, exact type matching is tested in factory tests
            assert 'question_type' in result['metadata']


class TestOllamaService:
    """Test OLLAMA service integration"""
    
    @pytest.fixture
    def service(self):
        """Create OLLAMA service instance"""
        return OllamaService()
    
    def test_service_initialization(self, service):
        """Test service initializes with config"""
        assert service.host is not None
        assert service.model is not None
        assert service.timeout > 0
    
    @patch('src.services.ollama_service.requests.get')
    def test_availability_check_success(self, mock_get, service):
        """Test successful availability check"""
        mock_get.return_value.status_code = 200
        
        assert service.is_available() is True
    
    @patch('src.services.ollama_service.requests.get')
    def test_availability_check_failure(self, mock_get, service):
        """Test failed availability check"""
        mock_get.side_effect = Exception("Connection error")
        
        assert service.is_available() is False
    
    @patch('src.services.ollama_service.requests.get')
    def test_list_models(self, mock_get, service):
        """Test listing models"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'models': [
                {'name': 'phi3:mini'},
                {'name': 'llama3.2:1b'}
            ]
        }
        
        models = service.list_models()
        
        assert 'phi3:mini' in models
        assert 'llama3.2:1b' in models
    
    @patch('src.services.ollama_service.requests.post')
    def test_generate_response_success(self, mock_post, service):
        """Test successful response generation"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'response': 'Generated text'
        }
        
        response = service.generate_response("Test prompt")
        
        assert response == 'Generated text'
    
    @patch('src.services.ollama_service.requests.post')
    def test_generate_response_model_not_found(self, mock_post, service):
        """Test handling of model not found"""
        mock_post.return_value.status_code = 404
        
        response = service.generate_response("Test prompt")
        
        assert "not found" in response.lower()
    
    @patch('src.services.ollama_service.requests.post')
    def test_generate_response_timeout(self, mock_post, service):
        """Test handling of timeout"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()
        
        response = service.generate_response("Test prompt")
        
        assert "too long" in response.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
