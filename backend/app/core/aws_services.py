from typing import Dict, Any, List
from app.schemas.questionnaire import (
    ComputePreference, DatabaseType, StorageNeeds, 
    TrafficVolume, GeographicalReach, DataSensitivity
)

class AWSServicesConfig:
    """Configuration for AWS services based on user requirements"""
    
    @staticmethod
    def get_compute_services() -> Dict[ComputePreference, Dict[str, Any]]:
        return {
            ComputePreference.SERVERLESS: {
                "service": "AWS Lambda",
                "description": "Serverless compute for event-driven applications",
                "security": ["IAM roles", "VPC endpoints", "Lambda layers"],
                "cost_factor": 0.8,
                "scaling": "automatic"
            },
            ComputePreference.CONTAINERS: {
                "service": "Amazon ECS/Fargate",
                "description": "Managed container orchestration",
                "security": ["Task roles", "VPC", "Security groups", "ECR scanning"],
                "cost_factor": 1.2,
                "scaling": "horizontal"
            },
            ComputePreference.VMS: {
                "service": "Amazon EC2",
                "description": "Virtual machines with full control",
                "security": ["Security groups", "IAM roles", "Systems Manager"],
                "cost_factor": 1.0,
                "scaling": "manual/auto"
            }
        }
    
    @staticmethod
    def get_database_services() -> Dict[DatabaseType, Dict[str, Any]]:
        return {
            DatabaseType.SQL: {
                "service": "Amazon RDS",
                "description": "Managed relational database",
                "options": ["MySQL", "PostgreSQL", "Aurora"],
                "security": ["Encryption at rest", "VPC", "Parameter groups"],
                "cost_factor": 1.5
            },
            DatabaseType.NOSQL: {
                "service": "Amazon DynamoDB",
                "description": "Managed NoSQL database",
                "options": ["On-demand", "Provisioned"],
                "security": ["Encryption", "IAM policies", "VPC endpoints"],
                "cost_factor": 1.0
            }
        }
    
    @staticmethod
    def get_storage_services() -> Dict[StorageNeeds, Dict[str, Any]]:
        return {
            StorageNeeds.MINIMAL: {
                "service": "Amazon S3",
                "tier": "Standard",
                "size_estimate": "< 100GB",
                "security": ["Bucket policies", "Encryption", "Access logging"],
                "cost_factor": 0.5
            },
            StorageNeeds.MODERATE: {
                "service": "Amazon S3",
                "tier": "Standard + Intelligent Tiering",
                "size_estimate": "100GB - 1TB",
                "security": ["Bucket policies", "Encryption", "Versioning", "MFA delete"],
                "cost_factor": 1.0
            },
            StorageNeeds.EXTENSIVE: {
                "service": "Amazon S3 + EFS",
                "tier": "Multi-tier storage",
                "size_estimate": "> 1TB",
                "security": ["Bucket policies", "Encryption", "Versioning", "Access points"],
                "cost_factor": 2.0
            }
        }
    
    @staticmethod
    def get_networking_services(traffic_volume: TrafficVolume, geographical_reach: GeographicalReach) -> List[Dict[str, Any]]:
        services = []
        
        if traffic_volume in [TrafficVolume.MEDIUM, TrafficVolume.HIGH]:
            services.append({
                "service": "Application Load Balancer",
                "description": "Distribute incoming traffic",
                "security": ["Security groups", "SSL/TLS termination"]
            })
        
        if geographical_reach in [GeographicalReach.MULTI_REGION, GeographicalReach.GLOBAL]:
            services.append({
                "service": "Amazon CloudFront",
                "description": "Global content delivery network",
                "security": ["WAF integration", "SSL/TLS", "Origin access control"]
            })
            services.append({
                "service": "Amazon Route 53",
                "description": "DNS and traffic routing",
                "security": ["Health checks", "Failover routing"]
            })
        
        return services
    
    @staticmethod
    def get_security_services(data_sensitivity: DataSensitivity, compliance_requirements: List[str]) -> List[str]:
        security_features = [
            "VPC with private subnets",
            "Security Groups",
            "IAM roles and policies",
            "CloudTrail logging",
            "S3 bucket encryption",
            "S3 public access block"
        ]
        
        if data_sensitivity == DataSensitivity.CONFIDENTIAL:
            security_features.extend([
                "Amazon GuardDuty",
                "AWS Config",
                "AWS Security Hub",
                "VPC Flow Logs"
            ])
        
        security_features.append("Amazon Macie for S3 monitoring")
        
        compliance_security = {
            "hipaa": ["AWS KMS", "CloudHSM", "Dedicated tenancy"],
            "pci": ["AWS Inspector", "Certificate Manager", "WAF"],
            "sox": ["AWS CloudFormation", "AWS Organizations"],
            "gdpr": ["Data residency controls", "Encryption in transit"]
        }
        
        for compliance in compliance_requirements:
            if compliance in compliance_security:
                security_features.extend(compliance_security[compliance])
        
        return list(set(security_features))