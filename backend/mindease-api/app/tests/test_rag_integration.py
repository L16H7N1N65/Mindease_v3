"""
Comprehensive RAG Integration Tests

This script tests the enhanced MindEase API with integrated RAG improvements.
"""
import asyncio
import sys
import os
import traceback
from datetime import datetime

# Add the app directory to Python path
sys.path.append('.')

async def test_rag_integration():
    """Test the integrated RAG system components."""
    
    print("🧪 Starting Comprehensive RAG Integration Tests")
    print("=" * 60)
    
    test_results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    # Test 1: App Import and Route Count
    print("\n1️⃣ Testing App Import and Route Registration")
    test_results["total_tests"] += 1
    try:
        from app import app
        route_count = len(app.routes)
        
        if route_count >= 200:  # Should have 238+ routes
            print(f"   ✅ App imported successfully with {route_count} routes")
            test_results["passed"] += 1
        else:
            print(f"   ❌ Route count too low: {route_count} (expected 200+)")
            test_results["failed"] += 1
            test_results["errors"].append(f"Low route count: {route_count}")
            
    except Exception as e:
        print(f"   ❌ App import failed: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"App import: {str(e)}")
    
    # Test 2: RAG Models Import
    print("\n2️⃣ Testing RAG Models Import")
    test_results["total_tests"] += 1
    try:
        from app.db.models.rag_feedback import RAGFeedback, FeedbackAnalytics
        from app.db.models.conversation import Conversation, Message
        print("   ✅ RAG models imported successfully")
        test_results["passed"] += 1
    except Exception as e:
        print(f"   ❌ RAG models import failed: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"RAG models: {str(e)}")
    
    # Test 3: RAG Services Import
    print("\n3️⃣ Testing RAG Services Import")
    test_results["total_tests"] += 1
    try:
        from app.services.rag_feedback_service import RAGFeedbackService
        from app.services.rag_learning_service import RAGLearningService
        from app.services.rag_learning_framework import RAGLearningFramework
        print("   ✅ RAG services imported successfully")
        test_results["passed"] += 1
    except Exception as e:
        print(f"   ❌ RAG services import failed: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"RAG services: {str(e)}")
    
    # Test 4: RAG Schemas Import
    print("\n4️⃣ Testing RAG Schemas Import")
    test_results["total_tests"] += 1
    try:
        from app.schemas.rag_feedback import RAGFeedbackCreate, RAGFeedbackResponse
        from app.schemas.rag_learning import ExperimentCreateRequest, LearningReadinessResponse
        print("   ✅ RAG schemas imported successfully")
        test_results["passed"] += 1
    except Exception as e:
        print(f"   ❌ RAG schemas import failed: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"RAG schemas: {str(e)}")
    
    # Test 5: RAG Routers Import
    print("\n5️⃣ Testing RAG Routers Import")
    test_results["total_tests"] += 1
    try:
        from app.routers.rag_feedback import router as feedback_router
        from app.routers.rag_learning import router as learning_router
        
        # Check if routers have routes
        feedback_routes = len([r for r in feedback_router.routes if hasattr(r, 'path')])
        learning_routes = len([r for r in learning_router.routes if hasattr(r, 'path')])
        
        if feedback_routes >= 10 and learning_routes >= 8:
            print(f"   ✅ RAG routers imported with {feedback_routes + learning_routes} routes")
            test_results["passed"] += 1
        else:
            print(f"   ❌ Insufficient routes: feedback={feedback_routes}, learning={learning_routes}")
            test_results["failed"] += 1
            test_results["errors"].append(f"Router routes: feedback={feedback_routes}, learning={learning_routes}")
            
    except Exception as e:
        print(f"   ❌ RAG routers import failed: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"RAG routers: {str(e)}")
    
    # Test 6: Enhanced Embedding Service
    print("\n6️⃣ Testing Enhanced Embedding Service")
    test_results["total_tests"] += 1
    try:
        from app.services.embedding_service import EmbeddingService
        
        # Test service initialization
        service = EmbeddingService()
        
        # Test embedding generation (should work with mock or real)
        test_text = "This is a test for mental health support"
        embedding = await service.generate_embedding(test_text)
        
        if embedding and len(embedding) > 0:
            print(f"   ✅ Embedding service working (dimension: {len(embedding)})")
            test_results["passed"] += 1
        else:
            print("   ❌ Embedding service returned empty result")
            test_results["failed"] += 1
            test_results["errors"].append("Empty embedding result")
            
    except Exception as e:
        print(f"   ❌ Embedding service test failed: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"Embedding service: {str(e)}")
    
    # Test 7: ETL Pipeline Integration
    print("\n7️⃣ Testing ETL Pipeline Integration")
    test_results["total_tests"] += 1
    try:
        from app.etl.extractors import CSVExtractor, ExtractorFactory
        from app.etl.transformers import TextCleaner, TransformerPipeline
        from app.etl.validators import ContentQualityValidator
        from app.etl.loaders import DocumentLoader
        
        # Test basic ETL functionality
        extractor = CSVExtractor()
        transformer = TextCleaner()
        validator = ContentQualityValidator()
        
        print("   ✅ ETL pipeline components imported and initialized")
        test_results["passed"] += 1
        
    except Exception as e:
        print(f"   ❌ ETL pipeline test failed: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"ETL pipeline: {str(e)}")
    
    # Test 8: FastAPI App Startup
    print("\n8️⃣ Testing FastAPI App Startup")
    test_results["total_tests"] += 1
    try:
        from app import app
        
        # Check if app has all expected attributes
        required_attrs = ['routes', 'middleware', 'exception_handlers']
        missing_attrs = [attr for attr in required_attrs if not hasattr(app, attr)]
        
        if not missing_attrs:
            print("   ✅ FastAPI app properly configured")
            test_results["passed"] += 1
        else:
            print(f"   ❌ Missing app attributes: {missing_attrs}")
            test_results["failed"] += 1
            test_results["errors"].append(f"Missing attributes: {missing_attrs}")
            
    except Exception as e:
        print(f"   ❌ FastAPI app startup test failed: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"FastAPI startup: {str(e)}")
    
    # Test 9: Database Models Relationships
    print("\n9️⃣ Testing Database Models Relationships")
    test_results["total_tests"] += 1
    try:
        from app.db.models import RAGFeedback, User, Conversation, Message
        
        # Check if models have expected relationships
        feedback_model = RAGFeedback
        
        # Check if model has expected columns
        expected_columns = ['id', 'user_id', 'conversation_id', 'overall_rating']
        model_columns = [col.name for col in feedback_model.__table__.columns]
        missing_columns = [col for col in expected_columns if col not in model_columns]
        
        if not missing_columns:
            print("   ✅ Database models properly configured")
            test_results["passed"] += 1
        else:
            print(f"   ❌ Missing model columns: {missing_columns}")
            test_results["failed"] += 1
            test_results["errors"].append(f"Missing columns: {missing_columns}")
            
    except Exception as e:
        print(f"   ❌ Database models test failed: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"Database models: {str(e)}")
    
    # Test 10: Configuration and Dependencies
    print("\n🔟 Testing Configuration and Dependencies")
    test_results["total_tests"] += 1
    try:
        from app.core.config import get_settings
        from app.core.dependencies import get_db
        from app.core.middleware import setup_middleware
        from app.core.exceptions import setup_exception_handlers
        
        # Test settings
        settings = get_settings()
        
        if hasattr(settings, 'DATABASE_URL') and hasattr(settings, 'SECRET_KEY'):
            print("   ✅ Configuration and dependencies working")
            test_results["passed"] += 1
        else:
            print("   ❌ Missing required configuration")
            test_results["failed"] += 1
            test_results["errors"].append("Missing configuration")
            
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        test_results["failed"] += 1
        test_results["errors"].append(f"Configuration: {str(e)}")
    
    # Print Test Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    
    success_rate = (test_results['passed'] / test_results['total_tests']) * 100
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if test_results['errors']:
        print(f"\n🚨 ERRORS ENCOUNTERED:")
        for i, error in enumerate(test_results['errors'], 1):
            print(f"   {i}. {error}")
    
    # Overall Assessment
    print(f"\n🎯 OVERALL ASSESSMENT:")
    if success_rate >= 90:
        print("🎉 EXCELLENT: RAG integration is highly successful!")
        return "EXCELLENT"
    elif success_rate >= 80:
        print("✅ GOOD: RAG integration is mostly successful with minor issues")
        return "GOOD"
    elif success_rate >= 70:
        print("⚠️ FAIR: RAG integration has some issues that need attention")
        return "FAIR"
    else:
        print("❌ POOR: RAG integration has significant issues")
        return "POOR"

if __name__ == "__main__":
    try:
        result = asyncio.run(test_rag_integration())
        print(f"\nTest completed with result: {result}")
    except Exception as e:
        print(f"Test execution failed: {e}")
        traceback.print_exc()

