from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class DiagramNode(BaseModel):
    id: str = Field(..., description="Unique node identifier")
    type: str = Field(default="default", description="Node type for React Flow")
    data: Dict[str, Any] = Field(..., description="Node data including label")
    position: Dict[str, float] = Field(..., description="Node position coordinates")

class DiagramEdge(BaseModel):
    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    type: str = Field(default="default", description="Edge type for React Flow")

class DiagramData(BaseModel):
    nodes: List[DiagramNode] = Field(..., description="List of diagram nodes")
    edges: List[DiagramEdge] = Field(..., description="List of diagram edges")

class CostBreakdown(BaseModel):
    service: str = Field(..., description="AWS service name")
    estimated_monthly_cost: str = Field(..., description="Estimated monthly cost")
    description: str = Field(..., description="Service description")

class ArchitectureResponse(BaseModel):
    id: str = Field(..., description="Unique architecture identifier")
    project_name: str = Field(..., description="Project name")
    services: Dict[str, str] = Field(..., description="Selected AWS services by category")
    security_features: List[str] = Field(..., description="List of security features")
    estimated_cost: str = Field(..., description="Total estimated monthly cost range")
    cost_breakdown: List[CostBreakdown] = Field(..., description="Detailed cost breakdown")
    diagram_data: DiagramData = Field(..., description="Architecture diagram data")
    terraform_template: str = Field(..., description="Complete Terraform template")
    cloudformation_template: str = Field(..., description="Complete CloudFormation template")
    recommendations: List[str] = Field(default_factory=list, description="Architecture recommendations")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "arch-123e4567-e89b-12d3-a456-426614174000",
                "project_name": "E-commerce Platform",
                "services": {
                    "compute": "Amazon ECS/Fargate",
                    "database": "Amazon RDS (MySQL)",
                    "storage": "Amazon S3"
                },
                "security_features": [
                    "VPC with private subnets",
                    "Security Groups",
                    "IAM roles and policies"
                ],
                "estimated_cost": "$250-400/month",
                "cost_breakdown": [],
                "diagram_data": {"nodes": [], "edges": []},
                "terraform_template": "# Terraform configuration...",
                "cloudformation_template": "# CloudFormation template...",
                "recommendations": []
            }
        }