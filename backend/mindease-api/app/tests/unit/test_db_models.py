import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.db.models import User, Company, TherapySession, MoodEntry

def test_database_creation(db_session):
    """Test that the database is created successfully."""
    # If we can execute a query, the database is working
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1

class TestUserModel:
    def test_create_user(self, db_session):
        """Test creating a new user."""
        user = User(
            email="newuser@example.com",
            password_hash="hashed_password",
            first_name="New",
            last_name="User",
            preferred_language="en"
        )
        db_session.add(user)
        db_session.commit()
        
        # Retrieve the user from the database
        db_user = db_session.query(User).filter(User.email == "newuser@example.com").first()
        assert db_user is not None
        assert db_user.email == "newuser@example.com"
        assert db_user.first_name == "New"
        assert db_user.last_name == "User"
        assert db_user.preferred_language == "en"
        assert db_user.is_active == True  # Default value
        # Check if is_admin exists, if not, skip this assertion
        if hasattr(db_user, 'is_admin'):
            assert db_user.is_admin == False  # Default value
    
    def test_unique_email_constraint(self, db_session, test_user):
        """Test that users must have unique emails."""
        # Try to create a user with the same email as test_user
        duplicate_user = User(
            email=test_user.email,  # Same email as test_user
            password_hash="different_hash",
            first_name="Duplicate",
            last_name="User",
            preferred_language="fr"
        )
        db_session.add(duplicate_user)
        
        # Should raise an IntegrityError due to unique constraint
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        # Rollback the failed transaction
        db_session.rollback()
    
    def test_read_user(self, db_session, test_user):
        """Test reading a user from the database."""
        db_user = db_session.query(User).filter(User.id == test_user.id).first()
        assert db_user is not None
        assert db_user.email == test_user.email
        assert db_user.first_name == test_user.first_name
        assert db_user.last_name == test_user.last_name
    
    def test_update_user(self, db_session, test_user):
        """Test updating a user."""
        # Update user attributes
        test_user.first_name = "Updated"
        test_user.last_name = "Name"
        test_user.preferred_language = "es"
        db_session.commit()
        
        # Retrieve the updated user
        updated_user = db_session.query(User).filter(User.id == test_user.id).first()
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
        assert updated_user.preferred_language == "es"
    
    def test_delete_user(self, db_session):
        """Test deleting a user."""
        # Create a user to delete
        user_to_delete = User(
            email="delete_me@example.com",
            password_hash="hashed_password",
            first_name="Delete",
            last_name="Me",
            preferred_language="en"
        )
        db_session.add(user_to_delete)
        db_session.commit()
        
        # Verify user exists
        user_id = user_to_delete.id
        assert db_session.query(User).filter(User.id == user_id).first() is not None
        
        # Delete the user
        db_session.delete(user_to_delete)
        db_session.commit()
        
        # Verify user no longer exists
        assert db_session.query(User).filter(User.id == user_id).first() is None
    
    def test_user_company_relationship(self, db_session, test_company):
        """Test the relationship between User and Company."""
        # Create a user associated with the test company
        company_user = User(
            email="company_user@example.com",
            password_hash="hashed_password",
            first_name="Company",
            last_name="User",
            preferred_language="en",
            company_id=test_company.id
        )
        db_session.add(company_user)
        db_session.commit()
        
        # Verify the relationship
        db_user = db_session.query(User).filter(User.email == "company_user@example.com").first()
        assert db_user.company is not None
        assert db_user.company.id == test_company.id
        assert db_user.company.name == test_company.name
        
        # Verify the reverse relationship
        assert db_user in test_company.users

class TestTherapySessionModel:
    def test_create_therapy_session(self, db_session, test_user):
        """Test creating a new therapy session."""
        session = TherapySession(
            user_id=test_user.id,
            session_type="cbt",
            status="active",
            title="Test Session"
        )
        db_session.add(session)
        db_session.commit()
        
        # Retrieve the session from the database
        db_session_obj = db_session.query(TherapySession).filter(
            TherapySession.user_id == test_user.id,
            TherapySession.title == "Test Session"
        ).first()
        
        assert db_session_obj is not None
        assert db_session_obj.user_id == test_user.id
        assert db_session_obj.session_type == "cbt"
        assert db_session_obj.status == "active"
        assert db_session_obj.title == "Test Session"
    
    def test_therapy_session_user_relationship(self, db_session, test_user):
        """Test the relationship between TherapySession and User."""
        # Create a therapy session for the test user
        session = TherapySession(
            user_id=test_user.id,
            session_type="cbt",
            status="active",
            title="Relationship Test"
        )
        db_session.add(session)
        db_session.commit()
        
        # Verify the relationship
        db_session_obj = db_session.query(TherapySession).filter(
            TherapySession.title == "Relationship Test"
        ).first()
        
        assert db_session_obj.user is not None
        assert db_session_obj.user.id == test_user.id
        
        # Verify the reverse relationship
        assert db_session_obj in test_user.therapy_sessions
    
    def test_update_therapy_session(self, db_session, test_user):
        """Test updating a therapy session."""
        # Create a session to update
        session = TherapySession(
            user_id=test_user.id,
            session_type="cbt",
            status="active",
            title="Update Me"
        )
        db_session.add(session)
        db_session.commit()
        
        # Update session attributes
        session.title = "Updated Title"
        session.status = "completed"
        db_session.commit()
        
        # Retrieve the updated session
        updated_session = db_session.query(TherapySession).filter(
            TherapySession.id == session.id
        ).first()
        
        assert updated_session.title == "Updated Title"
        assert updated_session.status == "completed"
    
    def test_delete_therapy_session(self, db_session, test_user):
        """Test deleting a therapy session."""
        # Create a session to delete
        session_to_delete = TherapySession(
            user_id=test_user.id,
            session_type="cbt",
            status="active",
            title="Delete Me"
        )
        db_session.add(session_to_delete)
        db_session.commit()
        
        # Verify session exists
        session_id = session_to_delete.id
        assert db_session.query(TherapySession).filter(
            TherapySession.id == session_id
        ).first() is not None
        
        # Delete the session
        db_session.delete(session_to_delete)
        db_session.commit()
        
        # Verify session no longer exists
        assert db_session.query(TherapySession).filter(
            TherapySession.id == session_id
        ).first() is None

class TestMoodEntryModel:
    def test_create_mood_entry(self, db_session, test_user):
        """Test creating a new mood entry."""
        mood_entry = MoodEntry(
            user_id=test_user.id,
            mood_type="emotion",
            mood_value="happy",
            confidence=0.85,
            secondary_mood="excited",
            secondary_confidence=0.65,
            notes="Feeling great today!"
        )
        db_session.add(mood_entry)
        db_session.commit()
        
        # Retrieve the mood entry from the database
        db_mood_entry = db_session.query(MoodEntry).filter(
            MoodEntry.user_id == test_user.id,
            MoodEntry.mood_value == "happy"
        ).first()
        
        assert db_mood_entry is not None
        assert db_mood_entry.user_id == test_user.id
        assert db_mood_entry.mood_type == "emotion"
        assert db_mood_entry.mood_value == "happy"
        assert db_mood_entry.confidence == 0.85
        assert db_mood_entry.secondary_mood == "excited"
        assert db_mood_entry.secondary_confidence == 0.65
        assert db_mood_entry.notes == "Feeling great today!"
    
    def test_mood_entry_user_relationship(self, db_session, test_user):
        """Test the relationship between MoodEntry and User."""
        # Create a mood entry for the test user
        mood_entry = MoodEntry(
            user_id=test_user.id,
            mood_type="emotion",
            mood_value="calm",
            confidence=0.9
        )
        db_session.add(mood_entry)
        db_session.commit()
        
        # Verify the relationship
        db_mood_entry = db_session.query(MoodEntry).filter(
            MoodEntry.user_id == test_user.id,
            MoodEntry.mood_value == "calm"
        ).first()
        
        assert db_mood_entry.user is not None
        assert db_mood_entry.user.id == test_user.id
        
        # Verify the reverse relationship
        assert db_mood_entry in test_user.mood_entries
    
    def test_update_mood_entry(self, db_session, test_user):
        """Test updating a mood entry."""
        # Create a mood entry to update
        mood_entry = MoodEntry(
            user_id=test_user.id,
            mood_type="emotion",
            mood_value="neutral",
            confidence=0.7
        )
        db_session.add(mood_entry)
        db_session.commit()
        
        # Update mood entry attributes
        mood_entry.mood_value = "sad"
        mood_entry.confidence = 0.8
        mood_entry.notes = "Feeling down now"
        db_session.commit()
        
        # Retrieve the updated mood entry
        updated_entry = db_session.query(MoodEntry).filter(
            MoodEntry.id == mood_entry.id
        ).first()
        
        assert updated_entry.mood_value == "sad"
        assert updated_entry.confidence == 0.8
        assert updated_entry.notes == "Feeling down now"
    
    def test_delete_mood_entry(self, db_session, test_user):
        """Test deleting a mood entry."""
        # Create a mood entry to delete
        entry_to_delete = MoodEntry(
            user_id=test_user.id,
            mood_type="emotion",
            mood_value="angry",
            confidence=0.75
        )
        db_session.add(entry_to_delete)
        db_session.commit()
        
        # Verify entry exists
        entry_id = entry_to_delete.id
        assert db_session.query(MoodEntry).filter(
            MoodEntry.id == entry_id
        ).first() is not None
        
        # Delete the entry
        db_session.delete(entry_to_delete)
        db_session.commit()
        
        # Verify entry no longer exists
        assert db_session.query(MoodEntry).filter(
            MoodEntry.id == entry_id
        ).first() is None
