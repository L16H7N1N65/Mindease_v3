"""
Document models for the MindEase API.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector


from app.db.models.base import TimestampMixin, Base

class Document(Base, TimestampMixin):
    """
    Document model for storing content with vector embeddings.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    category = Column(String(100), nullable=True, index=True)
    doc_metadata = Column(JSON, nullable=True)
    language = Column(String(5), nullable=True, index=True) 
    # Use string references for relationships to avoid circular imports
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    #embeddings = relationship("DocumentEmbedding", back_populates="document", cascade="all, delete-orphan")
    embeddings = relationship(
        "DocumentEmbedding",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    
    document_metadata = relationship("DocumentMetadata", back_populates="document", cascade="all, delete-orphan")

    # Use string-based relationships to avoid import issues
    user = relationship("User", back_populates="documents")
    organization = relationship("Organization", back_populates="documents")


class DocumentEmbedding(Base, TimestampMixin):
    """
    Document embedding model for storing vector embeddings separately.
    """
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)  # Content that was embedded
    embedding = Column(Vector(384), nullable=False)  # Vector embedding
    model_name = Column(String(100), nullable=False)  # Model used for embedding
    
    # Use string-based relationship
    document = relationship("Document", back_populates="embeddings")


class DocumentMetadata(Base, TimestampMixin):
    """
    Document metadata model for storing key-value pairs associated with documents.
    """
    __tablename__ = "document_metadata"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    key = Column(String(100), nullable=False, index=True)
    value = Column(String(255), nullable=False)
    
    # Use string-based relationship
    document = relationship("Document", back_populates="document_metadata")