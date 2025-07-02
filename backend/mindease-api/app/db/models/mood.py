"""
Mood tracking related models for user mood entries and analytics
"""
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import relationship

from app.db.models.base import Base, TimestampMixin

class MoodEntry(Base, TimestampMixin):
    """User mood entry model"""
    __tablename__ = "mood_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mood_score = Column(Integer, nullable=False)  # 1-10 scale
    energy_level = Column(Integer, nullable=True)  # 1-10 scale
    notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="mood_entries")
    factors = relationship("MoodFactor", back_populates="mood_entry", cascade="all, delete-orphan")

class MoodFactor(Base, TimestampMixin):
    """Factors affecting mood entries"""
    __tablename__ = "mood_factors"
    
    id = Column(Integer, primary_key=True, index=True)
    mood_entry_id = Column(Integer, ForeignKey("mood_entries.id"), nullable=False)
    factor_type = Column(String(50), nullable=False)  # e.g., "sleep", "exercise", "stress"
    factor_value = Column(Float, nullable=True)  # Numeric value if applicable
    factor_note = Column(String(255), nullable=True)  # Additional notes
    
    # Relationships
    mood_entry = relationship("MoodEntry", back_populates="factors")
