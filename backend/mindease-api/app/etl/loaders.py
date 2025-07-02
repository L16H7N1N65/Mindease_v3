"""
ETL Loaders Module

This module provides optimized database loading components for the MindEase ETL pipeline.
Handles batch processing, embedding generation, and efficient database operations.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.db.session import get_db
from app.db.models.document import Document, DocumentEmbedding
from app.db.models.auth import User
from app.services.embedding_service import EmbeddingService
from app.core.config import settings

logger = logging.getLogger(__name__)


class BatchLoader:
    """Base class for batch loading operations with optimized database writes."""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.embedding_service = EmbeddingService()
        
    async def load_batch(
        self, 
        session: AsyncSession, 
        items: List[Dict[str, Any]]
    ) -> Tuple[int, int]:
        """
        Load a batch of items to database.
        
        Returns:
            Tuple of (successful_inserts, failed_inserts)
        """
        raise NotImplementedError


class DocumentLoader(BatchLoader):
    """Optimized loader for document data with embedding generation."""
    
    def __init__(self, batch_size: int = 50):
        super().__init__(batch_size)
        
    async def load_documents(
        self,
        session: AsyncSession,
        documents: List[Dict[str, Any]],
        user_id: Optional[int] = None,
        organization_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Load documents with embeddings in optimized batches.
        
        Args:
            session: Database session
            documents: List of document dictionaries
            user_id: Optional user ID for user-specific documents
            organization_id: Optional organization ID for org-specific documents
            
        Returns:
            Loading statistics and results
        """
        logger.info(f"Starting document loading: {len(documents)} documents")
        
        total_processed = 0
        total_successful = 0
        total_failed = 0
        failed_documents = []
        
        # Process documents in batches
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            
            try:
                successful, failed = await self._load_document_batch(
                    session, batch, user_id, organization_id
                )
                total_successful += successful
                total_failed += failed
                total_processed += len(batch)
                
                logger.info(f"Batch {i//self.batch_size + 1}: {successful} successful, {failed} failed")
                
            except Exception as e:
                logger.error(f"Batch loading failed: {str(e)}")
                failed_documents.extend(batch)
                total_failed += len(batch)
                total_processed += len(batch)
        
        return {
            "total_processed": total_processed,
            "successful": total_successful,
            "failed": total_failed,
            "success_rate": total_successful / total_processed if total_processed > 0 else 0,
            "failed_documents": failed_documents
        }
    
    async def _load_document_batch(
        self,
        session: AsyncSession,
        batch: List[Dict[str, Any]],
        user_id: Optional[int],
        organization_id: Optional[int]
    ) -> Tuple[int, int]:
        """Load a single batch of documents."""
        successful = 0
        failed = 0
        
        # Prepare document records
        document_records = []
        embedding_records = []
        
        for doc_data in batch:
            try:
                # Generate embedding for document content
                content = doc_data.get('content', '')
                if not content:
                    logger.warning(f"Empty content for document: {doc_data.get('title', 'Unknown')}")
                    failed += 1
                    continue
                
                # Generate embedding
                embedding = await self.embedding_service.generate_embedding(content)
                if embedding is None:
                    logger.warning(f"Failed to generate embedding for: {doc_data.get('title', 'Unknown')}")
                    failed += 1
                    continue
                
                # Prepare document record
                doc_record = {
                    'title': doc_data.get('title', 'Untitled'),
                    'content': content,
                    'category': doc_data.get('category', 'general'),
                    'source': doc_data.get('source', 'unknown'),
                    'metadata': doc_data.get('metadata', {}),
                    'user_id': user_id,
                    'organization_id': organization_id,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
                
                document_records.append(doc_record)
                
                # Prepare embedding record (will be linked after document insert)
                embedding_records.append({
                    'content': content,
                    'embedding': embedding,
                    'model_name': self.embedding_service.model_name,
                    'created_at': datetime.utcnow()
                })
                
            except Exception as e:
                logger.error(f"Error preparing document: {str(e)}")
                failed += 1
        
        # Bulk insert documents
        if document_records:
            try:
                # Insert documents and get IDs
                stmt = insert(Document).values(document_records)
                stmt = stmt.on_conflict_do_nothing()  # Skip duplicates
                result = await session.execute(stmt)
                
                # Get inserted document IDs
                doc_ids_result = await session.execute(
                    text("""
                    SELECT id, title FROM documents 
                    WHERE title = ANY(:titles) 
                    AND created_at >= :created_after
                    ORDER BY id DESC
                    LIMIT :limit
                    """),
                    {
                        'titles': [doc['title'] for doc in document_records],
                        'created_after': datetime.utcnow().replace(minute=0, second=0, microsecond=0),
                        'limit': len(document_records)
                    }
                )
                
                doc_ids = [row[0] for row in doc_ids_result.fetchall()]
                
                # Insert embeddings with document IDs
                if doc_ids and len(doc_ids) == len(embedding_records):
                    for i, embedding_record in enumerate(embedding_records):
                        embedding_record['document_id'] = doc_ids[i]
                    
                    embedding_stmt = insert(DocumentEmbedding).values(embedding_records)
                    embedding_stmt = embedding_stmt.on_conflict_do_nothing()
                    await session.execute(embedding_stmt)
                
                await session.commit()
                successful = len(document_records)
                
                logger.info(f"Successfully loaded {successful} documents with embeddings")
                
            except IntegrityError as e:
                await session.rollback()
                logger.error(f"Integrity error during batch insert: {str(e)}")
                failed = len(document_records)
                
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Database error during batch insert: {str(e)}")
                failed = len(document_records)
        
        return successful, failed


class MetadataLoader(BatchLoader):
    """Loader for document metadata and categorization."""
    
    async def load_metadata(
        self,
        session: AsyncSession,
        metadata_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Load or update document metadata in batches.
        
        Args:
            session: Database session
            metadata_updates: List of metadata update dictionaries
            
        Returns:
            Update statistics
        """
        logger.info(f"Starting metadata loading: {len(metadata_updates)} updates")
        
        successful = 0
        failed = 0
        
        for i in range(0, len(metadata_updates), self.batch_size):
            batch = metadata_updates[i:i + self.batch_size]
            
            try:
                for update in batch:
                    document_id = update.get('document_id')
                    metadata = update.get('metadata', {})
                    category = update.get('category')
                    
                    if not document_id:
                        failed += 1
                        continue
                    
                    # Update document metadata
                    update_stmt = text("""
                        UPDATE documents 
                        SET metadata = :metadata,
                            category = COALESCE(:category, category),
                            updated_at = :updated_at
                        WHERE id = :document_id
                    """)
                    
                    await session.execute(update_stmt, {
                        'metadata': metadata,
                        'category': category,
                        'updated_at': datetime.utcnow(),
                        'document_id': document_id
                    })
                    
                    successful += 1
                
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error updating metadata batch: {str(e)}")
                failed += len(batch)
        
        return {
            "total_processed": len(metadata_updates),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(metadata_updates) if metadata_updates else 0
        }


class EmbeddingLoader(BatchLoader):
    """Specialized loader for embedding operations."""
    
    def __init__(self, batch_size: int = 25):
        super().__init__(batch_size)
        
    async def regenerate_embeddings(
        self,
        session: AsyncSession,
        document_ids: Optional[List[int]] = None,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Regenerate embeddings for existing documents.
        
        Args:
            session: Database session
            document_ids: Optional list of specific document IDs
            force_regenerate: Whether to regenerate existing embeddings
            
        Returns:
            Regeneration statistics
        """
        logger.info("Starting embedding regeneration")
        
        # Get documents that need embeddings
        if document_ids:
            query = text("""
                SELECT d.id, d.content, d.title
                FROM documents d
                LEFT JOIN document_embeddings de ON d.id = de.document_id
                WHERE d.id = ANY(:document_ids)
                AND (de.id IS NULL OR :force_regenerate = true)
            """)
            result = await session.execute(query, {
                'document_ids': document_ids,
                'force_regenerate': force_regenerate
            })
        else:
            query = text("""
                SELECT d.id, d.content, d.title
                FROM documents d
                LEFT JOIN document_embeddings de ON d.id = de.document_id
                WHERE de.id IS NULL OR :force_regenerate = true
            """)
            result = await session.execute(query, {
                'force_regenerate': force_regenerate
            })
        
        documents = result.fetchall()
        
        if not documents:
            return {
                "total_processed": 0,
                "successful": 0,
                "failed": 0,
                "message": "No documents need embedding regeneration"
            }
        
        logger.info(f"Found {len(documents)} documents for embedding regeneration")
        
        successful = 0
        failed = 0
        
        # Process in batches
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            
            try:
                embedding_records = []
                
                for doc_id, content, title in batch:
                    try:
                        # Generate new embedding
                        embedding = await self.embedding_service.generate_embedding(content)
                        if embedding is None:
                            logger.warning(f"Failed to generate embedding for document {doc_id}: {title}")
                            failed += 1
                            continue
                        
                        embedding_records.append({
                            'document_id': doc_id,
                            'content': content,
                            'embedding': embedding,
                            'model_name': self.embedding_service.model_name,
                            'created_at': datetime.utcnow()
                        })
                        
                    except Exception as e:
                        logger.error(f"Error generating embedding for document {doc_id}: {str(e)}")
                        failed += 1
                
                # Upsert embeddings
                if embedding_records:
                    if force_regenerate:
                        # Delete existing embeddings first
                        delete_stmt = text("""
                            DELETE FROM document_embeddings 
                            WHERE document_id = ANY(:doc_ids)
                        """)
                        await session.execute(delete_stmt, {
                            'doc_ids': [rec['document_id'] for rec in embedding_records]
                        })
                    
                    # Insert new embeddings
                    stmt = insert(DocumentEmbedding).values(embedding_records)
                    stmt = stmt.on_conflict_do_nothing()
                    await session.execute(stmt)
                    
                    successful += len(embedding_records)
                
                await session.commit()
                logger.info(f"Batch {i//self.batch_size + 1}: {len(embedding_records)} embeddings processed")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error processing embedding batch: {str(e)}")
                failed += len(batch)
        
        return {
            "total_processed": len(documents),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(documents) if documents else 0
        }


class ETLLoader:
    """Main ETL loader orchestrator."""
    
    def __init__(self):
        self.document_loader = DocumentLoader()
        self.metadata_loader = MetadataLoader()
        self.embedding_loader = EmbeddingLoader()
        
    async def load_dataset(
        self,
        session: AsyncSession,
        dataset: Dict[str, Any],
        user_id: Optional[int] = None,
        organization_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Load a complete dataset with documents, metadata, and embeddings.
        
        Args:
            session: Database session
            dataset: Complete dataset dictionary
            user_id: Optional user ID
            organization_id: Optional organization ID
            
        Returns:
            Complete loading statistics
        """
        logger.info(f"Starting dataset loading: {dataset.get('name', 'Unknown')}")
        
        results = {
            "dataset_name": dataset.get('name', 'Unknown'),
            "started_at": datetime.utcnow(),
            "documents": {},
            "metadata": {},
            "embeddings": {},
            "total_time": 0
        }
        
        try:
            # Load documents
            documents = dataset.get('documents', [])
            if documents:
                doc_results = await self.document_loader.load_documents(
                    session, documents, user_id, organization_id
                )
                results["documents"] = doc_results
            
            # Load additional metadata
            metadata_updates = dataset.get('metadata_updates', [])
            if metadata_updates:
                meta_results = await self.metadata_loader.load_metadata(
                    session, metadata_updates
                )
                results["metadata"] = meta_results
            
            # Regenerate embeddings if requested
            if dataset.get('regenerate_embeddings', False):
                embedding_results = await self.embedding_loader.regenerate_embeddings(
                    session, force_regenerate=True
                )
                results["embeddings"] = embedding_results
            
            results["completed_at"] = datetime.utcnow()
            results["total_time"] = (results["completed_at"] - results["started_at"]).total_seconds()
            results["status"] = "completed"
            
            logger.info(f"Dataset loading completed in {results['total_time']:.2f} seconds")
            
        except Exception as e:
            results["error"] = str(e)
            results["status"] = "failed"
            results["completed_at"] = datetime.utcnow()
            results["total_time"] = (results["completed_at"] - results["started_at"]).total_seconds()
            logger.error(f"Dataset loading failed: {str(e)}")
        
        return results


# Utility functions for common loading operations

async def load_documents_from_file(
    file_path: str,
    user_id: Optional[int] = None,
    organization_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Load documents from a file using the ETL loader.
    
    Args:
        file_path: Path to the document file
        user_id: Optional user ID
        organization_id: Optional organization ID
        
    Returns:
        Loading results
    """
    from app.etl.extractors import ExtractorFactory
    from app.etl.transformers import TransformerPipeline
    
    # Extract data from file
    extractor = ExtractorFactory.create_extractor(file_path)
    raw_data = await extractor.extract()
    
    # Transform data
    transformer = TransformerPipeline()
    transformed_data = await transformer.transform(raw_data)
    
    # Load to database
    async with get_db() as session:
        loader = ETLLoader()
        results = await loader.load_dataset(
            session, 
            {"documents": transformed_data, "name": file_path},
            user_id,
            organization_id
        )
    
    return results


async def bulk_regenerate_embeddings(
    document_ids: Optional[List[int]] = None,
    force: bool = False
) -> Dict[str, Any]:
    """
    Bulk regenerate embeddings for documents.
    
    Args:
        document_ids: Optional list of specific document IDs
        force: Whether to force regeneration of existing embeddings
        
    Returns:
        Regeneration results
    """
    async with get_db() as session:
        loader = EmbeddingLoader()
        results = await loader.regenerate_embeddings(
            session, document_ids, force
        )
    
    return results

