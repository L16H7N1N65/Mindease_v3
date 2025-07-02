"""
Enhanced chatbot service with RAG capabilities for mental health support.
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models.auth import User
from app.db.models.mood import MoodEntry
from app.db.models.therapy import TherapySession
from app.services.document_search_service import DocumentSearchService
from app.services.mistral import MistralService
from app.services.embedding_service import EmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConversationMemory:
    """Simple conversation memory for maintaining context."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversations = {}
    
    def add_message(self, user_id: int, role: str, content: str):
        """Add a message to user's conversation history."""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        self.conversations[user_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        })
        
        # Keep only recent messages
        if len(self.conversations[user_id]) > self.max_history:
            self.conversations[user_id] = self.conversations[user_id][-self.max_history:]
    
    def get_history(self, user_id: int) -> List[Dict]:
        """Get conversation history for a user."""
        return self.conversations.get(user_id, [])
    
    def clear_history(self, user_id: int):
        """Clear conversation history for a user."""
        if user_id in self.conversations:
            del self.conversations[user_id]


class ChatbotService:
    """Enhanced chatbot service with RAG capabilities."""
    
    def __init__(
        self,
        db: Session,
        document_search_service: DocumentSearchService,
        mistral_service: MistralService,
        embedding_service: EmbeddingService
    ):
        """
        Initialize the chatbot service.
        
        Args:
            db: Database session
            document_search_service: Document search service for RAG
            mistral_service: Mistral AI service
            embedding_service: Embedding service
        """
        self.db = db
        self.document_search = document_search_service
        self.mistral = mistral_service
        self.embedding_service = embedding_service
        self.conversation_memory = ConversationMemory()
        
        # Crisis keywords for safety detection
        self.crisis_keywords = [
            "suicide", "kill myself", "end my life", "want to die", "hurt myself",
            "self-harm", "cutting", "overdose", "jump off", "hang myself",
            "suicidal", "hopeless", "worthless", "better off dead"
        ]
    
    async def get_rag_response(
        self,
        user_message: str,
        user_id: int,
        language: str = "en",
        include_mood_context: bool = True,
        include_therapy_context: bool = True
    ) -> Dict:
        """
        Generate a RAG-enhanced response using document context.
        
        Args:
            user_message: User's message
            user_id: User ID
            language: Response language (en/fr)
            include_mood_context: Whether to include user's mood data
            include_therapy_context: Whether to include therapy progress
            
        Returns:
            Dictionary with response, sources, and metadata
        """
        try:
            # Check for crisis indicators
            crisis_detected = self._detect_crisis(user_message)
            if crisis_detected:
                return await self._handle_crisis_response(user_id, language)
            
            # Get user context for personalized retrieval
            user_context = await self._get_user_context(
                user_id, include_mood_context, include_therapy_context
            )
            
            # Enhance query with user context
            enhanced_query = self._enhance_query_with_context(user_message, user_context)
            
            # Search for relevant documents
            relevant_docs = await self.document_search.semantic_search(
                query=enhanced_query,
                limit=5,
                similarity_threshold=0.7,
                user_id=user_id
            )
            
            # Assemble context from retrieved documents
            # context = self._assemble_context(relevant_docs, user_context)
            # if context:
            #     user_with_ctx = f"{context}\n\nUser: {user_message}"
            # else:
            #     user_with_ctx = user_message

            # response = self.mistral.get_response(
            #     user_message=user_with_ctx,
            #     language=language,
            #     conversation_history=conversation_history[-6:]
            # )

            
            # # Get conversation history
            # conversation_history = self.conversation_memory.get_history(user_id)
            
            # # Generate response with Mistral
            # response = self.mistral.get_response(
            #     user_message=user_message,
            #     language=language,
            #     conversation_history=conversation_history[-6:]  # Last 6 messages
            # )
            context_block      = self._assemble_context(relevant_docs, user_context)
            history            = self.conversation_memory.get_history(user_id)[-6:]
            prompt_with_ctx    = "\n\n".join(filter(None, [context_block, *[m["content"] for m in history], user_message]))

            
            org_api_key = await self._get_organization_api_key(user_id, "mistral")
            mistral_service = MistralService(api_key=org_api_key)

            enhanced_response = await mistral_service.get_response(
                prompt_with_ctx,
                #enhanced_response,
                language=language,
                conversation_history=history
)
            # Generate the RAG-enhanced response
            # enhanced_response = self.mistral.get_response(
            #     user_message=prompt_with_ctx,
            #     language=language,
            #     conversation_history=history
            # )
            
            # Enhance response with context if needed
            enhanced_response = self._enhance_response_with_context(
                enhanced_response, context_block, relevant_docs
            )
            
            # Store conversation
            self.conversation_memory.add_message(user_id, "user", user_message)
            self.conversation_memory.add_message(user_id, "assistant", enhanced_response)
            
            # Prepare response with metadata
            result = {
                "response": enhanced_response,
                "sources": [
                    {
                        "title": doc["title"],
                        "category": doc["category"],
                        "similarity": doc["similarity"],
                        "source": doc["source"]
                    }
                    for doc in relevant_docs[:3]  # Top 3 sources
                ],
                "user_context": user_context,
                "crisis_detected": False,
                "timestamp": datetime.utcnow(),
                "language": language
            }
            
            # Log interaction for analytics
            await self._log_interaction(user_id, user_message, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {str(e)}")
            return await self._get_fallback_response(language)
    
    async def _get_user_context(
        self,
        user_id: int,
        include_mood: bool = True,
        include_therapy: bool = True
    ) -> Dict:
        """
        Get user context for personalized responses.
        
        Args:
            user_id: User ID
            include_mood: Include recent mood data
            include_therapy: Include therapy progress
            
        Returns:
            Dictionary with user context
        """
        context = {"user_id": user_id}
        
        try:
            # Get user info
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                context["user_info"] = {
                    "username": user.username,
                    "created_at": user.created_at
                }
            
            # Get recent mood data
            if include_mood:
                recent_moods = (
                    self.db.query(MoodEntry)
                    .filter(MoodEntry.user_id == user_id)
                    .order_by(MoodEntry.created_at.desc())
                    .limit(5)
                    .all()
                )
                if recent_moods:
                    context["recent_moods"] = [
                        {
                            "mood_score": mood.mood_score,
                            "energy_level": mood.energy_level,
                            "created_at": mood.created_at
                        }
                        for mood in recent_moods
                    ]
                    # Calculate average mood
                    avg_mood = sum(m.mood_score for m in recent_moods) / len(recent_moods)
                    context["avg_mood"] = avg_mood
            
            # Get therapy progress
            if include_therapy:
                recent_sessions = self.db.query(TherapySession).filter(
                    TherapySession.user_id == user_id
                ).order_by(TherapySession.created_at.desc()).limit(3).all()
                
                if recent_sessions:
                    context["therapy_progress"] = [
                        {
                            "session_type": session.session_type,
                            "progress_score": session.progress_score,
                            "created_at": session.created_at
                        }
                        for session in recent_sessions
                    ]
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting user context: {str(e)}")
            return context
    
    def _enhance_query_with_context(self, query: str, user_context: Dict) -> str:
        """
        Enhance the search query with user context.
        
        Args:
            query: Original query
            user_context: User context data
            
        Returns:
            Enhanced query string
        """
        enhanced_query = query
        
        # Add mood context if available
        if "avg_mood" in user_context:
            avg_mood = user_context["avg_mood"]
            if avg_mood < 3:
                enhanced_query += " depression anxiety low mood"
            elif avg_mood > 7:
                enhanced_query += " positive mood wellbeing"
            else:
                enhanced_query += " moderate mood balance"
        
        # Add therapy context
        if "therapy_progress" in user_context:
            recent_session = user_context["therapy_progress"][0]
            session_type = recent_session.get("session_type", "")
            if session_type:
                enhanced_query += f" {session_type} therapy"
        
        return enhanced_query
    
    def _assemble_context(self, documents: List[Dict], user_context: Dict) -> str:
        """
        Assemble context from retrieved documents and user data.
        
        Args:
            documents: Retrieved documents
            user_context: User context data
            
        Returns:
            Assembled context string
        """
        context_parts = []
        
        # Add document context
        if documents:
            context_parts.append("Relevant information from knowledge base:")
            for i, doc in enumerate(documents[:3], 1):
                # Truncate content to avoid token limits
                content = doc["content"][:500] + "..." if len(doc["content"]) > 500 else doc["content"]
                context_parts.append(f"{i}. {doc['title']}: {content}")
        
        # Add user mood context
        if "avg_mood" in user_context:
            avg_mood = user_context["avg_mood"]
            mood_desc = "low" if avg_mood < 4 else "moderate" if avg_mood < 7 else "good"
            context_parts.append(f"User's recent mood level: {mood_desc} (score: {avg_mood:.1f}/10)")
        
        # Add therapy context
        if "therapy_progress" in user_context and user_context["therapy_progress"]:
            recent_session = user_context["therapy_progress"][0]
            context_parts.append(f"Recent therapy focus: {recent_session.get('session_type', 'general')}")
        
        return "\n\n".join(context_parts)
    
    def _enhance_response_with_context(
        self,
        response: str,
        context: str,
        documents: List[Dict]
    ) -> str:
        """
        Enhance the response with additional context if needed.
        
        Args:
            response: Original response from Mistral
            context: Assembled context
            documents: Retrieved documents
            
        Returns:
            Enhanced response
        """
        # For now, return the original response
        # Could add logic to append relevant document references
        return response
    
    def _detect_crisis(self, message: str) -> bool:
        """
        Detect crisis indicators in user message.
        
        Args:
            message: User message
            
        Returns:
            True if crisis indicators detected
        """
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.crisis_keywords)
    
    async def _handle_crisis_response(self, user_id: int, language: str) -> Dict:
        """
        Handle crisis situation with appropriate response.
        
        Args:
            user_id: User ID
            language: Response language
            
        Returns:
            Crisis response dictionary
        """
        if language == "fr":
            crisis_response = """Je suis inquiet pour votre sécurité. Si vous avez des pensées suicidaires ou d'automutilation, veuillez contacter immédiatement:

• Numéro national français de prévention du suicide: 3114 (gratuit, 24h/24)
• Services d'urgence: 15 (SAMU) ou 112
• SOS Amitié: 09 72 39 40 50

Vous n'êtes pas seul(e). Des professionnels sont là pour vous aider."""
        else:
            crisis_response = """I'm concerned about your safety. If you're having thoughts of suicide or self-harm, please reach out for immediate help:

• National Suicide Prevention Lifeline: 988 (US)
• Crisis Text Line: Text HOME to 741741
• Emergency Services: 911
• International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/

You are not alone. Professional help is available."""
        
        # Log crisis event for follow-up
        logger.warning(f"Crisis detected for user {user_id}")
        
        return {
            "response": crisis_response,
            "sources": [],
            "user_context": {},
            "crisis_detected": True,
            "timestamp": datetime.utcnow(),
            "language": language
        }
    
    async def _get_fallback_response(self, language: str) -> Dict:
        """
        Get fallback response when system fails.
        
        Args:
            language: Response language
            
        Returns:
            Fallback response dictionary
        """
        if language == "fr":
            fallback = "Je suis désolé, je rencontre des difficultés techniques. Veuillez réessayer dans quelques instants."
        else:
            fallback = "I'm sorry, I'm experiencing technical difficulties. Please try again in a few moments."
        
        return {
            "response": fallback,
            "sources": [],
            "user_context": {},
            "crisis_detected": False,
            "timestamp": datetime.utcnow(),
            "language": language
        }
    
    async def _log_interaction(self, user_id: int, message: str, response: Dict):
        """
        Log interaction for analytics and improvement.
        
        Args:
            user_id: User ID
            message: User message
            response: System response
        """
        try:
            # Could store in database for analytics
            logger.info(f"Chat interaction - User {user_id}: {len(message)} chars, "
                       f"{len(response['sources'])} sources, crisis: {response['crisis_detected']}")
        except Exception as e:
            logger.error(f"Error logging interaction: {str(e)}")
    
    async def get_conversation_summary(self, user_id: int) -> Dict:
        """
        Get a summary of the user's conversation.
        
        Args:
            user_id: User ID
            
        Returns:
            Conversation summary
        """
        try:
            history = self.conversation_memory.get_history(user_id)
            if not history:
                return {"summary": "No conversation history", "message_count": 0}
            
            user_messages = [msg for msg in history if msg["role"] == "user"]
            assistant_messages = [msg for msg in history if msg["role"] == "assistant"]
            
            return {
                "message_count": len(history),
                "user_messages": len(user_messages),
                "assistant_messages": len(assistant_messages),
                "first_message": history[0]["timestamp"] if history else None,
                "last_message": history[-1]["timestamp"] if history else None,
                "recent_topics": [msg["content"][:100] for msg in user_messages[-3:]]
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation summary: {str(e)}")
            return {"error": str(e)}
    
    def clear_conversation(self, user_id: int):
        """
        Clear conversation history for a user.
        
        Args:
            user_id: User ID
        """
        self.conversation_memory.clear_history(user_id)

