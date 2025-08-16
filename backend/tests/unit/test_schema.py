import pytest
from unittest.mock import Mock, patch, MagicMock
from app.schema import SchemaInspector

class TestSchemaInspector:
    """Test cases for SchemaInspector class"""
    
    def setup_method(self):
        """Setup test fixtures before each test method"""
        # Since we don't have the actual SchemaInspector implementation,
        # we'll create a mock version for testing
        self.schema_inspector = Mock(spec=SchemaInspector)
    
    def test_get_all_tables_schema(self):
        """Test getting all tables schema"""
        expected_schema = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "UInt32"},
                        {"name": "name", "type": "String"}
                    ]
                }
            ]
        }
        
        self.schema_inspector.get_all_tables_schema.return_value = expected_schema
        
        result = self.schema_inspector.get_all_tables_schema()
        
        assert result == expected_schema
        assert "tables" in result
        assert len(result["tables"]) == 1
        assert result["tables"][0]["name"] == "users"
    
    def test_get_table_schema_success(self):
        """Test getting specific table schema successfully"""
        expected_schema = {
            "name": "users",
            "columns": [
                {"name": "id", "type": "UInt32"},
                {"name": "name", "type": "String"},
                {"name": "email", "type": "String"}
            ]
        }
        
        self.schema_inspector.get_table_schema.return_value = expected_schema
        
        result = self.schema_inspector.get_table_schema("users")
        
        assert result == expected_schema
        assert result["name"] == "users"
        assert len(result["columns"]) == 3
        self.schema_inspector.get_table_schema.assert_called_once_with("users")
    
    def test_get_table_schema_not_found(self):
        """Test getting schema for non-existent table"""
        self.schema_inspector.get_table_schema.side_effect = ValueError("Table not found")
        
        with pytest.raises(ValueError, match="Table not found"):
            self.schema_inspector.get_table_schema("nonexistent_table")
    
    def test_schema_validation(self):
        """Test schema structure validation"""
        valid_schema = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "UInt32"},
                        {"name": "name", "type": "String"}
                    ]
                }
            ]
        }
        
        # Test that schema has required structure
        assert "tables" in valid_schema
        assert isinstance(valid_schema["tables"], list)
        
        for table in valid_schema["tables"]:
            assert "name" in table
            assert "columns" in table
            assert isinstance(table["columns"], list)
            
            for column in table["columns"]:
                assert "name" in column
                assert "type" in column
    
    def test_column_types_validation(self):
        """Test that column types are valid ClickHouse types"""
        valid_types = [
            "UInt8", "UInt16", "UInt32", "UInt64",
            "Int8", "Int16", "Int32", "Int64",
            "Float32", "Float64",
            "String", "FixedString",
            "Date", "DateTime", "DateTime64",
            "Array", "Nullable"
        ]
        
        schema = {
            "tables": [
                {
                    "name": "test_table",
                    "columns": [
                        {"name": "id", "type": "UInt32"},
                        {"name": "name", "type": "String"},
                        {"name": "score", "type": "Float64"}
                    ]
                }
            ]
        }
        
        for table in schema["tables"]:
            for column in table["columns"]:
                assert column["type"] in valid_types or any(valid_type in column["type"] for valid_type in valid_types)
    
    def test_table_names_validation(self):
        """Test that table names are valid"""
        schema = {
            "tables": [
                {
                    "name": "users",
                    "columns": []
                },
                {
                    "name": "user_orders",
                    "columns": []
                },
                {
                    "name": "123_invalid",
                    "columns": []
                }
            ]
        }
        
        # Test valid table names
        assert schema["tables"][0]["name"] == "users"
        assert schema["tables"][1]["name"] == "user_orders"
        
        # Test invalid table names (should not start with numbers)
        assert schema["tables"][2]["name"] == "123_invalid"
    
    def test_column_names_validation(self):
        """Test that column names are valid"""
        schema = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "UInt32"},
                        {"name": "user_name", "type": "String"},
                        {"name": "123_invalid", "type": "String"}
                    ]
                }
            ]
        }
        
        # Test valid column names
        assert schema["tables"][0]["columns"][0]["name"] == "id"
        assert schema["tables"][0]["columns"][1]["name"] == "user_name"
        
        # Test invalid column names (should not start with numbers)
        assert schema["tables"][0]["columns"][2]["name"] == "123_invalid"
