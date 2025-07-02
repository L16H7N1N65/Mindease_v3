"""
Authentication router for user registration, login, and profile management
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from app.db.session import get_db


from app.db.models import User, Role, Profile, Preference
from app.schemas.auth import (
    UserCreate, UserResponse, UserUpdate, Token,
    ProfileCreate, ProfileResponse, ProfileUpdate,
    PreferenceCreate, PreferenceResponse, PreferenceUpdate,
    RoleResponse
)
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user,
    get_current_active_user
)
from app.core.config import settings

# router = APIRouter(
#     prefix="/auth",
#     tags=["authentication"]
# )
# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=[("auth")])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with username, email, password, and role.
    
    - Validates password confirmation
    - Ensures terms are accepted
    - Creates user with specified role (defaults to authenticated user)
    - Creates default profile and preferences
    """
    # Check if user with email already exists
    db_user_email = db.query(User).filter(User.email == user_in.email).first()
    if db_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if user with username already exists
    db_user_username = db.query(User).filter(User.username == user_in.username).first()
    if db_user_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Get role
    role = db.query(Role).filter(Role.id == user_in.role_id).first()
    if not role:
        # Default to authenticated user role if specified role doesn't exist
        role = db.query(Role).filter(Role.name == "authenticated").first()
        if not role:
            # Create authenticated role if it doesn't exist
            role = Role(name="authenticated", description="Regular authenticated user")
            db.add(role)
            db.commit()
            db.refresh(role)
    
    # Create new user
    password_hash = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        is_active=user_in.is_active,
        terms_accepted=user_in.accept_terms,
        terms_accepted_at=datetime.utcnow() if user_in.accept_terms else None
    )
    db_user.roles.append(role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create profile
    profile = Profile(
        user_id=db_user.id,
        first_name=None,
        last_name=None
    )
    db.add(profile)
    
    # Create preferences
    preference = Preference(
        user_id=db_user.id,
        theme="light",
        language="en",
        notifications_enabled=True,
        email_notifications=True
    )
    db.add(preference)
    
    db.commit()
    db.refresh(db_user)
    return UserResponse.model_validate(db_user, from_attributes=True)
    #return db_user

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    - Authenticates user with email/username and password
    - Returns JWT access token
    """
    # Check if user exists by email or username
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token, token_type="bearer")
    #return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information.
    
    - Returns detailed user information including profile and preferences
    - Requires authentication
    """
    #return current_user
    return UserResponse.model_validate(current_user, from_attributes=True)

@router.put("/me", response_model=UserResponse)
async def update_user(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information.
    
    - Updates user fields (email, username, is_active)
    - Requires authentication
    """
    # Check if email is being changed and is already taken
    if user_in.email and user_in.email != current_user.email:
        db_user = db.query(User).filter(User.email == user_in.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Check if username is being changed and is already taken
    if user_in.username and user_in.username != current_user.username:
        db_user = db.query(User).filter(User.username == user_in.username).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update user fields
    for field, value in user_in.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user, from_attributes=True)
    #return current_user

@router.get("/me/profile", response_model=ProfileResponse)
async def read_user_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get current user profile.
    
    - Returns user profile information
    - Requires authentication
    """
    if not current_user.profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return current_user.profile

@router.put("/me/profile", response_model=ProfileResponse)
async def update_user_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile.
    
    - Updates profile fields
    - Creates profile if it doesn't exist
    - Requires authentication
    """
    if not current_user.profile:
        # Create profile if it doesn't exist
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(current_user)
    
    # Update profile fields
    for field, value in profile_in.dict(exclude_unset=True).items():
        setattr(current_user.profile, field, value)
    
    db.add(current_user.profile)
    db.commit()
    db.refresh(current_user.profile)
    
    return current_user.profile

@router.get("/me/preferences", response_model=PreferenceResponse)
async def read_user_preferences(current_user: User = Depends(get_current_active_user)):
    """
    Get current user preferences.
    
    - Returns user preference settings
    - Requires authentication
    """
    if not current_user.preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found"
        )
    return current_user.preference

@router.put("/me/preferences", response_model=PreferenceResponse)
async def update_user_preferences(
    preference_in: PreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user preferences.
    
    - Updates preference settings
    - Creates preferences if they don't exist
    - Requires authentication
    """
    if not current_user.preference:
        # Create preferences if they don't exist
        preference = Preference(
            user_id=current_user.id,
            theme="light",
            language="en",
            notifications_enabled=True,
            email_notifications=True
        )
        db.add(preference)
        db.commit()
        db.refresh(current_user)
    
    # Update preference fields
    for field, value in preference_in.dict(exclude_unset=True).items():
        setattr(current_user.preference, field, value)
    
    db.add(current_user.preference)
    db.commit()
    db.refresh(current_user.preference)
    
    return current_user.preference

@router.get("/me/roles", response_model=List[RoleResponse])
async def read_user_roles(current_user: User = Depends(get_current_active_user)):
    """
    Get current user roles.
    
    - Returns list of user roles with permissions
    - Requires authentication
    """
    return current_user.roles
