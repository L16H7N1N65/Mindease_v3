"""
Document service for document search and retrieval.
"""
import logging
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.db.models.document import Document, DocumentMetadata
from app.services.embedding_service import EmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document search and retrieval."""
    
    def __init__(self, db: Session, embedding_service: EmbeddingService):
        """
        Initialize the document service.
        
        Args:
            db: Database session
            embedding_service: Embedding service for generating embeddings
        """
        self.db = db
        self.embedding_service = embedding_service
    
    def search_documents(
        self, 
        query: str, 
        limit: int = 10, 
        threshold: float = 0.7,
        filters: Optional[Dict[str, str]] = None
    ) -> List[Tuple[Document, float]]:
        """
        Search for documents similar to the query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            threshold: Minimum similarity threshold (0-1)
            filters: Optional metadata filters (key-value pairs)
            
        Returns:
            List of (document, similarity) tuples
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embedding(query)
            if not query_embedding:
                logger.error("Failed to generate embedding for query")
                return []
            
            # Build base query
            base_query = self.db.query(Document)
            
            # Apply metadata filters if provided
            if filters:
                for key, value in filters.items():
                    base_query = base_query.join(
                        DocumentMetadata,
                        Document.id == DocumentMetadata.document_id
                    ).filter(
                        DocumentMetadata.key == key,
                        DocumentMetadata.value == value
                    )
            
            # Execute vector search using pgvector
            # This requires the pgvector extension to be installed in PostgreSQL
            documents = base_query.order_by(
                func.cosine_distance(Document.embedding, query_embedding)
            ).limit(limit * 2).all()  # Fetch more than needed for threshold filtering
            
            # Calculate similarities and filter by threshold
            results = []
            for doc in documents:
                similarity = self.embedding_service.calculate_similarity(
                    query_embedding, doc.embedding
                )
                if similarity >= threshold:
                    results.append((doc, similarity))
            
            # Sort by similarity (highest first) and limit results
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]
        
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    def get_document_with_metadata(self, document_id: int) -> Optional[Tuple[Document, Dict[str, str]]]:
        """
        Get a document with its metadata.
        
        Args:
            document_id: Document ID
            
        Returns:
            Tuple of (document, metadata dict) or None if not found
        """
        try:
            document = self.db.query(Document).filter(Document.id == document_id).first()
            if not document:
                return None
            
            # Get metadata
            metadata_records = self.db.query(DocumentMetadata).filter(
                DocumentMetadata.document_id == document_id
            ).all()
            
            metadata = {record.key: record.value for record in metadata_records}
            
            return document, metadata
        
        except Exception as e:
            logger.error(f"Error getting document with metadata: {str(e)}")
            return None
    
    def get_document_count(self, filters: Optional[Dict[str, str]] = None) -> int:
        """
        Get the count of documents, optionally filtered.
        
        Args:
            filters: Optional metadata filters (key-value pairs)
            
        Returns:
            Number of documents
        """
        try:
            query = self.db.query(func.count(Document.id))
            
            # Apply metadata filters if provided
            if filters:
                for key, value in filters.items():
                    query = query.join(
                        DocumentMetadata,
                        Document.id == DocumentMetadata.document_id
                    ).filter(
                        DocumentMetadata.key == key,
                        DocumentMetadata.value == value
                    )
            
            return query.scalar() or 0
        
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            return 0
    
    def get_metadata_keys(self) -> List[str]:
        """
        Get all unique metadata keys.
        
        Returns:
            List of unique metadata keys
        """
        try:
            result = self.db.query(DocumentMetadata.key).distinct().all()
            return [r[0] for r in result]
        
        except Exception as e:
            logger.error(f"Error getting metadata keys: {str(e)}")
            return []
    
    def get_metadata_values(self, key: str) -> List[str]:
        """
        Get all unique values for a metadata key.
        
        Args:
            key: Metadata key
            
        Returns:
            List of unique values for the key
        """
        try:
            result = self.db.query(DocumentMetadata.value).filter(
                DocumentMetadata.key == key
            ).distinct().all()
            return [r[0] for r in result]
        
        except Exception as e:
            logger.error(f"Error getting metadata values: {str(e)}")
            return []
