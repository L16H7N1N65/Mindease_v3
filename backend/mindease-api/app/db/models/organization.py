"""
Organization and API related models for multi-tenant support
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Numeric, JSON
from sqlalchemy.orm import relationship

from app.db.models.base import Base, TimestampMixin

class Organization(Base, TimestampMixin):
    """Organization model for multi-tenant support"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    logo_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    users = relationship("User", back_populates="organization", foreign_keys="User.organization_id")
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="organization", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="organization", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="organization", cascade="all, delete-orphan")
    users = relationship(
        "User",
        back_populates="organization",
        cascade="all, delete-orphan"
    )

class OrganizationMember(Base, TimestampMixin):
    """Organization membership model"""
    __tablename__ = "organization_members"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False)  # e.g., "admin", "member", "viewer"
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="members", foreign_keys=[organization_id])
    user = relationship("User", back_populates="memberships", foreign_keys=[user_id])


class ApiKey(Base, TimestampMixin):
    """API key for organization access"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    key_name = Column(String(100), nullable=False)
    key_prefix = Column(String(10), nullable=False)
    key_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="api_keys", foreign_keys=[organization_id])


class Subscription(Base, TimestampMixin):
    """Organization subscription plans"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="subscriptions", foreign_keys=[organization_id])
    plan = relationship("Plan", back_populates="subscriptions", foreign_keys=[plan_id])


class Plan(Base, TimestampMixin):
    """Subscription plan definitions"""
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)  # Fixed: Added Numeric type
    max_users = Column(Integer, nullable=False)
    max_documents = Column(Integer, nullable=False)
    features = Column(JSON)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan", cascade="all, delete-orphan")