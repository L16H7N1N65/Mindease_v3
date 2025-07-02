"""
Mood tracking related schemas for request validation and response serialization
"""
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field, validator

class MoodFactorBase(BaseModel):
    """Base schema for mood factor"""
    name: str
    description: Optional[str] = None
    factor_type: str = "custom"
    is_active: bool = True

class MoodFactorCreate(MoodFactorBase):
    """Schema for creating a mood factor"""
    pass

class MoodFactorUpdate(BaseModel):
    """Schema for updating a mood factor"""
    name: Optional[str] = None
    description: Optional[str] = None
    factor_type: Optional[str] = None
    is_active: Optional[bool] = None

class MoodFactorResponse(MoodFactorBase):
    """Schema for mood factor response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MoodEntryBase(BaseModel):
    """Base schema for mood entry"""
    mood_score: int = Field(..., ge=1, le=10)
    energy_level: int = Field(..., ge=1, le=10)
    anxiety_level: Optional[int] = Field(None, ge=1, le=10)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    exercise_minutes: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

    @validator("mood_score")
    def validate_mood_score(cls, v):
        if v < 1 or v > 10:
            raise ValueError("Mood score must be between 1 and 10")
        return v

    @validator("energy_level")
    def validate_energy_level(cls, v):
        if v < 1 or v > 10:
            raise ValueError("Energy level must be between 1 and 10")
        return v

class MoodEntryCreate(MoodEntryBase):
    """Schema for creating a mood entry"""
    allow_multiple_per_day: bool = False

class MoodEntryUpdate(BaseModel):
    """Schema for updating a mood entry"""
    mood_score: Optional[int] = Field(None, ge=1, le=10)
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    anxiety_level: Optional[int] = Field(None, ge=1, le=10)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    exercise_minutes: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

class MoodEntryResponse(MoodEntryBase):
    """Schema for mood entry response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MoodAnalytics(BaseModel):
    """Schema for mood analytics response"""
    period_days: int
    total_entries: int
    average_mood: float
    average_energy: float
    average_anxiety: float
    average_stress: float
    mood_trend: str  # "improving", "declining", "stable"
    insights: List[str]

class MoodTrend(BaseModel):
    """Schema for mood trend data point"""
    date: date
    average_mood: float
    average_energy: float
    entry_count: int

class MoodAnalyticsRequest(BaseModel):
    """Schema for mood analytics request"""
    start_date: datetime
    end_date: datetime
    group_by: str = "day"  # day, week, month

class MoodAnalyticsPoint(BaseModel):
    """Schema for a single point in mood analytics"""
    date: datetime
    mood_score_avg: float
    energy_level_avg: Optional[float] = None
    count: int

class MoodAnalyticsResponse(BaseModel):
    """Schema for mood analytics response"""
    data: List[MoodAnalyticsPoint]
    overall_avg_mood: float
    overall_avg_energy: Optional[float] = None
    total_entries: int
    start_date: datetime
    end_date: datetime
