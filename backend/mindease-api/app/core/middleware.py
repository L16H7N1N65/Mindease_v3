"""
Middleware Stack for MindEase API

This module provides comprehensive middleware for production-ready API deployment
including CORS, rate limiting, request logging, security headers, and monitoring.
"""

import time
import uuid
import logging
from typing import Callable, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis.asyncio as redis

from app.core.config import get_settings
from app.core.cache import get_redis_client

logger = logging.getLogger(__name__)
settings = get_settings()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request/response logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request details
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        logger.info(
            f"Request started - ID: {request_id}, "
            f"Method: {request.method}, "
            f"URL: {request.url}, "
            f"Client IP: {client_ip}, "
            f"User Agent: {user_agent}"
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response details
            logger.info(
                f"Request completed - ID: {request_id}, "
                f"Status: {response.status_code}, "
                f"Processing time: {process_time:.3f}s"
            )
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Request failed - ID: {request_id}, "
                f"Error: {str(e)}, "
                f"Processing time: {process_time:.3f}s"
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Add HSTS header for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Add CSP header
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-based rate limiting middleware."""
    
    def __init__(self, app: FastAPI, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Number of calls allowed
        self.period = period  # Time period in seconds
        self.redis_client: Optional[redis.Redis] = None
        
    async def get_redis(self) -> redis.Redis:
        """Get Redis client instance."""
        if not self.redis_client:
            self.redis_client = await get_redis_client()
        return self.redis_client
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/v1/health", "/docs", "/redoc"]:
            return await call_next(request)
        
        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        user_id = getattr(request.state, "user_id", None)
        
        # Use user ID if authenticated, otherwise use IP
        identifier = f"user:{user_id}" if user_id else f"ip:{client_ip}"
        
        try:
            redis_client = await self.get_redis()
            
            # Create rate limit key
            current_time = int(time.time())
            window_start = current_time - (current_time % self.period)
            rate_limit_key = f"rate_limit:{identifier}:{window_start}"
            
            # Check current count
            current_count = await redis_client.get(rate_limit_key)
            current_count = int(current_count) if current_count else 0
            
            if current_count >= self.calls:
                # Rate limit exceeded
                logger.warning(f"Rate limit exceeded for {identifier}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "detail": f"Maximum {self.calls} requests per {self.period} seconds",
                        "retry_after": self.period - (current_time % self.period)
                    },
                    headers={
                        "X-RateLimit-Limit": str(self.calls),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(window_start + self.period),
                        "Retry-After": str(self.period - (current_time % self.period))
                    }
                )
            
            # Increment counter
            pipe = redis_client.pipeline()
            pipe.incr(rate_limit_key)
            pipe.expire(rate_limit_key, self.period)
            await pipe.execute()
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            remaining = max(0, self.calls - current_count - 1)
            response.headers["X-RateLimit-Limit"] = str(self.calls)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(window_start + self.period)
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # Continue without rate limiting if Redis is unavailable
            return await call_next(request)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting API metrics."""
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.request_count = defaultdict(int)
        self.response_times = defaultdict(list)
        self.error_count = defaultdict(int)
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        method = request.method
        path = request.url.path
        
        try:
            response = await call_next(request)
            
            # Record metrics
            process_time = time.time() - start_time
            status_code = response.status_code
            
            # Update counters
            self.request_count[f"{method}:{path}"] += 1
            self.response_times[f"{method}:{path}"].append(process_time)
            
            if status_code >= 400:
                self.error_count[f"{method}:{path}:{status_code}"] += 1
            
            # Store metrics in Redis for persistence
            try:
                redis_client = await get_redis_client()
                metrics_key = f"metrics:{datetime.utcnow().strftime('%Y-%m-%d:%H')}"
                
                await redis_client.hincrby(metrics_key, f"requests:{method}:{path}", 1)
                await redis_client.hincrby(metrics_key, f"response_time:{method}:{path}", int(process_time * 1000))
                
                if status_code >= 400:
                    await redis_client.hincrby(metrics_key, f"errors:{method}:{path}:{status_code}", 1)
                
                # Set expiration for metrics (7 days)
                await redis_client.expire(metrics_key, 7 * 24 * 3600)
                
            except Exception as e:
                logger.error(f"Failed to store metrics: {str(e)}")
            
            return response
            
        except Exception as e:
            # Record error
            process_time = time.time() - start_time
            self.error_count[f"{method}:{path}:500"] += 1
            
            logger.error(f"Request error - {method} {path}: {str(e)}")
            raise


def setup_middleware(app: FastAPI) -> None:
    """
    Set up all middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly in production
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time", "X-RateLimit-*"]
    )
    
    # Add trusted host middleware
    if settings.ENVIRONMENT == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS
        )
    
    # Add compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add custom middleware (order matters - last added is executed first)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    
    # Add rate limiting middleware (optional)
    if getattr(settings, 'ENABLE_RATE_LIMITING', False):
        app.add_middleware(
            RateLimitMiddleware,
            calls=getattr(settings, 'RATE_LIMIT_CALLS', 100),
            period=getattr(settings, 'RATE_LIMIT_PERIOD', 60)
        )
    
    logger.info("Middleware stack configured successfully")


def get_metrics() -> Dict[str, Any]:
    """
    Get current application metrics.
    
    Returns:
        Dictionary containing current metrics
    """
    # This would typically be implemented with a proper metrics store
    # For now, return basic structure
    return {
        "requests_total": 0,
        "requests_per_endpoint": {},
        "average_response_time": 0.0,
        "error_rate": 0.0,
        "active_connections": 0
    }


async def get_redis_metrics() -> Dict[str, Any]:
    """
    Get metrics from Redis storage.
    
    Returns:
        Dictionary containing Redis-stored metrics
    """
    try:
        redis_client = await get_redis_client()
        current_hour = datetime.utcnow().strftime('%Y-%m-%d:%H')
        metrics_key = f"metrics:{current_hour}"
        
        metrics = await redis_client.hgetall(metrics_key)
        
        # Process metrics
        processed_metrics = {
            "current_hour": current_hour,
            "requests": {},
            "response_times": {},
            "errors": {}
        }
        
        for key, value in metrics.items():
            key_str = key.decode() if isinstance(key, bytes) else key
            value_int = int(value.decode() if isinstance(value, bytes) else value)
            
            if key_str.startswith("requests:"):
                endpoint = key_str.replace("requests:", "")
                processed_metrics["requests"][endpoint] = value_int
            elif key_str.startswith("response_time:"):
                endpoint = key_str.replace("response_time:", "")
                processed_metrics["response_times"][endpoint] = value_int
            elif key_str.startswith("errors:"):
                endpoint = key_str.replace("errors:", "")
                processed_metrics["errors"][endpoint] = value_int
        
        return processed_metrics
        
    except Exception as e:
        logger.error(f"Failed to get Redis metrics: {str(e)}")
        return {"error": "Failed to retrieve metrics"}


# Export middleware setup function
__all__ = [
    "setup_middleware",
    "RequestLoggingMiddleware",
    "SecurityHeadersMiddleware", 
    "RateLimitMiddleware",
    "MetricsMiddleware",
    "get_metrics",
    "get_redis_metrics"
]

