"""
Organization management related schemas
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

# Organization Schemas

class OrganizationBase(BaseModel):
    """Base schema for organization"""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    organization_type: str = Field(..., description="Type of organization")
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization"""
    pass

class OrganizationUpdate(BaseModel):
    """Schema for updating an organization"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    organization_type: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None

class OrganizationResponse(OrganizationBase):
    """Schema for organization response"""
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Organization Member Schemas

class OrganizationMemberBase(BaseModel):
    """Base schema for organization member"""
    role: str = "member"

class OrganizationMemberUpdate(BaseModel):
    """Schema for updating organization member"""
    role: Optional[str] = None
    is_active: Optional[bool] = None

class OrganizationMemberResponse(OrganizationMemberBase):
    """Schema for organization member response"""
    id: int
    organization_id: int
    user_id: int
    is_active: bool = True
    joined_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# API Key Schemas

class ApiKeyBase(BaseModel):
    """Base schema for API key"""
    name: str = Field(..., max_length=100)
    permissions: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None

class ApiKeyCreate(ApiKeyBase):
    """Schema for creating an API key"""
    pass

class ApiKeyResponse(ApiKeyBase):
    """Schema for API key response"""
    id: int
    organization_id: int
    key_value: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

