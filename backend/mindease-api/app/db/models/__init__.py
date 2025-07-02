"""
Main models module that imports all models for easy access
"""
from app.db.models.base import Base, TimestampMixin
from app.db.models.auth import User, Role, Permission, Profile, Preference
from app.db.models.document import Document, DocumentMetadata, DocumentEmbedding
from app.db.models.mood import MoodEntry, MoodFactor
from app.db.models.therapy import (
    TherapySession, TherapyExercise, TherapyProgram, 
    TherapyProgramActivity, TherapyProgramEnrollment, TherapyProgramProgress
)
from app.db.models.social import (
    SocialPost, SocialComment, SocialLike, 
    SocialTag, SocialPostTag
)
from app.db.models.organization import Organization, OrganizationMember, ApiKey, Subscription, Plan
from app.db.models.conversation import Conversation, Message, ChatAnalytics, ChatFeedback, ChatSettings
from app.db.models.rag_feedback import (
    RAGFeedback, FeedbackAnalytics, FeedbackTrainingData, ResponseImprovement
)

# Export all models
__all__ = [
    "Base", "TimestampMixin",
    "User", "Role", "Permission", "Profile", "Preference", 
    "Document", "DocumentMetadata", "DocumentEmbedding",
    "Subscription", "Plan",
    "MoodEntry", "MoodFactor",
    "TherapySession", "TherapyExercise", "TherapyProgram", 
    "TherapyProgramActivity", "TherapyProgramEnrollment", "TherapyProgramProgress",
    "SocialPost", "SocialComment", "SocialLike", "SocialTag", "SocialPostTag",
    "Organization", "OrganizationMember", "ApiKey", "Plan", "Subscription",
    "Conversation", "Message", "ChatAnalytics", "ChatFeedback", "ChatSettings",
    "RAGFeedback", "FeedbackAnalytics", "FeedbackTrainingData", "ResponseImprovement"
]
