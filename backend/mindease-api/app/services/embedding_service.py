"""
Embedding Service for generating document embeddings using sentence-transformers.
"""
import os
import logging
from typing import List, Optional
import numpy as np

# Set cache directory explicitly
CACHE_DIR = "/app/hf-cache"
os.environ["HF_HOME"] = CACHE_DIR


try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingService:
    """Service for generating document embeddings."""
    
    def __init__(self):
        """Initialize the embedding service."""
        self.model = None
        self.model_name = "all-MiniLM-L6-v2"  # Lightweight model
        self.embedding_dimension = 384  # Dimension for all-MiniLM-L6-v2
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(self.model_name, cache_folder=CACHE_DIR)
                logger.info(f"Loaded embedding model: {self.model_name} from {CACHE_DIR}")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")
                self.model = None
        else:
            logger.warning("sentence-transformers not available, using mock embeddings")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding
        """
        if self.model is not None:
            try:
                embedding = self.model.encode(text)
                return embedding.tolist()
            except Exception as e:
                logger.error(f"Error generating embedding: {e}")
                return self._generate_mock_embedding()
        else:
            return self._generate_mock_embedding()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if self.model is not None:
            try:
                embeddings = self.model.encode(texts)
                return [emb.tolist() for emb in embeddings]
            except Exception as e:
                logger.error(f"Error generating batch embeddings: {e}")
                return [self._generate_mock_embedding() for _ in texts]
        else:
            return [self._generate_mock_embedding() for _ in texts]
                
    def _generate_mock_embedding(self) -> List[float]:
        """Generate a mock embedding for testing purposes."""
        return np.random.normal(0, 1, self.embedding_dimension).tolist()
    
    def get_embedding_dimension(self) -> int:
        return self.embedding_dimension
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

# """
# Embedding Service for generating document embeddings using sentence-transformers.
# """
# import os
# os.environ["HF_HOME"] = "/app/hf-cache"
# os.environ["TRANSFORMERS_CACHE"] = "/app/hf-cache"
# import logging
# from typing import List, Optional
# import numpy as np

# try:
#     from sentence_transformers import SentenceTransformer
#     SENTENCE_TRANSFORMERS_AVAILABLE = True
# except ImportError:
#     SENTENCE_TRANSFORMERS_AVAILABLE = False

# from app.core.config import get_settings

# logger = logging.getLogger(__name__)
# settings = get_settings()


# class EmbeddingService:
#     """Service for generating document embeddings."""
    
#     def __init__(self):
#         """Initialize the embedding service."""
#         self.model = None
#         self.model_name = "all-MiniLM-L6-v2"  # Lightweight model
#         self.embedding_dimension = 384  # Dimension for all-MiniLM-L6-v2
        
#         if SENTENCE_TRANSFORMERS_AVAILABLE:
#             try:
#                 self.model = SentenceTransformer(self.model_name)
#                 logger.info(f"Loaded embedding model: {self.model_name}")
#             except Exception as e:
#                 logger.warning(f"Failed to load embedding model: {e}")
#                 self.model = None
#         else:
#             logger.warning("sentence-transformers not available, using mock embeddings")
    
#     async def generate_embedding(self, text: str) -> List[float]:
#         """
#         Generate embedding for a single text.
        
#         Args:
#             text: Input text
            
#         Returns:
#             List of floats representing the embedding
#         """
#         if self.model is not None:
#             try:
#                 embedding = self.model.encode(text)
#                 return embedding.tolist()
#             except Exception as e:
#                 logger.error(f"Error generating embedding: {e}")
#                 return self._generate_mock_embedding()
#         else:
#             return self._generate_mock_embedding()
    
#     def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
#         if self.model is not None:
#             embeddings = self.model.encode(texts)
#             return [emb.tolist() for emb in embeddings]
                
#     def _generate_mock_embedding(self) -> List[float]:
#         """Generate a mock embedding for testing purposes."""
#         # Generate random embedding with correct dimension
#         return np.random.normal(0, 1, self.embedding_dimension).tolist()
    
#     def get_embedding_dimension(self) -> int:
#         """Get the dimension of embeddings produced by this service."""
#         return self.embedding_dimension
    
#     def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
#         """
#         Calculate cosine similarity between two embeddings.
        
#         Args:
#             embedding1: First embedding
#             embedding2: Second embedding
            
#         Returns:
#             Cosine similarity score
#         """
#         try:
#             # Convert to numpy arrays
#             vec1 = np.array(embedding1)
#             vec2 = np.array(embedding2)
            
#             # Calculate cosine similarity
#             dot_product = np.dot(vec1, vec2)
#             norm1 = np.linalg.norm(vec1)
#             norm2 = np.linalg.norm(vec2)
            
#             if norm1 == 0 or norm2 == 0:
#                 return 0.0
            
#             return dot_product / (norm1 * norm2)
#         except Exception as e:
#             logger.error(f"Error calculating similarity: {e}")
#             return 0.0

