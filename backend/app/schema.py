from typing import Dict, List, Optional
from dataclasses import dataclass
from app.database import ch_client

@dataclass

class ColumnInfo:
    name: str
    type: str
    description: Optional[str] = None
    sample_values: List[str] = None

@dataclass

class TableInfo:
    name: str
    columns: List[ColumnInfo]
    description: Optional[str] = None
    row_count: Optional[int] = None

class SchemaIntrospector:
    def __init__(self):
        self.client = ch_client
        self._schema_cache = {}
    
    def get_table_schema(self, table_name: str) -> TableInfo:
        if table_name in self._schema_cache:
            return self._schema_cache[table_name]
            
        # Get column information
        columns_query = f"""
        SELECT name, type 
        FROM system.columns 
        WHERE table = '{table_name}' 
        AND database = '{self.client.client.database}'
        """
        
        result = self.client.execute_query(columns_query)
        if not result["success"]:
            raise Exception(f"Failed to get schema for {table_name}")
        
        columns = []
        for row in result["data"]:
            col_name, col_type = row
            # Get sample values
            sample_query = f"SELECT DISTINCT {col_name} FROM {table_name} LIMIT 5"
            samples = self.client.execute_query(sample_query)
            sample_values = [str(row[0]) for row in samples["data"]] if samples["success"] else []
            
            columns.append(ColumnInfo(
                name=col_name,
                type=col_type,
                sample_values=sample_values
            ))
        
        # Get row count
        count_query = f"SELECT COUNT(*) FROM {table_name}"
        count_result = self.client.execute_query(count_query)
        row_count = count_result["data"][0][0] if count_result["success"] else None
        
        table_info = TableInfo(
            name=table_name,
            columns=columns,
            row_count=row_count
        )
        
        self._schema_cache[table_name] = table_info
        return table_info
    
    def get_all_tables_schema(self) -> Dict[str, TableInfo]:
        tables_result = self.client.get_tables()
        if not tables_result["success"]:
            return {}
        
        schema = {}
        for row in tables_result["data"]:
            table_name = row[0]
            try:
                schema[table_name] = self.get_table_schema(table_name)
            except Exception as e:
                print(f"Failed to get schema for {table_name}: {e}")
                
        return schema

schema_inspector = SchemaIntrospector()
