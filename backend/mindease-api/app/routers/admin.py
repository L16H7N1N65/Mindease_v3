"""
Admin Router

This module provides admin API endpoints for dataset management,
system monitoring, and resource control.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_admin_user
from app.db.session import get_db
from app.db.models.auth import User
from app.services.admin_service import AdminService, DatasetManager, SystemMonitor, ResourceManager
from app.schemas.admin import (
    DatasetUploadResponse, DatasetListResponse, SystemHealthResponse,
    AnalyticsResponse, ResourceCleanupResponse, DatabaseOptimizationResponse
)

logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

router = APIRouter(tags=[("admin")])

@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    current_user: User = Depends(get_current_admin_user)
):
    """Get comprehensive system health information."""
    try:
        monitor = SystemMonitor()
        health_data = await monitor.get_system_health()
        return SystemHealthResponse(**health_data)
    except Exception as e:
        logger.error(f"Failed to get system health: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")


@router.get("/dashboard")
async def get_admin_dashboard(
    organization_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_admin_user)
):
    """Get comprehensive admin dashboard data."""
    try:
        admin_service = AdminService()
        dashboard_data = await admin_service.get_dashboard_data(organization_id)
        return JSONResponse(content=dashboard_data)
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")


@router.post("/datasets/upload", response_model=DatasetUploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    organization_id: Optional[int] = Form(None),
    validate_before_load: bool = Form(True),
    current_user: User = Depends(get_current_admin_user)
):
    """Upload and process a dataset file."""
    try:
        # Save uploaded file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process the dataset
            dataset_manager = DatasetManager()
            result = await dataset_manager.upload_dataset(
                file_path=tmp_file_path,
                user_id=current_user.id,
                organization_id=organization_id,
                dataset_name=dataset_name or file.filename,
                category=category,
                validate_before_load=validate_before_load
            )
            
            return DatasetUploadResponse(**result)
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {tmp_file_path}: {str(e)}")
                
    except Exception as e:
        logger.error(f"Dataset upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Dataset upload failed: {str(e)}")


@router.get("/datasets", response_model=DatasetListResponse)
async def list_datasets(
    user_id: Optional[int] = Query(None),
    organization_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_admin_user)
):
    """List available datasets with metadata."""
    try:
        dataset_manager = DatasetManager()
        result = await dataset_manager.list_datasets(
            user_id=user_id,
            organization_id=organization_id,
            limit=limit,
            offset=offset
        )
        return DatasetListResponse(**result)
    except Exception as e:
        logger.error(f"Failed to list datasets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list datasets: {str(e)}")


@router.delete("/datasets/{dataset_name}")
async def delete_dataset(
    dataset_name: str,
    organization_id: Optional[int] = Query(None),
    force: bool = Query(False),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a dataset and all its documents."""
    try:
        dataset_manager = DatasetManager()
        result = await dataset_manager.delete_dataset(
            dataset_name=dataset_name,
            user_id=current_user.id,
            organization_id=organization_id,
            force=force
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Failed to delete dataset {dataset_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete dataset: {str(e)}")


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    days: int = Query(30, ge=1, le=365),
    organization_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_admin_user)
):
    """Get analytics summary for the specified period."""
    try:
        monitor = SystemMonitor()
        analytics_data = await monitor.get_analytics_summary(
            days=days,
            organization_id=organization_id
        )
        return AnalyticsResponse(**analytics_data)
    except Exception as e:
        logger.error(f"Failed to get analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


@router.post("/maintenance/cleanup", response_model=ResourceCleanupResponse)
async def cleanup_old_files(
    days_old: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_admin_user)
):
    """Clean up old uploaded files."""
    try:
        resource_manager = ResourceManager()
        result = await resource_manager.cleanup_old_files(days_old=days_old)
        return ResourceCleanupResponse(**result)
    except Exception as e:
        logger.error(f"File cleanup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File cleanup failed: {str(e)}")


@router.post("/maintenance/optimize-db", response_model=DatabaseOptimizationResponse)
async def optimize_database(
    current_user: User = Depends(get_current_admin_user)
):
    """Perform database optimization operations."""
    try:
        resource_manager = ResourceManager()
        result = await resource_manager.optimize_database()
        return DatabaseOptimizationResponse(**result)
    except Exception as e:
        logger.error(f"Database optimization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database optimization failed: {str(e)}")


@router.post("/maintenance/regenerate-embeddings")
async def regenerate_embeddings(
    batch_size: int = Query(100, ge=10, le=1000),
    organization_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_admin_user)
):
    """Regenerate embeddings for all documents."""
    try:
        resource_manager = ResourceManager()
        result = await resource_manager.regenerate_embeddings(
            batch_size=batch_size,
            organization_id=organization_id
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Embedding regeneration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Embedding regeneration failed: {str(e)}")


@router.get("/users")
async def list_users(
    organization_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List users with admin information."""
    try:
        from sqlalchemy import text
        
        query = """
            SELECT 
                u.id,
                u.email,
                u.username,
                u.full_name,
                u.is_active,
                u.created_at,
                u.last_login,
                u.organization_id,
                COUNT(d.id) as document_count,
                COUNT(c.id) as conversation_count
            FROM users u
            LEFT JOIN documents d ON u.id = (d.metadata->>'uploaded_by')::int
            LEFT JOIN conversations c ON u.id = c.user_id
        """
        
        params = {}
        
        if organization_id:
            query += " WHERE u.organization_id = :organization_id"
            params['organization_id'] = organization_id
        
        query += """
            GROUP BY u.id, u.email, u.username, u.full_name, u.is_active, 
                     u.created_at, u.last_login, u.organization_id
            ORDER BY u.created_at DESC
            LIMIT :limit OFFSET :offset
        """
        
        params.update({'limit': limit, 'offset': offset})
        
        result = await db.execute(text(query), params)
        users = result.fetchall()
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM users"
        if organization_id:
            count_query += " WHERE organization_id = :organization_id"
        
        count_result = await db.execute(text(count_query), params)
        total_count = count_result.scalar()
        
        return {
            "users": [
                {
                    "id": row[0],
                    "email": row[1],
                    "username": row[2],
                    "full_name": row[3],
                    "is_active": row[4],
                    "created_at": row[5],
                    "last_login": row[6],
                    "organization_id": row[7],
                    "document_count": row[8],
                    "conversation_count": row[9]
                }
                for row in users
            ],
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to list users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list users: {str(e)}")


@router.get("/organizations")
async def list_organizations(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List organizations with statistics."""
    try:
        from sqlalchemy import text
        
        query = """
            SELECT 
                o.id,
                o.name,
                o.description,
                o.is_active,
                o.created_at,
                COUNT(DISTINCT u.id) as user_count,
                COUNT(DISTINCT d.id) as document_count
            FROM organizations o
            LEFT JOIN users u ON o.id = u.organization_id
            LEFT JOIN documents d ON o.id = d.organization_id
            GROUP BY o.id, o.name, o.description, o.is_active, o.created_at
            ORDER BY o.created_at DESC
            LIMIT :limit OFFSET :offset
        """
        
        result = await db.execute(text(query), {'limit': limit, 'offset': offset})
        organizations = result.fetchall()
        
        # Get total count
        count_result = await db.execute(text("SELECT COUNT(*) FROM organizations"))
        total_count = count_result.scalar()
        
        return {
            "organizations": [
                {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "is_active": row[3],
                    "created_at": row[4],
                    "user_count": row[5],
                    "document_count": row[6]
                }
                for row in organizations
            ],
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to list organizations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list organizations: {str(e)}")


@router.get("/logs")
async def get_system_logs(
    level: str = Query("INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_admin_user)
):
    """Get system logs (placeholder - implement based on your logging setup)."""
    try:
        # This is a placeholder implementation
        # In a real system, you would read from your log files or logging system
        
        import datetime
        
        # Mock log entries for demonstration
        logs = [
            {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "level": "INFO",
                "message": "System health check completed",
                "module": "admin_service"
            },
            {
                "timestamp": (datetime.datetime.utcnow() - datetime.timedelta(minutes=5)).isoformat(),
                "level": "INFO",
                "message": "Dataset upload completed successfully",
                "module": "dataset_manager"
            }
        ]
        
        return {
            "logs": logs[:limit],
            "total_count": len(logs),
            "level_filter": level,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Failed to get system logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system logs: {str(e)}")


@router.post("/test-etl")
async def test_etl_pipeline(
    test_data: Dict[str, Any],
    current_user: User = Depends(get_current_admin_user)
):
    """Test the ETL pipeline with sample data."""
    try:
        from app.etl.validators import ETLValidator
        from app.etl.transformers import TransformerPipeline
        
        # Validate test data
        validator = ETLValidator()
        validation_report = await validator.validate_dataset([test_data])
        
        # Transform test data
        transformer = TransformerPipeline()
        transformed_data = await transformer.transform([test_data])
        
        return {
            "status": "success",
            "validation_report": validation_report.to_dict(),
            "transformed_data": transformed_data,
            "message": "ETL pipeline test completed"
        }
        
    except Exception as e:
        logger.error(f"ETL pipeline test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ETL pipeline test failed: {str(e)}")


# Health check endpoint for load balancers
@router.get("/ping")
async def ping():
    """Simple health check endpoint."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

