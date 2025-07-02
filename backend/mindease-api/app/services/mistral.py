import requests
import json
from typing import Optional, Dict, Any, List
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)





class MistralService:
    """
    Service for interacting with Mistral 7B LLM.
    This service handles communication with the Mistral API for generating responses
    when rule-based CBT responses are insufficient.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_url = str(settings.MISTRAL_API_URL).rstrip("/")  
        
        # Use provided API key or fall back to environment variable
        actual_api_key = api_key or settings.MISTRAL_API_KEY
        
        self.headers = {
            "Authorization": f"Bearer {actual_api_key}",
            "Content-Type": "application/json",
        }
            
        # System prompt that guides Mistral to act as a CBT therapist
        self.system_prompt = {
            "en": """You are a professional cognitive behavioral therapist named MindEase. 
            Your responses should follow CBT principles, be empathetic, and focus on helping 
            the user identify negative thought patterns and develop healthier alternatives.
            Never diagnose the user or provide medical advice. If the user expresses thoughts 
            of self-harm or suicide, respond with empathy and encourage them to seek immediate 
            professional help. Keep responses concise (under 150 words) and conversational.""",
            
            "fr": """Vous êtes un thérapeute cognitivo-comportemental professionnel nommé MindEase.
            Vos réponses doivent suivre les principes de la TCC, être empathiques et aider 
            l'utilisateur à identifier les schémas de pensée négatifs et à développer des alternatives 
            plus saines. Ne diagnostiquez jamais l'utilisateur et ne fournissez pas de conseils médicaux.
            Si l'utilisateur exprime des pensées d'automutilation ou de suicide, répondez avec empathie 
            et encouragez-le à chercher immédiatement de l'aide professionnelle. Gardez les réponses 
            concises (moins de 150 mots) et conversationnelles."""
        }
    
    def get_response(
        self,
        user_message: str,
        language: str = "en",
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Get a response from Mistral 7B for a user message.
        
        Args:
            user_message: The user's message to respond to
            language: The language to respond in (en or fr)
            conversation_history: Optional list of previous messages in the conversation
            
        Returns:
            Mistral's response as a string
        """
        if language not in self.system_prompt:
            language = "en"
        history = conversation_history or []

        # build chat messages
        messages = [{"role": "system", "content": self.system_prompt[language]}]
        messages += history
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": settings.MISTRAL_MODEL,           
            "messages": messages,
            "temperature": settings.MISTRAL_TEMPERATURE,
            "max_tokens": settings.MISTRAL_MAX_TOKENS,
            "top_p": 0.9,
        }

        try:
            resp = requests.post(
                f"{self.api_url}/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            else:
                logger.error(f"Mistral API error {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.exception(f"Error calling Mistral API: {e}")

        # fallback
        if language == "fr":
            return "Je suis désolé, je ne peux pas répondre pour le moment. Veuillez réessayer plus tard."
        return "I'm sorry, I cannot respond at the moment. Please try again later."

        # if language not in ["en", "fr"]:
        #     language = "en"  # Default to English if unsupported language
            
        # if not conversation_history:
        #     conversation_history = []
            
        # try:
        #     # Prepare the messages for the API
        #     messages = [
        #         {"role": "system", "content": self.system_prompt[language]}
        #     ]
            
        #     # Add conversation history
        #     for msg in conversation_history:
        #         messages.append(msg)
                
        #     # Add the current user message
        #     messages.append({"role": "user", "content": user_message})
            
        #     # Prepare the request payload
        #     payload = {
        #         "model": "mistral-7b-instruct",
        #         "messages": messages,
        #         "temperature": 0.7,
        #         "max_tokens": 300,
        #         "top_p": 0.9
        #     }
            
        #     # Make the API request
        #     response = requests.post(
        #         f"{self.api_url}/v1/chat/completions",
        #         headers=self.headers,
        #         data=json.dumps(payload),
        #         timeout=10
        #     )
            
        #     # Parse the response
        #     if response.status_code == 200:
        #         response_data = response.json()
        #         return response_data["choices"][0]["message"]["content"]
        #     else:
        #         logger.error(f"Mistral API error: {response.status_code} - {response.text}")
        #         # Return a fallback response
        #         if language == "fr":
        #             return "Je suis désolé, je ne peux pas répondre pour le moment. Veuillez réessayer plus tard."
        #         return "I'm sorry, I cannot respond at the moment. Please try again later."
                
        # except Exception as e:
        #     logger.exception(f"Error calling Mistral API: {str(e)}")
        #     # Return a fallback response
        #     if language == "fr":
        #         return "Je suis désolé, une erreur s'est produite. Veuillez réessayer plus tard."
        #     return "I'm sorry, an error occurred. Please try again later."

# Create a singleton instance
# mistral_service = MistralService()

# def get_mistral_response(user_message: str, language: str = "en", 
#                          conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
#     """
#     Convenience function to get a response from the Mistral service.
    
#     Args:
#         user_message: The user's message to respond to
#         language: The language to respond in (en or fr)
#         conversation_history: Optional list of previous messages in the conversation
        
#     Returns:
#         Mistral's response as a string
#     """
#     return mistral_service.get_response(user_message, language, conversation_history)
# singleton instance
mistral_service = MistralService()

def get_mistral_response(
    user_message: str,
    language: str = "en",
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> str:
    return mistral_service.get_response(user_message, language, conversation_history)