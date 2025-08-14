import pytest
from unittest.mock import Mock, patch, MagicMock
from app.database import ClickHouseClient

class TestClickHouseClient:
    """Test cases for ClickHouseClient class"""
    
    def setup_method(self):
        """Setup test fixtures before each test method"""
        with patch('app.database.settings') as mock_settings:
            mock_settings.clickhouse_host = "localhost"
            mock_settings.clickhouse_port = 9000
            mock_settings.clickhouse_user = "default"
            mock_settings.clickhouse_password = ""
            mock_settings.clickhouse_database = "default"
            
            with patch('app.database.clickhouse_connect.get_client') as mock_get_client:
                self.mock_client = Mock()
                mock_get_client.return_value = self.mock_client
                self.ch_client = ClickHouseClient()
    
    def test_init(self):
        """Test ClickHouseClient initialization"""
        assert self.ch_client.client is not None
    
    @patch('app.database.clickhouse_connect.get_client')
    def test_init_connection_parameters(self, mock_get_client):
        """Test that connection parameters are passed correctly"""
        mock_get_client.return_value = Mock()
        
        with patch('app.database.settings') as mock_settings:
            mock_settings.clickhouse_host = "test-host"
            mock_settings.clickhouse_port = 1234
            mock_settings.clickhouse_user = "test-user"
            mock_settings.clickhouse_password = "test-pass"
            mock_settings.clickhouse_database = "test-db"
            
            ClickHouseClient()
            
            mock_get_client.assert_called_once_with(
                host="test-host",
                port=1234,
                username="test-user",
                password="test-pass",
                database="test-db"
            )
    
    def test_execute_query_success(self):
        """Test successful query execution"""
        # Mock successful query result
        mock_result = Mock()
        mock_result.result_rows = [["user1", "John"], ["user2", "Jane"]]
        mock_result.column_names = ["id", "name"]
        
        self.mock_client.query.return_value = mock_result
        
        result = self.ch_client.execute_query("SELECT * FROM users")
        
        assert result["success"] is True
        assert result["data"] == [["user1", "John"], ["user2", "Jane"]]
        assert result["columns"] == ["id", "name"]
        self.mock_client.query.assert_called_once_with("SELECT * FROM users")
    
    def test_execute_query_failure(self):
        """Test query execution failure"""
        # Mock query failure
        self.mock_client.query.side_effect = Exception("Syntax error")
        
        result = self.ch_client.execute_query("INVALID SQL")
        
        assert result["success"] is False
        assert "Syntax error" in result["error"]
    
    def test_execute_query_empty_result(self):
        """Test query execution with empty result"""
        # Mock empty result
        mock_result = Mock()
        mock_result.result_rows = []
        mock_result.column_names = ["id", "name"]
        
        self.mock_client.query.return_value = mock_result
        
        result = self.ch_client.execute_query("SELECT * FROM users WHERE 1=0")
        
        assert result["success"] is True
        assert result["data"] == []
        assert result["columns"] == ["id", "name"]
    
    def test_execute_query_large_result(self):
        """Test query execution with large result set"""
        # Mock large result
        mock_result = Mock()
        mock_result.result_rows = [["user" + str(i)] for i in range(1000)]
        mock_result.column_names = ["id"]
        
        self.mock_client.query.return_value = mock_result
        
        result = self.ch_client.execute_query("SELECT * FROM users")
        
        assert result["success"] is True
        assert len(result["data"]) == 1000
        assert result["columns"] == ["id"]
    
    def test_get_tables(self):
        """Test get_tables method"""
        # Mock tables result
        mock_result = Mock()
        mock_result.result_rows = [["users"], ["orders"], ["products"]]
        mock_result.column_names = ["table_name"]
        
        self.mock_client.query.return_value = mock_result
        
        result = self.ch_client.get_tables()
        
        assert result["success"] is True
        assert result["data"] == [["users"], ["orders"], ["products"]]
        assert result["columns"] == ["table_name"]
        self.mock_client.query.assert_called_once_with("SHOW TABLES")
    
    def test_execute_query_with_parameters(self):
        """Test query execution with different query types"""
        queries = [
            "SELECT * FROM users",
            "INSERT INTO users (name) VALUES ('John')",
            "UPDATE users SET name = 'Jane' WHERE id = 1",
            "DELETE FROM users WHERE id = 1",
            "CREATE TABLE test (id UInt32)"
        ]
        
        for query in queries:
            mock_result = Mock()
            mock_result.result_rows = []
            mock_result.column_names = []
            
            self.mock_client.query.return_value = mock_result
            
            result = self.ch_client.execute_query(query)
            
            assert result["success"] is True
            self.mock_client.query.assert_called_with(query)
    
    def test_execute_query_connection_error(self):
        """Test handling of connection errors"""
        # Mock connection error
        self.mock_client.query.side_effect = ConnectionError("Connection refused")
        
        result = self.ch_client.execute_query("SELECT * FROM users")
        
        assert result["success"] is False
        assert "Connection refused" in result["error"]
    
    def test_execute_query_timeout_error(self):
        """Test handling of timeout errors"""
        # Mock timeout error
        self.mock_client.query.side_effect = TimeoutError("Query timeout")
        
        result = self.ch_client.execute_query("SELECT * FROM users")
        
        assert result["success"] is False
        assert "Query timeout" in result["error"]
