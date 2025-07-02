import pytest
from fastapi.testclient import TestClient
from app.db.models.models import TherapyBuddy, User, DailyCheck

class TestBuddiesRoutes:
    def test_send_buddy_request(self, authorized_client, db_session, test_user):
        """Test sending a buddy request."""
        # Create another user to send request to
        buddy_user = User(
            email="buddy@example.com",
            password_hash="hashed_password",
            first_name="Buddy",
            last_name="User",
            preferred_language="en",
            is_active=True
        )
        db_session.add(buddy_user)
        db_session.commit()
        
        # Request data
        request_data = {
            "buddy_id": buddy_user.id
        }
        
        # Send buddy request
        response = authorized_client.post("/api/v1/buddies/request", json=request_data)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["buddy_id"] == buddy_user.id
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data
        
        # Verify request was created in database
        db_request = db_session.query(TherapyBuddy).filter(
            TherapyBuddy.user_id == test_user.id,
            TherapyBuddy.buddy_id == buddy_user.id
        ).first()
        assert db_request is not None
        assert db_request.status == "pending"
    
    def test_get_buddy_requests(self, authorized_client, db_session, test_user):
        """Test getting buddy requests for a user."""
        # Create another user
        other_user = User(
            email="other@example.com",
            password_hash="hashed_password",
            first_name="Other",
            last_name="User",
            preferred_language="en",
            is_active=True
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create a buddy request from other user to test user
        buddy_request = TherapyBuddy(
            user_id=other_user.id,
            buddy_id=test_user.id,
            status="pending"
        )
        db_session.add(buddy_request)
        db_session.commit()
        
        # Send get requests
        response = authorized_client.get("/api/v1/buddies/requests")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the one request we created
        
        # Verify request data
        request_found = False
        for request in data:
            if request["user_id"] == other_user.id and request["buddy_id"] == test_user.id:
                request_found = True
                assert request["status"] == "pending"
                break
        assert request_found
    
    def test_accept_buddy_request(self, authorized_client, db_session, test_user):
        """Test accepting a buddy request."""
        # Create another user
        other_user = User(
            email="accept@example.com",
            password_hash="hashed_password",
            first_name="Accept",
            last_name="User",
            preferred_language="en",
            is_active=True
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create a buddy request from other user to test user
        buddy_request = TherapyBuddy(
            user_id=other_user.id,
            buddy_id=test_user.id,
            status="pending"
        )
        db_session.add(buddy_request)
        db_session.commit()
        
        # Accept request data
        accept_data = {
            "request_id": buddy_request.id,
            "action": "accept"
        }
        
        # Send accept request
        response = authorized_client.post("/api/v1/buddies/respond", json=accept_data)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == buddy_request.id
        assert data["status"] == "accepted"
        
        # Verify database was updated
        db_session.refresh(buddy_request)
        assert buddy_request.status == "accepted"
    
    def test_reject_buddy_request(self, authorized_client, db_session, test_user):
        """Test rejecting a buddy request."""
        # Create another user
        other_user = User(
            email="reject@example.com",
            password_hash="hashed_password",
            first_name="Reject",
            last_name="User",
            preferred_language="en",
            is_active=True
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create a buddy request from other user to test user
        buddy_request = TherapyBuddy(
            user_id=other_user.id,
            buddy_id=test_user.id,
            status="pending"
        )
        db_session.add(buddy_request)
        db_session.commit()
        
        # Reject request data
        reject_data = {
            "request_id": buddy_request.id,
            "action": "reject"
        }
        
        # Send reject request
        response = authorized_client.post("/api/v1/buddies/respond", json=reject_data)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == buddy_request.id
        assert data["status"] == "rejected"
        
        # Verify database was updated
        db_session.refresh(buddy_request)
        assert buddy_request.status == "rejected"
    
    def test_get_active_buddies(self, authorized_client, db_session, test_user):
        """Test getting active buddies for a user."""
        # Create multiple users
        buddy1 = User(
            email="buddy1@example.com",
            password_hash="hashed_password",
            first_name="Buddy",
            last_name="One",
            preferred_language="en",
            is_active=True
        )
        buddy2 = User(
            email="buddy2@example.com",
            password_hash="hashed_password",
            first_name="Buddy",
            last_name="Two",
            preferred_language="en",
            is_active=True
        )
        db_session.add_all([buddy1, buddy2])
        db_session.commit()
        
        # Create accepted buddy relationships
        buddy_rel1 = TherapyBuddy(
            user_id=test_user.id,
            buddy_id=buddy1.id,
            status="accepted"
        )
        buddy_rel2 = TherapyBuddy(
            user_id=buddy2.id,
            buddy_id=test_user.id,
            status="accepted"
        )
        db_session.add_all([buddy_rel1, buddy_rel2])
        db_session.commit()
        
        # Send get buddies request
        response = authorized_client.get("/api/v1/buddies/active")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least the two buddies we created
        
        # Verify buddy data
        buddy_ids = [buddy["id"] for buddy in data]
        assert buddy1.id in buddy_ids
        assert buddy2.id in buddy_ids
    
    def test_remove_buddy(self, authorized_client, db_session, test_user):
        """Test removing a buddy relationship."""
        # Create another user
        other_user = User(
            email="remove@example.com",
            password_hash="hashed_password",
            first_name="Remove",
            last_name="User",
            preferred_language="en",
            is_active=True
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create an accepted buddy relationship
        buddy_rel = TherapyBuddy(
            user_id=test_user.id,
            buddy_id=other_user.id,
            status="accepted"
        )
        db_session.add(buddy_rel)
        db_session.commit()
        
        # Send remove buddy request
        response = authorized_client.delete(f"/api/v1/buddies/{buddy_rel.id}")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "successfully removed" in data["message"].lower()
        
        # Verify relationship was deleted
        deleted_rel = db_session.query(TherapyBuddy).filter(TherapyBuddy.id == buddy_rel.id).first()
        assert deleted_rel is None
    
    def test_share_daily_check(self, authorized_client, db_session, test_user):
        """Test sharing a daily check with a buddy."""
        # Create another user
        buddy_user = User(
            email="sharebuddy@example.com",
            password_hash="hashed_password",
            first_name="Share",
            last_name="Buddy",
            preferred_language="en",
            is_active=True
        )
        db_session.add(buddy_user)
        db_session.commit()
        
        # Create an accepted buddy relationship
        buddy_rel = TherapyBuddy(
            user_id=test_user.id,
            buddy_id=buddy_user.id,
            status="accepted"
        )
        db_session.add(buddy_rel)
        db_session.commit()
        
        # Create a daily check
        daily_check = DailyCheck(
            user_id=test_user.id,
            mood_score=7,
            notes="Feeling good today",
            shared_with_buddy=False
        )
        db_session.add(daily_check)
        db_session.commit()
        
        # Share data
        share_data = {
            "check_id": daily_check.id,
            "buddy_id": buddy_user.id
        }
        
        # Send share request
        response = authorized_client.post("/api/v1/buddies/share-check", json=share_data)
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == daily_check.id
        assert data["shared_with_buddy"] == True
        
        # Verify database was updated
        db_session.refresh(daily_check)
        assert daily_check.shared_with_buddy == True
    
    def test_unauthorized_access(self, client):
        """Test accessing buddy routes without authentication."""
        # Try to get buddies without authentication
        response = client.get("/api/v1/buddies/active")
        
        # Check response
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "not authenticated" in data["detail"].lower()
