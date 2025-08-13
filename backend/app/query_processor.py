from typing import Dict, List
from app.schema_embedder import schema_embedder
from app.context import SchemaContextBuilder
from app.llm import llm_client

class QueryProcessor:
    def __init__(self):
        self.schema_embedder = schema_embedder
        self.context_builder = SchemaContextBuilder()
        self.llm_client = llm_client
    
    def process_natural_query(self, natural_query: str) -> Dict:
        """Process natural language query with smart context retrieval"""
        
        # Step 1: Find relevant schema elements
        relevant_elements = self.schema_embedder.find_relevant_schema(
            natural_query, top_k=10
        )
        
        # Step 2: Extract relevant tables
        relevant_tables = self._extract_relevant_tables(relevant_elements)
        
        # Step 3: Build focused context
        focused_context = self._build_focused_context(relevant_elements, relevant_tables)
        
        # Step 4: Generate SQL with focused context
        sql_result = self.llm_client.generate_sql(natural_query, focused_context)
        
        # Step 5: Add metadata
        if sql_result["success"]:
            sql_result.update({
                "relevant_tables": relevant_tables,
                "context_elements_used": len(relevant_elements),
                "similarity_scores": [elem["similarity"] for elem in relevant_elements[:5]]
            })
        
        return sql_result
    
    def _extract_relevant_tables(self, relevant_elements: List[Dict]) -> List[str]:
        """Extract unique table names from relevant elements"""
        tables = set()
        
        for element in relevant_elements:
            if element["type"] == "table":
                tables.add(element["name"])
            elif element["type"] == "column":
                tables.add(element["table"])
        
        return list(tables)
    
    def _build_focused_context(self, relevant_elements: List[Dict], relevant_tables: List[str]) -> str:
        """Build focused schema context from relevant elements"""
        
        # Group elements by table
        table_elements = {}
        for element in relevant_elements:
            if element["type"] == "table":
                table_name = element["name"]
                if table_name not in table_elements:
                    table_elements[table_name] = {"table_info": element, "columns": []}
            elif element["type"] == "column":
                table_name = element["table"]
                if table_name not in table_elements:
                    table_elements[table_name] = {"table_info": None, "columns": []}
                table_elements[table_name]["columns"].append(element)
        
        # Build context string
        context_parts = []
        for table_name in relevant_tables:
            if table_name in table_elements:
                context_parts.append(
                    self._format_table_context_focused(table_name, table_elements[table_name])
                )
        
        return "\n\n".join(context_parts)
    
    def _format_table_context_focused(self, table_name: str, elements: Dict) -> str:
        """Format focused table context"""
        context = f"Table: {table_name}\n"
        
        # Add most relevant columns
        if elements["columns"]:
            context += "Relevant columns:\n"
            for col_element in elements["columns"][:8]:  # Limit to most relevant
                col_info = col_element["column_info"]
                context += f"  - {col_info.name} ({col_info.type})"
                if col_info.sample_values:
                    sample_str = ", ".join(col_info.sample_values[:2])
                    context += f" [examples: {sample_str}]"
                context += f" (similarity: {col_element['similarity']:.2f})\n"
        
        return context

query_processor = QueryProcessor()
