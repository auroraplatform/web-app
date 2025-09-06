from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# Query schemas
class QueryRequest(BaseModel):
    sql: str = Field(..., min_length=1, max_length=10000, description="SQL query to execute")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Query parameters")

class NaturalQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language query to process")

# Connection schemas
class ConnectionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Connection name")
    broker: str = Field(..., min_length=1, max_length=255, description="Kafka broker address")
    topic: str = Field(..., min_length=1, max_length=100, description="Kafka topic name")
    username: str = Field(..., min_length=1, max_length=100, description="Kafka username")
    password: str = Field(..., min_length=1, max_length=255, description="Kafka password")

class DisconnectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Connection name to disconnect")

class ConnectionResponse(BaseModel):
    success: bool
    message: str
    details: str
    return_code: int

# Certificate schemas
class CertificateUploadResponse(BaseModel):
    success: bool
    message: str
    file_info: Dict[str, Any]

# Common schemas
class ErrorResponse(BaseModel):
    """Common error response schema"""
    success: bool = False
    user_message: str
    debug_error: Optional[str] = None
    error_code: Optional[str] = None

class SuccessResponse(BaseModel):
    """Common success response schema"""
    success: bool = True
    message: str
    data: Optional[Any] = None
