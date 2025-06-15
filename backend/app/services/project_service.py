from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import json
from app.database import ProjectDB
from app.models.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListItem
from app.schemas.questionnaire import QuestionnaireRequest
from app.schemas.architecture import ArchitectureResponse
from app.core.architecture_generator import ArchitectureGenerator

class ProjectService:
    """Service for managing projects"""
    
    def __init__(self):
        self.generator = ArchitectureGenerator()
    
    def create_project(self, db: Session, project_data: ProjectCreate) -> ProjectResponse:
        """Create new project with generated architecture"""
        
        # Generate architecture
        architecture = self.generator.generate(project_data.questionnaire)
        
        # Use custom save name or project name from questionnaire
        save_name = project_data.save_name or project_data.questionnaire.project_name
        
        # Create database record
        db_project = ProjectDB(
            id=architecture.id,  # Use the same ID as architecture
            project_name=save_name,
            description=project_data.questionnaire.description,
            questionnaire_data=project_data.questionnaire.dict(),
            architecture_data=architecture.dict()
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        return ProjectResponse.from_orm(db_project)
    
    def create_project_with_architecture(self, db: Session, questionnaire: QuestionnaireRequest, architecture: ArchitectureResponse) -> ProjectResponse:
        """Create new project with pre-generated architecture"""
        
        # Create database record with provided architecture
        db_project = ProjectDB(
            id=str(uuid.uuid4()),  # Generate new ID for project
            project_name=questionnaire.project_name,
            description=questionnaire.description,
            questionnaire_data=questionnaire.dict(),
            architecture_data=architecture.dict()
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        return ProjectResponse.from_orm(db_project)
    
    def get_project(self, db: Session, project_id: str) -> Optional[ProjectResponse]:
        """Get project by ID"""
        db_project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if db_project:
            return ProjectResponse.from_orm(db_project)
        return None
    
    def get_project_by_name(self, db: Session, name: str) -> Optional[ProjectResponse]:
        """Get project by name"""
        db_project = db.query(ProjectDB).filter(ProjectDB.project_name == name).first()
        if db_project:
            return ProjectResponse.from_orm(db_project)
        return None
    
    def list_projects(self, db: Session, skip: int = 0, limit: int = 100) -> List[ProjectResponse]:
        """List all projects with full data including architecture"""
        db_projects = db.query(ProjectDB).offset(skip).limit(limit).all()
        return [ProjectResponse.from_orm(project) for project in db_projects]
    
    def list_projects_summary(self, db: Session, skip: int = 0, limit: int = 100) -> List[ProjectListItem]:
        """List all projects with summary data only (for performance if needed)"""
        db_projects = db.query(ProjectDB).offset(skip).limit(limit).all()
        return [ProjectListItem.from_orm(project) for project in db_projects]
    
    def update_project(self, db: Session, project_id: str, project_update: ProjectUpdate) -> Optional[ProjectResponse]:
        """Update project questionnaire and regenerate architecture"""
        
        db_project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if not db_project:
            return None
        
        # Generate new architecture with updated questionnaire
        new_architecture = self.generator.generate(project_update.questionnaire)
        
        # Update database record
        db_project.project_name = project_update.questionnaire.project_name
        db_project.description = project_update.questionnaire.description
        db_project.questionnaire_data = project_update.questionnaire.dict()
        db_project.architecture_data = new_architecture.dict()
        
        db.commit()
        db.refresh(db_project)
        
        return ProjectResponse.from_orm(db_project)
    
    def save_architecture_to_project(self, db: Session, project_id: str, architecture: ArchitectureResponse) -> bool:
        """Save architecture data to existing project"""
        
        db_project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if not db_project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        try:
            # Update the project with new architecture data
            db_project.architecture_data = architecture.dict()
            db.commit()
            db.refresh(db_project)
            return True
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to save architecture to project: {str(e)}")
    
    def regenerate_architecture(self, db: Session, project_id: str) -> Optional[ProjectResponse]:
        """Regenerate architecture for existing project using its questionnaire data"""
        
        db_project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if not db_project:
            return None
        
        # Recreate questionnaire from stored data
        questionnaire = QuestionnaireRequest(**db_project.questionnaire_data)
        
        # Generate new architecture
        new_architecture = self.generator.generate(questionnaire)
        
        # Update project with new architecture
        db_project.architecture_data = new_architecture.dict()
        db.commit()
        db.refresh(db_project)
        
        return ProjectResponse.from_orm(db_project)
    
    def delete_project(self, db: Session, project_id: str) -> bool:
        """Delete project"""
        db_project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if db_project:
            db.delete(db_project)
            db.commit()
            return True
        return False
    
    def get_architecture_from_project(self, db: Session, project_id: str) -> Optional[ArchitectureResponse]:
        """Get architecture data from saved project"""
        db_project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if db_project and db_project.architecture_data:
            return ArchitectureResponse(**db_project.architecture_data)
        return None