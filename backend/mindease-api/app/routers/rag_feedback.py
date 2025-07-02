"""
RAG Feedback Router

API endpoints for collecting, analyzing, and managing user feedback
on RAG-generated responses for continuous improvement.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.dependencies import get_current_user, get_db, get_current_admin_user
from app.db.models.auth import User
from app.db.models.rag_feedback import RAGFeedback, FeedbackAnalytics, ResponseImprovement
from app.schemas.rag_feedback import (
    RAGFeedbackCreate, QuickFeedback, DetailedFeedback,
    RAGFeedbackResponse, FeedbackAnalyticsResponse, FeedbackSummary,
    ResponseImprovementCreate, ResponseImprovementResponse,
    FeedbackTrends, CategoryPerformance, UserFeedbackHistory
)
from app.services.rag_feedback_service import RAGFeedbackService

# router = APIRouter(prefix="/api/v1/feedback", tags=["RAG Feedback"])
router = APIRouter(tags=[("feedback")])

@router.post("/quick", response_model=RAGFeedbackResponse)
async def submit_quick_feedback(
    feedback: QuickFeedback,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit quick thumbs up/down feedback on a RAG response.
    
    This endpoint allows users to quickly rate responses with a simple
    helpful/not helpful binary rating.
    """
    feedback_service = RAGFeedbackService(db)
    
    # Convert quick feedback to full feedback format
    feedback_data = RAGFeedbackCreate(
        user_query=feedback.user_query,
        rag_response=feedback.rag_response,
        is_helpful=feedback.is_helpful,
        conversation_id=feedback.conversation_id,
        message_id=feedback.message_id,
        overall_rating=5 if feedback.is_helpful else 1,  # Convert boolean to rating
        feedback_category="positive" if feedback.is_helpful else "negative"
    )
    
    # Create feedback record
    rag_feedback = await feedback_service.create_feedback(
        feedback_data=feedback_data,
        user_id=current_user.id
    )
    
    # Process feedback in background for analytics
    background_tasks.add_task(
        feedback_service.process_feedback_analytics,
        rag_feedback.id
    )
    
    return rag_feedback


@router.post("/detailed", response_model=RAGFeedbackResponse)
async def submit_detailed_feedback(
    feedback: DetailedFeedback,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit detailed feedback with comprehensive ratings and comments.
    
    This endpoint allows users to provide detailed feedback including
    multiple rating dimensions and free-text comments.
    """
    feedback_service = RAGFeedbackService(db)
    
    # Convert detailed feedback to full feedback format
    feedback_data = RAGFeedbackCreate(
        user_query=feedback.user_query,
        rag_response=feedback.rag_response,
        relevance_score=feedback.relevance_score,
        helpfulness_score=feedback.helpfulness_score,
        accuracy_score=feedback.accuracy_score,
        clarity_score=feedback.clarity_score,
        overall_rating=feedback.overall_rating,
        is_safe=feedback.is_safe,
        feedback_text=feedback.feedback_text,
        suggested_improvement=feedback.suggested_improvement,
        query_intent=feedback.query_intent,
        user_emotional_state=feedback.user_emotional_state,
        feedback_category="positive" if feedback.overall_rating >= 4 else "negative" if feedback.overall_rating <= 2 else "neutral"
    )
    
    # Create feedback record
    rag_feedback = await feedback_service.create_feedback(
        feedback_data=feedback_data,
        user_id=current_user.id
    )
    
    # Process feedback in background
    background_tasks.add_task(
        feedback_service.process_feedback_analytics,
        rag_feedback.id
    )
    
    # Check for safety concerns
    if not feedback.is_safe:
        background_tasks.add_task(
            feedback_service.handle_safety_concern,
            rag_feedback.id
        )
    
    return rag_feedback


@router.post("/", response_model=RAGFeedbackResponse)
async def submit_feedback(
    feedback: RAGFeedbackCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit comprehensive feedback on a RAG response.
    
    This is the main feedback endpoint that accepts all possible
    feedback fields and metadata.
    """
    feedback_service = RAGFeedbackService(db)
    
    # Create feedback record
    rag_feedback = await feedback_service.create_feedback(
        feedback_data=feedback,
        user_id=current_user.id
    )
    
    # Process feedback in background
    background_tasks.add_task(
        feedback_service.process_feedback_analytics,
        rag_feedback.id
    )
    
    return rag_feedback


@router.get("/my-feedback", response_model=List[RAGFeedbackResponse])
async def get_my_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's feedback history.
    """
    feedback_service = RAGFeedbackService(db)
    return await feedback_service.get_user_feedback(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


@router.get("/summary", response_model=FeedbackSummary)
async def get_feedback_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in summary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a summary of feedback for the current user's organization.
    """
    feedback_service = RAGFeedbackService(db)
    return await feedback_service.get_feedback_summary(
        organization_id=current_user.organization_id,
        days=days
    )


# Admin endpoints for feedback management and analytics

@router.get("/admin/analytics", response_model=List[FeedbackAnalyticsResponse])
async def get_feedback_analytics(
    period_type: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    days: int = Query(30, ge=1, le=365),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive feedback analytics (admin only).
    """
    feedback_service = RAGFeedbackService(db)
    return await feedback_service.get_feedback_analytics(
        period_type=period_type,
        days=days,
        organization_id=current_admin.organization_id
    )


@router.get("/admin/trends", response_model=FeedbackTrends)
async def get_feedback_trends(
    metric: str = Query("overall_rating", description="Metric to analyze trends for"),
    days: int = Query(30, ge=7, le=365),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get feedback trends over time (admin only).
    """
    feedback_service = RAGFeedbackService(db)
    return await feedback_service.get_feedback_trends(
        metric=metric,
        days=days,
        organization_id=current_admin.organization_id
    )


@router.get("/admin/category-performance", response_model=List[CategoryPerformance])
async def get_category_performance(
    days: int = Query(30, ge=1, le=365),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get performance metrics by query category (admin only).
    """
    feedback_service = RAGFeedbackService(db)
    return await feedback_service.get_category_performance(
        days=days,
        organization_id=current_admin.organization_id
    )


@router.get("/admin/all", response_model=List[RAGFeedbackResponse])
async def get_all_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: Optional[str] = Query(None, description="Filter by feedback category"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="Minimum overall rating"),
    max_rating: Optional[int] = Query(None, ge=1, le=5, description="Maximum overall rating"),
    query_intent: Optional[str] = Query(None, description="Filter by query intent"),
    safety_concerns_only: bool = Query(False, description="Show only safety concerns"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all feedback with filtering options (admin only).
    """
    feedback_service = RAGFeedbackService(db)
    return await feedback_service.get_filtered_feedback(
        organization_id=current_admin.organization_id,
        skip=skip,
        limit=limit,
        category=category,
        min_rating=min_rating,
        max_rating=max_rating,
        query_intent=query_intent,
        safety_concerns_only=safety_concerns_only
    )


@router.get("/admin/user/{user_id}/history", response_model=UserFeedbackHistory)
async def get_user_feedback_history(
    user_id: str,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed feedback history for a specific user (admin only).
    """
    feedback_service = RAGFeedbackService(db)
    return await feedback_service.get_user_feedback_history(
        user_id=user_id,
        organization_id=current_admin.organization_id
    )


# Response improvement tracking

@router.post("/admin/improvements", response_model=ResponseImprovementResponse)
async def create_improvement(
    improvement: ResponseImprovementCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a response improvement based on feedback (admin only).
    """
    feedback_service = RAGFeedbackService(db)
    return await feedback_service.create_improvement(
        improvement_data=improvement,
        implemented_by=current_admin.id
    )


@router.get("/admin/improvements", response_model=List[ResponseImprovementResponse])
async def get_improvements(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    improvement_type: Optional[str] = Query(None, description="Filter by improvement type"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get list of response improvements (admin only).
    """
    feedback_service = RAGFeedbackService(db)
    return await feedback_service.get_improvements(
        skip=skip,
        limit=limit,
        status=status,
        improvement_type=improvement_type,
        organization_id=current_admin.organization_id
    )


@router.put("/admin/improvements/{improvement_id}/status")
async def update_improvement_status(
    improvement_id: str,
    status: str,
    after_metrics: Optional[Dict[str, Any]] = None,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update the status of a response improvement (admin only).
    """
    feedback_service = RAGFeedbackService(db)
    return await feedback_service.update_improvement_status(
        improvement_id=improvement_id,
        status=status,
        after_metrics=after_metrics
    )


# Feedback export and reporting

@router.get("/admin/export")
async def export_feedback(
    format: str = Query("csv", regex="^(csv|json)$"),
    days: int = Query(30, ge=1, le=365),
    include_text: bool = Query(True, description="Include free-text feedback"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Export feedback data for analysis (admin only).
    """
    feedback_service = RAGFeedbackService(db)
    return await feedback_service.export_feedback(
        organization_id=current_admin.organization_id,
        format=format,
        days=days,
        include_text=include_text
    )


@router.post("/admin/generate-training-data")
async def generate_training_data(
    background_tasks: BackgroundTasks,
    min_feedback_count: int = Query(10, ge=1, description="Minimum feedback count per example"),
    quality_threshold: float = Query(0.7, ge=0.0, le=1.0, description="Quality threshold for inclusion"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Generate training data from feedback for model improvement (admin only).
    """
    feedback_service = RAGFeedbackService(db)
    
    # Start training data generation in background
    background_tasks.add_task(
        feedback_service.generate_training_data,
        organization_id=current_admin.organization_id,
        min_feedback_count=min_feedback_count,
        quality_threshold=quality_threshold
    )
    
    return {"message": "Training data generation started", "status": "processing"}

