from typing import Dict, List, Optional, Any
import json
import logging
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import ProjectDB
from app.schemas.questionnaire import QuestionnaireRequest
from app.core.architecture_generator import ArchitectureGenerator
from app.core.ai_security_advisor import AISecurityAdvisor
from app.core.enhanced_cost_calculator import EnhancedCostCalculator

logger = logging.getLogger(__name__)

class InfrastructureImportService:
    """Service for importing existing AWS infrastructure"""
    
    def __init__(self):
        self.architecture_generator = ArchitectureGenerator()
        self.security_advisor = AISecurityAdvisor()
        self.cost_calculator = EnhancedCostCalculator()
    
    async def scan_aws_account(self, aws_credentials: Dict[str, str], region: str = "us-east-1") -> Dict[str, Any]:
        """
        Scan AWS account and discover existing infrastructure
        """
        try:
            # Mock implementation for now - in real implementation this would use boto3
            # to scan the actual AWS account
            logger.info(f"Scanning AWS account in region {region}")
            
            # Simulate scanning delay
            await asyncio.sleep(2)
            
            # Mock discovered infrastructure
            discovered_infrastructure = {
                "account_id": aws_credentials.get("account_id", "123456789012"),
                "region": region,
                "scan_timestamp": datetime.utcnow().isoformat(),
                "services": {
                    "ec2": {
                        "instances": [
                            {
                                "instance_id": "i-1234567890abcdef0",
                                "instance_type": "t3.medium",
                                "state": "running",
                                "vpc_id": "vpc-12345678",
                                "subnet_id": "subnet-12345678",
                                "security_groups": ["sg-12345678"],
                                "tags": {"Name": "WebServer", "Environment": "production"}
                            }
                        ],
                        "security_groups": [
                            {
                                "group_id": "sg-12345678",
                                "group_name": "web-server-sg",
                                "description": "Security group for web server",
                                "inbound_rules": [
                                    {"protocol": "tcp", "port": 80, "source": "0.0.0.0/0"},
                                    {"protocol": "tcp", "port": 443, "source": "0.0.0.0/0"}
                                ]
                            }
                        ]
                    },
                    "rds": {
                        "instances": [
                            {
                                "db_instance_identifier": "prod-database",
                                "db_instance_class": "db.t3.micro",
                                "engine": "mysql",
                                "engine_version": "8.0.35",
                                "allocated_storage": 20,
                                "vpc_security_groups": ["sg-87654321"]
                            }
                        ]
                    },
                    "s3": {
                        "buckets": [
                            {
                                "bucket_name": "my-app-assets-bucket",
                                "region": region,
                                "encryption": {"enabled": True, "type": "AES256"},
                                "versioning": {"enabled": True},
                                "public_access": {"blocked": True}
                            }
                        ]
                    },
                    "lambda": {
                        "functions": [
                            {
                                "function_name": "process-uploads",
                                "runtime": "python3.9",
                                "memory_size": 256,
                                "timeout": 30,
                                "environment_variables": {"BUCKET_NAME": "my-app-assets-bucket"}
                            }
                        ]
                    },
                    "vpc": {
                        "vpcs": [
                            {
                                "vpc_id": "vpc-12345678",
                                "cidr_block": "10.0.0.0/16",
                                "state": "available",
                                "subnets": [
                                    {
                                        "subnet_id": "subnet-12345678",
                                        "cidr_block": "10.0.1.0/24",
                                        "availability_zone": f"{region}a",
                                        "type": "public"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
            
            return discovered_infrastructure
            
        except Exception as e:
            logger.error(f"Error scanning AWS account: {str(e)}")
            raise Exception(f"Failed to scan AWS account: {str(e)}")
    
    async def generate_terraform_from_infrastructure(self, infrastructure: Dict[str, Any]) -> str:
        """
        Generate Terraform configuration from discovered infrastructure
        """
        try:
            # Mock Terraform generation - in real implementation this would use
            # terraformer or similar tool to generate actual Terraform
            terraform_config = f'''# Generated Terraform configuration from AWS account scan
# Scan performed on: {infrastructure.get('scan_timestamp')}
# Account ID: {infrastructure.get('account_id')}
# Region: {infrastructure.get('region')}

terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "{infrastructure.get('region', 'us-east-1')}"
}}

# VPC Configuration
'''
            
            # Add VPC resources
            if "vpc" in infrastructure.get("services", {}):
                for vpc in infrastructure["services"]["vpc"]["vpcs"]:
                    terraform_config += f'''
resource "aws_vpc" "imported_vpc_{vpc['vpc_id'].replace('-', '_')}" {{
  cidr_block = "{vpc['cidr_block']}"
  
  tags = {{
    Name = "Imported VPC"
    ImportedFrom = "{infrastructure.get('account_id')}"
  }}
}}
'''
                    # Add subnets
                    for subnet in vpc.get("subnets", []):
                        terraform_config += f'''
resource "aws_subnet" "imported_subnet_{subnet['subnet_id'].replace('-', '_')}" {{
  vpc_id            = aws_vpc.imported_vpc_{vpc['vpc_id'].replace('-', '_')}.id
  cidr_block        = "{subnet['cidr_block']}"
  availability_zone = "{subnet['availability_zone']}"
  
  tags = {{
    Name = "Imported Subnet"
    Type = "{subnet['type']}"
  }}
}}
'''
            
            # Add EC2 instances
            if "ec2" in infrastructure.get("services", {}):
                for instance in infrastructure["services"]["ec2"]["instances"]:
                    terraform_config += f'''
resource "aws_instance" "imported_instance_{instance['instance_id'].replace('-', '_')}" {{
  ami           = "ami-0c02fb55956c7d316"  # Update with actual AMI
  instance_type = "{instance['instance_type']}"
  
  tags = {{
    Name = "{instance.get('tags', {}).get('Name', 'Imported Instance')}"
    Environment = "{instance.get('tags', {}).get('Environment', 'imported')}"
    ImportedFrom = "{infrastructure.get('account_id')}"
  }}
}}
'''
            
            # Add RDS instances
            if "rds" in infrastructure.get("services", {}):
                for db_instance in infrastructure["services"]["rds"]["instances"]:
                    terraform_config += f'''
resource "aws_db_instance" "imported_db_{db_instance['db_instance_identifier'].replace('-', '_')}" {{
  identifier     = "{db_instance['db_instance_identifier']}-imported"
  instance_class = "{db_instance['db_instance_class']}"
  engine         = "{db_instance['engine']}"
  engine_version = "{db_instance['engine_version']}"
  allocated_storage = {db_instance['allocated_storage']}
  
  skip_final_snapshot = true
  
  tags = {{
    Name = "Imported Database"
    ImportedFrom = "{infrastructure.get('account_id')}"
  }}
}}
'''
            
            # Add S3 buckets
            if "s3" in infrastructure.get("services", {}):
                for bucket in infrastructure["services"]["s3"]["buckets"]:
                    bucket_name_safe = bucket['bucket_name'].replace('-', '_').replace('.', '_')
                    terraform_config += f'''
resource "aws_s3_bucket" "imported_bucket_{bucket_name_safe}" {{
  bucket = "{bucket['bucket_name']}-imported"
  
  tags = {{
    Name = "Imported Bucket"
    ImportedFrom = "{infrastructure.get('account_id')}"
  }}
}}

resource "aws_s3_bucket_versioning" "imported_bucket_versioning_{bucket_name_safe}" {{
  bucket = aws_s3_bucket.imported_bucket_{bucket_name_safe}.id
  versioning_configuration {{
    status = "Enabled"
  }}
}}
'''
            
            # Add Lambda functions
            if "lambda" in infrastructure.get("services", {}):
                for func in infrastructure["services"]["lambda"]["functions"]:
                    func_name_safe = func['function_name'].replace('-', '_')
                    terraform_config += f'''
resource "aws_lambda_function" "imported_function_{func_name_safe}" {{
  filename         = "lambda_function.zip"  # Update with actual deployment package
  function_name    = "{func['function_name']}-imported"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  runtime         = "{func['runtime']}"
  memory_size     = {func['memory_size']}
  timeout         = {func['timeout']}
  
  tags = {{
    Name = "Imported Lambda"
    ImportedFrom = "{infrastructure.get('account_id')}"
  }}
}}

resource "aws_iam_role" "lambda_role" {{
  name = "imported-lambda-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "lambda.amazonaws.com"
        }}
      }}
    ]
  }})
}}
'''
            
            return terraform_config
            
        except Exception as e:
            logger.error(f"Error generating Terraform: {str(e)}")
            raise Exception(f"Failed to generate Terraform configuration: {str(e)}")
    
    async def generate_cloudformation_from_infrastructure(self, infrastructure: Dict[str, Any]) -> str:
        """
        Generate CloudFormation template from discovered infrastructure
        """
        try:
            # Mock CloudFormation generation
            cf_template = {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Description": f"CloudFormation template generated from AWS account scan - {infrastructure.get('account_id')}",
                "Parameters": {
                    "Environment": {
                        "Type": "String",
                        "Default": "imported",
                        "Description": "Environment name for imported resources"
                    }
                },
                "Resources": {}
            }
            
            # Add VPC resources
            if "vpc" in infrastructure.get("services", {}):
                for i, vpc in enumerate(infrastructure["services"]["vpc"]["vpcs"]):
                    vpc_id = f"ImportedVPC{i+1}"
                    cf_template["Resources"][vpc_id] = {
                        "Type": "AWS::EC2::VPC",
                        "Properties": {
                            "CidrBlock": vpc['cidr_block'],
                            "Tags": [
                                {"Key": "Name", "Value": "Imported VPC"},
                                {"Key": "ImportedFrom", "Value": infrastructure.get('account_id')}
                            ]
                        }
                    }
                    
                    # Add subnets
                    for j, subnet in enumerate(vpc.get("subnets", [])):
                        subnet_id = f"ImportedSubnet{i+1}{j+1}"
                        cf_template["Resources"][subnet_id] = {
                            "Type": "AWS::EC2::Subnet",
                            "Properties": {
                                "VpcId": {"Ref": vpc_id},
                                "CidrBlock": subnet['cidr_block'],
                                "AvailabilityZone": subnet['availability_zone'],
                                "Tags": [
                                    {"Key": "Name", "Value": "Imported Subnet"},
                                    {"Key": "Type", "Value": subnet['type']}
                                ]
                            }
                        }
            
            # Add EC2 instances
            if "ec2" in infrastructure.get("services", {}):
                for i, instance in enumerate(infrastructure["services"]["ec2"]["instances"]):
                    instance_id = f"ImportedInstance{i+1}"
                    cf_template["Resources"][instance_id] = {
                        "Type": "AWS::EC2::Instance",
                        "Properties": {
                            "ImageId": "ami-0c02fb55956c7d316",  # Update with actual AMI
                            "InstanceType": instance['instance_type'],
                            "Tags": [
                                {"Key": "Name", "Value": instance.get('tags', {}).get('Name', 'Imported Instance')},
                                {"Key": "Environment", "Value": instance.get('tags', {}).get('Environment', 'imported')},
                                {"Key": "ImportedFrom", "Value": infrastructure.get('account_id')}
                            ]
                        }
                    }
            
            # Add RDS instances
            if "rds" in infrastructure.get("services", {}):
                for i, db_instance in enumerate(infrastructure["services"]["rds"]["instances"]):
                    db_id = f"ImportedDatabase{i+1}"
                    cf_template["Resources"][db_id] = {
                        "Type": "AWS::RDS::DBInstance",
                        "Properties": {
                            "DBInstanceIdentifier": f"{db_instance['db_instance_identifier']}-imported",
                            "DBInstanceClass": db_instance['db_instance_class'],
                            "Engine": db_instance['engine'],
                            "EngineVersion": db_instance['engine_version'],
                            "AllocatedStorage": str(db_instance['allocated_storage']),
                            "MasterUsername": "admin",  # This would need to be configured
                            "MasterUserPassword": "ChangeMe123!",  # This would need to be secured
                            "Tags": [
                                {"Key": "Name", "Value": "Imported Database"},
                                {"Key": "ImportedFrom", "Value": infrastructure.get('account_id')}
                            ]
                        }
                    }
            
            return json.dumps(cf_template, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating CloudFormation: {str(e)}")
            raise Exception(f"Failed to generate CloudFormation template: {str(e)}")
    
    async def analyze_imported_security(self, infrastructure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze security posture of imported infrastructure
        """
        try:
            # Convert infrastructure to questionnaire format for security analysis
            mock_questionnaire = QuestionnaireRequest(
                project_name=f"Imported Infrastructure - {infrastructure.get('account_id')}",
                description="Imported from existing AWS account",
                traffic_volume="medium",
                data_sensitivity="medium",
                compute_preference="ec2",
                database_type="mysql" if "rds" in infrastructure.get("services", {}) else "none",
                storage_needs="standard",
                geographical_reach="single-region",
                budget_range="1000-5000",
                compliance_requirements=[]
            )
            
            # Create mock services based on discovered infrastructure
            services = {}
            if "ec2" in infrastructure.get("services", {}):
                services["compute"] = "ec2"
            if "rds" in infrastructure.get("services", {}):
                services["database"] = "rds"
            if "s3" in infrastructure.get("services", {}):
                services["storage"] = "s3"
            if "lambda" in infrastructure.get("services", {}):
                services["serverless"] = "lambda"
            
            # Analyze security using existing AI Security Advisor
            security_analysis = await self.security_advisor.analyze_project_security(
                project_id=f"imported-{infrastructure.get('account_id')}",
                questionnaire=mock_questionnaire,
                services=services,
                include_ai_recommendations=True,
                security_level="medium"
            )
            
            # Add specific findings for imported infrastructure
            imported_findings = []
            
            # Check for security group issues
            if "ec2" in infrastructure.get("services", {}):
                for sg in infrastructure["services"]["ec2"].get("security_groups", []):
                    for rule in sg.get("inbound_rules", []):
                        if rule.get("source") == "0.0.0.0/0":
                            imported_findings.append({
                                "severity": "high",
                                "category": "network_security",
                                "title": f"Open Security Group Rule in {sg['group_name']}",
                                "description": f"Security group {sg['group_name']} has a rule allowing access from anywhere (0.0.0.0/0) on port {rule['port']}",
                                "recommendation": "Restrict access to specific IP ranges or security groups",
                                "resource_id": sg['group_id']
                            })
            
            # Check for unencrypted resources
            if "s3" in infrastructure.get("services", {}):
                for bucket in infrastructure["services"]["s3"]["buckets"]:
                    if not bucket.get("encryption", {}).get("enabled"):
                        imported_findings.append({
                            "severity": "medium",
                            "category": "data_protection",
                            "title": f"Unencrypted S3 Bucket: {bucket['bucket_name']}",
                            "description": f"S3 bucket {bucket['bucket_name']} does not have encryption enabled",
                            "recommendation": "Enable server-side encryption for the S3 bucket",
                            "resource_id": bucket['bucket_name']
                        })
            
            # Add imported findings to security analysis
            security_analysis["imported_findings"] = imported_findings
            security_analysis["import_timestamp"] = infrastructure.get('scan_timestamp')
            
            return security_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing imported security: {str(e)}")
            raise Exception(f"Failed to analyze imported infrastructure security: {str(e)}")
    
    async def generate_architecture_diagram(self, infrastructure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate architecture diagram from imported infrastructure
        """
        try:
            # Create diagram data structure
            diagram_data = {
                "nodes": [],
                "edges": [],
                "metadata": {
                    "source": "imported",
                    "account_id": infrastructure.get('account_id'),
                    "region": infrastructure.get('region'),
                    "scan_timestamp": infrastructure.get('scan_timestamp')
                }
            }
            
            node_id = 0
            
            # Add VPC nodes
            if "vpc" in infrastructure.get("services", {}):
                for vpc in infrastructure["services"]["vpc"]["vpcs"]:
                    vpc_node_id = node_id
                    diagram_data["nodes"].append({
                        "id": str(vpc_node_id),
                        "type": "vpc",
                        "label": f"VPC ({vpc['vpc_id']})",
                        "properties": {
                            "cidr_block": vpc['cidr_block'],
                            "vpc_id": vpc['vpc_id']
                        },
                        "position": {"x": 100, "y": 100}
                    })
                    node_id += 1
                    
                    # Add subnet nodes
                    for subnet in vpc.get("subnets", []):
                        subnet_node_id = node_id
                        diagram_data["nodes"].append({
                            "id": str(subnet_node_id),
                            "type": "subnet",
                            "label": f"Subnet ({subnet['subnet_id']})",
                            "properties": {
                                "cidr_block": subnet['cidr_block'],
                                "type": subnet['type'],
                                "availability_zone": subnet['availability_zone']
                            },
                            "position": {"x": 200, "y": 200}
                        })
                        
                        # Connect subnet to VPC
                        diagram_data["edges"].append({
                            "id": f"edge_{vpc_node_id}_{subnet_node_id}",
                            "source": str(vpc_node_id),
                            "target": str(subnet_node_id),
                            "type": "contains"
                        })
                        node_id += 1
            
            # Add EC2 instances
            if "ec2" in infrastructure.get("services", {}):
                for instance in infrastructure["services"]["ec2"]["instances"]:
                    instance_node_id = node_id
                    diagram_data["nodes"].append({
                        "id": str(instance_node_id),
                        "type": "ec2",
                        "label": f"EC2 ({instance['instance_type']})",
                        "properties": {
                            "instance_id": instance['instance_id'],
                            "instance_type": instance['instance_type'],
                            "state": instance['state'],
                            "name": instance.get('tags', {}).get('Name', 'Unnamed')
                        },
                        "position": {"x": 300, "y": 300}
                    })
                    node_id += 1
            
            # Add RDS instances
            if "rds" in infrastructure.get("services", {}):
                for db_instance in infrastructure["services"]["rds"]["instances"]:
                    db_node_id = node_id
                    diagram_data["nodes"].append({
                        "id": str(db_node_id),
                        "type": "rds",
                        "label": f"RDS ({db_instance['engine']})",
                        "properties": {
                            "identifier": db_instance['db_instance_identifier'],
                            "instance_class": db_instance['db_instance_class'],
                            "engine": db_instance['engine'],
                            "engine_version": db_instance['engine_version']
                        },
                        "position": {"x": 400, "y": 400}
                    })
                    node_id += 1
            
            # Add S3 buckets
            if "s3" in infrastructure.get("services", {}):
                for bucket in infrastructure["services"]["s3"]["buckets"]:
                    bucket_node_id = node_id
                    diagram_data["nodes"].append({
                        "id": str(bucket_node_id),
                        "type": "s3",
                        "label": f"S3 Bucket",
                        "properties": {
                            "bucket_name": bucket['bucket_name'],
                            "region": bucket['region'],
                            "encryption_enabled": bucket.get('encryption', {}).get('enabled', False),
                            "versioning_enabled": bucket.get('versioning', {}).get('enabled', False)
                        },
                        "position": {"x": 500, "y": 200}
                    })
                    node_id += 1
            
            # Add Lambda functions
            if "lambda" in infrastructure.get("services", {}):
                for func in infrastructure["services"]["lambda"]["functions"]:
                    lambda_node_id = node_id
                    diagram_data["nodes"].append({
                        "id": str(lambda_node_id),
                        "type": "lambda",
                        "label": f"Lambda ({func['function_name']})",
                        "properties": {
                            "function_name": func['function_name'],
                            "runtime": func['runtime'],
                            "memory_size": func['memory_size'],
                            "timeout": func['timeout']
                        },
                        "position": {"x": 600, "y": 300}
                    })
                    node_id += 1
            
            return diagram_data
            
        except Exception as e:
            logger.error(f"Error generating diagram: {str(e)}")
            raise Exception(f"Failed to generate architecture diagram: {str(e)}")
    
    async def create_imported_project(
        self, 
        db: Session, 
        user_id: str,
        infrastructure: Dict[str, Any],
        project_name: str,
        template_type: str = "terraform"
    ) -> str:
        """
        Create a new project from imported infrastructure
        """
        try:
            # Generate templates
            if template_type == "terraform":
                template = await self.generate_terraform_from_infrastructure(infrastructure)
            else:
                template = await self.generate_cloudformation_from_infrastructure(infrastructure)
            
            # Generate diagram
            diagram_data = await self.generate_architecture_diagram(infrastructure)
            
            # Analyze security
            security_analysis = await self.analyze_imported_security(infrastructure)
            
            # Create project in database
            project = ProjectDB(
                user_id=user_id,
                project_name=project_name,
                description=f"Imported from AWS account {infrastructure.get('account_id')}",
                questionnaire_data={
                    "project_name": project_name,
                    "description": f"Imported infrastructure scan from {infrastructure.get('account_id')}",
                    "import_source": "aws_account_scan",
                    "scan_timestamp": infrastructure.get('scan_timestamp')
                },
                generated_architecture={
                    "services": self._extract_services_from_infrastructure(infrastructure),
                    "terraform_template": template if template_type == "terraform" else "",
                    "cloudformation_template": template if template_type == "cloudformation" else "",
                    "diagram_data": diagram_data,
                    "security_analysis": security_analysis,
                    "imported_infrastructure": infrastructure
                },
                template_type=template_type
            )
            
            db.add(project)
            db.commit()
            db.refresh(project)
            
            logger.info(f"Created imported project {project.id} for user {user_id}")
            return project.id
            
        except Exception as e:
            logger.error(f"Error creating imported project: {str(e)}")
            db.rollback()
            raise Exception(f"Failed to create imported project: {str(e)}")
    
    def _extract_services_from_infrastructure(self, infrastructure: Dict[str, Any]) -> Dict[str, str]:
        """Extract services mapping from infrastructure data"""
        services = {}
        
        infra_services = infrastructure.get("services", {})
        
        if "ec2" in infra_services and infra_services["ec2"].get("instances"):
            services["compute"] = "ec2"
        
        if "rds" in infra_services and infra_services["rds"].get("instances"):
            services["database"] = "rds"
        
        if "s3" in infra_services and infra_services["s3"].get("buckets"):
            services["storage"] = "s3"
        
        if "lambda" in infra_services and infra_services["lambda"].get("functions"):
            services["serverless"] = "lambda"
        
        if "vpc" in infra_services and infra_services["vpc"].get("vpcs"):
            services["network"] = "vpc"
        
        return services