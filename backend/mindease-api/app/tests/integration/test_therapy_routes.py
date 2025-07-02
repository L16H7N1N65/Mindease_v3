import pytest
from fastapi.testclient import TestClient
from app.db.models.models import TherapySession, TherapyMessage

class TestTherapyRoutes:
    def test_create_therapy_session(self, authorized_client, test_user):
        """Test creating a new therapy session."""
        # Session data
        session_data = {
            "session_type": "cbt",
            "title": "Test Therapy Session"
        }
        
        # Send create session request
        response = authorized_client.post("/api/v1/therapy/sessions", json=session_data)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == session_data["title"]
        assert data["session_type"] == session_data["session_type"]
        assert data["user_id"] == test_user.id
        assert data["status"] == "active"  # Default value
        assert "id" in data
        assert "created_at" in data
    
    def test_get_user_sessions(self, authorized_client, db_session, test_user):
        """Test getting all therapy sessions for a user."""
        # Create multiple sessions for the test user
        session1 = TherapySession(
            user_id=test_user.id,
            session_type="cbt",
            status="active",
            title="Session 1"
        )
        session2 = TherapySession(
            user_id=test_user.id,
            session_type="mindfulness",
            status="active",
            title="Session 2"
        )
        db_session.add_all([session1, session2])
        db_session.commit()
        
        # Send get sessions request
        response = authorized_client.get("/api/v1/therapy/sessions")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least the two sessions we created
        
        # Verify session data
        session_titles = [session["title"] for session in data]
        assert "Session 1" in session_titles
        assert "Session 2" in session_titles
    
    def test_get_session_by_id(self, authorized_client, db_session, test_user):
        """Test getting a specific therapy session by ID."""
        # Create a session
        session = TherapySession(
            user_id=test_user.id,
            session_type="cbt",
            status="active",
            title="Get By ID Test"
        )
        db_session.add(session)
        db_session.commit()
        
        # Send get session request
        response = authorized_client.get(f"/api/v1/therapy/sessions/{session.id}")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session.id
        assert data["title"] == "Get By ID Test"
        assert data["user_id"] == test_user.id
    
    def test_get_nonexistent_session(self, authorized_client):
        """Test getting a session that doesn't exist."""
        # Send get session request with non-existent ID
        response = authorized_client.get("/api/v1/therapy/sessions/99999")
        
        # Check response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_update_session(self, authorized_client, db_session, test_user):
        """Test updating a therapy session."""
        # Create a session to update
        session = TherapySession(
            user_id=test_user.id,
            session_type="cbt",
            status="active",
            title="Update Test"
        )
        db_session.add(session)
        db_session.commit()
        
        # Update data
        update_data = {
            "title": "Updated Title",
            "status": "completed"
        }
        
        # Send update request
        response = authorized_client.put(f"/api/v1/therapy/sessions/{session.id}", json=update_data)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session.id
        assert data["title"] == "Updated Title"
        assert data["status"] == "completed"
        
        # Verify database was updated
        db_session.refresh(session)
        assert session.title == "Updated Title"
        assert session.status == "completed"
    
    def test_delete_session(self, authorized_client, db_session, test_user):
        """Test deleting a therapy session."""
        # Create a session to delete
        session = TherapySession(
            user_id=test_user.id,
            session_type="cbt",
            status="active",
            title="Delete Test"
        )
        db_session.add(session)
        db_session.commit()
        session_id = session.id
        
        # Send delete request
        response = authorized_client.delete(f"/api/v1/therapy/sessions/{session_id}")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "successfully deleted" in data["message"].lower()
        
        # Verify session was deleted
        deleted_session = db_session.query(TherapySession).filter(TherapySession.id == session_id).first()
        assert deleted_session is None
    
    def test_send_message(self, authorized_client, db_session, test_user):
        """Test sending a message in a therapy session."""
        # Create a session
        session = TherapySession(
            user_id=test_user.id,
            session_type="cbt",
            status="active",
            title="Message Test"
        )
        db_session.add(session)
        db_session.commit()
        
        # Message data
        message_data = {
            "content": "This is a test message from the user"
        }
        
        # Send message request
        response = authorized_client.post(f"/api/v1/therapy/sessions/{session.id}/messages", json=message_data)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == message_data["content"]
        assert data["sender"] == "user"
        assert data["session_id"] == session.id
        assert "id" in data
        assert "sent_at" in data
        
        # Verify message was created in database
        db_message = db_session.query(TherapyMessage).filter(
            TherapyMessage.session_id == session.id,
            TherapyMessage.content == message_data["content"]
        ).first()
        assert db_message is not None
    
    def test_get_session_messages(self, authorized_client, db_session, test_user):
        """Test getting all messages for a therapy session."""
        # Create a session
        session = TherapySession(
            user_id=test_user.id,
            session_type="cbt",
            status="active",
            title="Get Messages Test"
        )
        db_session.add(session)
        db_session.commit()
        
        # Create multiple messages
        message1 = TherapyMessage(
            session_id=session.id,
            sender="user",
            content="User message 1",
            response_type="text"
        )
        message2 = TherapyMessage(
            session_id=session.id,
            sender="ai",
            content="AI response 1",
            response_type="text"
        )
        db_session.add_all([message1, message2])
        db_session.commit()
        
        # Send get messages request
        response = authorized_client.get(f"/api/v1/therapy/sessions/{session.id}/messages")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Verify message data
        message_contents = [message["content"] for message in data]
        assert "User message 1" in message_contents
        assert "AI response 1" in message_contents
    
    def test_unauthorized_access(self, client):
        """Test accessing therapy routes without authentication."""
        # Try to get sessions without authentication
        response = client.get("/api/v1/therapy/sessions")
        
        # Check response
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "not authenticated" in data["detail"].lower()
