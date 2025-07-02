"""
ASGI entry-point for MindEase (placed inside the package so `uvicorn app.main:app` works).
"""
from app import create_app
app = create_app()