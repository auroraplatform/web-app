# app/context.py
from typing import List
from app.schema import TableInfo, schema_inspector

class SchemaContextBuilder:
    def __init__(self):
        self.inspector = schema_inspector
    
    def build_context_for_tables(self, table_names: List[str]) -> str:
        """Build schema context string for specific tables"""
        context_parts = []
        
        for table_name in table_names:
            try:
                table_info = self.inspector.get_table_schema(table_name)
                context_parts.append(self._format_table_context(table_info))
            except Exception as e:
                print(f"Error getting context for {table_name}: {e}")
        
        return "\n\n".join(context_parts)
    
    def _format_table_context(self, table_info: TableInfo) -> str:
        """Format single table context"""
        context = f"Table: {table_info.name}"
        if table_info.row_count:
            context += f" ({table_info.row_count:,} rows)"
        
        context += "\nColumns:\n"
        
        for col in table_info.columns:
            context += f"  - {col.name} ({col.type})"
            if col.sample_values:
                sample_str = ", ".join(col.sample_values[:3])
                context += f" [examples: {sample_str}]"
            context += "\n"
        
        return context
    
    def get_all_tables_context(self) -> str:
        """Get context for all tables in database"""
        schema = self.inspector.get_all_tables_schema()
        table_names = list(schema.keys())
        return self.build_context_for_tables(table_names)

context_builder = SchemaContextBuilder()