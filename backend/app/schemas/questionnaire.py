from pydantic import BaseModel, Field, validator
from typing import List
from enum import Enum

class TrafficVolume(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class DataSensitivity(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"

class ComputePreference(str, Enum):
    SERVERLESS = "serverless"
    CONTAINERS = "containers"
    VMS = "vms"

class DatabaseType(str, Enum):
    SQL = "sql"
    NOSQL = "nosql"
    NONE = "none"

class StorageNeeds(str, Enum):
    MINIMAL = "minimal"
    MODERATE = "moderate"
    EXTENSIVE = "extensive"

class GeographicalReach(str, Enum):
    SINGLE_REGION = "single_region"
    MULTI_REGION = "multi_region"
    GLOBAL = "global"

class BudgetRange(str, Enum):
    STARTUP = "startup"
    MEDIUM = "medium"
    ENTERPRISE = "enterprise"

class ComplianceRequirement(str, Enum):
    HIPAA = "hipaa"
    PCI = "pci"
    SOX = "sox"
    GDPR = "gdpr"
    NONE = "none"

class QuestionnaireRequest(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    traffic_volume: TrafficVolume
    data_sensitivity: DataSensitivity
    compute_preference: ComputePreference
    database_type: DatabaseType
    storage_needs: StorageNeeds
    geographical_reach: GeographicalReach
    budget_range: BudgetRange
    compliance_requirements: List[ComplianceRequirement] = Field(default_factory=list)

    @validator('project_name')
    def validate_project_name(cls, v):
        if not v.strip():
            raise ValueError('Project name cannot be empty')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()

    class Config:
        use_enum_values = True