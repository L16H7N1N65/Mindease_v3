# Health Check Router for MindEase API

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional

from app.core.monitoring import (
    get_system_health,
    get_system_metrics,
    get_detailed_metrics
)
from app.core.dependencies import get_current_admin_user, get_current_admin_user
from app.db.models.auth import User

router = APIRouter(tags=["health"])


@router.get("/", response_model=Dict[str, Any])
async def basic_health_check():
    """
    Basic health check endpoint.
    
    Returns:
        Basic health status
    """
    return {
        "status": "healthy",
        "service": "mindease-api",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health_check():
    """
    Detailed health check with all system components.
    
    Returns:
        Comprehensive health status
    """
    return await get_system_health()


@router.get("/metrics", response_model=Dict[str, Any])
async def system_metrics():
    """
    Get current system metrics.
    
    Returns:
        Current system performance metrics
    """
    return await get_system_metrics()


@router.get("/metrics/detailed", response_model=Dict[str, Any])
async def detailed_metrics(
    hours: int = 24,
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get detailed metrics summary (admin only).
    
    Args:
        hours: Number of hours to include in summary
        current_admin: Current admin user
        
    Returns:
        Detailed metrics and health summary
    """
    return await get_detailed_metrics(hours)

