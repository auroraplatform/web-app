import clickhouse_connect

from app.config import settings

class ClickHouseClient:
    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host=settings.clickhouse_host,
            port=settings.clickhouse_port,
            username=settings.clickhouse_user,
            password=settings.clickhouse_password,
            database=settings.clickhouse_database
        )
    
    def execute_query(self, query: str):
        try:
            result = self.client.query(query)
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
