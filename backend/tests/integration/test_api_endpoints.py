import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

class TestAPIEndpoints:
    """Integration tests for API endpoints"""
    
    def setup_method(self):
        """Setup test fixtures before each test method"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        assert response.json() == {"message": "NL ClickHouse Query API"}
    
    def test_health_check_endpoint_success(self, mock_clickhouse):
        """Test health check endpoint with successful database connection"""
        with patch('app.main.ch_client', mock_clickhouse):
            response = self.client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["clickhouse_connected"] is True
    
    def test_health_check_endpoint_failure(self, mock_clickhouse):
        """Test health check endpoint with database connection failure"""
        mock_clickhouse.get_tables.return_value = {"success": False, "error": "Connection failed"}
        
        with patch('app.main.ch_client', mock_clickhouse):
            response = self.client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["clickhouse_connected"] is False
    
    def test_get_tables_endpoint(self, mock_clickhouse):
        """Test get tables endpoint"""
        with patch('app.main.ch_client', mock_clickhouse):
            response = self.client.get("/tables")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "users" in [row[0] for row in data["data"]]
            assert "orders" in [row[0] for row in data["data"]]
    
    def test_get_schema_endpoint(self, mock_schema_inspector):
        """Test get schema endpoint"""
        with patch('app.main.schema_inspector', mock_schema_inspector):
            response = self.client.get("/schema")
            
            assert response.status_code == 200
            data = response.json()
            assert "tables" in data
            assert len(data["tables"]) > 0
    
    def test_get_table_schema_endpoint_success(self, mock_schema_inspector):
        """Test get specific table schema endpoint successfully"""
        with patch('app.main.schema_inspector', mock_schema_inspector):
            response = self.client.get("/schema/users")
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "users"
            assert "columns" in data
    
    def test_get_table_schema_endpoint_not_found(self, mock_schema_inspector):
        """Test get specific table schema endpoint with non-existent table"""
        mock_schema_inspector.get_table_schema.side_effect = ValueError("Table not found")
        
        with patch('app.main.schema_inspector', mock_schema_inspector):
            response = self.client.get("/schema/nonexistent")
            
            assert response.status_code == 200
            data = response.json()
            assert "error" in data
            assert "Table not found" in data["error"]
    
    def test_execute_query_endpoint_success(self, mock_clickhouse):
        """Test execute query endpoint successfully"""
        with patch('app.main.ch_client', mock_clickhouse):
            response = self.client.post("/query", json={"sql": "SELECT * FROM users"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            assert "columns" in data
    
    def test_execute_query_endpoint_missing_sql(self, mock_clickhouse):
        """Test execute query endpoint with missing SQL"""
        with patch('app.main.ch_client', mock_clickhouse):
            response = self.client.post("/query", json={})
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True  # This might need adjustment based on actual implementation
    
    def test_generate_sql_endpoint_success(self, mock_openai, mock_context_builder):
        """Test generate SQL endpoint successfully"""
        with patch('app.main.llm_client') as mock_llm, \
             patch('app.main.context_builder', mock_context_builder):
            
            mock_llm.generate_sql.return_value = {
                "success": True,
                "sql": "SELECT * FROM users",
                "model_used": "gpt-3.5-turbo"
            }
            mock_llm.explain_query.return_value = "This query selects all users"
            
            response = self.client.post("/generate-sql", json={"query": "show all users"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "SELECT" in data["sql"]
            assert "explanation" in data
    
    def test_generate_sql_endpoint_missing_query(self, mock_context_builder):
        """Test generate SQL endpoint with missing query"""
        with patch('app.main.context_builder', mock_context_builder):
            response = self.client.post("/generate-sql", json={})
            
            assert response.status_code == 200
            data = response.json()
            assert "error" in data
            assert data["error"] == "Query is required"
    
    def test_generate_sql_endpoint_empty_query(self, mock_context_builder):
        """Test generate SQL endpoint with empty query string"""
        with patch('app.main.context_builder', mock_context_builder):
            response = self.client.post("/generate-sql", json={"query": ""})
            
            assert response.status_code == 200
            data = response.json()
            assert "error" in data
            assert data["error"] == "Query is required"
    
    def test_smart_query_endpoint_success(self, mock_query_processor, mock_clickhouse, mock_openai):
        """Test smart query endpoint successfully"""
        with patch('app.main.query_processor', mock_query_processor), \
             patch('app.main.ch_client', mock_clickhouse), \
             patch('app.main.llm_client') as mock_llm:
            
            mock_llm.explain_query.return_value = "This query selects all users"
            
            response = self.client.post("/smart-query", json={"query": "show all users"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "sql" in data
            assert "execution" in data
            assert "explanation" in data
    
    def test_smart_query_endpoint_missing_query(self, mock_query_processor):
        """Test smart query endpoint with missing query"""
        with patch('app.main.query_processor', mock_query_processor):
            response = self.client.post("/smart-query", json={})
            
            assert response.status_code == 200
            data = response.json()
            assert "error" in data
            assert data["error"] == "Query is required"
    
    def test_embed_schema_endpoint_success(self, mock_schema_embedder, mock_embedding_manager):
        """Test embed schema endpoint successfully"""
        with patch('app.main.schema_embedder', mock_schema_embedder), \
             patch('app.main.embedding_manager', mock_embedding_manager):
            
            response = self.client.post("/embed-schema")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["embedded_elements"] == 2
            assert "successfully" in data["message"]
    
    def test_embed_schema_endpoint_failure(self, mock_schema_embedder):
        """Test embed schema endpoint with failure"""
        mock_schema_embedder.embed_schema.side_effect = Exception("Embedding failed")
        
        with patch('app.main.schema_embedder', mock_schema_embedder):
            response = self.client.post("/embed-schema")
            
            assert response.status_code == 200
            data = response.json()
            assert "error" in data
            assert "Embedding failed" in data["error"]
    
    def test_invalid_endpoint(self):
        """Test invalid endpoint returns 404"""
        response = self.client.get("/invalid-endpoint")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Test method not allowed returns 405"""
        response = self.client.put("/")
        
        assert response.status_code == 405
    
    def test_request_validation(self):
        """Test request validation for endpoints"""
        # Test with invalid JSON
        response = self.client.post("/query", data="invalid json", headers={"Content-Type": "application/json"})
        
        assert response.status_code == 422
    
    def test_response_headers(self):
        """Test response headers are set correctly"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
