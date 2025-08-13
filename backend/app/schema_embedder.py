from typing import Dict, List
from app.schema import TableInfo, schema_inspector
from app.embeddings import embedding_manager

class SchemaEmbedder:
    def __init__(self):
        self.inspector = schema_inspector
        self.embedding_manager = embedding_manager
        self._embedded_elements = {}
    
    def embed_schema(self):
        """Embed all schema elements for semantic search"""
        schema = self.inspector.get_all_tables_schema()
        
        embedded_elements = []
        
        for table_name, table_info in schema.items():
            # Embed table-level information
            table_description = self._create_table_description(table_info)
            embedded_elements.append({
                'type': 'table',
                'name': table_name,
                'description': table_description,
                'full_info': table_info
            })
            
            # Embed each column
            for column in table_info.columns:
                column_description = self._create_column_description(table_name, column)
                embedded_elements.append({
                    'type': 'column',
                    'table': table_name,
                    'name': column.name,
                    'description': column_description,
                    'column_info': column
                })
        
        # Generate embeddings for all descriptions
        descriptions = [elem['description'] for elem in embedded_elements]
        embeddings = self.embedding_manager.embed_batch(descriptions)
        
        # Store embedded elements
        for elem, embedding in zip(embedded_elements, embeddings):
            elem['embedding'] = embedding
        
        self._embedded_elements = {
            elem['description']: elem for elem in embedded_elements
        }
        
        print(f"Embedded {len(embedded_elements)} schema elements")
        return embedded_elements
    
    def _create_table_description(self, table_info: TableInfo) -> str:
        """Create searchable description for table"""
        description = f"Table {table_info.name}"
        
        # Add column names for context
        column_names = [col.name for col in table_info.columns]
        description += f" with columns: {', '.join(column_names)}"
        
        # Add sample values context
        sample_context = []
        for col in table_info.columns[:5]:  # First 5 columns
            if col.sample_values:
                sample_context.append(f"{col.name} contains {', '.join(col.sample_values[:2])}")
        
        if sample_context:
            description += f". Sample data: {'; '.join(sample_context)}"
        
        return description
    
    def _create_column_description(self, table_name: str, column) -> str:
        """Create searchable description for column"""
        description = f"Column {column.name} in table {table_name} of type {column.type}"
        
        if column.sample_values:
            description += f" with example values: {', '.join(column.sample_values[:3])}"
        
        return description
    
    def find_relevant_schema(self, natural_query: str, top_k: int = 10) -> List[Dict]:
        """Find schema elements relevant to natural language query"""
        if not self._embedded_elements:
            self.embed_schema()
        
        descriptions = list(self._embedded_elements.keys())
        similar_descriptions = self.embedding_manager.find_similar(
            natural_query, descriptions, top_k
        )
        
        relevant_elements = []
        for description, similarity in similar_descriptions:
            element = self._embedded_elements[description].copy()
            element['similarity'] = similarity
            relevant_elements.append(element)
        
        return relevant_elements

schema_embedder = SchemaEmbedder()
