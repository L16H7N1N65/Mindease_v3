"""
FastAPI application factory for MindEase API.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.middleware import setup_middleware
from app.core.exceptions import setup_exception_handlers
from app.db.session import init_db
from app.routers import auth, mood, therapy, social, organization, document, chat, admin, health, rag_feedback, rag_learning

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
# from huggingface_hub import login
# login(token=settings.HF_TOKEN)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting up MindEase API...")
    init_db()
    yield
    # Shutdown
    logger.info("Shutting down MindEase API...")


def create_app() -> FastAPI:
    """
    Create FastAPI application with all configurations and routes.
    
    Returns:
        FastAPI application instance
    """
    # Create FastAPI app with lifespan
    app = FastAPI(
        title="MindEase API",
        description="Mental health and wellness platform API with RAG chatbot",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Include routers with API prefix
    api_prefix = "/api/v1"
    
    app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["authentication"])
    app.include_router(mood.router, prefix=f"{api_prefix}/mood", tags=["mood"])
    app.include_router(therapy.router, prefix=f"{api_prefix}/therapy", tags=["therapy"])
    app.include_router(social.router, prefix=f"{api_prefix}/social", tags=["social"])
    app.include_router(organization.router, prefix=f"{api_prefix}/organization", tags=["organization"])
    app.include_router(document.router, prefix=f"{api_prefix}/document", tags=["document"])
    app.include_router(chat.router, prefix=f"{api_prefix}/chat", tags=["chat"])
    app.include_router(admin.router, prefix=f"{api_prefix}/admin", tags=["admin"])
    app.include_router(rag_feedback.router, prefix=f"{api_prefix}/rag/feedback", tags=["rag-feedback"])
    app.include_router(rag_learning.router, prefix=f"{api_prefix}/rag/learning", tags=["rag-learning"])
    app.include_router(health.router, prefix=f"{api_prefix}/health", tags=["health"])
    
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "MindEase API - Mental Health Platform",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }
    
    return app


# Create the app instance
app = create_app()
