import clickhouse_connect
from typing import Dict, List, Any, Optional
from app.config import settings
from app.sql_security import sql_validator

class ClickHouseClient:
    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host=settings.clickhouse_host,
            port=settings.clickhouse_port,
            username=settings.clickhouse_user,
            password=settings.clickhouse_password,
            database=settings.clickhouse_database
        )
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> Dict:
        """Execute SQL query with optional parameters"""
        try:
            if parameters:
                return self.execute_parameterized_query(query, parameters)
            else:
                return self.execute_parameterized_query(query, {})

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_parameterized_query(self, query_template: str, parameters: Dict[str, Any]) -> Dict:
        """Execute parameterized query"""
        try:
            # Validate the template
            validation = sql_validator.validate_sql(query_template)
            if not validation.is_safe:
                return {
                    "success": False,
                    "error": f"SQL template validation failed: {validation.error_message}",
                    "security_error": True
                }
            
            # Execute with parameters
            result = self.client.query(query_template, parameters=parameters)

            return {
                "success": True,
                "data": result.result_rows,
                "columns": result.column_names
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_tables(self):
        query = "SHOW TABLES"
        return self.execute_query(query)

ch_client = ClickHouseClient()
