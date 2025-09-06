from doctest import debug
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import ch_client
from app.schema import schema_inspector
from app.llm import llm_client
from app.context import context_builder
from app.query_processor import query_processor
from app.schema_embedder import schema_embedder
from app.embeddings import embedding_manager
from app.sql_security import sql_validator
from app.schemas.schemas import QueryRequest, NaturalQueryRequest, ErrorResponse, ConnectionRequest, DisconnectRequest
from app.services.ca_certificate_service import CACertificateService
from app.services.connection_service import ConnectionService
from pathlib import Path
import os
import boto3
from botocore.exceptions import ClientError

def create_detailed_error(user_message: str, debug_error: str = None, status_code: int = 400):
    """Create structured error response with optional debug info"""
    error_detail = ErrorResponse(
        success=False,
        user_message=user_message,
        debug_error=debug_error
    )

    raise HTTPException(status_code=status_code, detail=error_detail.dict())

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

# Initialize services
ca_cert_service = CACertificateService()
connection_service = ConnectionService()

@app.get("/api")
async def root():
    return {"message": "NL ClickHouse Query API"}

@app.post("/api/upload-ca-cert")
async def upload_ca_certificate(file: UploadFile = File(...)):
    """Upload CA certificate to web-app EC2 instance"""
    try:
        content = await file.read()
        result = ca_cert_service.upload_certificate(content, file.filename)
        return result

    except Exception as e:
        create_detailed_error(
            user_message=f"Certificate upload failed: {str(e)}",
            debug_error=str(e),
            status_code=400 if isinstance(e, (ValueError, FileNotFoundError, PermissionError)) else 500
        )

@app.post("/api/connect-kafka")
async def connect_kafka(request: ConnectionRequest):
    """Execute connect script with the uploaded CA certificate"""
    try:
          # Get the certificate info from the CA certificate service
        if ca_cert_service.ca_cert_path:
            connection_service.set_certificate_info(ca_cert_service.ca_cert_path)
        else:
            raise FileNotFoundError("No certificate uploaded. Please upload a CA certificate first.")
            
        result = connection_service.execute_connection_script(request.dict())
        return result

    except Exception as e:
        create_detailed_error(
            # user_message="Failed to connect to Kafka",
            user_message=str(e),
            debug_error=str(e),
            status_code=400 if isinstance(e, (FileNotFoundError)) else 500
        )

@app.post("/api/disconnect-kafka")
async def disconnect_kafka(request: DisconnectRequest):
    """Execute disconnect script to remove a Kafka connection"""
    try:
        result = connection_service.execute_disconnect_script(request.name)
        return result

    except Exception as e:
        create_detailed_error(
            user_message="Failed to disconnect from Kafka",
            debug_error=str(e),
            status_code=500
        )

@app.get("/api/grafana-url")
async def get_grafana_url():
    """Get Grafana dashboard URL from SSM Parameter Store"""
    try:
        # Initialize SSM client
        ssm_client = boto3.client('ssm', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))
        
        # Get Grafana URL from SSM Parameter Store
        response = ssm_client.get_parameter(
            Name='/aurora/grafana-url',
            WithDecryption=False
        )
        
        grafana_url = response['Parameter']['Value']
        
        return {
            "success": True,
            "grafana_url": grafana_url
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ParameterNotFound':
            create_detailed_error(
                user_message="Grafana URL not found in configuration",
                debug_error=f"SSM Parameter '/aurora/grafana-url' not found: {str(e)}",
                status_code=404
            )
        else:
            create_detailed_error(
                user_message="Failed to retrieve Grafana URL",
                debug_error=f"AWS SSM error: {str(e)}",
                status_code=500
            )
    except Exception as e:
        create_detailed_error(
            user_message="Failed to retrieve Grafana URL",
            debug_error=str(e),
            status_code=500
        )

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
FILE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = FILE_DIR.parent.parent

candidates = [
    PROJECT_ROOT / "frontend" / "out",
    Path("/frontend/out"),
    Path(os.getenv("FRONTEND_OUT_DIR")) if os.getenv("FRONTEND_OUT_DIR") else None,
]

static_dir = next((p for p in candidates if p and p.exists()), None)

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
