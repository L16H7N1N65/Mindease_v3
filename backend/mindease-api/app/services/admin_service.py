"""
Admin Services Module

This module provides comprehensive admin services for dataset management,
system monitoring, and resource control in the MindEase platform.
"""

import asyncio
import logging
import os
import shutil
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import psutil
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, select
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import get_db
from app.db.models.document import Document, DocumentEmbedding
from app.db.models.auth import User
from app.db.models.organization import Organization
from app.db.models.conversation import Conversation, Message
from app.etl.pipeline import ETLPipeline
from app.etl.extractors import ExtractorFactory
from app.etl.transformers import TransformerPipeline
from app.etl.loaders import ETLLoader
from app.etl.validators import ETLValidator
from app.core.config import settings

logger = logging.getLogger(__name__)


class DatasetManager:
    """Manages dataset operations including upload, processing, and organization."""
    
    def __init__(self):
        self.etl_pipeline = ETLPipeline()
        self.validator = ETLValidator()
        self.loader = ETLLoader()
        self.upload_dir = Path(settings.UPLOAD_DIR if hasattr(settings, 'UPLOAD_DIR') else '/tmp/uploads')
        self.upload_dir.mkdir(exist_ok=True)
        
    async def upload_dataset(
        self,
        file_path: str,
        user_id: int,
        organization_id: Optional[int] = None,
        dataset_name: Optional[str] = None,
        category: Optional[str] = None,
        validate_before_load: bool = True
    ) -> Dict[str, Any]:
        """
        Upload and process a dataset file.
        
        Args:
            file_path: Path to the uploaded file
            user_id: ID of the user uploading the dataset
            organization_id: Optional organization ID
            dataset_name: Optional name for the dataset
            category: Optional category for the documents
            validate_before_load: Whether to validate before loading
            
        Returns:
            Processing results and statistics
        """
        logger.info(f"Starting dataset upload: {file_path}")
        
        start_time = datetime.utcnow()
        
        try:
            # Extract data from file
            extractor = ExtractorFactory.create_extractor(file_path)
            raw_data = await extractor.extract()
            
            if not raw_data:
                return {
                    "status": "error",
                    "message": "No data extracted from file",
                    "file_path": file_path
                }
            
            # Transform data
            transformer = TransformerPipeline()
            transformed_data = await transformer.transform(raw_data)
            
            # Add metadata
            for item in transformed_data:
                if category:
                    item['category'] = category
                if dataset_name:
                    item.setdefault('metadata', {})['dataset'] = dataset_name
                item.setdefault('metadata', {})['uploaded_by'] = user_id
                item.setdefault('metadata', {})['upload_date'] = start_time.isoformat()
            
            # Validate if requested
            validation_report = None
            if validate_before_load:
                validation_report = await self.validator.validate_dataset(transformed_data)
                
                if not validation_report.is_valid:
                    return {
                        "status": "validation_failed",
                        "message": f"Validation failed: {validation_report.errors} errors, {validation_report.critical_issues} critical issues",
                        "validation_report": validation_report.to_dict(),
                        "file_path": file_path
                    }
            
            # Load to database
            async with get_db() as session:
                load_results = await self.loader.load_dataset(
                    session,
                    {
                        "name": dataset_name or Path(file_path).stem,
                        "documents": transformed_data
                    },
                    user_id,
                    organization_id
                )
            
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            return {
                "status": "success",
                "message": f"Dataset uploaded successfully",
                "file_path": file_path,
                "dataset_name": dataset_name or Path(file_path).stem,
                "processing_time": processing_time,
                "extracted_items": len(raw_data),
                "transformed_items": len(transformed_data),
                "load_results": load_results,
                "validation_report": validation_report.to_dict() if validation_report else None
            }
            
        except Exception as e:
            logger.error(f"Dataset upload failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Upload failed: {str(e)}",
                "file_path": file_path
            }
    
    async def list_datasets(
        self,
        user_id: Optional[int] = None,
        organization_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List available datasets with metadata.
        
        Args:
            user_id: Optional filter by user
            organization_id: Optional filter by organization
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of datasets with metadata
        """
        async with get_db() as session:
            # Build query
            query = """
                SELECT 
                    metadata->>'dataset' as dataset_name,
                    category,
                    COUNT(*) as document_count,
                    MIN(created_at) as first_uploaded,
                    MAX(created_at) as last_uploaded,
                    metadata->>'uploaded_by' as uploaded_by,
                    organization_id
                FROM documents 
                WHERE metadata->>'dataset' IS NOT NULL
            """
            
            params = {}
            
            if user_id:
                query += " AND (metadata->>'uploaded_by')::int = :user_id"
                params['user_id'] = user_id
            
            if organization_id:
                query += " AND organization_id = :organization_id"
                params['organization_id'] = organization_id
            
            query += """
                GROUP BY 
                    metadata->>'dataset', 
                    category, 
                    metadata->>'uploaded_by',
                    organization_id
                ORDER BY last_uploaded DESC
                LIMIT :limit OFFSET :offset
            """
            
            params.update({'limit': limit, 'offset': offset})
            
            result = await session.execute(text(query), params)
            datasets = result.fetchall()
            
            # Get total count
            count_query = """
                SELECT COUNT(DISTINCT metadata->>'dataset') 
                FROM documents 
                WHERE metadata->>'dataset' IS NOT NULL
            """
            
            if user_id:
                count_query += " AND (metadata->>'uploaded_by')::int = :user_id"
            if organization_id:
                count_query += " AND organization_id = :organization_id"
            
            count_result = await session.execute(text(count_query), params)
            total_count = count_result.scalar()
            
            return {
                "datasets": [
                    {
                        "name": row[0],
                        "category": row[1],
                        "document_count": row[2],
                        "first_uploaded": row[3],
                        "last_uploaded": row[4],
                        "uploaded_by": row[5],
                        "organization_id": row[6]
                    }
                    for row in datasets
                ],
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
    
    async def delete_dataset(
        self,
        dataset_name: str,
        user_id: int,
        organization_id: Optional[int] = None,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Delete a dataset and all its documents.
        
        Args:
            dataset_name: Name of the dataset to delete
            user_id: ID of the user requesting deletion
            organization_id: Optional organization ID
            force: Whether to force deletion without additional checks
            
        Returns:
            Deletion results
        """
        logger.info(f"Deleting dataset: {dataset_name}")
        
        async with get_db() as session:
            try:
                # Check if user has permission to delete
                check_query = """
                    SELECT COUNT(*) 
                    FROM documents 
                    WHERE metadata->>'dataset' = :dataset_name
                    AND (metadata->>'uploaded_by')::int = :user_id
                """
                
                params = {
                    'dataset_name': dataset_name,
                    'user_id': user_id
                }
                
                if organization_id:
                    check_query += " AND organization_id = :organization_id"
                    params['organization_id'] = organization_id
                
                result = await session.execute(text(check_query), params)
                user_documents = result.scalar()
                
                if user_documents == 0 and not force:
                    return {
                        "status": "error",
                        "message": "No documents found for this dataset or insufficient permissions"
                    }
                
                # Get document IDs to delete embeddings first
                doc_ids_query = """
                    SELECT id 
                    FROM documents 
                    WHERE metadata->>'dataset' = :dataset_name
                """
                
                if organization_id:
                    doc_ids_query += " AND organization_id = :organization_id"
                
                doc_ids_result = await session.execute(text(doc_ids_query), params)
                doc_ids = [row[0] for row in doc_ids_result.fetchall()]
                
                # Delete embeddings first
                if doc_ids:
                    delete_embeddings_query = """
                        DELETE FROM document_embeddings 
                        WHERE document_id = ANY(:doc_ids)
                    """
                    await session.execute(text(delete_embeddings_query), {'doc_ids': doc_ids})
                
                # Delete documents
                delete_docs_query = """
                    DELETE FROM documents 
                    WHERE metadata->>'dataset' = :dataset_name
                """
                
                if organization_id:
                    delete_docs_query += " AND organization_id = :organization_id"
                
                delete_result = await session.execute(text(delete_docs_query), params)
                deleted_count = delete_result.rowcount
                
                await session.commit()
                
                logger.info(f"Deleted dataset {dataset_name}: {deleted_count} documents")
                
                return {
                    "status": "success",
                    "message": f"Dataset '{dataset_name}' deleted successfully",
                    "deleted_documents": deleted_count,
                    "deleted_embeddings": len(doc_ids)
                }
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to delete dataset {dataset_name}: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Failed to delete dataset: {str(e)}"
                }


class SystemMonitor:
    """Monitors system health, resources, and performance."""
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health information."""
        health_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "services": {},
            "resources": {},
            "database": {},
            "storage": {}
        }
        
        try:
            # Check database connectivity
            async with get_db() as session:
                db_result = await session.execute(text("SELECT 1"))
                health_data["services"]["database"] = {
                    "status": "healthy",
                    "response_time": "< 100ms"
                }
                
                # Get database statistics
                db_stats = await self._get_database_stats(session)
                health_data["database"] = db_stats
                
        except Exception as e:
            health_data["services"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_data["status"] = "degraded"
        
        # Get system resources
        try:
            health_data["resources"] = await self._get_resource_usage()
        except Exception as e:
            logger.error(f"Failed to get resource usage: {str(e)}")
            health_data["resources"] = {"error": str(e)}
        
        # Get storage information
        try:
            health_data["storage"] = await self._get_storage_info()
        except Exception as e:
            logger.error(f"Failed to get storage info: {str(e)}")
            health_data["storage"] = {"error": str(e)}
        
        return health_data
    
    async def _get_database_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {}
        
        try:
            # Document counts
            doc_count_result = await session.execute(text("SELECT COUNT(*) FROM documents"))
            stats["total_documents"] = doc_count_result.scalar()
            
            # Embedding counts
            embedding_count_result = await session.execute(text("SELECT COUNT(*) FROM document_embeddings"))
            stats["total_embeddings"] = embedding_count_result.scalar()
            
            # User counts
            user_count_result = await session.execute(text("SELECT COUNT(*) FROM users"))
            stats["total_users"] = user_count_result.scalar()
            
            # Conversation counts
            conv_count_result = await session.execute(text("SELECT COUNT(*) FROM conversations"))
            stats["total_conversations"] = conv_count_result.scalar()
            
            # Database size
            db_size_result = await session.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """))
            stats["database_size"] = db_size_result.scalar()
            
            # Recent activity (last 24 hours)
            recent_docs_result = await session.execute(text("""
                SELECT COUNT(*) FROM documents 
                WHERE created_at > NOW() - INTERVAL '24 hours'
            """))
            stats["documents_last_24h"] = recent_docs_result.scalar()
            
            recent_convs_result = await session.execute(text("""
                SELECT COUNT(*) FROM conversations 
                WHERE created_at > NOW() - INTERVAL '24 hours'
            """))
            stats["conversations_last_24h"] = recent_convs_result.scalar()
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {str(e)}")
            stats["error"] = str(e)
        
        return stats
    
    async def _get_resource_usage(self) -> Dict[str, Any]:
        """Get system resource usage."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
                "used": psutil.virtual_memory().used
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            },
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
    
    async def _get_storage_info(self) -> Dict[str, Any]:
        """Get storage information."""
        storage_info = {}
        
        # Check upload directory
        upload_dir = Path(settings.UPLOAD_DIR if hasattr(settings, 'UPLOAD_DIR') else '/tmp/uploads')
        if upload_dir.exists():
            total_size = sum(f.stat().st_size for f in upload_dir.rglob('*') if f.is_file())
            file_count = len(list(upload_dir.rglob('*')))
            
            storage_info["upload_directory"] = {
                "path": str(upload_dir),
                "total_size": total_size,
                "file_count": file_count,
                "exists": True
            }
        else:
            storage_info["upload_directory"] = {
                "path": str(upload_dir),
                "exists": False
            }
        
        return storage_info
    
    async def get_analytics_summary(
        self,
        days: int = 30,
        organization_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get analytics summary for the specified period."""
        async with get_db() as session:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            analytics = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "documents": {},
                "conversations": {},
                "users": {},
                "embeddings": {}
            }
            
            try:
                # Document analytics
                doc_query = """
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as count,
                        category
                    FROM documents 
                    WHERE created_at >= :start_date 
                    AND created_at <= :end_date
                """
                
                params = {'start_date': start_date, 'end_date': end_date}
                
                if organization_id:
                    doc_query += " AND organization_id = :organization_id"
                    params['organization_id'] = organization_id
                
                doc_query += " GROUP BY DATE(created_at), category ORDER BY date"
                
                doc_result = await session.execute(text(doc_query), params)
                doc_data = doc_result.fetchall()
                
                analytics["documents"] = {
                    "daily_counts": [
                        {"date": row[0].isoformat(), "count": row[1], "category": row[2]}
                        for row in doc_data
                    ],
                    "total_period": sum(row[1] for row in doc_data)
                }
                
                # Conversation analytics
                conv_query = """
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as count
                    FROM conversations 
                    WHERE created_at >= :start_date 
                    AND created_at <= :end_date
                """
                
                if organization_id:
                    conv_query += " AND organization_id = :organization_id"
                
                conv_query += " GROUP BY DATE(created_at) ORDER BY date"
                
                conv_result = await session.execute(text(conv_query), params)
                conv_data = conv_result.fetchall()
                
                analytics["conversations"] = {
                    "daily_counts": [
                        {"date": row[0].isoformat(), "count": row[1]}
                        for row in conv_data
                    ],
                    "total_period": sum(row[1] for row in conv_data)
                }
                
                # User activity analytics
                user_query = """
                    SELECT 
                        DATE(last_login) as date,
                        COUNT(*) as active_users
                    FROM users 
                    WHERE last_login >= :start_date 
                    AND last_login <= :end_date
                """
                
                if organization_id:
                    user_query += " AND organization_id = :organization_id"
                
                user_query += " GROUP BY DATE(last_login) ORDER BY date"
                
                user_result = await session.execute(text(user_query), params)
                user_data = user_result.fetchall()
                
                analytics["users"] = {
                    "daily_active": [
                        {"date": row[0].isoformat(), "active_users": row[1]}
                        for row in user_data
                    ],
                    "total_active_period": len(set(row[1] for row in user_data))
                }
                
            except Exception as e:
                logger.error(f"Failed to get analytics: {str(e)}")
                analytics["error"] = str(e)
            
            return analytics


class ResourceManager:
    """Manages system resources and cleanup operations."""
    
    async def cleanup_old_files(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up old uploaded files."""
        upload_dir = Path(settings.UPLOAD_DIR if hasattr(settings, 'UPLOAD_DIR') else '/tmp/uploads')
        
        if not upload_dir.exists():
            return {"status": "error", "message": "Upload directory does not exist"}
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        deleted_files = 0
        deleted_size = 0
        errors = []
        
        try:
            for file_path in upload_dir.rglob('*'):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    if file_mtime < cutoff_date:
                        try:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            deleted_files += 1
                            deleted_size += file_size
                        except Exception as e:
                            errors.append(f"Failed to delete {file_path}: {str(e)}")
            
            return {
                "status": "success",
                "deleted_files": deleted_files,
                "deleted_size": deleted_size,
                "errors": errors,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Cleanup failed: {str(e)}"
            }
    
    async def optimize_database(self) -> Dict[str, Any]:
        """Perform database optimization operations."""
        async with get_db() as session:
            try:
                # Vacuum analyze for better performance
                await session.execute(text("VACUUM ANALYZE documents"))
                await session.execute(text("VACUUM ANALYZE document_embeddings"))
                await session.execute(text("VACUUM ANALYZE conversations"))
                await session.execute(text("VACUUM ANALYZE messages"))
                
                # Update statistics
                await session.execute(text("ANALYZE"))
                
                await session.commit()
                
                return {
                    "status": "success",
                    "message": "Database optimization completed",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                await session.rollback()
                return {
                    "status": "error",
                    "message": f"Database optimization failed: {str(e)}"
                }
    
    async def regenerate_embeddings(
        self,
        batch_size: int = 100,
        organization_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Regenerate embeddings for all documents."""
        from app.etl.loaders import EmbeddingLoader
        
        async with get_db() as session:
            # Get document IDs that need embedding regeneration
            query = "SELECT id FROM documents"
            params = {}
            
            if organization_id:
                query += " WHERE organization_id = :organization_id"
                params['organization_id'] = organization_id
            
            result = await session.execute(text(query), params)
            document_ids = [row[0] for row in result.fetchall()]
            
            if not document_ids:
                return {
                    "status": "success",
                    "message": "No documents found for embedding regeneration"
                }
            
            # Process in batches
            loader = EmbeddingLoader(batch_size=batch_size)
            results = await loader.regenerate_embeddings(
                session, document_ids, force_regenerate=True
            )
            
            return {
                "status": "success",
                "message": "Embedding regeneration completed",
                "results": results
            }


class AdminService:
    """Main admin service orchestrator."""
    
    def __init__(self):
        self.dataset_manager = DatasetManager()
        self.system_monitor = SystemMonitor()
        self.resource_manager = ResourceManager()
    
    async def get_dashboard_data(
        self,
        organization_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard data for admin interface."""
        dashboard = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_health": {},
            "analytics": {},
            "datasets": {},
            "resources": {}
        }
        
        try:
            # Get system health
            dashboard["system_health"] = await self.system_monitor.get_system_health()
            
            # Get analytics summary
            dashboard["analytics"] = await self.system_monitor.get_analytics_summary(
                days=7, organization_id=organization_id
            )
            
            # Get recent datasets
            dashboard["datasets"] = await self.dataset_manager.list_datasets(
                organization_id=organization_id, limit=10
            )
            
            # Get resource usage
            dashboard["resources"] = await self.system_monitor._get_resource_usage()
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {str(e)}")
            dashboard["error"] = str(e)
        
        return dashboard


# Utility functions for admin operations

async def quick_health_check() -> bool:
    """Quick health check for system availability."""
    try:
        async with get_db() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def get_system_stats() -> Dict[str, Any]:
    """Get basic system statistics."""
    monitor = SystemMonitor()
    return await monitor.get_system_health()


async def upload_and_process_dataset(
    file_path: str,
    user_id: int,
    **kwargs
) -> Dict[str, Any]:
    """Upload and process a dataset file."""
    manager = DatasetManager()
    return await manager.upload_dataset(file_path, user_id, **kwargs)

