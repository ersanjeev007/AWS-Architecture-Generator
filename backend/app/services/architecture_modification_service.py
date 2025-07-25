from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

from app.database import ProjectDB
from app.schemas.questionnaire import QuestionnaireRequest
from app.core.architecture_generator import ArchitectureGenerator

class ArchitectureModificationService:
    def __init__(self, db: Session):
        self.db = db

    def modify_architecture(
        self, 
        project_id: str, 
        user_id: str,
        questionnaire_updates: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        regenerate: bool = False
    ) -> Optional[ProjectDB]:
        """Modify existing architecture with new parameters"""
        
        # Get the project
        project = self.db.query(ProjectDB).filter(
            ProjectDB.id == project_id,
            ProjectDB.user_id == user_id
        ).first()
        
        if not project:
            return None
        
        # Update questionnaire data if provided
        if questionnaire_updates:
            current_questionnaire = project.questionnaire_data or {}
            current_questionnaire.update(questionnaire_updates)
            project.questionnaire_data = current_questionnaire
        
        # Update user preferences if provided
        if user_preferences:
            current_preferences = project.user_preferences or {}
            current_preferences.update(user_preferences)
            project.user_preferences = current_preferences
        
        # Regenerate architecture if requested or if significant changes were made
        if regenerate or questionnaire_updates:
            questionnaire = QuestionnaireRequest(**project.questionnaire_data)
            generator = ArchitectureGenerator()
            
            # Generate new architecture with user preferences
            architecture_data = generator.generate_architecture(
                questionnaire=questionnaire,
                user_preferences=project.user_preferences
            )
            
            project.architecture_data = architecture_data
        
        # Update timestamp
        project.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(project)
        
        return project

    def update_service_configuration(
        self, 
        project_id: str, 
        user_id: str,
        service_type: str,
        configuration: Dict[str, Any]
    ) -> Optional[ProjectDB]:
        """Update specific service configuration"""
        
        project = self.db.query(ProjectDB).filter(
            ProjectDB.id == project_id,
            ProjectDB.user_id == user_id
        ).first()
        
        if not project:
            return None
        
        # Update user preferences for the specific service
        if not project.user_preferences:
            project.user_preferences = {}
        
        # Map service types to preference keys
        service_preference_map = {
            'rds': {
                'storage_gb': 'rds_storage_gb',
                'instance_class': 'rds_instance_class',
                'engine': 'rds_engine',
                'multi_az': 'rds_multi_az'
            },
            'ec2': {
                'instance_type': 'ec2_instance_type',
                'storage_size': 'ec2_storage_size',
                'storage_type': 'ec2_storage_type'
            },
            'lambda': {
                'memory_mb': 'lambda_memory_mb',
                'timeout': 'lambda_timeout',
                'runtime': 'lambda_runtime'
            },
            's3': {
                'storage_class': 's3_storage_class',
                'versioning': 's3_versioning',
                'encryption': 's3_encryption'
            },
            'cloudfront': {
                'price_class': 'cloudfront_price_class',
                'caching_behavior': 'cloudfront_caching'
            }
        }
        
        if service_type in service_preference_map:
            service_mapping = service_preference_map[service_type]
            for config_key, value in configuration.items():
                if config_key in service_mapping:
                    preference_key = service_mapping[config_key]
                    project.user_preferences[preference_key] = value
        
        # Regenerate architecture with new preferences
        questionnaire = QuestionnaireRequest(**project.questionnaire_data)
        generator = ArchitectureGenerator()
        
        architecture_data = generator.generate_architecture(
            questionnaire=questionnaire,
            user_preferences=project.user_preferences
        )
        
        project.architecture_data = architecture_data
        project.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(project)
        
        return project

    def clone_architecture(
        self, 
        project_id: str, 
        user_id: str,
        new_project_name: str,
        modifications: Optional[Dict[str, Any]] = None
    ) -> Optional[ProjectDB]:
        """Clone existing architecture with optional modifications"""
        
        # Get the original project
        original_project = self.db.query(ProjectDB).filter(
            ProjectDB.id == project_id,
            ProjectDB.user_id == user_id
        ).first()
        
        if not original_project:
            return None
        
        # Create new project with cloned data
        new_project = ProjectDB(
            id=str(uuid.uuid4()),
            project_name=new_project_name,
            description=f"Cloned from {original_project.project_name}",
            user_id=user_id,
            questionnaire_data=original_project.questionnaire_data.copy(),
            architecture_data=original_project.architecture_data.copy(),
            user_preferences=original_project.user_preferences.copy() if original_project.user_preferences else {}
        )
        
        # Apply modifications if provided
        if modifications:
            if 'questionnaire_updates' in modifications:
                new_project.questionnaire_data.update(modifications['questionnaire_updates'])
            
            if 'user_preferences' in modifications:
                new_project.user_preferences.update(modifications['user_preferences'])
            
            # Regenerate architecture with modifications
            questionnaire = QuestionnaireRequest(**new_project.questionnaire_data)
            generator = ArchitectureGenerator()
            
            architecture_data = generator.generate_architecture(
                questionnaire=questionnaire,
                user_preferences=new_project.user_preferences
            )
            
            new_project.architecture_data = architecture_data
        
        self.db.add(new_project)
        self.db.commit()
        self.db.refresh(new_project)
        
        return new_project

    def get_available_configurations(self, service_type: str) -> Dict[str, Any]:
        """Get available configuration options for a service type"""
        
        configurations = {
            'rds': {
                'instance_classes': [
                    'db.t3.micro', 'db.t3.small', 'db.t3.medium', 'db.t3.large',
                    'db.t3.xlarge', 'db.t3.2xlarge', 'db.m5.large', 'db.m5.xlarge',
                    'db.m5.2xlarge', 'db.m5.4xlarge', 'db.r5.large', 'db.r5.xlarge'
                ],
                'engines': ['mysql', 'postgresql', 'mariadb', 'oracle', 'sqlserver'],
                'storage_range': {'min': 20, 'max': 16384, 'step': 1},
                'storage_types': ['gp2', 'gp3', 'io1', 'io2']
            },
            'ec2': {
                'instance_types': [
                    't3.micro', 't3.small', 't3.medium', 't3.large', 't3.xlarge',
                    'm5.large', 'm5.xlarge', 'm5.2xlarge', 'm5.4xlarge',
                    'c5.large', 'c5.xlarge', 'c5.2xlarge', 'c5.4xlarge',
                    'r5.large', 'r5.xlarge', 'r5.2xlarge', 'r5.4xlarge'
                ],
                'storage_types': ['gp2', 'gp3', 'io1', 'io2', 'st1', 'sc1'],
                'storage_range': {'min': 8, 'max': 16384, 'step': 1}
            },
            'lambda': {
                'memory_range': {'min': 128, 'max': 10240, 'step': 64},
                'timeout_range': {'min': 1, 'max': 900, 'step': 1},
                'runtimes': [
                    'python3.9', 'python3.10', 'python3.11', 'nodejs18.x', 'nodejs20.x',
                    'java11', 'java17', 'dotnet6', 'go1.x', 'ruby3.2'
                ]
            },
            's3': {
                'storage_classes': [
                    'STANDARD', 'STANDARD_IA', 'ONEZONE_IA', 'REDUCED_REDUNDANCY',
                    'GLACIER', 'DEEP_ARCHIVE', 'INTELLIGENT_TIERING'
                ],
                'encryption_options': ['AES256', 'aws:kms'],
                'versioning_options': ['Enabled', 'Suspended']
            },
            'cloudfront': {
                'price_classes': ['PriceClass_All', 'PriceClass_200', 'PriceClass_100'],
                'caching_behaviors': ['CachingOptimized', 'CachingDisabled', 'CachingOptimizedForUncompressedObjects']
            }
        }
        
        return configurations.get(service_type, {})