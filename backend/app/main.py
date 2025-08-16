from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from app.database import ch_client
from app.schema import schema_inspector
from app.llm import llm_client
from app.context import context_builder
from app.query_processor import query_processor
from app.schema_embedder import schema_embedder
from app.embeddings import embedding_manager
from app.sql_security import sql_validator

app = FastAPI(title="NL to ClickHouse Query Tool")

# Pydantic models for request validation
class QueryRequest(BaseModel):
    sql: str = Field(..., min_length=1, max_length=10000, description="SQL query to execute")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Query parameters")

class NaturalQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language query to process")

@app.get("/")
async def root():
    return {"message": "NL ClickHouse Query API"}

@app.get("/tables")
async def get_tables():
    return ch_client.get_tables()

@app.post("/query")
async def execute_query(request: QueryRequest):
    """Execute SQL query with security validation"""
    result = ch_client.execute_query(request.sql, request.parameters)
    if not result["success"]:
        if result.get("security_error"):
            raise HTTPException(status_code=400, detail=result["error"])
        else:
            raise HTTPException(status_code=500, detail=result["error"])

    return result

@app.get("/schema")
async def get_schema():
    """Get complete database schema"""
    return schema_inspector.get_all_tables_schema()

@app.get("/schema/{table_name}")
async def get_table_schema(table_name: str):
    """Get schema for specific table"""
    try:
        return schema_inspector.get_table_schema(table_name)
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    tables = ch_client.get_tables()
    return {
        "status": "healthy" if tables["success"] else "unhealthy",
        "clickhouse_connected": tables["success"]
    }

@app.post("/generate-sql")
async def generate_sql(request: dict):
    """Generate SQL from natural language"""
    natural_query = request.get("query")
    
    # Validate natural language query
    if not natural_query or not natural_query.strip():
        raise HTTPException(
            status_code=400, 
            detail="Natural language query cannot be empty, null, or contain only whitespace"
        )
    
    # For now, use all tables context (we'll optimize this tomorrow)
    schema_context = context_builder.get_all_tables_context()
    
    # Generate SQL
    result = llm_client.generate_sql(natural_query, schema_context)
    
    if result["success"]:
        # Add query explanation
        explanation = llm_client.explain_query(result["sql"])
        result["explanation"] = explanation
    
    return result

@app.post("/smart-query")
async def smart_query(request: NaturalQueryRequest):
    """Process natural language query with smart context retrieval"""
    # Validate natural language query
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=400, 
            detail="Natural language query cannot be empty, null, or contain only whitespace"
        )

    # Process with smart context retrieval
    result = query_processor.process_natural_query(request.query)
    
    if result["success"]:
        execution_result = ch_client.execute_query(result["sql"], result["parameters"])
        if not execution_result["success"]:
            if execution_result.get("security_error"):
                raise HTTPException(status_code=400, detail=execution_result["error"])
            else:
                raise HTTPException(status_code=500, detail=execution_result["error"])

        result.update({
            "execution": execution_result
        })
    
    return result

@app.post("/embed-schema")
async def embed_schema_endpoint():
    """Force re-embedding of schema (for testing)"""
    try:
        elements = schema_embedder.embed_schema()
        embedding_manager._save_cache()  # Save to disk
        return {
            "success": True,
            "embedded_elements": len(elements),
            "message": "Schema embedded successfully"
        }
    except Exception as e:
        return {"error": str(e)}
