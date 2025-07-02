"""
Data transformers for cleaning and standardizing data in the ETL pipeline.
Handles data validation, cleaning, and normalization for mental health datasets.
"""
import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union

import bleach

# Configure logging
logger = logging.getLogger(__name__)


class BaseTransformer(ABC):
    """Base class for all data transformers."""
    
    def __init__(self, **kwargs):
        """
        Initialize the transformer.
        
        Args:
            **kwargs: Configuration options
        """
        self.config = kwargs
        
    @abstractmethod
    def transform(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Transform a single data record.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Transformed data dictionary or None if invalid
        """
        pass


class TextCleaner(BaseTransformer):
    def __init__(self, 
                 remove_html: bool = True,
                 normalize_whitespace: bool = True,
                 remove_special_chars: bool = False,
                 min_length: int = 10,  # Reduced from 50
                 max_length: int = 100000,  # Increased from 50000
                 **kwargs):
        super().__init__(**kwargs)
        self.remove_html = remove_html
        self.normalize_whitespace = normalize_whitespace
        self.remove_special_chars = remove_special_chars
        self.min_length = min_length
        self.max_length = max_length
        
    def transform(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not isinstance(data, dict):
            return None
            
        cleaned_data = data.copy()
        
        # Clean text fields
        text_fields = ['content', 'title', 'description', 'text', 'body']
        for field in text_fields:
            if field in cleaned_data and isinstance(cleaned_data[field], str):
                cleaned_text = self._clean_text(cleaned_data[field])
                # Only update if cleaning produced valid content
                if cleaned_text:
                    cleaned_data[field] = cleaned_text
                # Else: leave original text but warn
                else:
                    logger.warning(f"Text cleaning removed all content for field {field}")
                    # Don't remove the field, just leave it as is
            elif field in cleaned_data:
                # Handle non-string text fields
                try:
                    cleaned_data[field] = str(cleaned_data[field])
                except:
                    del cleaned_data[field]
        
        # Validate that we have essential content - make this less strict
        content_fields = ['content', 'text', 'body', 'description']
        has_content = any(
            field in cleaned_data and cleaned_data[field] 
            for field in content_fields
        )
        
        if not has_content:
            logger.warning("No valid content fields found after cleaning")
            # Instead of returning None, try to preserve original data
            # Look for any text-like field
            for key, value in data.items():
                if isinstance(value, str) and value.strip():
                    cleaned_data['content'] = value
                    has_content = True
                    break
            
            if not has_content:
                return None
            
        return cleaned_data
    
    def _clean_text(self, text: str) -> Optional[str]:
        """Clean text with less aggressive rules"""
        if not text or not isinstance(text, str):
            return None
            
        original_length = len(text)
        
        # Remove HTML tags but keep content
        if self.remove_html:
            text = bleach.clean(text, tags=[], strip=True)
        
        # Normalize whitespace but don't be too aggressive
        if self.normalize_whitespace:
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
        
        # Remove special characters only if requested
        if self.remove_special_chars:
            text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', '', text)
        
        # Check length constraints - be more lenient
        if len(text) < self.min_length:
            logger.warning(f"Text too short after cleaning: {len(text)} < {self.min_length}")
            # Return original text if it was significantly altered
            if original_length >= self.min_length:
                return text
            return None
            
        if len(text) > self.max_length:
            logger.warning(f"Text too long after cleaning: {len(text)} > {self.max_length}")
            # Truncate but keep
            return text[:self.max_length] + " [TRUNCATED]"
            
        return text


class FieldStandardizer(BaseTransformer):
    """Transformer for standardizing field names and values."""
    
    def __init__(self, 
                 field_mapping: Optional[Dict[str, str]] = None,
                 required_fields: Optional[List[str]] = None,
                 default_values: Optional[Dict[str, Any]] = None,
                 **kwargs):
        """
        Initialize field standardizer.
        
        Args:
            field_mapping: Mapping of old field names to new field names
            required_fields: List of required field names
            default_values: Default values for missing fields
            **kwargs: Additional options
        """
        super().__init__(**kwargs)
        self.field_mapping = field_mapping or self._get_default_field_mapping()
        self.required_fields = required_fields or ['content']
        self.default_values = default_values or {}
        
    def transform(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Standardize field names and values."""
        if not isinstance(data, dict):
            return None
            
        standardized_data = {}
        
        # Apply field mapping
        for old_field, value in data.items():
            new_field = self.field_mapping.get(old_field, old_field)
            standardized_data[new_field] = value
        
        # Add default values for missing fields
        for field, default_value in self.default_values.items():
            if field not in standardized_data:
                standardized_data[field] = default_value
        
        # Check required fields
        for field in self.required_fields:
            if field not in standardized_data or not standardized_data[field]:
                logger.warning(f"Missing required field: {field}")
                return None
        
        # Standardize specific field values
        standardized_data = self._standardize_values(standardized_data)
        
        return standardized_data
    
    def _get_default_field_mapping(self) -> Dict[str, str]:
        """Get default field name mappings."""
        return {
            # Content fields
            'text': 'content',
            'body': 'content',
            'description': 'content',
            'message': 'content',
            'post': 'content',
            
            # Title fields
            'header': 'title',
            'subject': 'title',
            'name': 'title',
            'heading': 'title',
            
            # Category fields
            'type': 'category',
            'class': 'category',
            'tag': 'category',
            'label': 'category',
            
            # Metadata fields
            'author': 'metadata.author',
            'date': 'metadata.date',
            'source': 'metadata.source',
            'url': 'metadata.url',
        }
    
    def _standardize_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize specific field values."""
        # Standardize category values
        if 'category' in data and isinstance(data['category'], str):
            data['category'] = data['category'].lower().strip()
        
        # Standardize boolean values
        boolean_fields = ['is_published', 'is_active', 'is_verified']
        for field in boolean_fields:
            if field in data:
                data[field] = self._to_boolean(data[field])
        
        # Standardize date fields
        date_fields = ['created_at', 'updated_at', 'published_at']
        for field in date_fields:
            if field in data:
                data[field] = self._to_datetime(data[field])
        
        return data
    
    def _to_boolean(self, value: Any) -> bool:
        """Convert value to boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'on', 'active']
        if isinstance(value, (int, float)):
            return bool(value)
        return False
    
    def _to_datetime(self, value: Any) -> Optional[datetime]:
        """Convert value to datetime."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            # Try common date formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        return None


class ContentValidator(BaseTransformer):
    """Validator for content quality and relevance with improved scoring"""
    
    def __init__(self,
                 mental_health_keywords: Optional[Set[str]] = None,
                 min_relevance_score: float = 0.01,  # Very low threshold
                 **kwargs):
        super().__init__(**kwargs)
        self.mental_health_keywords = mental_health_keywords or self._get_mental_health_keywords()
        self.min_relevance_score = min_relevance_score
        
    def transform(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate content quality and relevance"""
        if not isinstance(data, dict):
            return None
        
        content = data.get('content', '')
        if not content:
            return None
        
        # Calculate relevance score with improved algorithm
        relevance_score = self._calculate_relevance_score(content)
        
        # Add metadata regardless of score
        validated_data = data.copy()
        validated_data['metadata'] = validated_data.get('metadata', {})
        validated_data['metadata']['relevance_score'] = relevance_score
        validated_data['metadata']['validated_at'] = datetime.utcnow().isoformat()
        
        # Don't reject based on score, just log
        if relevance_score < self.min_relevance_score:
            logger.info(f"Content relevance score low: {relevance_score:.4f}")
        
        return validated_data
    
    def _calculate_relevance_score(self, content: str) -> float:
        """More accurate relevance scoring"""
        content_lower = content.lower()
        word_count = len(content_lower.split())
        
        # No content case
        if word_count == 0:
            return 0.0
        
        # Count keyword matches with partial matching
        keyword_matches = 0
        for keyword in self.mental_health_keywords:
            if keyword in content_lower:
                # Weight by keyword importance
                if keyword in self.primary_keywords:
                    keyword_matches += 3
                else:
                    keyword_matches += 1
        
        # Calculate base score
        score = keyword_matches / (word_count ** 0.5)  # Square root scaling
        
        # Add bonus for therapy-specific terms
        therapy_bonus = 0
        for term in self.therapy_terms:
            if term in content_lower:
                therapy_bonus += 0.2
                
        return min(1.0, score + therapy_bonus)
    
    def _get_mental_health_keywords(self) -> Set[str]:
        """Comprehensive list of mental health keywords"""
        self.primary_keywords = {
            'therapy', 'counseling', 'mental health', 'depression', 'anxiety',
            'ptsd', 'trauma', 'bipolar', 'ocd', 'adhd', 'autism', 'addiction',
            'recovery', 'healing', 'wellbeing', 'psychologist', 'psychiatrist'
        }
        
        secondary_keywords = {
            'stress', 'mood', 'emotion', 'behavior', 'cognitive', 'dbt', 'cbt',
            'mindfulness', 'meditation', 'self-care', 'coping', 'resilience',
            'support', 'intervention', 'diagnosis', 'treatment', 'symptom',
            'disorder', 'condition', 'clinical', 'therapeutic', 'session'
        }
        
        self.therapy_terms = {
            'client', 'therapist', 'session', 'treatment plan', 'progress note',
            'clinical', 'intervention', 'counseling', 'psychotherapy'
        }
        
        return self.primary_keywords | secondary_keywords
    
    def _get_blocked_keywords(self) -> Set[str]:
        """Get keywords that indicate content should be blocked."""
        return {
            # Inappropriate content
            'explicit', 'graphic', 'violent', 'harmful',
            'illegal', 'dangerous', 'toxic', 'abusive',
            
            # Spam indicators
            'buy now', 'click here', 'free money', 'get rich',
            'miracle cure', 'instant results', 'guaranteed',
            
            # Medical misinformation
            'cure all', 'miracle drug', 'secret remedy',
            'doctors hate', 'big pharma conspiracy'
        }
    
    def _contains_blocked_content(self, content: str) -> bool:
        """Check if content contains blocked keywords."""
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in self.blocked_keywords)
    
    def _calculate_relevance_score(self, content: str) -> float:
        """Calculate relevance score based on mental health keywords."""
        content_lower = content.lower()
        content_words = set(re.findall(r'\b\w+\b', content_lower))
        
        # Count matching keywords
        matching_keywords = content_words.intersection(self.mental_health_keywords)
        
        if not content_words:
            return 0.0
        
        # Calculate score as ratio of matching keywords to total words
        base_score = len(matching_keywords) / len(content_words)
        
        # Boost score if multiple different keyword categories are present
        category_boost = min(len(matching_keywords) / 10, 0.5)
        
        return min(base_score + category_boost, 1.0)


class MetadataEnricher(BaseTransformer):
    """Transformer for enriching data with additional metadata."""
    
    def __init__(self, **kwargs):
        """Initialize metadata enricher."""
        super().__init__(**kwargs)
        
    def transform(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Enrich data with additional metadata."""
        if not isinstance(data, dict):
            return None
        
        enriched_data = data.copy()
        metadata = enriched_data.get('metadata', {})
        
        # Add processing metadata
        metadata['processed_at'] = datetime.utcnow().isoformat()
        metadata['processor_version'] = '1.0.0'
        
        # Extract content statistics
        content = enriched_data.get('content', '')
        if content:
            metadata['content_stats'] = self._get_content_stats(content)
        
        # Generate content hash for deduplication
        if content:
            import hashlib
            content_hash = hashlib.md5(content.encode()).hexdigest()
            metadata['content_hash'] = content_hash
        
        # Extract language (simple heuristic)
        if content:
            metadata['language'] = self._detect_language(content)
        
        # Categorize content type
        metadata['content_type'] = self._categorize_content(enriched_data)
        
        enriched_data['metadata'] = metadata
        return enriched_data
    
    def _get_content_stats(self, content: str) -> Dict[str, int]:
        """Get basic content statistics."""
        words = re.findall(r'\b\w+\b', content)
        sentences = re.split(r'[.!?]+', content)
        paragraphs = content.split('\n\n')
        
        return {
            'char_count': len(content),
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'paragraph_count': len([p for p in paragraphs if p.strip()]),
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0
        }
    
    def _detect_language(self, content: str) -> str:
        """Simple language detection based on common words."""
        content_lower = content.lower()
        
        # English indicators
        english_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        english_count = sum(1 for word in english_words if word in content_lower)
        
        # French indicators
        french_words = {'le', 'la', 'les', 'de', 'du', 'des', 'et', 'ou', 'dans', 'sur', 'avec', 'pour'}
        french_count = sum(1 for word in french_words if word in content_lower)
        
        if english_count > french_count:
            return 'en'
        elif french_count > 0:
            return 'fr'
        else:
            return 'unknown'
    
    def _categorize_content(self, data: Dict[str, Any]) -> str:
        """Categorize content based on structure and content."""
        content = data.get('content', '')
        title = data.get('title', '')
        
        # Check for specific patterns
        if 'questionnaire' in title.lower() or 'survey' in title.lower():
            return 'questionnaire'
        elif 'therapy' in content.lower() or 'treatment' in content.lower():
            return 'therapy_guide'
        elif 'research' in title.lower() or 'study' in title.lower():
            return 'research_paper'
        elif len(content.split('\n')) > 10:
            return 'article'
        else:
            return 'general'


class TransformerPipeline:
    """Pipeline for applying multiple transformers in sequence."""
    
    def __init__(self, transformers: List[BaseTransformer]):
        """
        Initialize transformer pipeline.
        
        Args:
            transformers: List of transformers to apply in order
        """
        self.transformers = transformers
        
    def transform(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Apply all transformers in sequence.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Transformed data or None if any transformer rejects it
        """
        current_data = data
        
        for transformer in self.transformers:
            try:
                current_data = transformer.transform(current_data)
                if current_data is None:
                    logger.debug(f"Data rejected by {transformer.__class__.__name__}")
                    return None
            except Exception as e:
                logger.error(f"Error in {transformer.__class__.__name__}: {e}")
                return None
        
        return current_data
    
    def transform_batch(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform a batch of data records.
        
        Args:
            data_list: List of data dictionaries
            
        Returns:
            List of successfully transformed data records
        """
        results = []
        
        for data in data_list:
            transformed = self.transform(data)
            if transformed is not None:
                results.append(transformed)
        
        return results


# Convenience functions
def create_default_pipeline() -> TransformerPipeline:
    """Create a default transformer pipeline for mental health data."""
    transformers = [
        TextCleaner(
            remove_html=True,
            normalize_whitespace=True,
            min_length=10,  # Reduced from 50
            max_length=100000,  # Increased from 50000
            remove_special_chars=False  # Less aggressive
        ),
        FieldStandardizer(
            required_fields=['content'],
            default_values={
                'category': 'general',
                'language': 'en'
            }
        ),
        ContentValidator(
            min_relevance_score=0.1
        ),
        MetadataEnricher()
    ]
    
    return TransformerPipeline(transformers)


def transform_data(data: Dict[str, Any], pipeline: Optional[TransformerPipeline] = None) -> Optional[Dict[str, Any]]:
    """
    Transform a single data record using the default or provided pipeline.
    
    Args:
        data: Input data dictionary
        pipeline: Optional custom pipeline (uses default if None)
        
    Returns:
        Transformed data or None if rejected
    """
    if pipeline is None:
        pipeline = create_default_pipeline()
    
    return pipeline.transform(data)

