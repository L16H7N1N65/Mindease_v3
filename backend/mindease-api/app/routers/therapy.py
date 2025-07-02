"""
Therapy session and program management router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.db.session import get_db
from app.db.models import (
    User, TherapySession, TherapyExercise, TherapyProgram, 
    TherapyProgramActivity, TherapyProgramEnrollment, TherapyProgramProgress
)
from app.schemas.therapy import (
    TherapySessionCreate, TherapySessionResponse, TherapySessionUpdate,
    TherapyExerciseCreate, TherapyExerciseResponse, TherapyExerciseUpdate,
    TherapyProgramResponse, TherapyProgramEnrollmentCreate, 
    TherapyProgramEnrollmentResponse, TherapyProgramProgressResponse
)
from app.core.security import get_current_active_user

# router = APIRouter(
#     prefix="/therapy",
#     tags=["therapy"]
# )

router = APIRouter(tags=[("therapy")])
# Therapy Session Endpoints

@router.post("/sessions", response_model=TherapySessionResponse, status_code=status.HTTP_201_CREATED)
async def create_therapy_session(
    session: TherapySessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new therapy session.
    
    - Records session type, start time, and optional notes
    - Links to current user
    - Can be used for guided or self-directed sessions
    """
    db_session = TherapySession(
        user_id=current_user.id,
        session_type=session.session_type,
        start_time=session.start_time or datetime.utcnow(),
        notes=session.notes
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return db_session

@router.get("/sessions", response_model=List[TherapySessionResponse])
async def get_therapy_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session_type: Optional[str] = Query(None, description="Filter by session type"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get therapy sessions for the current user.
    
    - Supports pagination and filtering
    - Returns sessions in descending order (newest first)
    """
    query = db.query(TherapySession).filter(TherapySession.user_id == current_user.id)
    
    if session_type:
        query = query.filter(TherapySession.session_type == session_type)
    
    if start_date:
        query = query.filter(func.date(TherapySession.start_time) >= start_date)
    if end_date:
        query = query.filter(func.date(TherapySession.start_time) <= end_date)
    
    sessions = query.order_by(desc(TherapySession.start_time)).offset(skip).limit(limit).all()
    
    return sessions

@router.get("/sessions/{session_id}", response_model=TherapySessionResponse)
async def get_therapy_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific therapy session by ID."""
    session = db.query(TherapySession).filter(
        and_(
            TherapySession.id == session_id,
            TherapySession.user_id == current_user.id
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapy session not found"
        )
    
    return session

@router.put("/sessions/{session_id}", response_model=TherapySessionResponse)
async def update_therapy_session(
    session_id: int,
    session_update: TherapySessionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a therapy session."""
    session = db.query(TherapySession).filter(
        and_(
            TherapySession.id == session_id,
            TherapySession.user_id == current_user.id
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapy session not found"
        )
    
    update_data = session_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    session.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(session)
    
    return session

@router.post("/sessions/{session_id}/complete", response_model=TherapySessionResponse)
async def complete_therapy_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a therapy session as completed."""
    session = db.query(TherapySession).filter(
        and_(
            TherapySession.id == session_id,
            TherapySession.user_id == current_user.id
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapy session not found"
        )
    
    if session.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is already completed"
        )
    
    session.end_time = datetime.utcnow()
    session.completed = True
    
    # Calculate duration
    if session.start_time:
        duration = session.end_time - session.start_time
        session.duration_seconds = int(duration.total_seconds())
    
    db.commit()
    db.refresh(session)
    
    return session

# Therapy Exercise Endpoints

@router.post("/sessions/{session_id}/exercises", response_model=TherapyExerciseResponse, status_code=status.HTTP_201_CREATED)
async def create_therapy_exercise(
    session_id: int,
    exercise: TherapyExerciseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add an exercise to a therapy session."""
    # Verify session belongs to user
    session = db.query(TherapySession).filter(
        and_(
            TherapySession.id == session_id,
            TherapySession.user_id == current_user.id
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapy session not found"
        )
    
    db_exercise = TherapyExercise(
        session_id=session_id,
        exercise_type=exercise.exercise_type,
        duration_seconds=exercise.duration_seconds,
        settings=exercise.settings,
        results=exercise.results
    )
    
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    
    return db_exercise

@router.get("/exercises/{exercise_id}", response_model=TherapyExerciseResponse)
async def get_therapy_exercise(
    exercise_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific therapy exercise."""
    exercise = db.query(TherapyExercise).join(TherapySession).filter(
        and_(
            TherapyExercise.id == exercise_id,
            TherapySession.user_id == current_user.id
        )
    ).first()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapy exercise not found"
        )
    
    return exercise

@router.put("/exercises/{exercise_id}/complete", response_model=TherapyExerciseResponse)
async def complete_therapy_exercise(
    exercise_id: int,
    results: dict = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a therapy exercise as completed with optional results."""
    exercise = db.query(TherapyExercise).join(TherapySession).filter(
        and_(
            TherapyExercise.id == exercise_id,
            TherapySession.user_id == current_user.id
        )
    ).first()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapy exercise not found"
        )
    
    exercise.completed = True
    if results:
        exercise.results = results
    
    db.commit()
    db.refresh(exercise)
    
    return exercise

# Therapy Program Endpoints

@router.get("/programs", response_model=List[TherapyProgramResponse])
async def get_therapy_programs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    target_condition: Optional[str] = Query(None, description="Filter by target condition"),
    db: Session = Depends(get_db)
):
    """
    Get available therapy programs.
    
    - Returns active therapy programs
    - Optional filtering by target condition
    """
    query = db.query(TherapyProgram).filter(TherapyProgram.is_active == True)
    
    if target_condition:
        query = query.filter(TherapyProgram.target_condition == target_condition)
    
    programs = query.offset(skip).limit(limit).all()
    
    return programs

@router.get("/programs/{program_id}", response_model=TherapyProgramResponse)
async def get_therapy_program(
    program_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific therapy program by ID."""
    program = db.query(TherapyProgram).filter(
        and_(
            TherapyProgram.id == program_id,
            TherapyProgram.is_active == True
        )
    ).first()
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapy program not found"
        )
    
    return program

@router.post("/programs/{program_id}/enroll", response_model=TherapyProgramEnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_therapy_program(
    program_id: int,
    enrollment: TherapyProgramEnrollmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enroll the current user in a therapy program."""
    # Check if program exists
    program = db.query(TherapyProgram).filter(
        and_(
            TherapyProgram.id == program_id,
            TherapyProgram.is_active == True
        )
    ).first()
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapy program not found"
        )
    
    # Check if user is already enrolled
    existing_enrollment = db.query(TherapyProgramEnrollment).filter(
        and_(
            TherapyProgramEnrollment.user_id == current_user.id,
            TherapyProgramEnrollment.program_id == program_id,
            TherapyProgramEnrollment.completed == False
        )
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this program"
        )
    
    db_enrollment = TherapyProgramEnrollment(
        user_id=current_user.id,
        program_id=program_id,
        start_date=enrollment.start_date or datetime.utcnow()
    )
    
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    
    return db_enrollment

@router.get("/enrollments", response_model=List[TherapyProgramEnrollmentResponse])
async def get_user_enrollments(
    active_only: bool = Query(True, description="Return only active enrollments"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get therapy program enrollments for the current user."""
    query = db.query(TherapyProgramEnrollment).filter(
        TherapyProgramEnrollment.user_id == current_user.id
    )
    
    if active_only:
        query = query.filter(TherapyProgramEnrollment.completed == False)
    
    enrollments = query.order_by(desc(TherapyProgramEnrollment.start_date)).all()
    
    return enrollments

@router.get("/enrollments/{enrollment_id}/progress", response_model=List[TherapyProgramProgressResponse])
async def get_enrollment_progress(
    enrollment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get progress for a specific enrollment."""
    # Verify enrollment belongs to user
    enrollment = db.query(TherapyProgramEnrollment).filter(
        and_(
            TherapyProgramEnrollment.id == enrollment_id,
            TherapyProgramEnrollment.user_id == current_user.id
        )
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    progress = db.query(TherapyProgramProgress).filter(
        TherapyProgramProgress.enrollment_id == enrollment_id
    ).order_by(TherapyProgramProgress.activity_id).all()
    
    return progress

@router.post("/enrollments/{enrollment_id}/activities/{activity_id}/complete", response_model=TherapyProgramProgressResponse)
async def complete_program_activity(
    enrollment_id: int,
    activity_id: int,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a program activity as completed."""
    # Verify enrollment belongs to user
    enrollment = db.query(TherapyProgramEnrollment).filter(
        and_(
            TherapyProgramEnrollment.id == enrollment_id,
            TherapyProgramEnrollment.user_id == current_user.id
        )
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    # Check if progress already exists
    progress = db.query(TherapyProgramProgress).filter(
        and_(
            TherapyProgramProgress.enrollment_id == enrollment_id,
            TherapyProgramProgress.activity_id == activity_id
        )
    ).first()
    
    if not progress:
        progress = TherapyProgramProgress(
            enrollment_id=enrollment_id,
            activity_id=activity_id
        )
        db.add(progress)
    
    progress.completed = True
    progress.completed_at = datetime.utcnow()
    progress.notes = notes
    
    db.commit()
    db.refresh(progress)
    
    return progress

