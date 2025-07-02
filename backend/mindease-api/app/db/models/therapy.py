"""
Therapy related models including sessions, exercises, and progress tracking
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.models.base import Base, TimestampMixin

class TherapySession(Base, TimestampMixin):
    """Therapy session model"""
    __tablename__ = "therapy_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_type = Column(String(50), nullable=False)  # e.g., "breathing", "meditation", "cbt"
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    completed = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="therapy_sessions")
    exercises = relationship("TherapyExercise", back_populates="session", cascade="all, delete-orphan")

class TherapyExercise(Base, TimestampMixin):
    """Individual therapy exercise within a session"""
    __tablename__ = "therapy_exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("therapy_sessions.id"), nullable=False)
    exercise_type = Column(String(50), nullable=False)  # e.g., "4-7-8-breathing", "body-scan"
    duration_seconds = Column(Integer, nullable=True)
    completed = Column(Boolean, default=False)
    settings = Column(JSONB, nullable=True)  # Exercise-specific settings
    results = Column(JSONB, nullable=True)  # Exercise-specific results
    
    # Relationships
    session = relationship("TherapySession", back_populates="exercises")

class TherapyProgram(Base, TimestampMixin):
    """Predefined therapy program template"""
    __tablename__ = "therapy_programs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    duration_days = Column(Integer, nullable=False)
    target_condition = Column(String(50), nullable=True)  # e.g., "anxiety", "depression"
    is_active = Column(Boolean, default=True)
    
    # Relationships
    activities = relationship("TherapyProgramActivity", back_populates="program", cascade="all, delete-orphan")
    enrollments = relationship("TherapyProgramEnrollment", back_populates="program", cascade="all, delete-orphan")

class TherapyProgramActivity(Base, TimestampMixin):
    """Activity within a therapy program"""
    __tablename__ = "therapy_program_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("therapy_programs.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    activity_type = Column(String(50), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    settings = Column(JSONB, nullable=True)
    
    # Relationships
    program = relationship("TherapyProgram", back_populates="activities")

class TherapyProgramEnrollment(Base, TimestampMixin):
    """User enrollment in a therapy program"""
    __tablename__ = "therapy_program_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    program_id = Column(Integer, ForeignKey("therapy_programs.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    current_day = Column(Integer, default=1)
    completed = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User")
    program = relationship("TherapyProgram", back_populates="enrollments")
    progress = relationship("TherapyProgramProgress", back_populates="enrollment", cascade="all, delete-orphan")

class TherapyProgramProgress(Base, TimestampMixin):
    """Progress tracking for therapy program activities"""
    __tablename__ = "therapy_program_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("therapy_program_enrollments.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("therapy_program_activities.id"), nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    enrollment = relationship("TherapyProgramEnrollment", back_populates="progress")
    activity = relationship("TherapyProgramActivity")
