"""
Authentication related models including User, Role, Profile, and Preference
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, func
from sqlalchemy.orm import relationship

from app.db.models.base import Base, TimestampMixin

# Association table for many-to-many relationship between users and roles
user_role = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True)
)

class User(Base, TimestampMixin):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    email_confirmed = Column(Boolean, default=False)
    email_confirmed_at = Column(DateTime, nullable=True)
    terms_accepted = Column(Boolean, default=False)
    terms_accepted_at = Column(DateTime, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Relationships - using string references to avoid circular imports
    roles = relationship("Role", secondary=user_role, back_populates="users")
    profile = relationship("Profile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    preference = relationship("Preference", uselist=False, back_populates="user", cascade="all, delete-orphan")
    mood_entries = relationship("MoodEntry", back_populates="user", cascade="all, delete-orphan")
    therapy_sessions = relationship("TherapySession", back_populates="user", cascade="all, delete-orphan")
    social_posts = relationship("SocialPost", back_populates="user", cascade="all, delete-orphan")
    social_comments = relationship("SocialComment", back_populates="user", cascade="all, delete-orphan")
    social_likes    = relationship("SocialLike",  back_populates="user",
    cascade="all, delete-orphan")
    memberships = relationship("OrganizationMember", back_populates="user")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    chat_analytics = relationship("ChatAnalytics", back_populates="user", cascade="all, delete-orphan")
    chat_feedback = relationship("ChatFeedback", back_populates="user", cascade="all, delete-orphan")
    chat_settings = relationship("ChatSettings", uselist=False, back_populates="user", cascade="all, delete-orphan")
    organization = relationship("Organization", back_populates="users",
    foreign_keys=[organization_id])
    rag_feedback = relationship(
        "RAGFeedback",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    

class Role(Base, TimestampMixin):
    """Role model for role-based access control"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    
    # Relationships
    users = relationship("User", secondary=user_role, back_populates="roles")
    permissions = relationship("Permission", back_populates="role", cascade="all, delete-orphan")

    

class Permission(Base, TimestampMixin):
    """Permission model for CRUD operations on resources"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    resource = Column(String(50), nullable=False)
    can_create = Column(Boolean, default=False)
    can_read = Column(Boolean, default=True)
    can_update = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    
    # Relationships
    role = relationship("Role", back_populates="permissions")

class Profile(Base, TimestampMixin):
    """User profile information"""
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    bio = Column(String(500), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="profile")

class Preference(Base, TimestampMixin):
    """User preferences for application settings"""
    __tablename__ = "preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    theme = Column(String(20), default="light", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    notifications_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="preference")
