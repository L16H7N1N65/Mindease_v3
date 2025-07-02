"""
Custom Exception Handlers for MindEase API

This module provides comprehensive error handling with standardized responses,
logging, and monitoring for production-ready error management.
"""

import logging
import traceback
from typing import Dict, Any, Optional, Union
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from pydantic import ValidationError
import redis.exceptions

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MindEaseException(Exception):
    """Base exception class for MindEase API."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(MindEaseException):
    """Authentication related errors."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(MindEaseException):
    """Authorization related errors."""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class ValidationError(MindEaseException):
    """Data validation errors."""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(MindEaseException):
    """Resource not found errors."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND_ERROR",
            details=details
        )


class ConflictError(MindEaseException):
    """Resource conflict errors."""
    
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT_ERROR",
            details=details
        )


class DatabaseError(MindEaseException):
    """Database operation errors."""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details
        )


class ExternalServiceError(MindEaseException):
    """External service integration errors."""
    
    def __init__(self, message: str = "External service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details
        )


class RateLimitError(MindEaseException):
    """Rate limiting errors."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_ERROR",
            details=details
        )


class ETLError(MindEaseException):
    """ETL pipeline errors."""
    
    def __init__(self, message: str = "ETL operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="ETL_ERROR",
            details=details
        )


class EmbeddingError(MindEaseException):
    """Embedding generation errors."""
    
    def __init__(self, message: str = "Embedding generation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="EMBEDDING_ERROR",
            details=details
        )


class ChatbotError(MindEaseException):
    """Chatbot service errors."""
    
    def __init__(self, message: str = "Chatbot service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="CHATBOT_ERROR",
            details=details
        )


def create_error_response(
    request: Request,
    error: Union[Exception, MindEaseException],
    status_code: int,
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create standardized error response.
    
    Args:
        request: FastAPI request object
        error: Exception instance
        status_code: HTTP status code
        error_code: Application-specific error code
        message: Error message
        details: Additional error details
        
    Returns:
        JSONResponse with standardized error format
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    error_response = {
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "path": str(request.url.path),
            "method": request.method
        }
    }
    
    # Add details if provided
    if details:
        error_response["error"]["details"] = details
    
    # Add stack trace in development
    if settings.ENVIRONMENT == "development":
        error_response["error"]["traceback"] = traceback.format_exc()
    
    # Log error
    log_error(request, error, status_code, error_code, message, details)
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


def log_error(
    request: Request,
    error: Exception,
    status_code: int,
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log error with comprehensive context.
    
    Args:
        request: FastAPI request object
        error: Exception instance
        status_code: HTTP status code
        error_code: Application-specific error code
        message: Error message
        details: Additional error details
    """
    request_id = getattr(request.state, "request_id", "unknown")
    user_id = getattr(request.state, "user_id", "anonymous")
    
    log_data = {
        "request_id": request_id,
        "user_id": user_id,
        "error_code": error_code,
        "status_code": status_code,
        "message": message,
        "path": str(request.url.path),
        "method": request.method,
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown")
    }
    
    if details:
        log_data["details"] = details
    
    # Log at appropriate level
    if status_code >= 500:
        logger.error(f"Server error: {log_data}", exc_info=error)
    elif status_code >= 400:
        logger.warning(f"Client error: {log_data}")
    else:
        logger.info(f"Request processed: {log_data}")


async def mindease_exception_handler(request: Request, exc: MindEaseException) -> JSONResponse:
    """Handle custom MindEase exceptions."""
    return create_error_response(
        request=request,
        error=exc,
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    return create_error_response(
        request=request,
        error=exc,
        status_code=exc.status_code,
        error_code="HTTP_ERROR",
        message=exc.detail,
        details={"status_code": exc.status_code}
    )


async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions."""
    return create_error_response(
        request=request,
        error=exc,
        status_code=exc.status_code,
        error_code="HTTP_ERROR",
        message=exc.detail,
        details={"status_code": exc.status_code}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })
    
    return create_error_response(
        request=request,
        error=exc,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"validation_errors": errors}
    )


async def response_validation_exception_handler(request: Request, exc: ResponseValidationError) -> JSONResponse:
    """Handle response validation errors."""
    return create_error_response(
        request=request,
        error=exc,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="RESPONSE_VALIDATION_ERROR",
        message="Response validation failed",
        details={"validation_errors": exc.errors()}
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors."""
    if isinstance(exc, IntegrityError):
        return create_error_response(
            request=request,
            error=exc,
            status_code=status.HTTP_409_CONFLICT,
            error_code="DATABASE_INTEGRITY_ERROR",
            message="Database integrity constraint violation",
            details={"constraint": str(exc.orig) if hasattr(exc, 'orig') else None}
        )
    elif isinstance(exc, DataError):
        return create_error_response(
            request=request,
            error=exc,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="DATABASE_DATA_ERROR",
            message="Invalid data format for database operation",
            details={"data_error": str(exc.orig) if hasattr(exc, 'orig') else None}
        )
    else:
        return create_error_response(
            request=request,
            error=exc,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            message="Database operation failed",
            details={"error_type": type(exc).__name__}
        )


async def redis_exception_handler(request: Request, exc: redis.exceptions.RedisError) -> JSONResponse:
    """Handle Redis connection and operation errors."""
    return create_error_response(
        request=request,
        error=exc,
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        error_code="CACHE_SERVICE_ERROR",
        message="Cache service temporarily unavailable",
        details={"service": "redis", "error_type": type(exc).__name__}
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unhandled exceptions."""
    return create_error_response(
        request=request,
        error=exc,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        details={"error_type": type(exc).__name__}
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Set up all exception handlers for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Custom exception handlers
    app.add_exception_handler(MindEaseException, mindease_exception_handler)
    
    # HTTP exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    
    # Validation exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ResponseValidationError, response_validation_exception_handler)
    
    # Database exception handlers
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    # Redis exception handlers
    app.add_exception_handler(redis.exceptions.RedisError, redis_exception_handler)
    
    # Generic exception handler (catch-all)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Exception handlers configured successfully")


# Export exception classes and setup function
__all__ = [
    "MindEaseException",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "DatabaseError",
    "ExternalServiceError",
    "RateLimitError",
    "ETLError",
    "EmbeddingError",
    "ChatbotError",
    "setup_exception_handlers",
    "create_error_response",
    "log_error",
    ""
]

