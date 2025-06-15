from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.schemas.questionnaire import QuestionnaireRequest
from app.schemas.architecture import ArchitectureResponse

class ProjectCreate(BaseModel):
    """Create new project"""
    questionnaire: QuestionnaireRequest
    save_name: Optional[str] = None  # Optional custom name for saving

class ProjectUpdate(BaseModel):
    """Update existing project"""
    questionnaire: QuestionnaireRequest

class ProjectResponse(BaseModel):
    """Project response with full data"""
    id: str
    project_name: str
    description: str
    questionnaire_data: Dict[str, Any]
    architecture_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectListItem(BaseModel):
    """Project list item (summary)"""
    id: str
    project_name: str
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True