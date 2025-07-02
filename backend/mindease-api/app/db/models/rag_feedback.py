"""
RAG Feedback Models for MindEase

Database models to store and analyze user feedback on RAG-generated responses
for continuous learning and improvement.
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.db.models.base import Base, TimestampMixin


class RAGFeedback(Base, TimestampMixin):
    """
    User feedback on RAG-generated responses.
    
    This model stores detailed feedback from users about the quality,
    relevance, and helpfulness of RAG system responses.
    """
    __tablename__ = "rag_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User and conversation context
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True),
    ForeignKey("conversations.id"), nullable=False)
    message_id = Column(UUID(as_uuid=True),
    ForeignKey("conversation_messages.id"), nullable=True)
    
    # Query and response data
    user_query = Column(Text, nullable=False)
    rag_response = Column(Text, nullable=False)
    retrieved_documents = Column(JSON, nullable=True)  # List of document IDs and scores
    
    # Feedback scores (1-5 scale)
    relevance_score = Column(Integer, nullable=True)  # How relevant was the response?
    helpfulness_score = Column(Integer, nullable=True)  # How helpful was the response?
    accuracy_score = Column(Integer, nullable=True)  # How accurate was the response?
    clarity_score = Column(Integer, nullable=True)  # How clear was the response?
    
    # Overall satisfaction
    overall_rating = Column(Integer, nullable=True)  # Overall 1-5 rating
    
    # Detailed feedback
    feedback_text = Column(Text, nullable=True)  # Free-text feedback
    feedback_category = Column(String(50), nullable=True)  # positive, negative, neutral
    
    # Specific feedback types
    is_helpful = Column(Boolean, nullable=True)
    is_accurate = Column(Boolean, nullable=True)
    is_safe = Column(Boolean, nullable=True)  # Important for mental health context
    is_empathetic = Column(Boolean, nullable=True)
    
    # Improvement suggestions
    suggested_improvement = Column(Text, nullable=True)
    missing_information = Column(Text, nullable=True)
    
    # Context metadata
    query_intent = Column(String(100), nullable=True)  # symptom_inquiry, treatment_seeking, crisis, etc.
    user_emotional_state = Column(String(50), nullable=True)  # anxious, depressed, neutral, etc.
    session_context = Column(JSON, nullable=True)  # Additional session metadata
    
    # System metadata
    model_version = Column(String(50), nullable=True)
    embedding_model = Column(String(100), nullable=True)
    retrieval_method = Column(String(50), nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="rag_feedback")
    conversation = relationship("Conversation", back_populates="feedback")
    message      = relationship("Message",       back_populates="rag_feedback")
    
    def __repr__(self):
        return f"<RAGFeedback(id={self.id}, user_id={self.user_id}, overall_rating={self.overall_rating})>"


class FeedbackAnalytics(Base, TimestampMixin):
    """
    Aggregated analytics from RAG feedback for performance monitoring.
    
    This model stores computed metrics and trends from user feedback
    to track RAG system performance over time.
    """
    __tablename__ = "feedback_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Time period for analytics
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    
    # Aggregated metrics
    total_feedback_count = Column(Integer, default=0)
    avg_relevance_score = Column(Float, nullable=True)
    avg_helpfulness_score = Column(Float, nullable=True)
    avg_accuracy_score = Column(Float, nullable=True)
    avg_clarity_score = Column(Float, nullable=True)
    avg_overall_rating = Column(Float, nullable=True)
    
    # Response quality metrics
    positive_feedback_rate = Column(Float, nullable=True)  # % of positive feedback
    negative_feedback_rate = Column(Float, nullable=True)  # % of negative feedback
    safety_concern_rate = Column(Float, nullable=True)  # % flagged as unsafe
    
    # Performance by category
    category_performance = Column(JSON, nullable=True)  # Performance by query intent
    emotional_state_performance = Column(JSON, nullable=True)  # Performance by user emotional state
    
    # Improvement tracking
    common_complaints = Column(JSON, nullable=True)  # Most common negative feedback themes
    improvement_suggestions = Column(JSON, nullable=True)  # Aggregated improvement suggestions
    
    # System performance
    avg_response_time_ms = Column(Float, nullable=True)
    retrieval_accuracy = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<FeedbackAnalytics(period={self.period_type}, avg_rating={self.avg_overall_rating})>"


class FeedbackTrainingData(Base, TimestampMixin):
    """
    Processed feedback data for training and fine-tuning models.
    
    This model stores feedback data in a format suitable for machine learning
    training, including features and labels derived from user feedback.
    """
    __tablename__ = "feedback_training_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Source feedback
    feedback_id = Column(UUID(as_uuid=True), ForeignKey("rag_feedback.id"), nullable=False)
    
    # Training features
    query_embedding = Column(JSON, nullable=True)  # Serialized embedding vector
    response_embedding = Column(JSON, nullable=True)  # Serialized embedding vector
    document_embeddings = Column(JSON, nullable=True)  # Retrieved document embeddings
    
    # Feature engineering
    query_length = Column(Integer, nullable=True)
    response_length = Column(Integer, nullable=True)
    semantic_similarity_score = Column(Float, nullable=True)
    retrieval_confidence = Column(Float, nullable=True)
    
    # Labels for training
    quality_label = Column(String(20), nullable=True)  # high, medium, low
    binary_label = Column(Boolean, nullable=True)  # good/bad response
    regression_target = Column(Float, nullable=True)  # Normalized score 0-1
    
    # Training metadata
    training_set = Column(String(50), nullable=True)  # train, validation, test
    data_quality = Column(String(20), nullable=True)  # high, medium, low
    is_used_for_training = Column(Boolean, default=False)
    
    # Relationships
    feedback = relationship("RAGFeedback", backref="training_data")
    
    def __repr__(self):
        return f"<FeedbackTrainingData(id={self.id}, quality_label={self.quality_label})>"


class ResponseImprovement(Base, TimestampMixin):
    """
    Track improvements made to responses based on feedback.
    
    This model stores information about how responses were improved
    based on user feedback and the impact of those improvements.
    """
    __tablename__ = "response_improvements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Original feedback that triggered improvement
    feedback_id = Column(UUID(as_uuid=True), ForeignKey("rag_feedback.id"), nullable=False)
    
    # Improvement details
    improvement_type = Column(String(50), nullable=False)  # document_update, model_retrain, prompt_engineering
    improvement_description = Column(Text, nullable=False)
    
    # Implementation details
    implemented_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    implementation_date = Column(DateTime, default=datetime.utcnow)
    
    # Impact measurement
    before_metrics = Column(JSON, nullable=True)  # Metrics before improvement
    after_metrics = Column(JSON, nullable=True)  # Metrics after improvement
    impact_score = Column(Float, nullable=True)  # Measured improvement impact
    
    # Status tracking
    status = Column(String(20), default="planned")  # planned, implemented, validated, rolled_back
    validation_feedback_count = Column(Integer, default=0)
    
    # Relationships
    feedback = relationship("RAGFeedback", backref="improvements")
    implementer = relationship("User", foreign_keys=[implemented_by])
    
    def __repr__(self):
        return f"<ResponseImprovement(id={self.id}, type={self.improvement_type}, status={self.status})>"

