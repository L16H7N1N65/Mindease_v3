"""
RAG Feedback Schemas for API requests and responses.

Pydantic schemas for handling RAG feedback data in API endpoints.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class FeedbackCategory(str, Enum):
    """Feedback category enumeration."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class QueryIntent(str, Enum):
    """Query intent classification."""
    SYMPTOM_INQUIRY = "symptom_inquiry"
    TREATMENT_SEEKING = "treatment_seeking"
    CRISIS_SUPPORT = "crisis_support"
    INFORMATION_SEEKING = "information_seeking"
    COPING_STRATEGIES = "coping_strategies"
    MEDICATION_INQUIRY = "medication_inquiry"
    THERAPY_QUESTIONS = "therapy_questions"
    GENERAL_SUPPORT = "general_support"


class EmotionalState(str, Enum):
    """User emotional state classification."""
    ANXIOUS = "anxious"
    DEPRESSED = "depressed"
    STRESSED = "stressed"
    CALM = "calm"
    HOPEFUL = "hopeful"
    CONFUSED = "confused"
    ANGRY = "angry"
    NEUTRAL = "neutral"


class ImprovementType(str, Enum):
    """Type of improvement made based on feedback."""
    DOCUMENT_UPDATE = "document_update"
    MODEL_RETRAIN = "model_retrain"
    PROMPT_ENGINEERING = "prompt_engineering"
    RETRIEVAL_TUNING = "retrieval_tuning"
    SAFETY_ENHANCEMENT = "safety_enhancement"


# Request Schemas

class RAGFeedbackCreate(BaseModel):
    """Schema for creating new RAG feedback."""
    
    # Required fields
    user_query: str = Field(..., min_length=1, max_length=2000, description="The user's original query")
    rag_response: str = Field(..., min_length=1, max_length=5000, description="The RAG system's response")
    
    # Optional context
    conversation_id: Optional[str] = Field(None, description="ID of the conversation")
    message_id: Optional[str] = Field(None, description="ID of the specific message")
    
    # Feedback scores (1-5 scale)
    relevance_score: Optional[int] = Field(None, ge=1, le=5, description="Relevance rating (1-5)")
    helpfulness_score: Optional[int] = Field(None, ge=1, le=5, description="Helpfulness rating (1-5)")
    accuracy_score: Optional[int] = Field(None, ge=1, le=5, description="Accuracy rating (1-5)")
    clarity_score: Optional[int] = Field(None, ge=1, le=5, description="Clarity rating (1-5)")
    overall_rating: Optional[int] = Field(None, ge=1, le=5, description="Overall rating (1-5)")
    
    # Boolean feedback
    is_helpful: Optional[bool] = Field(None, description="Was the response helpful?")
    is_accurate: Optional[bool] = Field(None, description="Was the response accurate?")
    is_safe: Optional[bool] = Field(None, description="Was the response safe and appropriate?")
    is_empathetic: Optional[bool] = Field(None, description="Was the response empathetic?")
    
    # Detailed feedback
    feedback_text: Optional[str] = Field(None, max_length=1000, description="Free-text feedback")
    feedback_category: Optional[FeedbackCategory] = Field(None, description="Feedback category")
    
    # Improvement suggestions
    suggested_improvement: Optional[str] = Field(None, max_length=500, description="Suggested improvements")
    missing_information: Optional[str] = Field(None, max_length=500, description="What information was missing?")
    
    # Context metadata
    query_intent: Optional[QueryIntent] = Field(None, description="Intent of the user's query")
    user_emotional_state: Optional[EmotionalState] = Field(None, description="User's emotional state")
    session_context: Optional[Dict[str, Any]] = Field(None, description="Additional session context")
    
    @validator('feedback_text')
    def validate_feedback_text(cls, v):
        if v and len(v.strip()) == 0:
            return None
        return v


class QuickFeedback(BaseModel):
    """Schema for quick thumbs up/down feedback."""
    
    user_query: str = Field(..., min_length=1, max_length=2000)
    rag_response: str = Field(..., min_length=1, max_length=5000)
    is_helpful: bool = Field(..., description="Thumbs up (True) or thumbs down (False)")
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None


class DetailedFeedback(BaseModel):
    """Schema for detailed feedback with all metrics."""
    
    user_query: str = Field(..., min_length=1, max_length=2000)
    rag_response: str = Field(..., min_length=1, max_length=5000)
    
    # All rating scores required for detailed feedback
    relevance_score: int = Field(..., ge=1, le=5)
    helpfulness_score: int = Field(..., ge=1, le=5)
    accuracy_score: int = Field(..., ge=1, le=5)
    clarity_score: int = Field(..., ge=1, le=5)
    overall_rating: int = Field(..., ge=1, le=5)
    
    # Required safety assessment
    is_safe: bool = Field(..., description="Safety assessment required")
    
    # Optional detailed fields
    feedback_text: Optional[str] = Field(None, max_length=1000)
    suggested_improvement: Optional[str] = Field(None, max_length=500)
    query_intent: Optional[QueryIntent] = None
    user_emotional_state: Optional[EmotionalState] = None


# Response Schemas

class RAGFeedbackResponse(BaseModel):
    """Schema for RAG feedback response."""
    
    id: str
    user_id: str
    user_query: str
    rag_response: str
    
    # Scores
    relevance_score: Optional[int]
    helpfulness_score: Optional[int]
    accuracy_score: Optional[int]
    clarity_score: Optional[int]
    overall_rating: Optional[int]
    
    # Boolean feedback
    is_helpful: Optional[bool]
    is_accurate: Optional[bool]
    is_safe: Optional[bool]
    is_empathetic: Optional[bool]
    
    # Text feedback
    feedback_text: Optional[str]
    feedback_category: Optional[str]
    suggested_improvement: Optional[str]
    missing_information: Optional[str]
    
    # Context
    query_intent: Optional[str]
    user_emotional_state: Optional[str]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackAnalyticsResponse(BaseModel):
    """Schema for feedback analytics response."""
    
    id: str
    period_start: datetime
    period_end: datetime
    period_type: str
    
    # Metrics
    total_feedback_count: int
    avg_relevance_score: Optional[float]
    avg_helpfulness_score: Optional[float]
    avg_accuracy_score: Optional[float]
    avg_clarity_score: Optional[float]
    avg_overall_rating: Optional[float]
    
    # Rates
    positive_feedback_rate: Optional[float]
    negative_feedback_rate: Optional[float]
    safety_concern_rate: Optional[float]
    
    # Performance data
    category_performance: Optional[Dict[str, Any]]
    emotional_state_performance: Optional[Dict[str, Any]]
    common_complaints: Optional[List[str]]
    improvement_suggestions: Optional[List[str]]
    
    class Config:
        from_attributes = True


class FeedbackSummary(BaseModel):
    """Schema for feedback summary statistics."""
    
    total_feedback: int
    avg_rating: float
    positive_rate: float
    negative_rate: float
    safety_concerns: int
    
    # Recent trends
    recent_feedback_count: int
    rating_trend: str  # "improving", "declining", "stable"
    
    # Top issues
    top_complaints: List[str]
    top_suggestions: List[str]


class ResponseImprovementCreate(BaseModel):
    """Schema for creating response improvements."""
    
    feedback_id: str = Field(..., description="ID of the feedback that triggered this improvement")
    improvement_type: ImprovementType = Field(..., description="Type of improvement")
    improvement_description: str = Field(..., min_length=10, max_length=1000, description="Description of the improvement")
    
    # Optional implementation details
    before_metrics: Optional[Dict[str, Any]] = Field(None, description="Metrics before improvement")
    expected_impact: Optional[str] = Field(None, max_length=500, description="Expected impact description")


class ResponseImprovementResponse(BaseModel):
    """Schema for response improvement response."""
    
    id: str
    feedback_id: str
    improvement_type: str
    improvement_description: str
    
    # Implementation details
    implemented_by: Optional[str]
    implementation_date: Optional[datetime]
    status: str
    
    # Impact measurement
    before_metrics: Optional[Dict[str, Any]]
    after_metrics: Optional[Dict[str, Any]]
    impact_score: Optional[float]
    validation_feedback_count: int
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Analytics and Reporting Schemas

class FeedbackTrends(BaseModel):
    """Schema for feedback trends over time."""
    
    period: str
    data_points: List[Dict[str, Any]]  # Time series data
    trend_direction: str  # "up", "down", "stable"
    trend_strength: float  # 0-1 indicating strength of trend


class CategoryPerformance(BaseModel):
    """Schema for performance by category."""
    
    category: str
    feedback_count: int
    avg_rating: float
    positive_rate: float
    common_issues: List[str]
    improvement_opportunities: List[str]


class UserFeedbackHistory(BaseModel):
    """Schema for user's feedback history."""
    
    user_id: str
    total_feedback_given: int
    avg_rating_given: float
    feedback_frequency: str  # "high", "medium", "low"
    recent_feedback: List[RAGFeedbackResponse]
    
    # User patterns
    preferred_query_types: List[str]
    common_emotional_states: List[str]
    feedback_quality: str  # "detailed", "basic", "minimal"

