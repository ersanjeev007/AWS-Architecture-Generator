from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AWSAccountBase(BaseModel):
    """Base AWS Account model"""
    account_name: str = Field(..., min_length=1, max_length=100)
    aws_region: str = Field(default="us-west-2")
    description: Optional[str] = None

class AWSAccountCreate(AWSAccountBase):
    """Create AWS Account with credentials"""
    aws_access_key_id: str = Field(..., min_length=16, max_length=128)
    aws_secret_access_key: str = Field(..., min_length=16, max_length=128)
    aws_session_token: Optional[str] = None

class AWSAccountUpdate(BaseModel):
    """Update AWS Account (without credentials)"""
    account_name: Optional[str] = Field(None, min_length=1, max_length=100)
    aws_region: Optional[str] = None
    description: Optional[str] = None

class AWSAccountResponse(AWSAccountBase):
    """AWS Account response (no credentials exposed)"""
    id: str
    is_active: bool
    last_validated: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AWSAccountListItem(BaseModel):
    """AWS Account list item (summary)"""
    id: str
    account_name: str
    aws_region: str
    is_active: bool
    last_validated: Optional[datetime] = None

    class Config:
        from_attributes = True

class DeploymentRequest(BaseModel):
    """Infrastructure deployment request"""
    project_id: str
    aws_account_id: str
    template_type: str = Field(..., pattern="^(terraform|cloudformation)$")
    dry_run: bool = Field(default=True)

class DestroyRequest(BaseModel):
    """Infrastructure destruction request"""
    deployment_id: str
    aws_account_id: str
    template_type: str = Field(..., pattern="^(terraform|cloudformation)$")
    dry_run: bool = Field(default=True)
    force_destroy: bool = Field(default=False)
    
class DeploymentResponse(BaseModel):
    """Infrastructure deployment response"""
    deployment_id: str
    status: str
    message: str
    output: Optional[str] = None
    error: Optional[str] = None