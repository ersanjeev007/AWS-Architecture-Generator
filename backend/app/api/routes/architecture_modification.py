from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.database import get_db
from app.api.routes.auth import get_current_user
from app.services.architecture_modification_service import ArchitectureModificationService
from app.schemas.architecture import ArchitectureResponse
from app.schemas.auth import UserPreferences
from pydantic import BaseModel

router = APIRouter()

class ArchitectureModificationRequest(BaseModel):
    questionnaire_updates: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None
    regenerate: bool = False

class ServiceConfigurationRequest(BaseModel):
    service_type: str
    configuration: Dict[str, Any]

class CloneArchitectureRequest(BaseModel):
    new_project_name: str
    questionnaire_updates: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None

@router.put("/{project_id}/modify")
async def modify_architecture(
    project_id: str,
    request: ArchitectureModificationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Modify existing architecture"""
    try:
        service = ArchitectureModificationService(db)
        
        modified_project = service.modify_architecture(
            project_id=project_id,
            user_id=current_user.id,
            questionnaire_updates=request.questionnaire_updates,
            user_preferences=request.user_preferences,
            regenerate=request.regenerate
        )
        
        if not modified_project:
            raise HTTPException(status_code=404, detail="Architecture not found")
        
        return {
            "message": "Architecture modified successfully",
            "project": {
                "id": modified_project.id,
                "project_name": modified_project.project_name,
                "description": modified_project.description,
                "questionnaire_data": modified_project.questionnaire_data,
                "architecture_data": modified_project.architecture_data,
                "user_preferences": modified_project.user_preferences,
                "updated_at": modified_project.updated_at
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error modifying architecture: {str(e)}")

@router.put("/{project_id}/service-config")
async def update_service_configuration(
    project_id: str,
    request: ServiceConfigurationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update specific service configuration"""
    try:
        service = ArchitectureModificationService(db)
        
        modified_project = service.update_service_configuration(
            project_id=project_id,
            user_id=current_user.id,
            service_type=request.service_type,
            configuration=request.configuration
        )
        
        if not modified_project:
            raise HTTPException(status_code=404, detail="Architecture not found")
        
        return {
            "message": f"{request.service_type.upper()} configuration updated successfully",
            "project": {
                "id": modified_project.id,
                "architecture_data": modified_project.architecture_data,
                "user_preferences": modified_project.user_preferences,
                "updated_at": modified_project.updated_at
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating service configuration: {str(e)}")

@router.post("/{project_id}/clone")
async def clone_architecture(
    project_id: str,
    request: CloneArchitectureRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clone existing architecture with optional modifications"""
    try:
        service = ArchitectureModificationService(db)
        
        modifications = {}
        if request.questionnaire_updates:
            modifications['questionnaire_updates'] = request.questionnaire_updates
        if request.user_preferences:
            modifications['user_preferences'] = request.user_preferences
        
        cloned_project = service.clone_architecture(
            project_id=project_id,
            user_id=current_user.id,
            new_project_name=request.new_project_name,
            modifications=modifications if modifications else None
        )
        
        if not cloned_project:
            raise HTTPException(status_code=404, detail="Original architecture not found")
        
        return {
            "message": "Architecture cloned successfully",
            "project": {
                "id": cloned_project.id,
                "project_name": cloned_project.project_name,
                "description": cloned_project.description,
                "questionnaire_data": cloned_project.questionnaire_data,
                "architecture_data": cloned_project.architecture_data,
                "user_preferences": cloned_project.user_preferences,
                "created_at": cloned_project.created_at
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cloning architecture: {str(e)}")

@router.get("/service-configurations/{service_type}")
async def get_service_configurations(
    service_type: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available configuration options for a service type"""
    try:
        service = ArchitectureModificationService(db)
        configurations = service.get_available_configurations(service_type)
        
        if not configurations:
            raise HTTPException(status_code=404, detail=f"Service type {service_type} not supported")
        
        return {
            "service_type": service_type,
            "configurations": configurations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting service configurations: {str(e)}")

@router.get("/{project_id}/preferences")
async def get_user_preferences(
    project_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user preferences for a specific project"""
    try:
        from app.database import ProjectDB
        
        project = db.query(ProjectDB).filter(
            ProjectDB.id == project_id,
            ProjectDB.user_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Architecture not found")
        
        return {
            "project_id": project_id,
            "user_preferences": project.user_preferences or {},
            "default_preferences": {
                "rds_storage_gb": 20,
                "ec2_instance_type": "t3.medium",
                "rds_instance_class": "db.t3.micro",
                "lambda_memory_mb": 128,
                "s3_storage_class": "STANDARD",
                "cloudfront_price_class": "PriceClass_All"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user preferences: {str(e)}")

@router.put("/{project_id}/preferences")
async def update_user_preferences(
    project_id: str,
    preferences: UserPreferences,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences for a specific project"""
    try:
        service = ArchitectureModificationService(db)
        
        modified_project = service.modify_architecture(
            project_id=project_id,
            user_id=current_user.id,
            user_preferences=preferences.model_dump(exclude_unset=True),
            regenerate=True
        )
        
        if not modified_project:
            raise HTTPException(status_code=404, detail="Architecture not found")
        
        return {
            "message": "User preferences updated successfully",
            "project_id": project_id,
            "user_preferences": modified_project.user_preferences,
            "updated_at": modified_project.updated_at
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user preferences: {str(e)}")