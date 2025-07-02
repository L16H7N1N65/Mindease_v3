import pytest
from sqlalchemy.exc import IntegrityError
import app.db.models as models
from app.db.models import Company, TherapyMessage, CBTRule, TherapyBuddy, ReferralCode
from app.db.models import APIKey    

class TestCompanyModel:
    def test_create_company(self, db_session):
        """Test creating a new company."""
        company = Company(
            name="New Company",
            contact_email="contact@newcompany.com",
            subscription_tier="standard"
        )
        db_session.add(company)
        db_session.commit()
        
        # Retrieve the company from the database
        db_company = db_session.query(Company).filter(Company.name == "New Company").first()
        assert db_company is not None
        assert db_company.name == "New Company"
        assert db_company.contact_email == "contact@newcompany.com"
        assert db_company.subscription_tier == "standard"
    
    def test_update_company(self, db_session, test_company):
        """Test updating a company."""
        # Update company attributes
        test_company.name = "Updated Company"
        test_company.subscription_tier = "premium"
        db_session.commit()
        
        # Retrieve the updated company
        updated_company = db_session.query(Company).filter(Company.id == test_company.id).first()
        assert updated_company.name == "Updated Company"
        assert updated_company.subscription_tier == "premium"
    
    def test_delete_company(self, db_session):
        """Test deleting a company."""
        # Create a company to delete
        company_to_delete = Company(
            name="Delete Me Company",
            contact_email="delete@example.com",
            subscription_tier="basic"
        )
        db_session.add(company_to_delete)
        db_session.commit()
        
        # Verify company exists
        company_id = company_to_delete.id
        assert db_session.query(Company).filter(Company.id == company_id).first() is not None
        
        # Delete the company
        db_session.delete(company_to_delete)
        db_session.commit()
        
        # Verify company no longer exists
        assert db_session.query(Company).filter(Company.id == company_id).first() is None

class TestTherapyMessageModel:
    def test_create_therapy_message(self, db_session, test_user):
        """Test creating a new therapy message."""
        # First create a therapy session
        from app.db.models import TherapySession
        session = TherapySession(
            user_id=test_user.id,
            session_type="cbt",
            status="active",
            title="Message Test Session"
        )
        db_session.add(session)
        db_session.commit()
        
        # Create a message for the session
        message = TherapyMessage(
            session_id=session.id,
            sender="user",
            content="This is a test message",
            response_type="text"
        )
        db_session.add(message)
        db_session.commit()
        
        # Retrieve the message from the database
        db_message = db_session.query(TherapyMessage).filter(
            TherapyMessage.session_id == session.id,
            TherapyMessage.content == "This is a test message"
        ).first()
        
        assert db_message is not None
        assert db_message.session_id == session.id
        assert db_message.sender == "user"
        assert db_message.content == "This is a test message"
        assert db_message.response_type == "text"
    
    def test_therapy_message_session_relationship(self, db_session, test_user):
        """Test the relationship between TherapyMessage and TherapySession."""
        # Create a therapy session
        from app.db.models import TherapySession
        session = TherapySession(
            user_id=test_user.id,
            session_type="cbt",
            status="active",
            title="Relationship Test Session"
        )
        db_session.add(session)
        db_session.commit()
        
        # Create a message for the session
        message = TherapyMessage(
            session_id=session.id,
            sender="ai",
            content="AI response message",
            response_type="text"
        )
        db_session.add(message)
        db_session.commit()
        
        # Verify the relationship
        db_message = db_session.query(TherapyMessage).filter(
            TherapyMessage.content == "AI response message"
        ).first()
        
        assert db_message.session is not None
        assert db_message.session.id == session.id
        
        # Verify the reverse relationship
        assert db_message in session.messages
    
    def test_update_therapy_message(self, db_session, test_user):
        """Test updating a therapy message."""
        # Create a therapy session
        from app.db.models import TherapySession
        session = TherapySession(
            user_id=test_user.id,
            session_type="cbt",
            status="active",
            title="Update Message Test"
        )
        db_session.add(session)
        db_session.commit()
        
        # Create a message to update
        message = TherapyMessage(
            session_id=session.id,
            sender="user",
            content="Original message",
            response_type="text"
        )
        db_session.add(message)
        db_session.commit()
        
        # Update message attributes
        message.content = "Updated message"
        message.response_type = "suggestion"
        db_session.commit()
        
        # Retrieve the updated message
        updated_message = db_session.query(TherapyMessage).filter(
            TherapyMessage.id == message.id
        ).first()
        
        assert updated_message.content == "Updated message"
        assert updated_message.response_type == "suggestion"
    
    def test_delete_therapy_message(self, db_session, test_user):
        """Test deleting a therapy message."""
        # Create a therapy session
        from app.db.models import TherapySession
        session = TherapySession(
            user_id=test_user.id,
            session_type="cbt",
            status="active",
            title="Delete Message Test"
        )
        db_session.add(session)
        db_session.commit()
        
        # Create a message to delete
        message_to_delete = TherapyMessage(
            session_id=session.id,
            sender="user",
            content="Delete this message",
            response_type="text"
        )
        db_session.add(message_to_delete)
        db_session.commit()
        
        # Verify message exists
        message_id = message_to_delete.id
        assert db_session.query(TherapyMessage).filter(
            TherapyMessage.id == message_id
        ).first() is not None
        
        # Delete the message
        db_session.delete(message_to_delete)
        db_session.commit()
        
        # Verify message no longer exists
        assert db_session.query(TherapyMessage).filter(
            TherapyMessage.id == message_id
        ).first() is None

class TestCBTRuleModel:
    def test_create_cbt_rule(self, db_session):
        """Test creating a new CBT rule."""
        rule = CBTRule(
            trigger_pattern="feeling (sad|depressed|down)",
            response_template="I notice you're feeling {0}. Let's explore that further.",
            priority=3,
            category="mood_support"
        )
        db_session.add(rule)
        db_session.commit()
        
        # Retrieve the rule from the database
        db_rule = db_session.query(CBTRule).filter(
            CBTRule.category == "mood_support"
        ).first()
        
        assert db_rule is not None
        assert "feeling (sad|depressed|down)" in db_rule.trigger_pattern
        assert "I notice you're feeling {0}" in db_rule.response_template
        assert db_rule.priority == 3
        assert db_rule.category == "mood_support"
        assert db_rule.is_active == True  # Default value
    
    def test_update_cbt_rule(self, db_session):
        """Test updating a CBT rule."""
        # Create a rule to update
        rule = CBTRule(
            trigger_pattern="anxiety pattern",
            response_template="Original template",
            priority=5,
            category="anxiety"
        )
        db_session.add(rule)
        db_session.commit()
        
        # Update rule attributes
        rule.response_template = "Updated template"
        rule.priority = 2
        rule.is_active = False
        db_session.commit()
        
        # Retrieve the updated rule
        updated_rule = db_session.query(CBTRule).filter(
            CBTRule.id == rule.id
        ).first()
        
        assert updated_rule.response_template == "Updated template"
        assert updated_rule.priority == 2
        assert updated_rule.is_active == False
    
    def test_delete_cbt_rule(self, db_session):
        """Test deleting a CBT rule."""
        # Create a rule to delete
        rule_to_delete = CBTRule(
            trigger_pattern="delete pattern",
            response_template="Delete template",
            priority=1,
            category="test"
        )
        db_session.add(rule_to_delete)
        db_session.commit()
        
        # Verify rule exists
        rule_id = rule_to_delete.id
        assert db_session.query(CBTRule).filter(
            CBTRule.id == rule_id
        ).first() is not None
        
        # Delete the rule
        db_session.delete(rule_to_delete)
        db_session.commit()
        
        # Verify rule no longer exists
        assert db_session.query(CBTRule).filter(
            CBTRule.id == rule_id
        ).first() is None

class TestTherapyBuddyModel:
    def test_create_therapy_buddy(self, db_session):
        """Test creating a new therapy buddy relationship."""
        # Create two users
        from app.db.models import User
        user1 = User(
            email="user1@example.com",
            password_hash="hashed_password",
            first_name="User",
            last_name="One"
        )
        user2 = User(
            email="user2@example.com",
            password_hash="hashed_password",
            first_name="User",
            last_name="Two"
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create buddy relationship
        buddy = TherapyBuddy(
            user_id=user1.id,
            buddy_id=user2.id,
            status="pending"
        )
        db_session.add(buddy)
        db_session.commit()
        
        # Retrieve the buddy relationship from the database
        db_buddy = db_session.query(TherapyBuddy).filter(
            TherapyBuddy.user_id == user1.id,
            TherapyBuddy.buddy_id == user2.id
        ).first()
        
        assert db_buddy is not None
        assert db_buddy.user_id == user1.id
        assert db_buddy.buddy_id == user2.id
        assert db_buddy.status == "pending"
    
    def test_therapy_buddy_user_relationship(self, db_session):
        """Test the relationship between TherapyBuddy and User."""
        # Create two users
        from app.db.models import User
        user1 = User(
            email="buddy1@example.com",
            password_hash="hashed_password",
            first_name="Buddy",
            last_name="One"
        )
        user2 = User(
            email="buddy2@example.com",
            password_hash="hashed_password",
            first_name="Buddy",
            last_name="Two"
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create buddy relationship
        buddy = TherapyBuddy(
            user_id=user1.id,
            buddy_id=user2.id,
            status="accepted"
        )
        db_session.add(buddy)
        db_session.commit()
        
        # Verify the relationships
        db_buddy = db_session.query(TherapyBuddy).filter(
            TherapyBuddy.user_id == user1.id,
            TherapyBuddy.buddy_id == user2.id
        ).first()
        
        assert db_buddy.user is not None
        assert db_buddy.user.id == user1.id
        assert db_buddy.buddy is not None
        assert db_buddy.buddy.id == user2.id
        
        # Verify the reverse relationships
        assert db_buddy in user1.sent_buddy_requests
        assert db_buddy in user2.received_buddy_requests
    
    def test_update_therapy_buddy(self, db_session):
        """Test updating a therapy buddy relationship."""
        # Create two users
        from app.db.models import User
        user1 = User(
            email="update1@example.com",
            password_hash="hashed_password",
            first_name="Update",
            last_name="One"
        )
        user2 = User(
            email="update2@example.com",
            password_hash="hashed_password",
            first_name="Update",
            last_name="Two"
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create buddy relationship to update
        buddy = TherapyBuddy(
            user_id=user1.id,
            buddy_id=user2.id,
            status="pending"
        )
        db_session.add(buddy)
        db_session.commit()
        
        # Update buddy attributes
        buddy.status = "accepted"
        from datetime import datetime
        buddy.last_interaction = datetime.utcnow()
        db_session.commit()
        
        # Retrieve the updated buddy relationship
        updated_buddy = db_session.query(TherapyBuddy).filter(
            TherapyBuddy.id == buddy.id
        ).first()
        
        assert updated_buddy.status == "accepted"
        assert updated_buddy.last_interaction is not None
    
    def test_delete_therapy_buddy(self, db_session):
        """Test deleting a therapy buddy relationship."""
        # Create two users
        from app.db.models import User
        user1 = User(
            email="delete1@example.com",
            password_hash="hashed_password",
            first_name="Delete",
            last_name="One"
        )
        user2 = User(
            email="delete2@example.com",
            password_hash="hashed_password",
            first_name="Delete",
            last_name="Two"
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create buddy relationship to delete
        buddy_to_delete = TherapyBuddy(
            user_id=user1.id,
            buddy_id=user2.id,
            status="pending"
        )
        db_session.add(buddy_to_delete)
        db_session.commit()
        
        # Verify buddy relationship exists
        buddy_id = buddy_to_delete.id
        assert db_session.query(TherapyBuddy).filter(
            TherapyBuddy.id == buddy_id
        ).first() is not None
        
        # Delete the buddy relationship
        db_session.delete(buddy_to_delete)
        db_session.commit()
        
        # Verify buddy relationship no longer exists
        assert db_session.query(TherapyBuddy).filter(
            TherapyBuddy.id == buddy_id
        ).first() is None

class TestReferralCodeModel:
    def test_create_referral_code(self, db_session, test_company, test_user):
        """Test creating a new referral code."""
        from datetime import datetime, timedelta
        
        referral = ReferralCode(
            code="TESTCODE123",
            company_id=test_company.id,
            creator_user_id=test_user.id,
            max_uses=5,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db_session.add(referral)
        db_session.commit()
        
        # Retrieve the referral code from the database
        db_referral = db_session.query(ReferralCode).filter(
            ReferralCode.code == "TESTCODE123"
        ).first()
        
        assert db_referral is not None
        assert db_referral.code == "TESTCODE123"
        assert db_referral.company_id == test_company.id
        assert db_referral.creator_user_id == test_user.id
        assert db_referral.max_uses == 5
        assert db_referral.current_uses == 0  # Default value
        assert db_referral.is_active == True  # Default value
    
    def test_referral_code_relationships(self, db_session, test_company, test_user):
        """Test the relationships for ReferralCode."""
        referral = ReferralCode(
            code="RELTEST456",
            company_id=test_company.id,
            creator_user_id=test_user.id,
            max_uses=10
        )
        db_session.add(referral)
        db_session.commit()
        
        # Verify the relationships
        db_referral = db_session.query(ReferralCode).filter(
            ReferralCode.code == "RELTEST456"
        ).first()
        
        assert db_referral.company is not None
        assert db_referral.company.id == test_company.id
        assert db_referral.creator is not None
        assert db_referral.creator.id == test_user.id
        
        # Verify the reverse relationship
        assert db_referral in test_company.referral_codes
    
    def test_update_referral_code(self, db_session, test_company):
        """Test updating a referral code."""
        referral = ReferralCode(
            code="UPDATE789",
            company_id=test_company.id,
            max_uses=3
        )
        db_session.add(referral)
        db_session.commit()
        
        # Update referral code attributes
        referral.current_uses = 2
        referral.is_active = False
        db_session.commit()
        
        # Retrieve the updated referral code
        updated_referral = db_session.query(ReferralCode).filter(
            ReferralCode.id == referral.id
        ).first()
        
        assert updated_referral.current_uses == 2
        assert updated_referral.is_active == False
    
    def test_delete_referral_code(self, db_session, test_company):
        """Test deleting a referral code."""
        referral_to_delete = ReferralCode(
            code="DELETE000",
            company_id=test_company.id,
            max_uses=1
        )
        db_session.add(referral_to_delete)
        db_session.commit()
        
        # Verify referral code exists
        referral_id = referral_to_delete.id
        assert db_session.query(ReferralCode).filter(
            ReferralCode.id == referral_id
        ).first() is not None
        
        # Delete the referral code
        db_session.delete(referral_to_delete)
        db_session.commit()
        
        # Verify referral code no longer exists
        assert db_session.query(ReferralCode).filter(
            ReferralCode.id == referral_id
        ).first() is None

class TestAPIKeyModel:
    def test_create_api_key(self, db_session, test_company):
        """Test creating a new API key."""
        api_key = APIKey(
            company_id=test_company.id,
            api_key="test_api_key_12345",
            name="Test API Key",
            rate_limit=200
        )
        db_session.add(api_key)
        db_session.commit()
        
        # Retrieve the API key from the database
        db_api_key = db_session.query(APIKey).filter(
            APIKey.api_key == "test_api_key_12345"
        ).first()
        
        assert db_api_key is not None
        assert db_api_key.company_id == test_company.id
        assert db_api_key.api_key == "test_api_key_12345"
        assert db_api_key.name == "Test API Key"
        assert db_api_key.rate_limit == 200
        assert db_api_key.is_active == True  # Default value
    
    def test_api_key_company_relationship(self, db_session, test_company):
        """Test the relationship between APIKey and Company."""
        api_key = APIKey(
            company_id=test_company.id,
            api_key="relationship_key_67890",
            name="Relationship Test Key"
        )
        db_session.add(api_key)
        db_session.commit()
        
        # Verify the relationship
        db_api_key = db_session.query(APIKey).filter(
            APIKey.api_key == "relationship_key_67890"
        ).first()
        
        assert db_api_key.company is not None
        assert db_api_key.company.id == test_company.id
        
        # Verify the reverse relationship
        assert db_api_key in test_company.api_keys
    
    def test_update_api_key(self, db_session, test_company):
        """Test updating an API key."""
        api_key = APIKey(
            company_id=test_company.id,
            api_key="update_key_abcde",
            name="Update Test Key",
            rate_limit=100
        )
        db_session.add(api_key)
        db_session.commit()
        
        # Update API key attributes
        api_key.name = "Updated Key Name"
        api_key.rate_limit = 150
        api_key.is_active = False
        db_session.commit()
        
        # Retrieve the updated API key
        updated_api_key = db_session.query(APIKey).filter(
            APIKey.id == api_key.id
        ).first()
        
        assert updated_api_key.name == "Updated Key Name"
        assert updated_api_key.rate_limit == 150
        assert updated_api_key.is_active == False
    
    def test_delete_api_key(self, db_session, test_company):
        """Test deleting an API key."""
        api_key_to_delete = APIKey(
            company_id=test_company.id,
            api_key="delete_key_fghij",
            name="Delete Test Key"
        )
        db_session.add(api_key_to_delete)
        db_session.commit()
        
        # Verify API key exists
        api_key_id = api_key_to_delete.id
        assert db_session.query(APIKey).filter(
            APIKey.id == api_key_id
        ).first() is not None
        
        # Delete the API key
        db_session.delete(api_key_to_delete)
        db_session.commit()
        
        # Verify API key no longer exists
        assert db_session.query(APIKey).filter(
            APIKey.id == api_key_id
        ).first() is None
