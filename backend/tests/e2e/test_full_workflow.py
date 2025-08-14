import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

class TestFullWorkflow:
    """End-to-end tests for complete application workflows"""
    
    def setup_method(self):
        """Setup test fixtures before each test method"""
        self.client = TestClient(app)
    
    def test_complete_natural_language_to_sql_workflow(self, mock_clickhouse, mock_context_builder):
        """Test complete workflow from natural language to SQL execution"""
        with patch('app.main.llm_client') as mock_llm, \
             patch('app.main.context_builder', mock_context_builder), \
             patch('app.main.ch_client', mock_clickhouse):
            
            # Mock LLM responses
            mock_llm.generate_sql.return_value = {
                "success": True,
                "sql": "SELECT * FROM users",
                "model_used": "gpt-3.5-turbo"
            }
            mock_llm.explain_query.return_value = "This query selects all users from the users table"
            
            # Test the complete workflow
            response = self.client.post("/generate-sql", json={"query": "show all users"})
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify SQL generation
            assert data["success"] is True
            assert "SELECT" in data["sql"]
            assert data["model_used"] == "gpt-3.5-turbo"
            
            # Verify explanation was added
            assert "explanation" in data
            assert "selects all users" in data["explanation"]
            
            # Verify context was used
            mock_context_builder.get_all_tables_context.assert_called_once()
    
    def test_complete_smart_query_workflow(self, mock_query_processor, mock_clickhouse, mock_openai):
        """Test complete smart query workflow with context retrieval and execution"""
        with patch('app.main.query_processor', mock_query_processor), \
             patch('app.main.ch_client', mock_clickhouse), \
             patch('app.main.llm_client') as mock_llm:
            
            # Mock query processor response
            mock_query_processor.process_natural_query.return_value = {
                "success": True,
                "sql": "SELECT COUNT(*) FROM users",
                "context_used": "users table with user information"
            }
            
            # Mock LLM explanation
            mock_llm.explain_query.return_value = "This query counts all users in the database"
            
            # Test the complete smart query workflow
            response = self.client.post("/smart-query", json={"query": "how many users do we have"})
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify the complete workflow
            assert data["success"] is True
            assert "sql" in data
            assert "execution" in data
            assert "explanation" in data
            assert "context_used" in data
            
            # Verify query processor was called
            mock_query_processor.process_natural_query.assert_called_once_with("how many users do we have")
            
            # Verify SQL execution
            mock_clickhouse.execute_query.assert_called_once_with("SELECT COUNT(*) FROM users")
            
            # Verify explanation generation
            mock_llm.explain_query.assert_called_once_with("SELECT COUNT(*) FROM users")
    
    def test_schema_embedding_workflow(self, mock_schema_embedder, mock_embedding_manager):
        """Test complete schema embedding workflow"""
        with patch('app.main.schema_embedder', mock_schema_embedder), \
             patch('app.main.embedding_manager', mock_embedding_manager):
            
            # Test schema embedding endpoint
            response = self.client.post("/embed-schema")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify embedding workflow
            assert data["success"] is True
            assert data["embedded_elements"] == 2
            assert "successfully" in data["message"]
            
            # Verify schema embedder was called
            mock_schema_embedder.embed_schema.assert_called_once()
            
            # Verify cache was saved
            mock_embedding_manager._save_cache.assert_called_once()
    
    def test_health_monitoring_workflow(self, mock_clickhouse):
        """Test health monitoring workflow"""
        with patch('app.main.ch_client', mock_clickhouse):
            # Test health check endpoint
            response = self.client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify health check workflow
            assert "status" in data
            assert "clickhouse_connected" in data
            
            # Verify database connectivity check
            mock_clickhouse.get_tables.assert_called_once()
    
    def test_schema_inspection_workflow(self, mock_schema_inspector):
        """Test complete schema inspection workflow"""
        with patch('app.main.schema_inspector', mock_schema_inspector):
            # Test get all schema
            response = self.client.get("/schema")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify schema inspection
            assert "tables" in data
            assert len(data["tables"]) > 0
            
            # Test get specific table schema
            table_response = self.client.get("/schema/users")
            
            assert table_response.status_code == 200
            table_data = table_response.json()
            
            # Verify specific table schema
            assert table_data["name"] == "users"
            assert "columns" in table_data
            
            # Verify schema inspector was called
            mock_schema_inspector.get_all_tables_schema.assert_called_once()
            mock_schema_inspector.get_table_schema.assert_called_once_with("users")
    
    def test_database_operations_workflow(self, mock_clickhouse):
        """Test complete database operations workflow"""
        with patch('app.main.ch_client', mock_clickhouse):
            # Test get tables
            tables_response = self.client.get("/tables")
            
            assert tables_response.status_code == 200
            tables_data = tables_response.json()
            
            # Verify tables retrieval
            assert tables_data["success"] is True
            assert "data" in tables_data
            assert "columns" in tables_data
            
            # Test execute query
            query_response = self.client.post("/query", json={"sql": "SELECT * FROM users LIMIT 5"})
            
            assert query_response.status_code == 200
            query_data = query_response.json()
            
            # Verify query execution
            assert query_data["success"] is True
            assert "data" in query_data
            assert "columns" in query_data
            
            # Verify database operations
            mock_clickhouse.get_tables.assert_called()
            mock_clickhouse.execute_query.assert_called_with("SELECT * FROM users LIMIT 5")
    
    def test_error_handling_workflow(self, mock_schema_inspector):
        """Test error handling workflow across the application"""
        with patch('app.main.schema_inspector', mock_schema_inspector):
            # Mock error scenario
            mock_schema_inspector.get_table_schema.side_effect = ValueError("Table not found")
            
            # Test error handling
            response = self.client.get("/schema/nonexistent_table")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify error handling
            assert "error" in data
            assert "Table not found" in data["error"]
            
            # Verify error was properly caught and formatted
            assert isinstance(data["error"], str)
    
    def test_performance_workflow(self, mock_clickhouse, mock_context_builder):
        """Test performance aspects of the workflow"""
        with patch('app.main.llm_client') as mock_llm, \
             patch('app.main.context_builder', mock_context_builder), \
             patch('app.main.ch_client', mock_clickhouse):
            
            # Mock fast response
            mock_llm.generate_sql.return_value = {
                "success": True,
                "sql": "SELECT * FROM users",
                "model_used": "gpt-3.5-turbo"
            }
            mock_llm.explain_query.return_value = "Fast response"
            
            # Test performance under load
            responses = []
            for i in range(5):
                response = self.client.post("/generate-sql", json={"query": f"query {i}"})
                responses.append(response)
            
            # Verify all responses were successful
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
            
            # Verify performance expectations
            assert len(responses) == 5
            assert mock_llm.generate_sql.call_count == 5
            assert mock_llm.explain_query.call_count == 5
