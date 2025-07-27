from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.aws_account import (
    AWSAccountCreate,
    AWSAccountUpdate,
    AWSAccountResponse,
    AWSAccountListItem,
    DeploymentRequest,
    DeploymentResponse,
    DestroyRequest
)
from app.services.aws_account_service import AWSAccountService
from app.services.deployment_service import DeploymentService

router = APIRouter()

def get_aws_account_service() -> AWSAccountService:
    return AWSAccountService()

def get_deployment_service() -> DeploymentService:
    return DeploymentService()

@router.post("/", response_model=AWSAccountResponse)
async def create_aws_account(
    account_data: AWSAccountCreate,
    db: Session = Depends(get_db),
    service: AWSAccountService = Depends(get_aws_account_service)
):
    """Create new AWS account with credentials"""
    try:
        account = service.create_account(db, account_data)
        return account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create AWS account: {str(e)}")

@router.get("/", response_model=List[AWSAccountListItem])
async def list_aws_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    service: AWSAccountService = Depends(get_aws_account_service)
):
    """List all AWS accounts"""
    try:
        accounts = service.list_accounts(db, skip=skip, limit=limit)
        return accounts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list AWS accounts: {str(e)}")

@router.get("/{account_id}", response_model=AWSAccountResponse)
async def get_aws_account(
    account_id: str,
    db: Session = Depends(get_db),
    service: AWSAccountService = Depends(get_aws_account_service)
):
    """Get AWS account by ID"""
    try:
        account = service.get_account(db, account_id)
        if not account:
            raise HTTPException(status_code=404, detail="AWS account not found")
        return account
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AWS account: {str(e)}")

@router.put("/{account_id}", response_model=AWSAccountResponse)
async def update_aws_account(
    account_id: str,
    account_update: AWSAccountUpdate,
    db: Session = Depends(get_db),
    service: AWSAccountService = Depends(get_aws_account_service)
):
    """Update AWS account information"""
    try:
        account = service.update_account(db, account_id, account_update)
        if not account:
            raise HTTPException(status_code=404, detail="AWS account not found")
        return account
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update AWS account: {str(e)}")

@router.delete("/{account_id}")
async def delete_aws_account(
    account_id: str,
    db: Session = Depends(get_db),
    service: AWSAccountService = Depends(get_aws_account_service)
):
    """Delete AWS account"""
    try:
        success = service.delete_account(db, account_id)
        if not success:
            raise HTTPException(status_code=404, detail="AWS account not found")
        return {"message": "AWS account deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete AWS account: {str(e)}")

@router.post("/validate-credentials")
async def validate_new_aws_credentials(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_session_token: str = None,
    region: str = "us-west-2",
    service: AWSAccountService = Depends(get_aws_account_service)
):
    """Validate new AWS credentials before account creation"""
    try:
        credentials = {
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "aws_session_token": aws_session_token,
            "region": region
        }
        
        validation_result = service.validate_credentials(credentials)
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate AWS credentials: {str(e)}")

@router.post("/{account_id}/validate")
async def validate_aws_account(
    account_id: str,
    db: Session = Depends(get_db),
    service: AWSAccountService = Depends(get_aws_account_service)
):
    """Validate AWS account credentials"""
    try:
        is_valid = service.validate_account(db, account_id)
        return {
            "account_id": account_id,
            "is_valid": is_valid,
            "message": "Credentials are valid" if is_valid else "Credentials are invalid or expired"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate AWS account: {str(e)}")

@router.post("/deploy", response_model=DeploymentResponse)
async def deploy_infrastructure(
    deployment_request: DeploymentRequest,
    db: Session = Depends(get_db),
    service: DeploymentService = Depends(get_deployment_service)
):
    """Deploy infrastructure to AWS"""
    try:
        result = service.deploy_infrastructure(db, deployment_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deploy infrastructure: {str(e)}")

@router.get("/deployments/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment_status(
    deployment_id: str,
    db: Session = Depends(get_db),
    service: DeploymentService = Depends(get_deployment_service)
):
    """Get deployment status"""
    try:
        deployment = service.get_deployment_status(db, deployment_id)
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")
        return deployment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get deployment status: {str(e)}")

@router.post("/destroy", response_model=DeploymentResponse)
async def destroy_infrastructure(
    destroy_request: DestroyRequest,
    db: Session = Depends(get_db),
    service: DeploymentService = Depends(get_deployment_service)
):
    """Destroy deployed infrastructure"""
    try:
        result = service.destroy_infrastructure(db, destroy_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to destroy infrastructure: {str(e)}")

@router.get("/deployments/project/{project_id}")
async def list_project_deployments(
    project_id: str,
    db: Session = Depends(get_db),
    service: DeploymentService = Depends(get_deployment_service)
):
    """List all deployments for a project"""
    try:
        deployments = service.list_deployments(db, project_id)
        return deployments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list deployments: {str(e)}")

@router.get("/deployment-status/project/{project_id}")
async def get_project_deployment_status(
    project_id: str,
    db: Session = Depends(get_db),
    service: DeploymentService = Depends(get_deployment_service)
):
    """Get current deployment status summary for a project"""
    try:
        status = service.get_project_deployment_status(db, project_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get deployment status: {str(e)}")