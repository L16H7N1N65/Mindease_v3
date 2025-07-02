"""
Chat-related schemas for RAG conversations.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Schema for incoming chat messages."""
    
    content: str = Field(..., description="Message content from user")
    language: Optional[str] = Field("en", description="Response language (en/fr)")
    include_mood_context: bool = Field(True, description="Include user's mood data in context")
    include_therapy_context: bool = Field(True, description="Include therapy progress in context")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID")
    
    class Config:
        from_attributes = True


class DocumentSource(BaseModel):
    """Schema for document sources in chat responses."""
    
    title: str = Field(..., description="Document title")
    category: str = Field(..., description="Document category")
    similarity: float = Field(..., description="Similarity score (0-1)")
    source: str = Field(..., description="Document source")
    
    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Schema for chat responses with RAG context."""
    
    id: str = Field(..., description="Response ID")
    content: str = Field(..., description="Generated response content")
    sources: List[DocumentSource] = Field(default=[], description="Source documents used")
    user_context: Dict[str, Any] = Field(default={}, description="User context used")
    crisis_detected: bool = Field(False, description="Whether crisis was detected")
    timestamp: datetime = Field(..., description="Response timestamp")
    language: str = Field("en", description="Response language")
    
    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    """Schema for conversation summary."""
    
    user_id: int = Field(..., description="User ID")
    message_count: int = Field(..., description="Total messages in conversation")
    user_messages: int = Field(..., description="Number of user messages")
    assistant_messages: int = Field(..., description="Number of assistant messages")
    first_message: Optional[datetime] = Field(None, description="Timestamp of first message")
    last_message: Optional[datetime] = Field(None, description="Timestamp of last message")
    recent_topics: List[str] = Field(default=[], description="Recent conversation topics")
    
    class Config:
        from_attributes = True


class DocumentSearchRequest(BaseModel):
    """Schema for document search requests."""
    
    query: str = Field(..., description="Search query")
    limit: int = Field(5, description="Maximum number of results", ge=1, le=20)
    similarity_threshold: float = Field(0.7, description="Minimum similarity score", ge=0.0, le=1.0)
    category_filter: Optional[str] = Field(None, description="Filter by document category")
    
    class Config:
        from_attributes = True


class DocumentResult(BaseModel):
    """Schema for document search results."""
    
    id: int = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    source: str = Field(..., description="Document source")
    category: str = Field(..., description="Document category")
    similarity: float = Field(..., description="Similarity score")
    created_at: datetime = Field(..., description="Document creation timestamp")
    updated_at: datetime = Field(..., description="Document update timestamp")
    metadata: Dict[str, str] = Field(default={}, description="Document metadata")
    
    class Config:
        from_attributes = True


class DocumentSearchResponse(BaseModel):
    """Schema for document search responses."""
    
    query: str = Field(..., description="Original search query")
    documents: List[DocumentResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Number of results returned")
    filters_applied: Optional[Dict] = Field(None, description="Filters that were applied")
    timestamp: datetime = Field(..., description="Search timestamp")
    
    class Config:
        from_attributes = True


class ConversationMessage(BaseModel):
    """Schema for individual conversation messages."""
    
    id: int = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    user_id: int = Field(..., description="User ID")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    sources: Optional[List[DocumentSource]] = Field(None, description="Sources for assistant messages")
    crisis_detected: bool = Field(False, description="Whether crisis was detected")
    timestamp: datetime = Field(..., description="Message timestamp")
    
    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Schema for creating new conversations."""
    
    title: Optional[str] = Field(None, description="Conversation title")
    language: str = Field("en", description="Conversation language")
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Schema for conversation responses."""
    
    id: str = Field(..., description="Conversation ID")
    user_id: int = Field(..., description="User ID")
    title: Optional[str] = Field(None, description="Conversation title")
    language: str = Field(..., description="Conversation language")
    message_count: int = Field(..., description="Number of messages")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ChatAnalytics(BaseModel):
    """Schema for chat analytics."""
    
    user_id: int = Field(..., description="User ID")
    total_conversations: int = Field(..., description="Total number of conversations")
    total_messages: int = Field(..., description="Total messages sent")
    avg_messages_per_conversation: float = Field(..., description="Average messages per conversation")
    crisis_events: int = Field(..., description="Number of crisis events detected")
    most_used_categories: List[str] = Field(..., description="Most frequently accessed document categories")
    language_preference: str = Field(..., description="Preferred language")
    last_activity: datetime = Field(..., description="Last chat activity")
    
    class Config:
        from_attributes = True


class ChatFeedback(BaseModel):
    """Schema for chat feedback."""
    
    message_id: str = Field(..., description="Message ID being rated")
    rating: int = Field(..., description="Rating (1-5)", ge=1, le=5)
    feedback_text: Optional[str] = Field(None, description="Optional feedback text")
    helpful_sources: List[int] = Field(default=[], description="IDs of helpful source documents")
    
    class Config:
        from_attributes = True


class ChatSettings(BaseModel):
    """Schema for user chat settings."""
    
    language: str = Field("en", description="Preferred language")
    include_mood_context: bool = Field(True, description="Include mood context by default")
    include_therapy_context: bool = Field(True, description="Include therapy context by default")
    crisis_alerts: bool = Field(True, description="Enable crisis detection alerts")
    conversation_memory: bool = Field(True, description="Enable conversation memory")
    
    class Config:
        from_attributes = True

