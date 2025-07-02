"""
Security utilities for the MindEase API.
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.db.models import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        plain_password: Plain text password
        password_hash: Hashed password
        
    Returns:
        True if password matches hash, False otherwise
    """
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    """
    Hash password.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(subject: Union[str, int], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token with subject.
    
    Args:
        subject: Subject (user ID) to encode in token
        expires_delta: Token expiration time
        
    Returns:
        JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from JWT token.
    
    Args:
        token: JWT token
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            logger.warning("Token missing sub field")
            raise credentials_exception
            
    except JWTError as e:
        logger.warning(f"JWT error: {str(e)}")
        raise credentials_exception
        
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        logger.warning(f"User not found: {user_id}")
        raise credentials_exception
        
    if not user.is_active:
        logger.warning(f"Inactive user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
        
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


def check_user_role(user: User, required_role: str) -> bool:
    """
    Check if user has required role.
    
    Args:
        user: User object
        required_role: Required role name
        
    Returns:
        True if user has role, False otherwise
    """
    return any(role.name == required_role for role in user.roles)


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current admin user.
    
    Args:
        current_user: Current user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is not an admin
    """
    if not (current_user.is_admin or check_user_role(current_user, "admin")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def check_user_permissions(user: User, resource: str, action: str) -> bool:
    """
    Check if user has permission to perform action on resource.
    
    Args:
        user: User object
        resource: Resource name
        action: Action to perform (create, read, update, delete)
        
    Returns:
        True if user has permission, False otherwise
    """
    # Admin users have all permissions
    if user.is_admin or check_user_role(user, "admin"):
        return True
    
    # Check role-based permissions
    for role in user.roles:
        for permission in role.permissions:
            if permission.resource == resource:
                if action == "create" and permission.can_create:
                    return True
                elif action == "read" and permission.can_read:
                    return True
                elif action == "update" and permission.can_update:
                    return True
                elif action == "delete" and permission.can_delete:
                    return True
    
    return False
