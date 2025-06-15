from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Basic Application Settings
    PROJECT_NAME: str = "AWS Architecture Generator"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS Settings - Simplified since nginx handles routing
    ALLOWED_HOSTS: List[str] = [
        "http://localhost",
        "http://localhost:80",
        "http://127.0.0.1",
        "*"  # Since nginx is handling the routing
    ]
    
    # AWS Settings (for future use)
    AWS_REGION: str = "us-west-2"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()