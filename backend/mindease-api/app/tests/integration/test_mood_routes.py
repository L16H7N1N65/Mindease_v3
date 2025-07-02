import pytest
from fastapi.testclient import TestClient
from app.db.models.models import MoodEntry

class TestMoodRoutes:
    def test_create_mood_entry(self, authorized_client, test_user):
        """Test creating a new mood entry."""
        # Mood entry data
        mood_data = {
            "mood_type": "emotion",
            "mood_value": "happy",
            "confidence": 0.85,
            "secondary_mood": "excited",
            "secondary_confidence": 0.65,
            "notes": "Feeling great today!"
        }
        
        # Send create mood entry request
        response = authorized_client.post("/api/v1/mood/entries", json=mood_data)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["mood_type"] == mood_data["mood_type"]
        assert data["mood_value"] == mood_data["mood_value"]
        assert data["confidence"] == mood_data["confidence"]
        assert data["secondary_mood"] == mood_data["secondary_mood"]
        assert data["secondary_confidence"] == mood_data["secondary_confidence"]
        assert data["notes"] == mood_data["notes"]
        assert data["user_id"] == test_user.id
        assert "id" in data
        assert "recorded_at" in data
    
    def test_get_user_mood_entries(self, authorized_client, db_session, test_user):
        """Test getting all mood entries for a user."""
        # Create multiple mood entries for the test user
        entry1 = MoodEntry(
            user_id=test_user.id,
            mood_type="emotion",
            mood_value="happy",
            confidence=0.9
        )
        entry2 = MoodEntry(
            user_id=test_user.id,
            mood_type="emotion",
            mood_value="calm",
            confidence=0.8
        )
        db_session.add_all([entry1, entry2])
        db_session.commit()
        
        # Send get mood entries request
        response = authorized_client.get("/api/v1/mood/entries")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least the two entries we created
        
        # Verify entry data
        mood_values = [entry["mood_value"] for entry in data]
        assert "happy" in mood_values
        assert "calm" in mood_values
    
    def test_get_mood_entry_by_id(self, authorized_client, db_session, test_user):
        """Test getting a specific mood entry by ID."""
        # Create a mood entry
        entry = MoodEntry(
            user_id=test_user.id,
            mood_type="emotion",
            mood_value="neutral",
            confidence=0.7,
            notes="Test entry"
        )
        db_session.add(entry)
        db_session.commit()
        
        # Send get mood entry request
        response = authorized_client.get(f"/api/v1/mood/entries/{entry.id}")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entry.id
        assert data["mood_value"] == "neutral"
        assert data["confidence"] == 0.7
        assert data["notes"] == "Test entry"
        assert data["user_id"] == test_user.id
    
    def test_get_nonexistent_mood_entry(self, authorized_client):
        """Test getting a mood entry that doesn't exist."""
        # Send get mood entry request with non-existent ID
        response = authorized_client.get("/api/v1/mood/entries/99999")
        
        # Check response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_update_mood_entry(self, authorized_client, db_session, test_user):
        """Test updating a mood entry."""
        # Create a mood entry to update
        entry = MoodEntry(
            user_id=test_user.id,
            mood_type="emotion",
            mood_value="sad",
            confidence=0.6
        )
        db_session.add(entry)
        db_session.commit()
        
        # Update data
        update_data = {
            "mood_value": "happy",
            "confidence": 0.9,
            "notes": "Feeling better now"
        }
        
        # Send update request
        response = authorized_client.put(f"/api/v1/mood/entries/{entry.id}", json=update_data)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entry.id
        assert data["mood_value"] == "happy"
        assert data["confidence"] == 0.9
        assert data["notes"] == "Feeling better now"
        
        # Verify database was updated
        db_session.refresh(entry)
        assert entry.mood_value == "happy"
        assert entry.confidence == 0.9
        assert entry.notes == "Feeling better now"
    
    def test_delete_mood_entry(self, authorized_client, db_session, test_user):
        """Test deleting a mood entry."""
        # Create a mood entry to delete
        entry = MoodEntry(
            user_id=test_user.id,
            mood_type="emotion",
            mood_value="angry",
            confidence=0.8
        )
        db_session.add(entry)
        db_session.commit()
        entry_id = entry.id
        
        # Send delete request
        response = authorized_client.delete(f"/api/v1/mood/entries/{entry_id}")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "successfully deleted" in data["message"].lower()
        
        # Verify entry was deleted
        deleted_entry = db_session.query(MoodEntry).filter(MoodEntry.id == entry_id).first()
        assert deleted_entry is None
    
    def test_get_mood_analytics(self, authorized_client, db_session, test_user):
        """Test getting mood analytics for a user."""
        # Create multiple mood entries with different dates
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        # Create entries for the past week
        for i in range(7):
            entry_date = datetime.utcnow() - timedelta(days=i)
            entry = MoodEntry(
                user_id=test_user.id,
                mood_type="emotion",
                mood_value="happy" if i % 2 == 0 else "sad",
                confidence=0.7 + (i * 0.03),
                recorded_at=entry_date
            )
            db_session.add(entry)
        db_session.commit()
        
        # Send get analytics request
        response = authorized_client.get("/api/v1/mood/analytics")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        
        # Verify analytics data structure
        assert "mood_distribution" in data
        assert "mood_trend" in data
        assert isinstance(data["mood_distribution"], dict)
        assert isinstance(data["mood_trend"], list)
        
        # Verify mood distribution contains our mood values
        assert "happy" in data["mood_distribution"]
        assert "sad" in data["mood_distribution"]
        
        # Verify mood trend has entries
        assert len(data["mood_trend"]) > 0
    
    def test_unauthorized_access(self, client):
        """Test accessing mood routes without authentication."""
        # Try to get mood entries without authentication
        response = client.get("/api/v1/mood/entries")
        
        # Check response
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "not authenticated" in data["detail"].lower()
