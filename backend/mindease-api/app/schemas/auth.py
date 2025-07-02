"""
Authentication schemas for request validation and response serialization
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator

class PermissionBase(BaseModel):
    """Base schema for permission"""
    resource: str
    can_create: bool = False
    can_read: bool = True
    can_update: bool = False
    can_delete: bool = False

class PermissionCreate(PermissionBase):
    """Schema for creating a permission"""
    role_id: int

class PermissionUpdate(BaseModel):
    """Schema for updating a permission"""
    resource: Optional[str] = None
    can_create: Optional[bool] = None
    can_read: Optional[bool] = None
    can_update: Optional[bool] = None
    can_delete: Optional[bool] = None

class PermissionResponse(PermissionBase):
    """Schema for permission response"""
    id: int
    role_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    """Base schema for role"""
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    """Schema for creating a role"""
    pass

class RoleUpdate(BaseModel):
    """Schema for updating a role"""
    name: Optional[str] = None
    description: Optional[str] = None

class RoleResponse(RoleBase):
    """Schema for role response"""
    id: int
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True

class ProfileBase(BaseModel):
    """Base schema for user profile"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None

class ProfileCreate(ProfileBase):
    """Schema for creating a profile"""
    user_id: int

class ProfileUpdate(BaseModel):
    """Schema for updating a profile"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None

class ProfileResponse(ProfileBase):
    """Schema for profile response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PreferenceBase(BaseModel):
    """Base schema for user preference"""
    theme: str = "light"
    language: str = "en"
    notifications_enabled: bool = True
    email_notifications: bool = True

class PreferenceCreate(PreferenceBase):
    """Schema for creating a preference"""
    user_id: int

class PreferenceUpdate(BaseModel):
    """Schema for updating a preference"""
    theme: Optional[str] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    email_notifications: Optional[bool] = None

class PreferenceResponse(PreferenceBase):
    """Schema for preference response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    """Base schema for user"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    is_active: bool = True

class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8)
    confirm_password: str
    accept_terms: bool = Field(..., description="User must accept terms and conditions")
    role_id: Optional[int] = 1  # Default to authenticated user role (1)

    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v
    
    @validator("accept_terms")
    def terms_accepted(cls, v):
        if not v:
            raise ValueError("Terms must be accepted")
        return v

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    email_confirmed: Optional[bool] = None

class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    email_confirmed: bool
    terms_accepted: bool
    created_at: datetime
    updated_at: datetime
    roles: List[RoleResponse] = []
    profile: Optional[ProfileResponse] = None
    preference: Optional[PreferenceResponse] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    """Schema for token payload"""
    sub: Optional[int] = None
