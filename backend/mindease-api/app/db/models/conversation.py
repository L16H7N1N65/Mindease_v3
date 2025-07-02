"""
Conversation models for persistent chat storage.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.db.models.base import Base


class Conversation(Base):
    """Model for chat conversations."""
    
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)
    language = Column(String(10), default="en", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    feedback = relationship(
    "RAGFeedback",
    back_populates="conversation",
    cascade="all, delete-orphan"
    )
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, title={self.title})>"


class Message(Base):
    """Model for individual messages in conversations."""
    
    __tablename__ = "conversation_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # Store document sources as JSON
    user_context = Column(JSON, nullable=True)  # Store user context as JSON
    crisis_detected = Column(Boolean, default=False, nullable=False)
    language = Column(String(10), default="en", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User", back_populates="chat_messages")
    rag_feedback = relationship(
    "RAGFeedback",
    back_populates="message",
    cascade="all, delete-orphan"
    )
    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"


# Alias for backward compatibility
ConversationMessage = Message


class ChatAnalytics(Base):
    """Model for chat analytics and statistics."""
    
    __tablename__ = "chat_analytics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_messages = Column(Integer, default=0, nullable=False)
    total_conversations = Column(Integer, default=0, nullable=False)
    crisis_events = Column(Integer, default=0, nullable=False)
    avg_response_time = Column(Float, nullable=True)
    most_used_categories = Column(JSON, nullable=True)
    language_usage = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="chat_analytics")
    
    def __repr__(self):
        return f"<ChatAnalytics(id={self.id}, user_id={self.user_id}, date={self.date})>"


class ChatFeedback(Base):
    """Model for chat feedback and ratings."""
    
    __tablename__ = "chat_feedback"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("conversation_messages.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 rating
    feedback_text = Column(Text, nullable=True)
    helpful_sources = Column(JSON, nullable=True)  # Document IDs that were helpful
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    message = relationship("Message")
    user = relationship("User", back_populates="chat_feedback")
    
    def __repr__(self):
        return f"<ChatFeedback(id={self.id}, message_id={self.message_id}, rating={self.rating})>"


class ChatSettings(Base):
    """Model for user chat settings and preferences."""
    
    __tablename__ = "chat_settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    language = Column(String(10), default="en", nullable=False)
    include_mood_context = Column(Boolean, default=True, nullable=False)
    include_therapy_context = Column(Boolean, default=True, nullable=False)
    crisis_alerts = Column(Boolean, default=True, nullable=False)
    conversation_memory = Column(Boolean, default=True, nullable=False)
    max_conversation_history = Column(Integer, default=10, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="chat_settings")
    
    def __repr__(self):
        return f"<ChatSettings(id={self.id}, user_id={self.user_id}, language={self.language})>"
