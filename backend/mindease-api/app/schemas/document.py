"""
Document management related schemas
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# Document Schemas

class DocumentBase(BaseModel):
    """Base schema for document"""
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class DocumentUpdate(BaseModel):
    """Schema for updating document metadata"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    tags: Optional[str] = None  # Comma-separated string that gets converted to list

class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: int
    user_id: int
    filename: str
    file_size: int
    mime_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Document Sharing Schemas

class DocumentShare(BaseModel):
    """Schema for document sharing"""
    expires_at: Optional[datetime] = None
    permissions: str = "read"  # read, write, admin

