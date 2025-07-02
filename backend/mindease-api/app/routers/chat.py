"""
Chat router with RAG capabilities for mental health conversations.
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_db
from app.db.models.auth import User
from app.services.chatbot_service import ChatbotService
from app.services.document_search_service import DocumentSearchService
from app.services.embedding_service import EmbeddingService
from app.services.mistral import MistralService
from app.schemas.chat import (
    ChatMessage, ChatResponse, ConversationSummary,
    DocumentSearchRequest, DocumentSearchResponse
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
# router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
router = APIRouter(tags=["chat"])

def get_chatbot_service(db: Session = Depends(get_db)) -> ChatbotService:
    """
    Dependency to get chatbot service with all required dependencies.
    
    Args:
        db: Database session
        
    Returns:
        Configured ChatbotService instance
    """
    try:
        # Initialize services
        embedding_service = EmbeddingService()
        document_search_service = DocumentSearchService(db, embedding_service)
        mistral_service = MistralService()
        
        # Create chatbot service
        chatbot_service = ChatbotService(
            db=db,
            document_search_service=document_search_service,
            mistral_service=mistral_service,
            embedding_service=embedding_service
        )
        
        return chatbot_service
        
    except Exception as e:
        logger.error(f"Error creating chatbot service: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize chatbot service"
        )


@router.post("/message", response_model=ChatResponse)
async def send_message(
    message: ChatMessage,
    current_user: User = Depends(get_current_active_user),
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Send a message to the RAG-enhanced chatbot.
    
    Args:
        message: Chat message from user
        current_user: Authenticated user
        chatbot_service: Chatbot service instance
        
    Returns:
        ChatResponse with RAG-enhanced reply
    """
    try:
        # Generate RAG response
        response_data = await chatbot_service.get_rag_response(
            user_message=message.content,
            user_id=current_user.id,
            language=message.language or "en",
            include_mood_context=message.include_mood_context,
            include_therapy_context=message.include_therapy_context
        )
        
        # Format response
        chat_response = ChatResponse(
            id=f"msg_{datetime.utcnow().timestamp()}",
            content=response_data["response"],
            sources=response_data["sources"],
            user_context=response_data.get("user_context", {}),
            crisis_detected=response_data["crisis_detected"],
            timestamp=response_data["timestamp"],
            language=response_data["language"]
        )
        
        logger.info(f"Chat response generated for user {current_user.id}")
        return chat_response
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


@router.get("/conversation/summary", response_model=ConversationSummary)
async def get_conversation_summary(
    current_user: User = Depends(get_current_active_user),
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Get summary of user's conversation history.
    
    Args:
        current_user: Authenticated user
        chatbot_service: Chatbot service instance
        
    Returns:
        ConversationSummary with chat statistics
    """
    try:
        summary_data = await chatbot_service.get_conversation_summary(current_user.id)
        
        return ConversationSummary(
            user_id=current_user.id,
            message_count=summary_data.get("message_count", 0),
            user_messages=summary_data.get("user_messages", 0),
            assistant_messages=summary_data.get("assistant_messages", 0),
            first_message=summary_data.get("first_message"),
            last_message=summary_data.get("last_message"),
            recent_topics=summary_data.get("recent_topics", [])
        )
        
    except Exception as e:
        logger.error(f"Error getting conversation summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation summary"
        )


@router.delete("/conversation/clear")
async def clear_conversation(
    current_user: User = Depends(get_current_active_user),
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Clear user's conversation history.
    
    Args:
        current_user: Authenticated user
        chatbot_service: Chatbot service instance
        
    Returns:
        Success message
    """
    try:
        chatbot_service.clear_conversation(current_user.id)
        
        return {
            "message": "Conversation history cleared successfully",
            "user_id": current_user.id,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear conversation"
        )


@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(
    search_request: DocumentSearchRequest,
    current_user: User = Depends(get_current_active_user),
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Search documents using semantic search.
    
    Args:
        search_request: Document search parameters
        current_user: Authenticated user
        chatbot_service: Chatbot service instance
        
    Returns:
        DocumentSearchResponse with relevant documents
    """
    try:
        # Perform semantic search
        documents = await chatbot_service.document_search.semantic_search(
            query=search_request.query,
            limit=search_request.limit,
            similarity_threshold=search_request.similarity_threshold,
            category_filter=search_request.category_filter,
            user_id=current_user.id
        )
        
        return DocumentSearchResponse(
            query=search_request.query,
            documents=documents,
            total_results=len(documents),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search documents"
        )


@router.get("/search/categories")
async def get_document_categories(
    current_user: User = Depends(get_current_active_user),
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Get available document categories.
    
    Args:
        current_user: Authenticated user
        chatbot_service: Chatbot service instance
        
    Returns:
        List of available categories
    """
    try:
        stats = await chatbot_service.document_search.get_document_statistics()
        categories = list(stats.get("categories", {}).keys())
        
        return {
            "categories": categories,
            "total_documents": stats.get("total_documents", 0),
            "embedding_coverage": stats.get("embedding_coverage", 0),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting document categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document categories"
        )


@router.get("/documents/{document_id}/similar")
async def get_similar_documents(
    document_id: int,
    limit: int = 5,
    similarity_threshold: float = 0.8,
    current_user: User = Depends(get_current_active_user),
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Get documents similar to a specific document.
    
    Args:
        document_id: ID of the reference document
        limit: Maximum number of similar documents
        similarity_threshold: Minimum similarity score
        current_user: Authenticated user
        chatbot_service: Chatbot service instance
        
    Returns:
        List of similar documents
    """
    try:
        similar_docs = await chatbot_service.document_search.get_similar_documents(
            document_id=document_id,
            limit=limit,
            similarity_threshold=similarity_threshold
        )
        
        return {
            "reference_document_id": document_id,
            "similar_documents": similar_docs,
            "count": len(similar_docs),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting similar documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get similar documents"
        )


@router.post("/search/advanced", response_model=DocumentSearchResponse)
async def advanced_search(
    query: str,
    filters: Dict = {},
    limit: int = 5,
    similarity_threshold: float = 0.7,
    current_user: User = Depends(get_current_active_user),
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Perform advanced document search with filters.
    
    Args:
        query: Search query
        filters: Additional filters (category, source, metadata, etc.)
        limit: Maximum number of results
        similarity_threshold: Minimum similarity score
        current_user: Authenticated user
        chatbot_service: Chatbot service instance
        
    Returns:
        DocumentSearchResponse with filtered results
    """
    try:
        documents = await chatbot_service.document_search.search_with_filters(
            query=query,
            filters=filters,
            limit=limit,
            similarity_threshold=similarity_threshold
        )
        
        return DocumentSearchResponse(
            query=query,
            documents=documents,
            total_results=len(documents),
            filters_applied=filters,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error in advanced search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform advanced search"
        )


@router.get("/health")
async def chat_health_check():
    """
    Health check endpoint for chat service.
    
    Returns:
        Service health status
    """
    try:
        return {
            "status": "healthy",
            "service": "chat",
            "timestamp": datetime.utcnow(),
            "features": [
                "rag_chat",
                "semantic_search", 
                "conversation_memory",
                "crisis_detection",
                "multi_language"
            ]
        }
        
    except Exception as e:
        logger.error(f"Chat health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat service unhealthy"
        )

