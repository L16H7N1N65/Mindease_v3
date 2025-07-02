"""
Social features related schemas
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# Social Post Schemas

class SocialPostBase(BaseModel):
    """Base schema for social post"""
    title: str = Field(..., max_length=200)
    content: str = Field(..., max_length=5000)
    is_anonymous: bool = False

class SocialPostCreate(SocialPostBase):
    """Schema for creating a social post"""
    tag_ids: Optional[List[int]] = None

class SocialPostUpdate(BaseModel):
    """Schema for updating a social post"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, max_length=5000)
    is_anonymous: Optional[bool] = None
    tag_ids: Optional[List[int]] = None

class SocialPostResponse(SocialPostBase):
    """Schema for social post response"""
    id: int
    user_id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Social Comment Schemas

class SocialCommentBase(BaseModel):
    """Base schema for social comment"""
    content: str = Field(..., max_length=2000)
    is_anonymous: bool = False

class SocialCommentCreate(SocialCommentBase):
    """Schema for creating a social comment"""
    parent_comment_id: Optional[int] = None

class SocialCommentUpdate(BaseModel):
    """Schema for updating a social comment"""
    content: Optional[str] = Field(None, max_length=2000)
    is_anonymous: Optional[bool] = None

class SocialCommentResponse(SocialCommentBase):
    """Schema for social comment response"""
    id: int
    post_id: int
    user_id: int
    parent_comment_id: Optional[int] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Social Tag Schemas

class SocialTagResponse(BaseModel):
    """Schema for social tag response"""
    id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Social Feed Schemas

class SocialFeedPostItem(BaseModel):
    """Schema for a post item in social feed"""
    post: SocialPostResponse
    like_count: int
    comment_count: int
    user_liked: bool

class SocialFeedResponse(BaseModel):
    """Schema for social feed response"""
    posts: List[Dict[str, Any]]
    total_count: int
    has_more: bool

