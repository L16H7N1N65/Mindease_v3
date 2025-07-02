"""
Base models module that defines common imports and base classes
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

Base = declarative_base()

class TimestampMixin:
    """Mixin that adds created_at and updated_at columns to models"""
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
