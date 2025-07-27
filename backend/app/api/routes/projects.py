from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListItem
from app.schemas.architecture import ArchitectureResponse
from app.schemas.questionnaire import QuestionnaireRequest
from app.services.project_service import ProjectService
from app.services.architecture_service import ArchitectureService
from app.core.architecture_generator import ArchitectureGenerator
from app.api.routes.auth import get_current_user

router = APIRouter()

def get_project_service() -> ProjectService:
    return ProjectService()

def get_architecture_service() -> ArchitectureService:
    return ArchitectureService()

def get_architecture_generator() -> ArchitectureGenerator:
    return ArchitectureGenerator()

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    project_service: ProjectService = Depends(get_project_service)
):
    """Create new project"""
    try:
        project = project_service.create_project(db, project_data)
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@router.post("/generate-architecture", response_model=dict)
async def create_project_with_architecture(
    questionnaire: QuestionnaireRequest,
    db: Session = Depends(get_db),
    project_service: ProjectService = Depends(get_project_service),
    architecture_service: ArchitectureService = Depends(get_architecture_service),
    generator: ArchitectureGenerator = Depends(get_architecture_generator)
):
    """Create new project and generate architecture"""
    try:
        # Generate the architecture
        architecture = await architecture_service.generate_architecture(questionnaire, generator)
        
        # Create project with the generated architecture
        project = project_service.create_project_with_architecture(db, questionnaire, architecture)
        
        return {
            "message": "Project created and architecture generated successfully",
            "project_id": project.id,
            "project_name": project.project_name,
            "architecture": architecture
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create project with architecture: {str(e)}")

@router.get("/", response_model=List[ProjectResponse])  # CHANGED: from ProjectListItem to ProjectResponse
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    project_service: ProjectService = Depends(get_project_service)
):
    """List all saved projects with architecture data"""  # UPDATED description
    try:
        projects = project_service.list_projects(db, skip=skip, limit=limit)
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {str(e)}")

@router.get("/summary", response_model=List[ProjectListItem])  # NEW: optional summary endpoint
async def list_projects_summary(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    project_service: ProjectService = Depends(get_project_service)
):
    """List projects with summary data only (for performance)"""
    try:
        projects = project_service.list_projects_summary(db, skip=skip, limit=limit)
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list projects summary: {str(e)}")

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    project_service: ProjectService = Depends(get_project_service)
):
    """Get project by ID"""
    try:
        project = project_service.get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    project_service: ProjectService = Depends(get_project_service)
):
    """Update project questionnaire and regenerate architecture"""
    try:
        project = project_service.update_project(db, project_id, project_update)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")

@router.put("/{project_id}/regenerate-architecture", response_model=dict)
async def regenerate_project_architecture(
    project_id: str,
    db: Session = Depends(get_db),
    project_service: ProjectService = Depends(get_project_service)
):
    """Regenerate architecture for existing project"""
    try:
        # Use the service method to regenerate architecture
        project = project_service.regenerate_architecture(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get the updated architecture
        architecture = project_service.get_architecture_from_project(db, project_id)
        
        return {
            "message": "Architecture regenerated successfully",
            "project_id": project_id,
            "architecture": architecture
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to regenerate architecture: {str(e)}")

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    project_service: ProjectService = Depends(get_project_service)
):
    """Delete project"""
    try:
        success = project_service.delete_project(db, project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")

@router.get("/{project_id}/architecture", response_model=ArchitectureResponse)
async def get_project_architecture(
    project_id: str,
    db: Session = Depends(get_db),
    project_service: ProjectService = Depends(get_project_service)
):
    """Get architecture from saved project"""
    try:
        architecture = project_service.get_architecture_from_project(db, project_id)
        if not architecture:
            raise HTTPException(status_code=404, detail="Project or architecture not found")
        return architecture
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get architecture: {str(e)}")