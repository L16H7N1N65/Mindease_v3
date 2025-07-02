"""
Authentication service for user management.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.models.auth import Permission, Role, User, user_role, UserRole

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication and user management."""
    
    def __init__(self, db: Session):
        """
        Initialize the authentication service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def authenticate(self, email: str, password: str) -> Optional[Tuple[User, str]]:
        """
        Authenticate a user and generate an access token.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (user, access_token) if authentication succeeds, None otherwise
        """
        try:
            # Find user by email
            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                logger.info(f"Authentication failed: User with email {email} not found")
                return None
            
            # Check password
            if not verify_password(password, user.password_hash):
                logger.info(f"Authentication failed: Invalid password for user {email}")
                return None
            
            # Check if user is active
            if not user.is_active:
                logger.info(f"Authentication failed: User {email} is inactive")
                return None
            
            # Generate access token
            access_token = create_access_token(
                subject=user.id,
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            
            return user, access_token
        
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return None
    
    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        role_id: Optional[int] = None,
        terms_accepted: bool = False
    ) -> Optional[User]:
        """
        Register a new user.
        
        Args:
            username: Username
            email: Email address
            password: Password
            role_id: Optional role ID
            terms_accepted: Whether terms are accepted
            
        Returns:
            Created user or None if registration fails
        """
        try:
            # Check if email already exists
            existing_user = self.db.query(User).filter(User.email == email).first()
            if existing_user:
                logger.info(f"Registration failed: Email {email} already exists")
                return None
            
            # Check if username already exists
            existing_username = self.db.query(User).filter(User.username == username).first()
            if existing_username:
                logger.info(f"Registration failed: Username {username} already exists")
                return None
            
            # Check terms acceptance
            if not terms_accepted:
                logger.info("Registration failed: Terms not accepted")
                return None
            
            # Create user
            user = User(
                username=username,
                email=email,
                password_hash=get_password_hash(password),
                is_active=True,
                terms_accepted=terms_accepted,
                terms_accepted_at=datetime.utcnow() if terms_accepted else None,
                email_confirmed=False  # Requires email confirmation
            )
            self.db.add(user)
            self.db.flush()  # Get user ID
            
            # Assign role if provided
            if role_id:
                role = self.db.query(Role).filter(Role.id == role_id).first()
                if role:
                    user_role = UserRole(user_id=user.id, role_id=role.id)
                    self.db.add(user_role)
                else:
                    logger.warning(f"Role with ID {role_id} not found")
            else:
                # Assign default user role
                default_role = self.db.query(Role).filter(Role.name == "user").first()
                if default_role:
                    user_role = UserRole(user_id=user.id, role_id=default_role.id)
                    self.db.add(user_role)
                else:
                    logger.warning("Default user role not found")
            
            self.db.commit()
            return user
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during user registration: {str(e)}")
            return None
    
    def confirm_email(self, user_id: int) -> bool:
        """
        Confirm a user's email address.
        
        Args:
            user_id: User ID
            
        Returns:
            True if confirmation succeeds, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.email_confirmed = True
            self.db.commit()
            return True
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during email confirmation: {str(e)}")
            return False
    
    def get_available_roles(self) -> list:
        """
        Get all available roles.
        
        Returns:
            List of roles
        """
        try:
            return self.db.query(Role).all()
        
        except Exception as e:
            logger.error(f"Error getting available roles: {str(e)}")
            return []
    
    def get_user_permissions(self, user_id: int) -> list:
        """
        Get all permissions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of permission names
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return []
            
            permissions = set()
            for role in user.roles:
                for permission in role.permissions:
                    permissions.add(permission.name)
            
            return list(permissions)
        
        except Exception as e:
            logger.error(f"Error getting user permissions: {str(e)}")
            return []
