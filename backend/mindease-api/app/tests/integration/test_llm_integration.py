import pytest
from fastapi.testclient import TestClient
from app.db.models.models import TherapySession, TherapyMessage
import requests
from unittest.mock import patch, MagicMock

class TestLLMIntegration:
    @patch('app.services.therapy_service.requests.post')
    def test_therapy_session_llm_integration(self, mock_post, authorized_client, db_session, test_user):
        """Test the integration between therapy sessions and the LLM service."""
        # Mock the LLM service response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "This is a mock response from the LLM service."
        }
        mock_post.return_value = mock_response
        
        # Create a therapy session
        session_data = {
            "session_type": "cbt",
            "title": "LLM Integration Test"
        }
        
        # Create session
        session_response = authorized_client.post("/api/v1/therapy/sessions", json=session_data)
        assert session_response.status_code == 200
        session_id = session_response.json()["id"]
        
        # Send a message that should trigger the LLM
        message_data = {
            "content": "I'm feeling anxious about my upcoming presentation."
        }
        
        # Send message
        message_response = authorized_client.post(
            f"/api/v1/therapy/sessions/{session_id}/messages", 
            json=message_data
        )
        
        # Check response
        assert message_response.status_code == 200
        
        # Verify that the LLM service was called
        mock_post.assert_called_once()
        
        # Check that the call was made with the correct data
        call_args = mock_post.call_args[1]
        assert "json" in call_args
        assert call_args["json"]["message"] == message_data["content"]
        assert call_args["json"]["session_id"] == session_id
        
        # Verify that an AI response was created in the database
        ai_message = db_session.query(TherapyMessage).filter(
            TherapyMessage.session_id == session_id,
            TherapyMessage.sender == "ai"
        ).first()
        
        assert ai_message is not None
        assert ai_message.content == "This is a mock response from the LLM service."
    
    @patch('app.services.therapy_service.requests.post')
    def test_therapy_session_llm_failure_handling(self, mock_post, authorized_client, db_session, test_user):
        """Test handling of LLM service failures."""
        # Mock a failed LLM service response
        mock_post.side_effect = requests.exceptions.RequestException("Service unavailable")
        
        # Create a therapy session
        session_data = {
            "session_type": "cbt",
            "title": "LLM Failure Test"
        }
        
        # Create session
        session_response = authorized_client.post("/api/v1/therapy/sessions", json=session_data)
        assert session_response.status_code == 200
        session_id = session_response.json()["id"]
        
        # Send a message
        message_data = {
            "content": "Can you help me with my anxiety?"
        }
        
        # Send message
        message_response = authorized_client.post(
            f"/api/v1/therapy/sessions/{session_id}/messages", 
            json=message_data
        )
        
        # Check response - should still succeed even if LLM fails
        assert message_response.status_code == 200
        
        # Verify that the LLM service was called
        mock_post.assert_called_once()
        
        # Verify that a fallback AI response was created in the database
        ai_message = db_session.query(TherapyMessage).filter(
            TherapyMessage.session_id == session_id,
            TherapyMessage.sender == "ai"
        ).first()
        
        assert ai_message is not None
        assert "unable to connect" in ai_message.content.lower() or "fallback" in ai_message.content.lower()
    
    @patch('app.services.therapy_service.requests.post')
    def test_therapy_session_with_language_preference(self, mock_post, authorized_client, db_session, test_user):
        """Test that user language preference is respected in LLM requests."""
        # Set user language preference to French
        test_user.preferred_language = "fr"
        db_session.commit()
        
        # Mock the LLM service response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Voici une réponse en français."
        }
        mock_post.return_value = mock_response
        
        # Create a therapy session
        session_data = {
            "session_type": "cbt",
            "title": "Test de langue"
        }
        
        # Create session
        session_response = authorized_client.post("/api/v1/therapy/sessions", json=session_data)
        assert session_response.status_code == 200
        session_id = session_response.json()["id"]
        
        # Send a message
        message_data = {
            "content": "Je me sens anxieux aujourd'hui."
        }
        
        # Send message
        message_response = authorized_client.post(
            f"/api/v1/therapy/sessions/{session_id}/messages", 
            json=message_data
        )
        
        # Check response
        assert message_response.status_code == 200
        
        # Verify that the LLM service was called with the correct language
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        assert "json" in call_args
        assert call_args["json"]["language"] == "fr"
        
        # Verify that the French AI response was saved
        ai_message = db_session.query(TherapyMessage).filter(
            TherapyMessage.session_id == session_id,
            TherapyMessage.sender == "ai"
        ).first()
        
        assert ai_message is not None
        assert ai_message.content == "Voici une réponse en français."
