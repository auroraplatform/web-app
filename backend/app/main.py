from doctest import debug
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
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
import os
from pathlib import Path

def create_detailed_error(user_message: str, debug_error: str = None, status_code: int = 400):
    """Create structured error response with optional debug info"""
    detail = {
        "success": False,
        "user_message": user_message,
        "debug_error": debug_error
    }

    raise HTTPException(status_code=status_code, detail=detail)

app = FastAPI(title="NL to ClickHouse Query Tool")

# CORS config
origins = [
    # Development mode
    "http://localhost:3000",
    "http://127.0.0.1:3000",

    # Production mode
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request validation
class QueryRequest(BaseModel):
    sql: str = Field(..., min_length=1, max_length=10000, description="SQL query to execute")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Query parameters")

class NaturalQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language query to process")

@app.get("/api")
async def root():
    return {"message": "NL ClickHouse Query API"}

@app.get("/api/tables")
async def get_tables():
    return ch_client.get_tables()

@app.post("/api/query")
async def execute_query(request: QueryRequest):
    """Execute SQL query with security validation"""
    result = ch_client.execute_query(request.sql, request.parameters)
    if not result["success"]:
        if result.get("security_error"):
            create_detailed_error(
                user_message="Invalid SQL query",
                debug_error=result["error"]
            )
        else:
            create_detailed_error(
                user_message="Failed to process query",
                debug_error=result["error"],
                status_code=500
            )

    return result

@app.get("/api/schema")
async def get_schema():
    """Get complete database schema"""
    return schema_inspector.get_all_tables_schema()

@app.get("/api/schema/{table_name}")
async def get_table_schema(table_name: str):
    """Get schema for specific table"""
    try:
        return schema_inspector.get_table_schema(table_name)
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    tables = ch_client.get_tables()
    return {
        "status": "healthy" if tables["success"] else "unhealthy",
        "clickhouse_connected": tables["success"]
    }

@app.post("/api/generate-sql")
async def generate_sql(request: dict):
    """Generate SQL from natural language"""
    natural_query = request.get("query")
    
    # Validate natural language query
    if not natural_query or not natural_query.strip():
        create_detailed_error(
            user_message="Natural language query cannot be empty, null, or contain only whitespace"
        )
    
    # Use all tables context
    schema_context = context_builder.get_all_tables_context()
    
    # Generate SQL
    result = llm_client.generate_sql(natural_query, schema_context)
    return result

@app.post("/api/smart-query")
async def smart_query(request: NaturalQueryRequest):
    """Process natural language query with smart context retrieval"""
    # Validate natural language query
    if not request.query or not request.query.strip():
        create_detailed_error(
            user_message="Natural language query cannot be empty, null, or contain only whitespace"
        )

    # Process with smart context retrieval
    result = query_processor.process_natural_query(request.query)
    
    if result["success"]:
        execution_result = ch_client.execute_query(result["sql"], result["parameters"])
        if not execution_result["success"]:
            if execution_result.get("security_error"):
                create_detailed_error(
                    user_message="Invalid SQL query",
                    debug_error=execution_result["error"]    
                )
            else:
                create_detailed_error(
                    user_message="Failed to process query",
                    debug_error=execution_result["error"],
                    status_code=500
                )

        result.update({
            "execution": execution_result
        })
    
    return result

@app.post("/api/embed-schema")
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

# Static file serving for production
static_dir = Path("../../frontend/out")

if static_dir.exists():
    # Mount static files
    app.mount("/static", StaticFiles(directory=static_dir / "_next/static"), name="static")
    app.mount("/_next", StaticFiles(directory=static_dir / "_next"), name="nextjs")
    
    # Catch-all route for SPA (must be last)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the Next.js frontend for all non-API routes"""
        # If it's an API route, let FastAPI handle it
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Try to serve the specific file first
        file_path = static_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        # For directories, try index.html
        index_path = static_dir / full_path / "index.html"
        if index_path.is_file():
            return FileResponse(index_path)
        
        # Fall back to root index.html for client-side routing
        root_index = static_dir / "index.html"
        if root_index.is_file():
            return FileResponse(root_index)
        
        raise HTTPException(status_code=404, detail="Page not found")
else:
    @app.get("/")
    async def dev_root():
        return {"message": "Frontend not built yet. Run 'npm run build' in your Next.js project and copy 'out' folder to 'frontend/out'"}
