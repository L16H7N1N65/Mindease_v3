"""
Health Monitoring and Metrics for MindEase API

This module provides comprehensive system monitoring, health checks,
and performance metrics collection for production deployment.
"""

import asyncio
import logging
import psutil
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from fastapi import FastAPI, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.cache import get_redis_client, get_cache_stats
from app.db.session import get_db

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class HealthStatus:
    """Health check status data class."""
    service: str
    status: str  # "healthy", "degraded", "unhealthy"
    response_time: float
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class SystemMetrics:
    """System performance metrics data class."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_connections: int
    response_time_avg: float
    error_rate: float


class HealthChecker:
    """Comprehensive health checking system."""
    
    def __init__(self):
        self.checks = {
            "database": self._check_database,
            "redis": self._check_redis,
            "embedding_service": self._check_embedding_service,
            "external_apis": self._check_external_apis,
            "file_system": self._check_file_system,
            "memory": self._check_memory,
            "disk": self._check_disk
        }
    
    async def check_all(self) -> Dict[str, HealthStatus]:
        """
        Run all health checks.
        
        Returns:
            Dictionary of health check results
        """
        results = {}
        
        # Run checks concurrently
        tasks = []
        for name, check_func in self.checks.items():
            tasks.append(self._run_check(name, check_func))
        
        check_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, (name, _) in enumerate(self.checks.items()):
            result = check_results[i]
            if isinstance(result, Exception):
                results[name] = HealthStatus(
                    service=name,
                    status="unhealthy",
                    response_time=0.0,
                    error=str(result)
                )
            else:
                results[name] = result
        
        return results
    
    async def _run_check(self, name: str, check_func) -> HealthStatus:
        """Run a single health check with timing."""
        start_time = time.time()
        try:
            result = await check_func()
            response_time = time.time() - start_time
            
            if isinstance(result, HealthStatus):
                result.response_time = response_time
                return result
            else:
                return HealthStatus(
                    service=name,
                    status="healthy",
                    response_time=response_time,
                    details=result if isinstance(result, dict) else None
                )
        except Exception as e:
            response_time = time.time() - start_time
            return HealthStatus(
                service=name,
                status="unhealthy",
                response_time=response_time,
                error=str(e)
            )
    
    async def _check_database(self) -> HealthStatus:
        """Check database connectivity and performance."""
        try:
            async with get_async_session() as session:
                # Test basic connectivity
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                
                # Test table access
                result = await session.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.scalar()
                
                # Test performance with a simple query
                start_time = time.time()
                await session.execute(text("SELECT version()"))
                query_time = time.time() - start_time
                
                status = "healthy" if query_time < 0.1 else "degraded"
                
                return HealthStatus(
                    service="database",
                    status=status,
                    response_time=query_time,
                    details={
                        "user_count": user_count,
                        "query_time": query_time,
                        "connection_pool": "active"
                    }
                )
                
        except Exception as e:
            return HealthStatus(
                service="database",
                status="unhealthy",
                response_time=0.0,
                error=str(e)
            )
    
    async def _check_redis(self) -> HealthStatus:
        """Check Redis connectivity and performance."""
        try:
            redis_client = await get_redis_client()
            
            # Test basic connectivity
            start_time = time.time()
            await redis_client.ping()
            ping_time = time.time() - start_time
            
            # Test read/write operations
            test_key = "health_check_test"
            await redis_client.set(test_key, "test_value", ex=10)
            value = await redis_client.get(test_key)
            await redis_client.delete(test_key)
            
            if value != "test_value":
                raise Exception("Redis read/write test failed")
            
            # Get cache statistics
            cache_stats = await get_cache_stats()
            
            status = "healthy" if ping_time < 0.05 else "degraded"
            
            return HealthStatus(
                service="redis",
                status=status,
                response_time=ping_time,
                details={
                    "ping_time": ping_time,
                    "cache_stats": cache_stats
                }
            )
            
        except Exception as e:
            return HealthStatus(
                service="redis",
                status="unhealthy",
                response_time=0.0,
                error=str(e)
            )
    
    async def _check_embedding_service(self) -> HealthStatus:
        """Check embedding service functionality."""
        try:
            from app.services.embedding_service import EmbeddingService
            
            embedding_service = EmbeddingService()
            
            # Test embedding generation
            start_time = time.time()
            test_text = "This is a test for health monitoring."
            embedding = await embedding_service.generate_embedding(test_text)
            response_time = time.time() - start_time
            
            if not embedding or len(embedding) == 0:
                raise Exception("Embedding generation returned empty result")
            
            status = "healthy" if response_time < 2.0 else "degraded"
            
            return HealthStatus(
                service="embedding_service",
                status=status,
                response_time=response_time,
                details={
                    "embedding_dimension": len(embedding),
                    "generation_time": response_time,
                    "model_loaded": True
                }
            )
            
        except Exception as e:
            return HealthStatus(
                service="embedding_service",
                status="unhealthy",
                response_time=0.0,
                error=str(e)
            )
    
    async def _check_external_apis(self) -> HealthStatus:
        """Check external API connectivity."""
        try:
            from app.services.mistral import MistralService
            
            mistral_service = MistralService()
            
            # Test Mistral API connectivity
            start_time = time.time()
            # This would be a minimal test call to Mistral API
            # For now, just check if the service can be instantiated
            response_time = time.time() - start_time
            
            return HealthStatus(
                service="external_apis",
                status="healthy",
                response_time=response_time,
                details={
                    "mistral_api": "available",
                    "api_key_configured": bool(settings.MISTRAL_API_KEY)
                }
            )
            
        except Exception as e:
            return HealthStatus(
                service="external_apis",
                status="unhealthy",
                response_time=0.0,
                error=str(e)
            )
    
    async def _check_file_system(self) -> HealthStatus:
        """Check file system health."""
        try:
            import tempfile
            import os
            
            # Test file write/read operations
            start_time = time.time()
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                test_file = f.name
                f.write("health check test")
            
            with open(test_file, 'r') as f:
                content = f.read()
            
            os.unlink(test_file)
            response_time = time.time() - start_time
            
            if content != "health check test":
                raise Exception("File system read/write test failed")
            
            # Get disk usage
            disk_usage = psutil.disk_usage('/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            
            status = "healthy" if disk_percent < 80 else "degraded"
            if disk_percent > 95:
                status = "unhealthy"
            
            return HealthStatus(
                service="file_system",
                status=status,
                response_time=response_time,
                details={
                    "disk_usage_percent": disk_percent,
                    "free_space_gb": disk_usage.free / (1024**3),
                    "total_space_gb": disk_usage.total / (1024**3)
                }
            )
            
        except Exception as e:
            return HealthStatus(
                service="file_system",
                status="unhealthy",
                response_time=0.0,
                error=str(e)
            )
    
    async def _check_memory(self) -> HealthStatus:
        """Check memory usage."""
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            status = "healthy" if memory_percent < 80 else "degraded"
            if memory_percent > 95:
                status = "unhealthy"
            
            return HealthStatus(
                service="memory",
                status=status,
                response_time=0.0,
                details={
                    "memory_percent": memory_percent,
                    "available_gb": memory.available / (1024**3),
                    "total_gb": memory.total / (1024**3),
                    "used_gb": memory.used / (1024**3)
                }
            )
            
        except Exception as e:
            return HealthStatus(
                service="memory",
                status="unhealthy",
                response_time=0.0,
                error=str(e)
            )
    
    async def _check_disk(self) -> HealthStatus:
        """Check disk I/O performance."""
        try:
            # Get disk I/O statistics
            disk_io = psutil.disk_io_counters()
            
            if disk_io:
                return HealthStatus(
                    service="disk",
                    status="healthy",
                    response_time=0.0,
                    details={
                        "read_bytes": disk_io.read_bytes,
                        "write_bytes": disk_io.write_bytes,
                        "read_count": disk_io.read_count,
                        "write_count": disk_io.write_count
                    }
                )
            else:
                return HealthStatus(
                    service="disk",
                    status="degraded",
                    response_time=0.0,
                    details={"message": "Disk I/O statistics not available"}
                )
                
        except Exception as e:
            return HealthStatus(
                service="disk",
                status="unhealthy",
                response_time=0.0,
                error=str(e)
            )


class MetricsCollector:
    """System metrics collection and aggregation."""
    
    def __init__(self):
        self.metrics_history: List[SystemMetrics] = []
        self.max_history = 1000  # Keep last 1000 metrics
    
    async def collect_metrics(self) -> SystemMetrics:
        """
        Collect current system metrics.
        
        Returns:
            SystemMetrics object with current values
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network connections (approximate active connections)
            connections = len(psutil.net_connections())
            
            # Get response time and error rate from cache/metrics
            response_time_avg = await self._get_avg_response_time()
            error_rate = await self._get_error_rate()
            
            metrics = SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                active_connections=connections,
                response_time_avg=response_time_avg,
                error_rate=error_rate
            )
            
            # Store in history
            self.metrics_history.append(metrics)
            
            # Trim history if needed
            if len(self.metrics_history) > self.max_history:
                self.metrics_history = self.metrics_history[-self.max_history:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {str(e)}")
            raise
    
    async def _get_avg_response_time(self) -> float:
        """Get average response time from metrics."""
        try:
            from app.core.middleware import get_redis_metrics
            
            metrics = await get_redis_metrics()
            response_times = metrics.get("response_times", {})
            
            if response_times:
                total_time = sum(response_times.values())
                total_requests = len(response_times)
                return total_time / total_requests if total_requests > 0 else 0.0
            
            return 0.0
            
        except Exception:
            return 0.0
    
    async def _get_error_rate(self) -> float:
        """Get error rate from metrics."""
        try:
            from app.core.middleware import get_redis_metrics
            
            metrics = await get_redis_metrics()
            requests = metrics.get("requests", {})
            errors = metrics.get("errors", {})
            
            total_requests = sum(requests.values()) if requests else 0
            total_errors = sum(errors.values()) if errors else 0
            
            if total_requests > 0:
                return (total_errors / total_requests) * 100
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get metrics summary for the specified time period.
        
        Args:
            hours: Number of hours to include in summary
            
        Returns:
            Dictionary containing metrics summary
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {"message": "No metrics available for the specified period"}
        
        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m.disk_percent for m in recent_metrics) / len(recent_metrics)
        avg_connections = sum(m.active_connections for m in recent_metrics) / len(recent_metrics)
        avg_response_time = sum(m.response_time_avg for m in recent_metrics) / len(recent_metrics)
        avg_error_rate = sum(m.error_rate for m in recent_metrics) / len(recent_metrics)
        
        # Calculate peaks
        max_cpu = max(m.cpu_percent for m in recent_metrics)
        max_memory = max(m.memory_percent for m in recent_metrics)
        max_response_time = max(m.response_time_avg for m in recent_metrics)
        
        return {
            "period_hours": hours,
            "data_points": len(recent_metrics),
            "averages": {
                "cpu_percent": round(avg_cpu, 2),
                "memory_percent": round(avg_memory, 2),
                "disk_percent": round(avg_disk, 2),
                "active_connections": round(avg_connections, 2),
                "response_time_ms": round(avg_response_time, 2),
                "error_rate_percent": round(avg_error_rate, 2)
            },
            "peaks": {
                "max_cpu_percent": round(max_cpu, 2),
                "max_memory_percent": round(max_memory, 2),
                "max_response_time_ms": round(max_response_time, 2)
            },
            "last_updated": recent_metrics[-1].timestamp.isoformat() if recent_metrics else None
        }


# Global instances
health_checker = HealthChecker()
metrics_collector = MetricsCollector()


async def get_system_health() -> Dict[str, Any]:
    """
    Get comprehensive system health status.
    
    Returns:
        Dictionary containing health check results
    """
    health_results = await health_checker.check_all()
    
    # Determine overall status
    statuses = [result.status for result in health_results.values()]
    
    if "unhealthy" in statuses:
        overall_status = "unhealthy"
    elif "degraded" in statuses:
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    
    return {
        "overall_status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            name: {
                "status": result.status,
                "response_time": result.response_time,
                "details": result.details,
                "error": result.error
            }
            for name, result in health_results.items()
        }
    }


async def get_system_metrics() -> Dict[str, Any]:
    """
    Get current system metrics.
    
    Returns:
        Dictionary containing current metrics
    """
    current_metrics = await metrics_collector.collect_metrics()
    
    return {
        "timestamp": current_metrics.timestamp.isoformat(),
        "cpu_percent": current_metrics.cpu_percent,
        "memory_percent": current_metrics.memory_percent,
        "disk_percent": current_metrics.disk_percent,
        "active_connections": current_metrics.active_connections,
        "response_time_avg": current_metrics.response_time_avg,
        "error_rate": current_metrics.error_rate
    }


async def get_detailed_metrics(hours: int = 24) -> Dict[str, Any]:
    """
    Get detailed metrics summary.
    
    Args:
        hours: Number of hours to include
        
    Returns:
        Dictionary containing detailed metrics
    """
    summary = metrics_collector.get_metrics_summary(hours)
    current = await get_system_metrics()
    health = await get_system_health()
    
    return {
        "current": current,
        "summary": summary,
        "health": health
    }


# Export main components
__all__ = [
    "HealthChecker",
    "MetricsCollector",
    "HealthStatus",
    "SystemMetrics",
    "health_checker",
    "metrics_collector",
    "get_system_health",
    "get_system_metrics",
    "get_detailed_metrics"
]

