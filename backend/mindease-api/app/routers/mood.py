"""
Mood tracking router for mood entries, analytics, and trend analysis
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.db.session import get_db
from app.db.models import User, MoodEntry, MoodFactor
from app.schemas.mood import (
    MoodEntryCreate, MoodEntryResponse, MoodEntryUpdate,
    MoodFactorCreate, MoodFactorResponse, MoodFactorUpdate,
    MoodAnalytics, MoodTrend
)
from app.core.security import get_current_active_user

# router = APIRouter(
#     prefix="/mood",
#     tags=["mood tracking"]
# )
router = APIRouter(tags=["mood"])
# Mood Entry Endpoints

@router.post("/entries", response_model=MoodEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_mood_entry(
    mood_entry: MoodEntryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new mood entry for the current user.
    
    - Records mood score, energy level, and optional notes
    - Automatically timestamps the entry
    - Links to current user
    """
    # Check if user already has an entry for today
    today = datetime.utcnow().date()
    existing_entry = db.query(MoodEntry).filter(
        and_(
            MoodEntry.user_id == current_user.id,
            func.date(MoodEntry.created_at) == today
        )
    ).first()
    
    if existing_entry and not mood_entry.allow_multiple_per_day:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mood entry already exists for today. Use update endpoint or set allow_multiple_per_day=true"
        )
    
    db_mood_entry = MoodEntry(
        user_id=current_user.id,
        mood_score=mood_entry.mood_score,
        energy_level=mood_entry.energy_level,
        anxiety_level=mood_entry.anxiety_level,
        stress_level=mood_entry.stress_level,
        sleep_hours=mood_entry.sleep_hours,
        exercise_minutes=mood_entry.exercise_minutes,
        notes=mood_entry.notes,
        tags=mood_entry.tags
    )
    
    db.add(db_mood_entry)
    db.commit()
    db.refresh(db_mood_entry)
    
    return db_mood_entry

@router.get("/entries", response_model=List[MoodEntryResponse])
async def get_mood_entries(
    skip: int = Query(0, ge=0, description="Number of entries to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of entries to return"),
    start_date: Optional[date] = Query(None, description="Filter entries from this date"),
    end_date: Optional[date] = Query(None, description="Filter entries until this date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get mood entries for the current user.
    
    - Supports pagination with skip/limit
    - Optional date range filtering
    - Returns entries in descending order (newest first)
    """
    query = db.query(MoodEntry).filter(MoodEntry.user_id == current_user.id)
    
    # Apply date filters
    if start_date:
        query = query.filter(func.date(MoodEntry.created_at) >= start_date)
    if end_date:
        query = query.filter(func.date(MoodEntry.created_at) <= end_date)
    
    # Apply pagination and ordering
    mood_entries = query.order_by(desc(MoodEntry.created_at)).offset(skip).limit(limit).all()
    
    return mood_entries

@router.get("/entries/{entry_id}", response_model=MoodEntryResponse)
async def get_mood_entry(
    entry_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific mood entry by ID.
    
    - Only returns entries belonging to the current user
    - Returns 404 if entry not found or doesn't belong to user
    """
    mood_entry = db.query(MoodEntry).filter(
        and_(
            MoodEntry.id == entry_id,
            MoodEntry.user_id == current_user.id
        )
    ).first()
    
    if not mood_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood entry not found"
        )
    
    return mood_entry

@router.put("/entries/{entry_id}", response_model=MoodEntryResponse)
async def update_mood_entry(
    entry_id: int,
    mood_entry_update: MoodEntryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific mood entry.
    
    - Only allows updating entries belonging to the current user
    - Updates only provided fields (partial update)
    - Returns updated entry
    """
    mood_entry = db.query(MoodEntry).filter(
        and_(
            MoodEntry.id == entry_id,
            MoodEntry.user_id == current_user.id
        )
    ).first()
    
    if not mood_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood entry not found"
        )
    
    # Update fields
    update_data = mood_entry_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mood_entry, field, value)
    
    mood_entry.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(mood_entry)
    
    return mood_entry

@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mood_entry(
    entry_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific mood entry.
    
    - Only allows deleting entries belonging to the current user
    - Returns 204 No Content on success
    """
    mood_entry = db.query(MoodEntry).filter(
        and_(
            MoodEntry.id == entry_id,
            MoodEntry.user_id == current_user.id
        )
    ).first()
    
    if not mood_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood entry not found"
        )
    
    db.delete(mood_entry)
    db.commit()

# Mood Analytics Endpoints

@router.get("/analytics", response_model=MoodAnalytics)
async def get_mood_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get mood analytics for the current user.
    
    - Calculates averages, trends, and insights
    - Configurable time period (1-365 days)
    - Returns comprehensive analytics data
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get mood entries for the period
    mood_entries = db.query(MoodEntry).filter(
        and_(
            MoodEntry.user_id == current_user.id,
            MoodEntry.created_at >= start_date
        )
    ).all()
    
    if not mood_entries:
        return MoodAnalytics(
            period_days=days,
            total_entries=0,
            average_mood=0,
            average_energy=0,
            average_anxiety=0,
            average_stress=0,
            mood_trend="stable",
            insights=["No mood entries found for this period"]
        )
    
    # Calculate averages
    total_entries = len(mood_entries)
    avg_mood = sum(entry.mood_score for entry in mood_entries) / total_entries
    avg_energy = sum(entry.energy_level for entry in mood_entries) / total_entries
    avg_anxiety = sum(entry.anxiety_level or 0 for entry in mood_entries) / total_entries
    avg_stress = sum(entry.stress_level or 0 for entry in mood_entries) / total_entries
    
    # Calculate trend (compare first half vs second half)
    mid_point = len(mood_entries) // 2
    if mid_point > 0:
        first_half_avg = sum(entry.mood_score for entry in mood_entries[:mid_point]) / mid_point
        second_half_avg = sum(entry.mood_score for entry in mood_entries[mid_point:]) / (total_entries - mid_point)
        
        if second_half_avg > first_half_avg + 0.5:
            trend = "improving"
        elif second_half_avg < first_half_avg - 0.5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    # Generate insights
    insights = []
    if avg_mood >= 7:
        insights.append("Your mood has been consistently positive!")
    elif avg_mood <= 4:
        insights.append("Your mood has been lower than usual. Consider reaching out for support.")
    
    if avg_energy >= 7:
        insights.append("Your energy levels have been high.")
    elif avg_energy <= 4:
        insights.append("Your energy levels have been low. Consider reviewing sleep and exercise habits.")
    
    if trend == "improving":
        insights.append("Great news! Your mood trend is improving over time.")
    elif trend == "declining":
        insights.append("Your mood trend shows some decline. Consider what factors might be contributing.")
    
    return MoodAnalytics(
        period_days=days,
        total_entries=total_entries,
        average_mood=round(avg_mood, 2),
        average_energy=round(avg_energy, 2),
        average_anxiety=round(avg_anxiety, 2),
        average_stress=round(avg_stress, 2),
        mood_trend=trend,
        insights=insights
    )

@router.get("/trends", response_model=List[MoodTrend])
async def get_mood_trends(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    interval: str = Query("daily", regex="^(daily|weekly)$", description="Trend interval"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get mood trends over time.
    
    - Returns mood data aggregated by day or week
    - Useful for charting and visualization
    - Configurable time period and interval
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    if interval == "daily":
        # Group by day
        trends = db.query(
            func.date(MoodEntry.created_at).label('date'),
            func.avg(MoodEntry.mood_score).label('avg_mood'),
            func.avg(MoodEntry.energy_level).label('avg_energy'),
            func.count(MoodEntry.id).label('entry_count')
        ).filter(
            and_(
                MoodEntry.user_id == current_user.id,
                MoodEntry.created_at >= start_date
            )
        ).group_by(
            func.date(MoodEntry.created_at)
        ).order_by(
            func.date(MoodEntry.created_at)
        ).all()
    else:  # weekly
        # Group by week
        trends = db.query(
            func.date_trunc('week', MoodEntry.created_at).label('date'),
            func.avg(MoodEntry.mood_score).label('avg_mood'),
            func.avg(MoodEntry.energy_level).label('avg_energy'),
            func.count(MoodEntry.id).label('entry_count')
        ).filter(
            and_(
                MoodEntry.user_id == current_user.id,
                MoodEntry.created_at >= start_date
            )
        ).group_by(
            func.date_trunc('week', MoodEntry.created_at)
        ).order_by(
            func.date_trunc('week', MoodEntry.created_at)
        ).all()
    
    return [
        MoodTrend(
            date=trend.date,
            average_mood=round(float(trend.avg_mood), 2),
            average_energy=round(float(trend.avg_energy), 2),
            entry_count=trend.entry_count
        )
        for trend in trends
    ]

# Mood Factor Endpoints

@router.post("/factors", response_model=MoodFactorResponse, status_code=status.HTTP_201_CREATED)
async def create_mood_factor(
    mood_factor: MoodFactorCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new mood factor for tracking.
    
    - Allows users to define custom factors that affect their mood
    - Examples: weather, work stress, social interactions
    """
    # Check if factor already exists for user
    existing_factor = db.query(MoodFactor).filter(
        and_(
            MoodFactor.user_id == current_user.id,
            MoodFactor.name == mood_factor.name
        )
    ).first()
    
    if existing_factor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mood factor with this name already exists"
        )
    
    db_mood_factor = MoodFactor(
        user_id=current_user.id,
        name=mood_factor.name,
        description=mood_factor.description,
        factor_type=mood_factor.factor_type,
        is_active=mood_factor.is_active
    )
    
    db.add(db_mood_factor)
    db.commit()
    db.refresh(db_mood_factor)
    
    return db_mood_factor

@router.get("/factors", response_model=List[MoodFactorResponse])
async def get_mood_factors(
    active_only: bool = Query(True, description="Return only active factors"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get mood factors for the current user.
    
    - Returns custom factors defined by the user
    - Optional filtering for active factors only
    """
    query = db.query(MoodFactor).filter(MoodFactor.user_id == current_user.id)
    
    if active_only:
        query = query.filter(MoodFactor.is_active == True)
    
    mood_factors = query.order_by(MoodFactor.name).all()
    
    return mood_factors

@router.put("/factors/{factor_id}", response_model=MoodFactorResponse)
async def update_mood_factor(
    factor_id: int,
    mood_factor_update: MoodFactorUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a mood factor.
    
    - Only allows updating factors belonging to the current user
    - Updates only provided fields
    """
    mood_factor = db.query(MoodFactor).filter(
        and_(
            MoodFactor.id == factor_id,
            MoodFactor.user_id == current_user.id
        )
    ).first()
    
    if not mood_factor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood factor not found"
        )
    
    # Update fields
    update_data = mood_factor_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mood_factor, field, value)
    
    mood_factor.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(mood_factor)
    
    return mood_factor

@router.delete("/factors/{factor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mood_factor(
    factor_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a mood factor.
    
    - Only allows deleting factors belonging to the current user
    - Returns 204 No Content on success
    """
    mood_factor = db.query(MoodFactor).filter(
        and_(
            MoodFactor.id == factor_id,
            MoodFactor.user_id == current_user.id
        )
    ).first()
    
    if not mood_factor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood factor not found"
        )
    
    db.delete(mood_factor)
    db.commit()

