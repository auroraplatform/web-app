from fastapi import FastAPI
from app.database import ch_client
from app.schema import schema_inspector
from app.llm import llm_client
from app.context import context_builder

app = FastAPI(title="NL to ClickHouse Query Tool")

@app.get("/")
async def root():
    return {"message": "NL ClickHouse Query API"}

@app.get("/tables")
async def get_tables():
    return ch_client.get_tables()

@app.post("/query")
async def execute_query(query: dict):
    sql = query.get("sql")
    return ch_client.execute_query(sql)

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
    
    if not natural_query:
        return {"error": "Query is required"}
    
    # For now, use all tables context (we'll optimize this tomorrow)
    schema_context = context_builder.get_all_tables_context()
    
    # Generate SQL
    result = llm_client.generate_sql(natural_query, schema_context)
    
    if result["success"]:
        # Add query explanation
        explanation = llm_client.explain_query(result["sql"])
        result["explanation"] = explanation
    
    return result
