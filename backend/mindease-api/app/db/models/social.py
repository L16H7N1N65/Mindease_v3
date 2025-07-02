"""
Social features related models for community interaction
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.models.base import Base, TimestampMixin

class SocialPost(Base, TimestampMixin):
    """User social post model"""
    __tablename__ = "social_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    is_anonymous = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="social_posts")
    comments = relationship("SocialComment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("SocialLike", back_populates="post", cascade="all, delete-orphan")
    tags = relationship("SocialPostTag", back_populates="post", cascade="all, delete-orphan")

class SocialComment(Base, TimestampMixin):
    """Comment on a social post"""
    __tablename__ = "social_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("social_posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_anonymous = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    post = relationship("SocialPost", back_populates="comments")
    user = relationship("User", back_populates="social_comments")
    likes = relationship("SocialLike", back_populates="comment", cascade="all, delete-orphan")

class SocialLike(Base, TimestampMixin):
    """Like on a post or comment"""
    __tablename__ = "social_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("social_posts.id"), nullable=True)
    comment_id = Column(Integer, ForeignKey("social_comments.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="social_likes")
    post = relationship("SocialPost", back_populates="likes")
    comment = relationship("SocialComment", back_populates="likes")

class SocialTag(Base, TimestampMixin):
    """Tag for categorizing social posts"""
    __tablename__ = "social_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    
    # Relationships
    posts = relationship("SocialPostTag", back_populates="tag")

class SocialPostTag(Base, TimestampMixin):
    """Association between posts and tags"""
    __tablename__ = "social_post_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("social_posts.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("social_tags.id"), nullable=False)
    
    # Relationships
    post = relationship("SocialPost", back_populates="tags")
    tag = relationship("SocialTag", back_populates="posts")
