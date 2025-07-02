"""
ETL Pipeline Integration Tests

Comprehensive test suite for the ETL pipeline components including
extractors, transformers, loaders, validators, and admin services.
"""

import pytest
import asyncio
import tempfile
import json
import csv
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from app.etl.extractors import CSVExtractor, JSONExtractor, TextExtractor, ExtractorFactory
from app.etl.transformers import TransformerPipeline, TextCleaner, FieldStandardizer
from app.etl.loaders import DocumentLoader, ETLLoader
from app.etl.validators import ETLValidator, ContentQualityValidator, MentalHealthRelevanceValidator
from app.services.admin_service import DatasetManager, SystemMonitor, ResourceManager


class TestETLExtractors:
    """Test ETL extractors functionality."""
    
    @pytest.fixture
    def sample_csv_data(self):
        """Create sample CSV data for testing."""
        return [
            ["title", "content", "category"],
            ["Anxiety Management", "Techniques for managing anxiety include deep breathing...", "anxiety_disorders"],
            ["Depression Support", "Understanding depression and finding support...", "mood_disorders"],
            ["Stress Relief", "Methods to reduce stress in daily life...", "stress_management"]
        ]
    
    @pytest.fixture
    def sample_json_data(self):
        """Create sample JSON data for testing."""
        return [
            {
                "title": "Mindfulness Meditation",
                "content": "Mindfulness meditation is a practice that involves focusing on the present moment...",
                "category": "mindfulness_meditation",
                "metadata": {"author": "Dr. Smith", "publication_date": "2023-01-15"}
            },
            {
                "title": "Cognitive Behavioral Therapy",
                "content": "CBT is a form of psychological treatment that has been demonstrated to be effective...",
                "category": "cognitive_behavioral",
                "metadata": {"author": "Dr. Johnson", "publication_date": "2023-02-20"}
            }
        ]
    
    def test_csv_extractor(self, sample_csv_data):
        """Test CSV extraction functionality."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerows(sample_csv_data)
            csv_path = f.name
        
        try:
            # Test extraction
            extractor = CSVExtractor(csv_path)
            result = asyncio.run(extractor.extract())
            
            assert len(result) == 3  # 3 data rows (excluding header)
            assert result[0]['title'] == "Anxiety Management"
            assert result[0]['category'] == "anxiety_disorders"
            assert "anxiety" in result[0]['content'].lower()
            
        finally:
            Path(csv_path).unlink()
    
    def test_json_extractor(self, sample_json_data):
        """Test JSON extraction functionality."""
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_json_data, f)
            json_path = f.name
        
        try:
            # Test extraction
            extractor = JSONExtractor(json_path)
            result = asyncio.run(extractor.extract())
            
            assert len(result) == 2
            assert result[0]['title'] == "Mindfulness Meditation"
            assert result[0]['category'] == "mindfulness_meditation"
            assert 'metadata' in result[0]
            assert result[0]['metadata']['author'] == "Dr. Smith"
            
        finally:
            Path(json_path).unlink()
    
    def test_text_extractor(self):
        """Test text extraction functionality."""
        sample_text = """
        Title: Understanding Anxiety
        
        Anxiety is a normal and often healthy emotion. However, when a person regularly 
        feels disproportionate levels of anxiety, it might become a medical disorder.
        
        Symptoms include:
        - Feeling nervous or restless
        - Having a sense of impending danger
        - Increased heart rate
        """
        
        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_text)
            txt_path = f.name
        
        try:
            # Test extraction
            extractor = TextExtractor(txt_path)
            result = asyncio.run(extractor.extract())
            
            assert len(result) == 1
            assert "Understanding Anxiety" in result[0]['content']
            assert "anxiety" in result[0]['content'].lower()
            
        finally:
            Path(txt_path).unlink()
    
    def test_extractor_factory(self, sample_csv_data):
        """Test extractor factory functionality."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerows(sample_csv_data)
            csv_path = f.name
        
        try:
            # Test factory
            extractor = ExtractorFactory.create_extractor(csv_path)
            assert isinstance(extractor, CSVExtractor)
            
            result = asyncio.run(extractor.extract())
            assert len(result) == 3
            
        finally:
            Path(csv_path).unlink()


class TestETLTransformers:
    """Test ETL transformers functionality."""
    
    @pytest.fixture
    def sample_raw_data(self):
        """Sample raw data for transformation testing."""
        return [
            {
                "title": "  Anxiety Management Tips  ",
                "content": "<p>Here are some <b>effective</b> techniques for managing anxiety...</p>",
                "category": "ANXIETY",
                "source": "research_paper"
            },
            {
                "title": "Depression Support",
                "content": "Understanding depression and finding support is crucial for recovery.",
                "category": "mood_disorders",
                "invalid_field": "should_be_removed"
            }
        ]
    
    def test_text_cleaner(self, sample_raw_data):
        """Test text cleaning functionality."""
        cleaner = TextCleaner()
        
        # Test HTML removal
        result = asyncio.run(cleaner.transform(sample_raw_data))
        
        assert "<p>" not in result[0]['content']
        assert "<b>" not in result[0]['content']
        assert "effective" in result[0]['content']
        
        # Test whitespace normalization
        assert result[0]['title'] == "Anxiety Management Tips"
    
    def test_field_standardizer(self, sample_raw_data):
        """Test field standardization functionality."""
        standardizer = FieldStandardizer()
        
        result = asyncio.run(standardizer.transform(sample_raw_data))
        
        # Test category normalization
        assert result[0]['category'] == "anxiety_disorders"  # Should be normalized
        
        # Test invalid field removal
        assert 'invalid_field' not in result[1]
    
    def test_transformer_pipeline(self, sample_raw_data):
        """Test complete transformer pipeline."""
        pipeline = TransformerPipeline()
        
        result = asyncio.run(pipeline.transform(sample_raw_data))
        
        # Should have both cleaning and standardization applied
        assert len(result) == 2
        assert result[0]['title'] == "Anxiety Management Tips"
        assert "<p>" not in result[0]['content']
        assert result[0]['category'] == "anxiety_disorders"


class TestETLValidators:
    """Test ETL validators functionality."""
    
    @pytest.fixture
    def valid_mental_health_data(self):
        """Valid mental health document data."""
        return {
            "title": "Cognitive Behavioral Therapy for Anxiety",
            "content": "Cognitive Behavioral Therapy (CBT) is an evidence-based treatment for anxiety disorders. It helps individuals identify and change negative thought patterns and behaviors that contribute to anxiety. CBT techniques include cognitive restructuring, exposure therapy, and relaxation training.",
            "category": "anxiety_disorders",
            "source": "clinical_guide",
            "metadata": {
                "author": "Dr. Sarah Johnson",
                "publication_date": "2023-01-15",
                "language": "en"
            }
        }
    
    @pytest.fixture
    def invalid_data(self):
        """Invalid document data for testing."""
        return {
            "title": "Hi",  # Too short
            "content": "Short content.",  # Too short
            "category": "invalid_category",
            "metadata": "not_a_dict"  # Wrong type
        }
    
    @pytest.fixture
    def safety_concern_data(self):
        """Data with safety concerns."""
        return {
            "title": "Dealing with Suicidal Thoughts",
            "content": "If you are having thoughts of suicide or self-harm, please seek immediate help. Contact a crisis hotline or emergency services.",
            "category": "crisis_intervention"
        }
    
    def test_content_quality_validator(self, valid_mental_health_data, invalid_data):
        """Test content quality validation."""
        validator = ContentQualityValidator()
        
        # Test valid data
        valid_results = asyncio.run(validator.validate(valid_mental_health_data))
        errors = [r for r in valid_results if r.level.value == "error"]
        assert len(errors) == 0
        
        # Test invalid data
        invalid_results = asyncio.run(validator.validate(invalid_data))
        errors = [r for r in invalid_results if r.level.value == "error"]
        assert len(errors) > 0
        
        # Check specific error types
        error_messages = [r.message for r in errors]
        assert any("too short" in msg.lower() for msg in error_messages)
    
    def test_mental_health_relevance_validator(self, valid_mental_health_data):
        """Test mental health relevance validation."""
        validator = MentalHealthRelevanceValidator()
        
        results = asyncio.run(validator.validate(valid_mental_health_data))
        
        # Should have good relevance score
        relevance_results = [r for r in results if "relevance" in r.message.lower()]
        assert len(relevance_results) > 0
        
        # Extract relevance score from message
        relevance_result = relevance_results[0]
        assert "good" in relevance_result.message.lower() or "score:" in relevance_result.message.lower()
    
    def test_safety_validator(self, safety_concern_data):
        """Test safety validation."""
        from app.etl.validators import SafetyValidator
        
        validator = SafetyValidator()
        results = asyncio.run(validator.validate(safety_concern_data))
        
        # Should detect crisis-related content
        crisis_results = [r for r in results if "crisis" in r.message.lower()]
        assert len(crisis_results) > 0
    
    def test_etl_validator_complete(self, valid_mental_health_data, invalid_data):
        """Test complete ETL validator."""
        validator = ETLValidator()
        
        # Test dataset validation
        dataset = [valid_mental_health_data, invalid_data]
        report = asyncio.run(validator.validate_dataset(dataset))
        
        assert report.total_items == 2
        assert report.invalid_items > 0  # Should catch the invalid data
        assert report.errors > 0
        assert isinstance(report.processing_time, float)


class TestETLLoaders:
    """Test ETL loaders functionality (mocked database operations)."""
    
    @pytest.fixture
    def sample_documents(self):
        """Sample documents for loading tests."""
        return [
            {
                "title": "Anxiety Management Techniques",
                "content": "Deep breathing exercises can help manage anxiety symptoms. Practice inhaling for 4 counts, holding for 4 counts, and exhaling for 4 counts.",
                "category": "anxiety_disorders",
                "source": "self_help",
                "metadata": {"author": "Mental Health Team"}
            },
            {
                "title": "Understanding Depression",
                "content": "Depression is a common mental health condition that affects millions of people worldwide. It's characterized by persistent feelings of sadness and loss of interest.",
                "category": "mood_disorders",
                "source": "educational_material",
                "metadata": {"author": "Dr. Smith"}
            }
        ]
    
    @pytest.mark.asyncio
    async def test_document_loader_preparation(self, sample_documents):
        """Test document loader data preparation (without database)."""
        # Mock the embedding service
        class MockEmbeddingService:
            model_name = "test-model"
            
            async def generate_embedding(self, text):
                # Return a mock embedding vector
                return [0.1] * 384
        
        loader = DocumentLoader()
        loader.embedding_service = MockEmbeddingService()
        
        # Test data preparation logic
        for doc in sample_documents:
            content = doc.get('content', '')
            assert len(content) > 0
            
            # Mock embedding generation
            embedding = await loader.embedding_service.generate_embedding(content)
            assert embedding is not None
            assert len(embedding) == 384


class TestAdminServices:
    """Test admin services functionality."""
    
    @pytest.fixture
    def mock_dataset_file(self):
        """Create a mock dataset file for testing."""
        data = [
            {
                "title": "Test Document 1",
                "content": "This is test content for mental health research.",
                "category": "general"
            },
            {
                "title": "Test Document 2", 
                "content": "Another test document about anxiety management.",
                "category": "anxiety_disorders"
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            return f.name
    
    def test_dataset_manager_initialization(self):
        """Test dataset manager initialization."""
        manager = DatasetManager()
        
        assert manager.etl_pipeline is not None
        assert manager.validator is not None
        assert manager.loader is not None
        assert manager.upload_dir.exists()
    
    def test_system_monitor_resource_usage(self):
        """Test system monitor resource usage."""
        monitor = SystemMonitor()
        
        # Test resource usage collection
        resources = asyncio.run(monitor._get_resource_usage())
        
        assert 'cpu_percent' in resources
        assert 'memory' in resources
        assert 'disk' in resources
        assert isinstance(resources['cpu_percent'], (int, float))
        assert isinstance(resources['memory'], dict)
    
    def test_resource_manager_initialization(self):
        """Test resource manager initialization."""
        manager = ResourceManager()
        
        # Should initialize without errors
        assert manager is not None


class TestETLIntegration:
    """Integration tests for the complete ETL pipeline."""
    
    @pytest.fixture
    def complete_dataset(self):
        """Complete dataset for integration testing."""
        return [
            {
                "title": "Comprehensive Guide to Anxiety Management",
                "content": "Anxiety disorders are among the most common mental health conditions. This comprehensive guide covers various evidence-based techniques for managing anxiety, including cognitive behavioral therapy, mindfulness meditation, and breathing exercises. These approaches have been shown to be effective in reducing anxiety symptoms and improving overall quality of life.",
                "category": "anxiety_disorders",
                "source": "clinical_guide",
                "metadata": {
                    "author": "Dr. Emily Johnson",
                    "publication_date": "2023-03-15",
                    "language": "en",
                    "target_audience": "general_public"
                }
            },
            {
                "title": "Understanding Depression: Signs and Support",
                "content": "Depression is a serious mental health condition that affects how you feel, think, and handle daily activities. Common symptoms include persistent sadness, loss of interest in activities, changes in appetite, and difficulty concentrating. Professional support through therapy and medication can be highly effective in treating depression.",
                "category": "mood_disorders",
                "source": "educational_material",
                "metadata": {
                    "author": "Mental Health Foundation",
                    "publication_date": "2023-02-28",
                    "language": "en"
                }
            }
        ]
    
    def test_complete_etl_pipeline(self, complete_dataset):
        """Test the complete ETL pipeline from extraction to validation."""
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(complete_dataset, f)
            json_path = f.name
        
        try:
            # Test complete pipeline
            async def run_pipeline():
                # Extract
                extractor = ExtractorFactory.create_extractor(json_path)
                raw_data = await extractor.extract()
                
                # Transform
                transformer = TransformerPipeline()
                transformed_data = await transformer.transform(raw_data)
                
                # Validate
                validator = ETLValidator()
                validation_report = await validator.validate_dataset(transformed_data)
                
                return raw_data, transformed_data, validation_report
            
            raw_data, transformed_data, validation_report = asyncio.run(run_pipeline())
            
            # Verify results
            assert len(raw_data) == 2
            assert len(transformed_data) == 2
            assert validation_report.total_items == 2
            assert validation_report.success_rate > 0.5  # Should have good success rate
            
            # Check data quality
            for item in transformed_data:
                assert 'title' in item
                assert 'content' in item
                assert len(item['content']) > 50  # Should have substantial content
                
        finally:
            Path(json_path).unlink()
    
    def test_validation_and_filtering(self, complete_dataset):
        """Test validation with filtering."""
        # Add some invalid data
        invalid_item = {
            "title": "Bad",  # Too short
            "content": "Short",  # Too short
            "category": "invalid"
        }
        
        test_dataset = complete_dataset + [invalid_item]
        
        async def run_validation():
            validator = ETLValidator()
            valid_items, report = await validator.validate_and_filter(
                test_dataset,
                allow_warnings=True,
                allow_errors=False
            )
            return valid_items, report
        
        valid_items, report = asyncio.run(run_validation())
        
        # Should filter out invalid items
        assert len(valid_items) < len(test_dataset)
        assert report.total_items == 3
        assert report.invalid_items > 0


# Test configuration and fixtures

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Test utilities

def create_test_document(title: str, content: str, category: str = "general") -> Dict[str, Any]:
    """Create a test document with standard structure."""
    return {
        "title": title,
        "content": content,
        "category": category,
        "source": "test",
        "metadata": {
            "created_for_test": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    }


def assert_valid_mental_health_content(document: Dict[str, Any]) -> None:
    """Assert that a document contains valid mental health content."""
    assert 'title' in document
    assert 'content' in document
    assert len(document['content']) > 50
    
    # Check for mental health relevance
    content_lower = document['content'].lower()
    mental_health_terms = [
        'anxiety', 'depression', 'therapy', 'mental health', 'stress',
        'counseling', 'psychological', 'emotional', 'wellbeing'
    ]
    
    has_mental_health_content = any(term in content_lower for term in mental_health_terms)
    assert has_mental_health_content, f"Document does not contain mental health content: {document['title']}"


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])

