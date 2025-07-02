import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import json
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.etl.search_documents import get_embedding, search_similar_documents

class TestDocumentSearch(unittest.TestCase):
    @patch('app.etl.search_documents.embed')
    def test_get_embedding(self, mock_embed):
        # Setup mock
        mock_embedding = np.array([0.1, 0.2, 0.3])
        mock_embed.return_value = np.array([mock_embedding])
        
        # Call function
        result = get_embedding("test query")
        
        # Assertions
        mock_embed.assert_called_once_with(["test query"])
        self.assertTrue(np.array_equal(result, mock_embedding))
    
    @patch('app.etl.search_documents.get_embedding')
    @patch('app.etl.search_documents.create_engine')
    def test_search_similar_documents(self, mock_create_engine, mock_get_embedding):
        # Setup mocks
        mock_embedding = np.array([0.1, 0.2, 0.3])
        mock_get_embedding.return_value = mock_embedding
        
        mock_connection = MagicMock()
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine
        
        # Mock query results
        mock_result = [
            (1, "Test content 1", json.dumps({"source": "test", "response": "Test response 1"}), 0.95),
            (2, "Test content 2", json.dumps({"source": "test", "response": "Test response 2"}), 0.85)
        ]
        mock_connection.execute.return_value = mock_result
        
        # Call function
        results = search_similar_documents("test query", limit=2, threshold=0.7)
        
        # Assertions
        mock_get_embedding.assert_called_once_with("test query")
        mock_create_engine.assert_called_once()
        mock_connection.execute.assert_called_once()
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['id'], 1)
        self.assertEqual(results[0]['content'], "Test content 1")
        self.assertEqual(results[0]['metadata'], {"source": "test", "response": "Test response 1"})
        self.assertEqual(results[0]['similarity'], 0.95)
        
        self.assertEqual(results[1]['id'], 2)
        self.assertEqual(results[1]['content'], "Test content 2")
        self.assertEqual(results[1]['metadata'], {"source": "test", "response": "Test response 2"})
        self.assertEqual(results[1]['similarity'], 0.85)

if __name__ == '__main__':
    unittest.main()
backend/mindease-api/tests/integration/test_document_routes.py [NEW]
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import json

def test_document_search_endpoint(client: TestClient, db_session: Session, test_admin_user):
    """Test the document search endpoint."""
    # Create a test token for admin user
    from app.core.security import create_access_token
    token = create_access_token(subject=test_admin_user.id)
    
    # Setup headers with token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test search query
    search_data = {
        "query": "anxiety management techniques",
        "limit": 3,
        "threshold": 0.5
    }
    
    # Mock the search_similar_documents function
    with pytest.MonkeyPatch.context() as mp:
        # Create mock search results
        mock_results = [
            {
                "id": 1,
                "content": "Here are some anxiety management techniques...",
                "metadata": json.dumps({"source": "dataset", "response": "Deep breathing is effective..."}),
                "similarity": 0.92
            },
            {
                "id": 2,
                "content": "Anxiety can be managed through various approaches...",
                "metadata": json.dumps({"source": "counselchat", "response": "CBT is a proven method..."}),
                "similarity": 0.85
            }
        ]
        
        # Mock the search_similar_documents function
        def mock_search(*args, **kwargs):
            return mock_results
        
        mp.setattr("app.routers.documents.search_similar_documents", mock_search)
        
        # Make request to search endpoint
        response = client.post("/api/documents/search", json=search_data, headers=headers)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == 1
        assert data[0]["similarity"] == 0.92
        assert data[1]["id"] == 2
        assert data[1]["similarity"] == 0.85

def test_document_count_endpoint(client: TestClient, db_session: Session, test_admin_user):
    """Test the document count endpoint."""
    # Create a test token for admin user
    from app.core.security import create_access_token
    token = create_access_token(subject=test_admin_user.id)
    
    # Setup headers with token
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Mock the database query
    with pytest.MonkeyPatch.context() as mp:
        # Mock the execute method to return a scalar that returns 42
        def mock_execute(*args, **kwargs):
            class MockScalar:
                def scalar(self):
                    return 42
            return MockScalar()
        
        mp.setattr("sqlalchemy.orm.Session.execute", mock_execute)
        
        # Make request to count endpoint
        response = client.get("/api/documents/count", headers=headers)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 42