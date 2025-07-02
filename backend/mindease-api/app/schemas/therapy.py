"""
Therapy session and program related schemas
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field

# Therapy Session Schemas

class TherapySessionBase(BaseModel):
    """Base schema for therapy session"""
    session_type: str = Field(..., description="Type of therapy session")
    start_time: Optional[datetime] = None
    notes: Optional[str] = None

class TherapySessionCreate(TherapySessionBase):
    """Schema for creating a therapy session"""
    pass

class TherapySessionUpdate(BaseModel):
    """Schema for updating a therapy session"""
    session_type: Optional[str] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None
    completed: Optional[bool] = None

class TherapySessionResponse(TherapySessionBase):
    """Schema for therapy session response"""
    id: int
    user_id: int
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    completed: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Therapy Exercise Schemas

class TherapyExerciseBase(BaseModel):
    """Base schema for therapy exercise"""
    exercise_type: str = Field(..., description="Type of exercise")
    duration_seconds: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None
    results: Optional[Dict[str, Any]] = None

class TherapyExerciseCreate(TherapyExerciseBase):
    """Schema for creating a therapy exercise"""
    pass

class TherapyExerciseUpdate(BaseModel):
    """Schema for updating a therapy exercise"""
    exercise_type: Optional[str] = None
    duration_seconds: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None
    results: Optional[Dict[str, Any]] = None
    completed: Optional[bool] = None

class TherapyExerciseResponse(TherapyExerciseBase):
    """Schema for therapy exercise response"""
    id: int
    session_id: int
    completed: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Therapy Program Schemas

class TherapyProgramBase(BaseModel):
    """Base schema for therapy program"""
    name: str
    description: Optional[str] = None
    target_condition: Optional[str] = None
    duration_weeks: Optional[int] = None
    difficulty_level: str = "beginner"

class TherapyProgramResponse(TherapyProgramBase):
    """Schema for therapy program response"""
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Therapy Program Enrollment Schemas

class TherapyProgramEnrollmentBase(BaseModel):
    """Base schema for therapy program enrollment"""
    start_date: Optional[datetime] = None

class TherapyProgramEnrollmentCreate(TherapyProgramEnrollmentBase):
    """Schema for creating a therapy program enrollment"""
    pass

class TherapyProgramEnrollmentResponse(TherapyProgramEnrollmentBase):
    """Schema for therapy program enrollment response"""
    id: int
    user_id: int
    program_id: int
    completed: bool = False
    completion_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Therapy Program Progress Schemas

class TherapyProgramProgressResponse(BaseModel):
    """Schema for therapy program progress response"""
    id: int
    enrollment_id: int
    activity_id: int
    completed: bool = False
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

