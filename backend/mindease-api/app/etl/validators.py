"""
ETL Validators Module

This module provides comprehensive data quality validation for the MindEase ETL pipeline.
Ensures data integrity, mental health relevance, and safety before database loading.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCategory(Enum):
    """Categories of validation checks."""
    CONTENT_QUALITY = "content_quality"
    MENTAL_HEALTH_RELEVANCE = "mental_health_relevance"
    SAFETY = "safety"
    DATA_INTEGRITY = "data_integrity"
    FORMATTING = "formatting"
    METADATA = "metadata"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    category: ValidationCategory
    level: ValidationLevel
    message: str
    field: Optional[str] = None
    value: Optional[str] = None
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "level": self.level.value,
            "message": self.message,
            "field": self.field,
            "value": self.value,
            "suggestion": self.suggestion
        }


@dataclass
class ValidationReport:
    """Complete validation report for a dataset."""
    total_items: int
    valid_items: int
    invalid_items: int
    warnings: int
    errors: int
    critical_issues: int
    results: List[ValidationResult]
    processing_time: float
    
    @property
    def success_rate(self) -> float:
        return self.valid_items / self.total_items if self.total_items > 0 else 0
    
    @property
    def is_valid(self) -> bool:
        return self.critical_issues == 0 and self.errors == 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_items": self.total_items,
            "valid_items": self.valid_items,
            "invalid_items": self.invalid_items,
            "warnings": self.warnings,
            "errors": self.errors,
            "critical_issues": self.critical_issues,
            "success_rate": self.success_rate,
            "is_valid": self.is_valid,
            "processing_time": self.processing_time,
            "results": [result.to_dict() for result in self.results]
        }


class BaseValidator:
    """Base class for all validators."""
    
    def __init__(self, name: str):
        self.name = name
        
    async def validate(self, data: Any) -> List[ValidationResult]:
        """Validate data and return results."""
        raise NotImplementedError
    
    def _create_result(
        self,
        category: ValidationCategory,
        level: ValidationLevel,
        message: str,
        field: Optional[str] = None,
        value: Optional[str] = None,
        suggestion: Optional[str] = None
    ) -> ValidationResult:
        """Helper to create validation results."""
        return ValidationResult(
            category=category,
            level=level,
            message=message,
            field=field,
            value=value,
            suggestion=suggestion
        )


class ContentQualityValidator(BaseValidator):
    """Validates content quality and completeness."""
    def __init__(self, min_content_length=50, max_content_length=50000, 
                 min_title_length=5, max_title_length=200):
        super().__init__("ContentQualityValidator")
        self.min_content_length = min_content_length
        self.max_content_length = max_content_length
        self.min_title_length = min_title_length
        self.max_title_length = max_title_length
        
    async def validate(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate content quality."""
        results = []
        
        # Validate title
        title = data.get('title', '').strip()
        if not title:
            results.append(self._create_result(
                ValidationCategory.CONTENT_QUALITY,
                ValidationLevel.ERROR,
                "Title is required",
                field="title",
                suggestion="Provide a descriptive title"
            ))
        elif len(title) < self.min_title_length:
            results.append(self._create_result(
                ValidationCategory.CONTENT_QUALITY,
                ValidationLevel.WARNING,
                f"Title too short (minimum {self.min_title_length} characters)",
                field="title",
                value=title,
                suggestion="Provide a more descriptive title"
            ))
        elif len(title) > self.max_title_length:
            results.append(self._create_result(
                ValidationCategory.CONTENT_QUALITY,
                ValidationLevel.ERROR,
                f"Title too long (maximum {self.max_title_length} characters)",
                field="title",
                value=title[:50] + "...",
                suggestion="Shorten the title"
            ))
        
        # Validate content
        content = data.get('content', '').strip()
        if not content:
            results.append(self._create_result(
                ValidationCategory.CONTENT_QUALITY,
                ValidationLevel.ERROR,
                "Content is required",
                field="content",
                suggestion="Provide meaningful content"
            ))
        elif len(content) < self.min_content_length:
            results.append(self._create_result(
                ValidationCategory.CONTENT_QUALITY,
                ValidationLevel.WARNING,
                f"Content too short (minimum {self.min_content_length} characters)",
                field="content",
                value=f"{len(content)} characters",
                suggestion="Provide more detailed content"
            ))
        elif len(content) > self.max_content_length:
            results.append(self._create_result(
                ValidationCategory.CONTENT_QUALITY,
                ValidationLevel.ERROR,
                f"Content too long (maximum {self.max_content_length} characters)",
                field="content",
                value=f"{len(content)} characters",
                suggestion="Split into multiple documents"
            ))
        
        # Check for meaningful content (not just whitespace/special chars)
        if content:
            word_count = len(content.split())
            if word_count < 10:
                results.append(self._create_result(
                    ValidationCategory.CONTENT_QUALITY,
                    ValidationLevel.WARNING,
                    f"Content has very few words ({word_count})",
                    field="content",
                    suggestion="Provide more substantial content"
                ))
            
            # Check for excessive repetition
            words = content.lower().split()
            if len(words) > 0:
                unique_words = set(words)
                repetition_ratio = len(unique_words) / len(words)
                if repetition_ratio < 0.3:
                    results.append(self._create_result(
                        ValidationCategory.CONTENT_QUALITY,
                        ValidationLevel.WARNING,
                        f"High word repetition detected ({repetition_ratio:.2%} unique)",
                        field="content",
                        suggestion="Reduce repetitive content"
                    ))
        
        return results


class MentalHealthRelevanceValidator(BaseValidator):
    """Validates mental health relevance of content."""
    
    def __init__(self, min_relevance_score=0.5):  # Add parameter
        super().__init__("MentalHealthRelevanceValidator")
        self.min_relevance_score = min_relevance_score
        
        # Mental health keywords and phrases
        self.mental_health_keywords = {
            'primary': {
                'anxiety', 'depression', 'stress', 'therapy', 'counseling', 'mental health',
                'psychological', 'psychiatry', 'psychotherapy', 'cognitive behavioral',
                'mindfulness', 'meditation', 'wellbeing', 'wellness', 'self-care',
                'emotional', 'mood', 'feelings', 'coping', 'resilience', 'trauma',
                'ptsd', 'bipolar', 'adhd', 'ocd', 'panic', 'phobia', 'addiction',
                'recovery', 'healing', 'support', 'therapeutic', 'intervention'
            },
            'secondary': {
                'health', 'care', 'treatment', 'diagnosis', 'symptoms', 'disorder',
                'condition', 'behavior', 'behavioral', 'social', 'relationship',
                'communication', 'confidence', 'self-esteem', 'motivation',
                'goal', 'progress', 'improvement', 'growth', 'development',
                'skill', 'technique', 'strategy', 'exercise', 'practice'
            },
            'therapeutic_approaches': {
                'cbt', 'dbt', 'emdr', 'act', 'mindfulness-based', 'solution-focused',
                'psychodynamic', 'humanistic', 'gestalt', 'narrative therapy',
                'family therapy', 'group therapy', 'art therapy', 'music therapy'
            }
        }
        
        # Categories for mental health content
        self.mental_health_categories = {
            'anxiety_disorders', 'mood_disorders', 'trauma_ptsd', 'addiction_recovery',
            'relationship_issues', 'self_esteem', 'stress_management', 'coping_skills',
            'therapeutic_techniques', 'mindfulness_meditation', 'cognitive_behavioral',
            'emotional_regulation', 'social_skills', 'life_transitions', 'grief_loss'
        }
        
    async def validate(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate mental health relevance."""
        results = []
        
        title = data.get('title', '').lower()
        content = data.get('content', '').lower()
        category = data.get('category', '').lower()
        
        # Calculate relevance score
        relevance_score = self._calculate_relevance_score(title + ' ' + content)
        
        if relevance_score < 0.1:
            results.append(self._create_result(
                ValidationCategory.MENTAL_HEALTH_RELEVANCE,
                ValidationLevel.ERROR,
                f"Low mental health relevance (score: {relevance_score:.2f})",
                field="content",
                suggestion="Ensure content is related to mental health topics"
            ))
        elif relevance_score < 0.3:
            results.append(self._create_result(
                ValidationCategory.MENTAL_HEALTH_RELEVANCE,
                ValidationLevel.WARNING,
                f"Moderate mental health relevance (score: {relevance_score:.2f})",
                field="content",
                suggestion="Consider adding more mental health context"
            ))
        else:
            results.append(self._create_result(
                ValidationCategory.MENTAL_HEALTH_RELEVANCE,
                ValidationLevel.INFO,
                f"Good mental health relevance (score: {relevance_score:.2f})",
                field="content"
            ))
        
        # Validate category
        if category and category not in self.mental_health_categories:
            results.append(self._create_result(
                ValidationCategory.MENTAL_HEALTH_RELEVANCE,
                ValidationLevel.WARNING,
                f"Category '{category}' not in standard mental health categories",
                field="category",
                suggestion=f"Consider using: {', '.join(list(self.mental_health_categories)[:5])}"
            ))
        
        # Check for therapeutic approach mentions
        therapeutic_mentions = self._find_therapeutic_approaches(content)
        if therapeutic_mentions:
            results.append(self._create_result(
                ValidationCategory.MENTAL_HEALTH_RELEVANCE,
                ValidationLevel.INFO,
                f"Therapeutic approaches mentioned: {', '.join(therapeutic_mentions)}",
                field="content"
            ))
        
        return results
    
    def _calculate_relevance_score(self, text: str) -> float:
        """Calculate mental health relevance score."""
        words = set(text.lower().split())
        
        primary_matches = len(words.intersection(self.mental_health_keywords['primary']))
        secondary_matches = len(words.intersection(self.mental_health_keywords['secondary']))
        therapeutic_matches = len(words.intersection(self.mental_health_keywords['therapeutic_approaches']))
        
        # Weighted scoring
        score = (
            primary_matches * 0.6 +
            secondary_matches * 0.3 +
            therapeutic_matches * 0.8
        ) / max(len(words), 1)
        
        return min(score, 1.0)
    
    def _find_therapeutic_approaches(self, text: str) -> List[str]:
        """Find mentioned therapeutic approaches."""
        found = []
        for approach in self.mental_health_keywords['therapeutic_approaches']:
            if approach in text:
                found.append(approach)
        return found


class SafetyValidator(BaseValidator):
    """Validates content safety and appropriateness."""
    
    def __init__(self):
        super().__init__("SafetyValidator")
        
        # Harmful content patterns
        self.harmful_patterns = {
            'self_harm': [
                r'\bsuicid[e|al]\b', r'\bself.?harm\b', r'\bcut(?:ting)?\s+(?:myself|yourself)\b',
                r'\bkill\s+(?:myself|yourself)\b', r'\bend\s+(?:my|your)\s+life\b'
            ],
            'violence': [
                r'\bhurt\s+(?:someone|others)\b', r'\bviolent\s+thoughts\b',
                r'\bharm\s+(?:someone|others)\b'
            ],
            'substance_abuse': [
                r'\bdrug\s+abuse\b', r'\boverdose\b', r'\baddiction\s+(?:to|with)\b'
            ],
            'inappropriate': [
                r'\bexplicit\b', r'\binappropriate\s+content\b'
            ]
        }
        
        # Crisis keywords that need special handling
        self.crisis_keywords = {
            'suicide', 'self-harm', 'overdose', 'crisis', 'emergency',
            'immediate danger', 'harm myself', 'end my life'
        }
        
    async def validate(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate content safety."""
        results = []
        
        title = data.get('title', '')
        content = data.get('content', '')
        full_text = (title + ' ' + content).lower()
        
        # Check for harmful patterns
        for category, patterns in self.harmful_patterns.items():
            for pattern in patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    results.append(self._create_result(
                        ValidationCategory.SAFETY,
                        ValidationLevel.CRITICAL,
                        f"Potentially harmful content detected: {category}",
                        field="content",
                        suggestion="Review content for safety and add appropriate warnings"
                    ))
        
        # Check for crisis keywords
        crisis_found = []
        for keyword in self.crisis_keywords:
            if keyword in full_text:
                crisis_found.append(keyword)
        
        if crisis_found:
            results.append(self._create_result(
                ValidationCategory.SAFETY,
                ValidationLevel.WARNING,
                f"Crisis-related content detected: {', '.join(crisis_found)}",
                field="content",
                suggestion="Ensure appropriate crisis resources and warnings are included"
            ))
        
        # Check for medical advice disclaimers
        if any(term in full_text for term in ['treatment', 'medication', 'diagnosis', 'medical']):
            if 'disclaimer' not in full_text and 'professional' not in full_text:
                results.append(self._create_result(
                    ValidationCategory.SAFETY,
                    ValidationLevel.WARNING,
                    "Medical content without professional disclaimer",
                    field="content",
                    suggestion="Add disclaimer about seeking professional medical advice"
                ))
        
        return results


class DataIntegrityValidator(BaseValidator):
    """Validates data integrity and consistency."""
    
    def __init__(self):
        super().__init__("DataIntegrityValidator")
        
    async def validate(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate data integrity."""
        results = []
        
        # Check required fields
        required_fields = ['title', 'content']
        for field in required_fields:
            if field not in data or not data[field]:
                results.append(self._create_result(
                    ValidationCategory.DATA_INTEGRITY,
                    ValidationLevel.ERROR,
                    f"Required field '{field}' is missing or empty",
                    field=field,
                    suggestion=f"Provide a value for {field}"
                ))
        
        # Validate data types
        string_fields = ['title', 'content', 'category', 'source']
        for field in string_fields:
            if field in data and not isinstance(data[field], str):
                results.append(self._create_result(
                    ValidationCategory.DATA_INTEGRITY,
                    ValidationLevel.ERROR,
                    f"Field '{field}' must be a string",
                    field=field,
                    value=str(type(data[field])),
                    suggestion=f"Convert {field} to string"
                ))
        
        # Validate metadata structure
        metadata = data.get('metadata', {})
        if metadata and not isinstance(metadata, dict):
            results.append(self._create_result(
                ValidationCategory.DATA_INTEGRITY,
                ValidationLevel.ERROR,
                "Metadata must be a dictionary",
                field="metadata",
                suggestion="Ensure metadata is properly formatted as key-value pairs"
            ))
        
        # Check for duplicate detection fields
        if 'id' in data or 'external_id' in data:
            results.append(self._create_result(
                ValidationCategory.DATA_INTEGRITY,
                ValidationLevel.INFO,
                "Document has identifier for duplicate detection",
                field="id"
            ))
        
        # Validate timestamps if present
        timestamp_fields = ['created_at', 'updated_at', 'published_at']
        for field in timestamp_fields:
            if field in data:
                try:
                    if isinstance(data[field], str):
                        datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                    elif not isinstance(data[field], datetime):
                        results.append(self._create_result(
                            ValidationCategory.DATA_INTEGRITY,
                            ValidationLevel.WARNING,
                            f"Invalid timestamp format in '{field}'",
                            field=field,
                            suggestion="Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                        ))
                except ValueError:
                    results.append(self._create_result(
                        ValidationCategory.DATA_INTEGRITY,
                        ValidationLevel.WARNING,
                        f"Invalid timestamp format in '{field}'",
                        field=field,
                        suggestion="Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                    ))
        
        return results


class FormattingValidator(BaseValidator):
    """Validates content formatting and structure."""
    
    def __init__(self):
        super().__init__("FormattingValidator")
        
    async def validate(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate formatting."""
        results = []
        
        content = data.get('content', '')
        
        # Check for HTML tags
        html_pattern = r'<[^>]+>'
        if re.search(html_pattern, content):
            results.append(self._create_result(
                ValidationCategory.FORMATTING,
                ValidationLevel.WARNING,
                "HTML tags detected in content",
                field="content",
                suggestion="Consider removing HTML tags or converting to markdown"
            ))
        
        # Check for excessive whitespace
        if re.search(r'\s{3,}', content):
            results.append(self._create_result(
                ValidationCategory.FORMATTING,
                ValidationLevel.INFO,
                "Excessive whitespace detected",
                field="content",
                suggestion="Clean up extra whitespace"
            ))
        
        # Check for proper sentence structure
        sentences = content.split('.')
        if len(sentences) > 1:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_sentence_length > 50:
                results.append(self._create_result(
                    ValidationCategory.FORMATTING,
                    ValidationLevel.INFO,
                    f"Long average sentence length ({avg_sentence_length:.1f} words)",
                    field="content",
                    suggestion="Consider breaking up long sentences"
                ))
        
        # Check for special characters that might cause issues
        problematic_chars = ['�', '\x00', '\ufffd']
        for char in problematic_chars:
            if char in content:
                results.append(self._create_result(
                    ValidationCategory.FORMATTING,
                    ValidationLevel.WARNING,
                    f"Problematic character detected: {repr(char)}",
                    field="content",
                    suggestion="Remove or replace problematic characters"
                ))
        
        return results


class MetadataValidator(BaseValidator):
    """Validates metadata completeness and accuracy."""
    
    def __init__(self):
        super().__init__("MetadataValidator")
        
        self.valid_categories = {
            'anxiety_disorders', 'mood_disorders', 'trauma_ptsd', 'addiction_recovery',
            'relationship_issues', 'self_esteem', 'stress_management', 'coping_skills',
            'therapeutic_techniques', 'mindfulness_meditation', 'cognitive_behavioral',
            'emotional_regulation', 'social_skills', 'life_transitions', 'grief_loss',
            'general'
        }
        
        self.valid_sources = {
            'research_paper', 'clinical_guide', 'therapy_manual', 'self_help',
            'educational_material', 'case_study', 'treatment_protocol', 'assessment_tool',
            'user_generated', 'expert_content', 'unknown'
        }
        
    async def validate(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate metadata."""
        results = []
        
        # Validate category
        category = data.get('category', '').lower()
        if category and category not in self.valid_categories:
            results.append(self._create_result(
                ValidationCategory.METADATA,
                ValidationLevel.WARNING,
                f"Unknown category: {category}",
                field="category",
                suggestion=f"Use one of: {', '.join(list(self.valid_categories)[:5])}"
            ))
        elif not category:
            results.append(self._create_result(
                ValidationCategory.METADATA,
                ValidationLevel.INFO,
                "No category specified, will default to 'general'",
                field="category",
                suggestion="Specify a relevant category"
            ))
        
        # Validate source
        source = data.get('source', '').lower()
        if source and source not in self.valid_sources:
            results.append(self._create_result(
                ValidationCategory.METADATA,
                ValidationLevel.INFO,
                f"Unknown source type: {source}",
                field="source",
                suggestion=f"Consider using: {', '.join(list(self.valid_sources)[:5])}"
            ))
        
        # Check metadata completeness
        metadata = data.get('metadata', {})
        recommended_fields = ['author', 'publication_date', 'language', 'target_audience']
        missing_fields = [field for field in recommended_fields if field not in metadata]
        
        if missing_fields:
            results.append(self._create_result(
                ValidationCategory.METADATA,
                ValidationLevel.INFO,
                f"Recommended metadata fields missing: {', '.join(missing_fields)}",
                field="metadata",
                suggestion="Add recommended metadata for better categorization"
            ))
        
        # Validate language if specified
        language = metadata.get('language', '').lower()
        if language and language not in ['en', 'fr', 'es', 'de', 'it', 'pt']:
            results.append(self._create_result(
                ValidationCategory.METADATA,
                ValidationLevel.WARNING,
                f"Unsupported language: {language}",
                field="metadata.language",
                suggestion="Use supported language codes (en, fr, es, de, it, pt)"
            ))
        
        return results


class ETLValidator:
    def __init__(self, enable_all: bool = True, config: dict = None):
        self.validators = []
        config = config or {}
        
        if enable_all:
            # Use default configuration
            self.validators = [
                ContentQualityValidator(min_content_length=10),
                MentalHealthRelevanceValidator(min_relevance_score=0.5),
                SafetyValidator(),
                DataIntegrityValidator(),
                FormattingValidator(),
                MetadataValidator()
            ]
        else:
            # Use custom configuration
            self.validators = [
                ContentQualityValidator(**config.get('content_quality', {})),
                MentalHealthRelevanceValidator(**config.get('relevance', {})),
                SafetyValidator(),
                DataIntegrityValidator(),
                FormattingValidator(),
                MetadataValidator()
            ]
    
    def add_validator(self, validator: BaseValidator):
        """Add a custom validator."""
        self.validators.append(validator)
    
    def remove_validator(self, validator_name: str):
        """Remove a validator by name."""
        self.validators = [v for v in self.validators if v.name != validator_name]
    
    async def validate_item(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate a single data item."""
        all_results = []
        
        for validator in self.validators:
            try:
                results = await validator.validate(data)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Validator {validator.name} failed: {str(e)}")
                all_results.append(ValidationResult(
                    category=ValidationCategory.DATA_INTEGRITY,
                    level=ValidationLevel.ERROR,
                    message=f"Validation failed: {str(e)}",
                    field="validator_error"
                ))
        
        return all_results
    
    async def validate_dataset(
        self, 
        dataset: List[Dict[str, Any]],
        max_concurrent: int = 10
    ) -> ValidationReport:
        """Validate an entire dataset."""
        start_time = datetime.utcnow()
        
        logger.info(f"Starting validation of {len(dataset)} items")
        
        # Process items concurrently
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def validate_with_semaphore(item):
            async with semaphore:
                return await self.validate_item(item)
        
        # Run validations
        validation_tasks = [validate_with_semaphore(item) for item in dataset]
        all_results = await asyncio.gather(*validation_tasks, return_exceptions=True)
        
        # Compile results
        total_results = []
        valid_items = 0
        invalid_items = 0
        warnings = 0
        errors = 0
        critical_issues = 0
        
        for i, results in enumerate(all_results):
            if isinstance(results, Exception):
                logger.error(f"Validation failed for item {i}: {str(results)}")
                invalid_items += 1
                errors += 1
                continue
            
            total_results.extend(results)
            
            # Count severity levels for this item
            item_errors = sum(1 for r in results if r.level == ValidationLevel.ERROR)
            item_critical = sum(1 for r in results if r.level == ValidationLevel.CRITICAL)
            item_warnings = sum(1 for r in results if r.level == ValidationLevel.WARNING)
            
            if item_critical > 0 or item_errors > 0:
                invalid_items += 1
            else:
                valid_items += 1
            
            warnings += item_warnings
            errors += item_errors
            critical_issues += item_critical
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        report = ValidationReport(
            total_items=len(dataset),
            valid_items=valid_items,
            invalid_items=invalid_items,
            warnings=warnings,
            errors=errors,
            critical_issues=critical_issues,
            results=total_results,
            processing_time=processing_time
        )
        
        logger.info(f"Validation completed in {processing_time:.2f}s: "
                   f"{valid_items}/{len(dataset)} valid items")
        
        return report
    
    async def validate_and_filter(
        self, 
        dataset: List[Dict[str, Any]],
        allow_warnings: bool = True,
        allow_errors: bool = False
    ) -> Tuple[List[Dict[str, Any]], ValidationReport]:
        """
        Validate dataset and return filtered valid items.
        
        Args:
            dataset: List of data items to validate
            allow_warnings: Whether to include items with warnings
            allow_errors: Whether to include items with errors
            
        Returns:
            Tuple of (valid_items, validation_report)
        """
        report = await self.validate_dataset(dataset)
        
        # Group results by item index
        item_results = {}
        current_index = 0
        
        for result in report.results:
            # This is a simplified approach - in practice, you'd need to track
            # which results belong to which items more precisely
            if current_index not in item_results:
                item_results[current_index] = []
            item_results[current_index].append(result)
            
            # Move to next item when we hit certain conditions
            # This is a heuristic and could be improved
            if len(item_results[current_index]) >= 3:
                current_index += 1
        
        # Filter items based on validation results
        valid_items = []
        for i, item in enumerate(dataset):
            item_validation_results = item_results.get(i, [])
            
            has_critical = any(r.level == ValidationLevel.CRITICAL for r in item_validation_results)
            has_errors = any(r.level == ValidationLevel.ERROR for r in item_validation_results)
            has_warnings = any(r.level == ValidationLevel.WARNING for r in item_validation_results)
            
            # Include item based on filtering criteria
            if has_critical:
                continue  # Never include critical issues
            elif has_errors and not allow_errors:
                continue
            elif has_warnings and not allow_warnings:
                continue
            else:
                valid_items.append(item)
        
        logger.info(f"Filtered dataset: {len(valid_items)}/{len(dataset)} items passed validation")
        
        return valid_items, report


# Utility functions for common validation operations

async def validate_document(document: Dict[str, Any]) -> ValidationReport:
    """Validate a single document."""
    validator = ETLValidator()
    results = await validator.validate_item(document)
    
    # Create a simple report for single item
    warnings = sum(1 for r in results if r.level == ValidationLevel.WARNING)
    errors = sum(1 for r in results if r.level == ValidationLevel.ERROR)
    critical = sum(1 for r in results if r.level == ValidationLevel.CRITICAL)
    
    return ValidationReport(
        total_items=1,
        valid_items=1 if critical == 0 and errors == 0 else 0,
        invalid_items=1 if critical > 0 or errors > 0 else 0,
        warnings=warnings,
        errors=errors,
        critical_issues=critical,
        results=results,
        processing_time=0.0
    )


async def quick_safety_check(content: str) -> bool:
    """Quick safety check for content."""
    validator = SafetyValidator()
    results = await validator.validate({'content': content})
    
    # Return False if any critical safety issues found
    return not any(r.level == ValidationLevel.CRITICAL for r in results)


async def calculate_mental_health_relevance(content: str) -> float:
    """Calculate mental health relevance score for content."""
    validator = MentalHealthRelevanceValidator()
    return validator._calculate_relevance_score(content)

__all__ = [
  "ValidationLevel",
  "ValidationCategory",
  "ValidationResult",
  "ValidationReport",
  "BaseValidator",
  "ETLValidator",
]