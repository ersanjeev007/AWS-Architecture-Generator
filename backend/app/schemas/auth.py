from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    full_name: Optional[str] = Field(None, max_length=255)

    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only letters, numbers, hyphens, and underscores')
        return v.lower()

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str]
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    user: UserResponse
    token: str
    expires_at: datetime

class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, max_length=255)
    full_name: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=4, max_length=100)

class UserPreferences(BaseModel):
    rds_storage_gb: Optional[int] = Field(default=20, ge=20, le=16384)
    ec2_instance_type: Optional[str] = Field(default="t3.medium")
    rds_instance_class: Optional[str] = Field(default="db.t3.micro")
    lambda_memory_mb: Optional[int] = Field(default=128, ge=128, le=10240)
    s3_storage_class: Optional[str] = Field(default="STANDARD")
    cloudfront_price_class: Optional[str] = Field(default="PriceClass_All")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rds_storage_gb": 50,
                "ec2_instance_type": "t3.large",
                "rds_instance_class": "db.t3.small",
                "lambda_memory_mb": 256,
                "s3_storage_class": "STANDARD_IA",
                "cloudfront_price_class": "PriceClass_100"
            }
        }