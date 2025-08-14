import pytest
import asyncio
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.database import ClickHouseClient
from app.llm import LLMClient
from app.schema import SchemaInspector
from app.embeddings import EmbeddingManager
from app.query_processor import QueryProcessor
from app.schema_embedder import SchemaEmbedder
from app.context import ContextBuilder

@pytest.fixture
def test_client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def mock_clickhouse():
    """Mock ClickHouse client"""
    mock_client = Mock(spec=ClickHouseClient)
    
    # Mock successful query execution
    mock_client.execute_query.return_value = {
        "success": True,
        "data": [["test_data"]],
        "columns": ["test_column"]
    }
    
    # Mock successful table retrieval
    mock_client.get_tables.return_value = {
        "success": True,
        "data": [["users"], ["orders"]],
        "columns": ["table_name"]
    }
    
    return mock_client

@pytest.fixture
def mock_openai():
    """Mock OpenAI client"""
    mock_client = Mock()
    
    # Mock successful chat completion
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="SELECT * FROM users"))]
    mock_client.chat.completions.create.return_value = mock_response
    
    return mock_client

@pytest.fixture
def mock_schema_inspector():
    """Mock schema inspector"""
    mock_inspector = Mock(spec=SchemaInspector)
    
    mock_inspector.get_all_tables_schema.return_value = {
        "tables": [
            {
                "name": "users",
                "columns": [
                    {"name": "id", "type": "UInt32"},
                    {"name": "name", "type": "String"},
                    {"name": "email", "type": "String"},
                    {"name": "created_at", "type": "DateTime"}
                ]
            },
            {
                "name": "orders",
                "columns": [
                    {"name": "id", "type": "UInt32"},
                    {"name": "user_id", "type": "UInt32"},
                    {"name": "amount", "type": "Float64"},
                    {"name": "order_date", "type": "DateTime"}
                ]
            }
        ]
    }
    
    mock_inspector.get_table_schema.return_value = {
        "name": "users",
        "columns": [
            {"name": "id", "type": "UInt32"},
            {"name": "name", "type": "String"},
            {"name": "email", "type": "String"},
            {"name": "created_at", "type": "DateTime"}
        ]
    }
    
    return mock_inspector

@pytest.fixture
def mock_embedding_manager():
    """Mock embedding manager"""
    mock_manager = Mock(spec=EmbeddingManager)
    mock_manager._save_cache.return_value = None
    return mock_manager

@pytest.fixture
def mock_query_processor():
    """Mock query processor"""
    mock_processor = Mock(spec=QueryProcessor)
    
    mock_processor.process_natural_query.return_value = {
        "success": True,
        "sql": "SELECT * FROM users",
        "context_used": "users table"
    }
    
    return mock_processor

@pytest.fixture
def mock_schema_embedder():
    """Mock schema embedder"""
    mock_embedder = Mock(spec=SchemaEmbedder)
    mock_embedder.embed_schema.return_value = ["users", "orders"]
    return mock_embedder

@pytest.fixture
def mock_context_builder():
    """Mock context builder"""
    mock_builder = Mock(spec=ContextBuilder)
    mock_builder.get_all_tables_context.return_value = "users table with columns: id, name, email, created_at"
    return mock_builder

@pytest.fixture
def sample_schema():
    """Sample database schema for testing"""
    return {
        "tables": [
            {
                "name": "users",
                "columns": [
                    {"name": "id", "type": "UInt32"},
                    {"name": "name", "type": "String"},
                    {"name": "email", "type": "String"},
                    {"name": "created_at", "type": "DateTime"}
                ]
            },
            {
                "name": "orders",
                "columns": [
                    {"name": "id", "type": "UInt32"},
                    {"name": "user_id", "type": "UInt32"},
                    {"name": "amount", "type": "Float64"},
                    {"name": "order_date", "type": "DateTime"}
                ]
            }
        ]
    }

@pytest.fixture
def sample_queries():
    """Sample natural language queries for testing"""
    return [
        "show all users",
        "count orders by user",
        "find users who made orders",
        "total revenue by month",
        "users created in the last 30 days"
    ]

@pytest.fixture
def mock_responses():
    """Mock API responses for testing"""
    return {
        "successful_sql": "SELECT * FROM users",
        "explanation": "This query retrieves all records from the users table",
        "error_message": "Invalid query syntax",
        "api_error": "OpenAI API rate limit exceeded"
    }

# Async test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
