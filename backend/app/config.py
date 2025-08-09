from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    clickhouse_host: str = "localhost"
    clickhouse_port: int = 8123
    clickhouse_user: str = ""
    clickhouse_password: str = ""
    clickhouse_database: str = "default"
    openai_api_key: str = ""
    
    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")

settings = Settings()
