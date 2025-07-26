from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging

from app.database import get_db
from app.api.routes.auth import get_current_user
from app.services.infrastructure_import_service import InfrastructureImportService
from app.schemas.auth import UserResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/infrastructure-import", tags=["infrastructure-import"])

class AWSCredentials(BaseModel):
    """AWS credentials for account scanning"""
    access_key_id: str = Field(..., description="AWS Access Key ID")
    secret_access_key: str = Field(..., description="AWS Secret Access Key")
    session_token: Optional[str] = Field(None, description="AWS Session Token (optional)")
    account_id: Optional[str] = Field(None, description="AWS Account ID")
    region: str = Field("us-east-1", description="AWS Region to scan")

class ImportProjectRequest(BaseModel):
    """Request to create project from imported infrastructure"""
    project_name: str = Field(..., description="Name for the new project")
    template_type: str = Field("terraform", pattern="^(terraform|cloudformation)$", description="Template type to generate")
    aws_credentials: AWSCredentials
    infrastructure_data: Optional[Dict[str, Any]] = Field(None, description="Pre-scanned infrastructure data")

class ScanResponse(BaseModel):
    """Response from AWS account scan"""
    success: bool
    infrastructure: Dict[str, Any]
    scan_summary: Dict[str, Any]

class ImportResponse(BaseModel):
    """Response from infrastructure import"""
    success: bool
    project_id: str
    project_name: str
    terraform_template: Optional[str] = None
    cloudformation_template: Optional[str] = None
    diagram_data: Dict[str, Any]
    security_analysis: Dict[str, Any]

@router.post("/scan-aws-account", response_model=ScanResponse)
async def scan_aws_account(
    credentials: AWSCredentials,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Scan AWS account to discover existing infrastructure
    """
    try:
        import_service = InfrastructureImportService()
        
        # Convert credentials to dict
        creds_dict = {
            "access_key_id": credentials.access_key_id,
            "secret_access_key": credentials.secret_access_key,
            "session_token": credentials.session_token,
            "account_id": credentials.account_id,
            "region": credentials.region
        }
        
        # Scan the AWS account
        infrastructure = await import_service.scan_aws_account(creds_dict, credentials.region)
        
        # Create scan summary
        services = infrastructure.get("services", {})
        scan_summary = {
            "total_services": len(services),
            "services_found": list(services.keys()),
            "resources_count": {
                service: len(resources) if isinstance(resources, dict) else len(resources.get("instances", [])) if isinstance(resources, dict) else 0
                for service, resources in services.items()
            },
            "scan_timestamp": infrastructure.get("scan_timestamp"),
            "region": infrastructure.get("region"),
            "account_id": infrastructure.get("account_id")
        }
        
        logger.info(f"Successfully scanned AWS account for user {current_user.id}")
        
        return ScanResponse(
            success=True,
            infrastructure=infrastructure,
            scan_summary=scan_summary
        )
        
    except Exception as e:
        logger.error(f"Error scanning AWS account: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to scan AWS account: {str(e)}")

@router.post("/import-infrastructure", response_model=ImportResponse)
async def import_infrastructure(
    request: ImportProjectRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Import infrastructure and create a new project
    """
    try:
        import_service = InfrastructureImportService()
        
        # Get infrastructure data - either from request or scan account
        if request.infrastructure_data:
            infrastructure = request.infrastructure_data
        else:
            # Scan the AWS account
            creds_dict = {
                "access_key_id": request.aws_credentials.access_key_id,
                "secret_access_key": request.aws_credentials.secret_access_key,
                "session_token": request.aws_credentials.session_token,
                "account_id": request.aws_credentials.account_id,
                "region": request.aws_credentials.region
            }
            
            infrastructure = await import_service.scan_aws_account(creds_dict, request.aws_credentials.region)
        
        # Create project from imported infrastructure
        project_id = await import_service.create_imported_project(
            db=db,
            user_id=current_user.id,
            infrastructure=infrastructure,
            project_name=request.project_name,
            template_type=request.template_type
        )
        
        # Generate templates and diagrams
        if request.template_type == "terraform":
            terraform_template = await import_service.generate_terraform_from_infrastructure(infrastructure)
            cloudformation_template = None
        else:
            terraform_template = None
            cloudformation_template = await import_service.generate_cloudformation_from_infrastructure(infrastructure)
        
        diagram_data = await import_service.generate_architecture_diagram(infrastructure)
        security_analysis = await import_service.analyze_imported_security(infrastructure)
        
        logger.info(f"Successfully imported infrastructure as project {project_id} for user {current_user.id}")
        
        return ImportResponse(
            success=True,
            project_id=project_id,
            project_name=request.project_name,
            terraform_template=terraform_template,
            cloudformation_template=cloudformation_template,
            diagram_data=diagram_data,
            security_analysis=security_analysis
        )
        
    except Exception as e:
        logger.error(f"Error importing infrastructure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to import infrastructure: {str(e)}")

@router.post("/generate-terraform")
async def generate_terraform_from_scan(
    infrastructure: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Generate Terraform configuration from scanned infrastructure
    """
    try:
        import_service = InfrastructureImportService()
        terraform_config = await import_service.generate_terraform_from_infrastructure(infrastructure)
        
        return {
            "success": True,
            "terraform_template": terraform_config,
            "account_id": infrastructure.get("account_id"),
            "region": infrastructure.get("region")
        }
        
    except Exception as e:
        logger.error(f"Error generating Terraform: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate Terraform: {str(e)}")

@router.post("/generate-cloudformation")
async def generate_cloudformation_from_scan(
    infrastructure: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Generate CloudFormation template from scanned infrastructure
    """
    try:
        import_service = InfrastructureImportService()
        cf_template = await import_service.generate_cloudformation_from_infrastructure(infrastructure)
        
        return {
            "success": True,
            "cloudformation_template": cf_template,
            "account_id": infrastructure.get("account_id"),
            "region": infrastructure.get("region")
        }
        
    except Exception as e:
        logger.error(f"Error generating CloudFormation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate CloudFormation: {str(e)}")

@router.post("/analyze-security")
async def analyze_imported_security(
    infrastructure: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Analyze security posture of imported infrastructure
    """
    try:
        import_service = InfrastructureImportService()
        security_analysis = await import_service.analyze_imported_security(infrastructure)
        
        return {
            "success": True,
            "security_analysis": security_analysis,
            "account_id": infrastructure.get("account_id"),
            "region": infrastructure.get("region")
        }
        
    except Exception as e:
        logger.error(f"Error analyzing security: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze security: {str(e)}")

@router.post("/generate-diagram")
async def generate_architecture_diagram(
    infrastructure: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Generate architecture diagram from imported infrastructure
    """
    try:
        import_service = InfrastructureImportService()
        diagram_data = await import_service.generate_architecture_diagram(infrastructure)
        
        return {
            "success": True,
            "diagram_data": diagram_data,
            "account_id": infrastructure.get("account_id"),
            "region": infrastructure.get("region")
        }
        
    except Exception as e:
        logger.error(f"Error generating diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate diagram: {str(e)}")