"""
Document management router for file upload, download, and sharing
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_
from typing import List, Optional
from datetime import datetime
import os
import uuid
import shutil
from pathlib import Path

from app.db.session import get_db
from app.db.models import User, Document
from app.schemas.document import (
    DocumentResponse, DocumentUpdate, DocumentShare
)
from app.core.security import get_current_active_user

# router = APIRouter(
#     prefix="/documents",
#     tags=["documents"]
# )
router = APIRouter(tags=["documents"])
# Configure upload directory
UPLOAD_DIR = Path("uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Document Management Endpoints

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a document.
    
    - Supports various file types (PDF, DOC, TXT, etc.)
    - Automatically generates unique filename
    - Stores metadata in database
    """
    # Validate file type
    allowed_extensions = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Get file size
    file_size = file_path.stat().st_size
    
    # Create database record
    db_document = Document(
        user_id=current_user.id,
        title=title or file.filename,
        description=description,
        filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        mime_type=file.content_type,
        tags=tags.split(',') if tags else None
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document

@router.get("", response_model=List[DocumentResponse])
async def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search in title and description"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get documents for the current user.
    
    - Supports pagination and search
    - Returns user's own documents and shared documents
    """
    query = db.query(Document).filter(Document.user_id == current_user.id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Document.title.ilike(search_term),
                Document.description.ilike(search_term)
            )
        )
    
    if tag:
        query = query.filter(Document.tags.contains([tag]))
    
    documents = query.order_by(desc(Document.created_at)).offset(skip).limit(limit).all()
    
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific document by ID."""
    document = db.query(Document).filter(
        and_(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document

@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download a document file."""
    document = db.query(Document).filter(
        and_(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found on disk"
        )
    
    return FileResponse(
        path=file_path,
        filename=document.filename,
        media_type=document.mime_type
    )

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update document metadata."""
    document = db.query(Document).filter(
        and_(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Update fields
    update_data = document_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == 'tags' and isinstance(value, str):
            # Convert comma-separated string to list
            value = value.split(',') if value else None
        setattr(document, field, value)
    
    document.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(document)
    
    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a document and its file."""
    document = db.query(Document).filter(
        and_(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file from disk
    file_path = Path(document.file_path)
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to delete file {file_path}: {e}")
    
    # Delete database record
    db.delete(document)
    db.commit()

# Document Sharing (placeholder for future implementation)

@router.post("/{document_id}/share", response_model=dict)
async def share_document(
    document_id: int,
    share_data: DocumentShare,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Share a document with other users.
    
    - Creates a shareable link or grants access to specific users
    - Placeholder for future implementation
    """
    document = db.query(Document).filter(
        and_(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Placeholder implementation
    share_token = str(uuid.uuid4())
    
    return {
        "message": "Document sharing feature coming soon",
        "share_token": share_token,
        "expires_at": share_data.expires_at
    }

@router.get("/{document_id}/shares")
async def get_document_shares(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get sharing information for a document."""
    document = db.query(Document).filter(
        and_(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Placeholder implementation
    return {
        "message": "Document sharing feature coming soon",
        "shares": []
    }

