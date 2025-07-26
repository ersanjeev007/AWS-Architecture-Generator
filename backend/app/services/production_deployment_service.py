import os
import json
import boto3
import asyncio
import subprocess
import tempfile
import shutil
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import uuid
from dataclasses import dataclass, asdict
from enum import Enum

from app.core.enhanced_security_templates import EnhancedSecurityTemplates
from app.core.template_generator import TemplateGenerator
from app.database import get_db, DeploymentDB
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class DeploymentStatus(Enum):
    PENDING = "pending"
    INITIALIZING = "initializing"
    PLANNING = "planning"
    APPLYING = "applying"
    COMPLETE = "complete"
    FAILED = "failed"
    DESTROYING = "destroying"
    DESTROYED = "destroyed"

class DeploymentTool(Enum):
    TERRAFORM = "terraform"
    CLOUDFORMATION = "cloudformation"

@dataclass
class DeploymentResult:
    deployment_id: str
    status: DeploymentStatus
    tool: DeploymentTool
    resources_created: List[Dict[str, str]]
    resources_failed: List[Dict[str, str]]
    output_variables: Dict[str, str]
    estimated_cost: float
    actual_cost: Optional[float]
    logs: List[str]
    errors: List[str]
    stack_outputs: Dict[str, Any]
    state_file_path: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

@dataclass
class SecurityPolicyStatus:
    policy_name: str
    description: str
    implemented: bool
    compliance_frameworks: List[str]
    resource_arn: Optional[str]
    last_checked: datetime
    remediation_required: bool
    remediation_steps: List[str]

class ProductionDeploymentService:
    """Production-ready deployment service for real AWS infrastructure"""
    
    def __init__(self, aws_credentials: Dict[str, str], region: str = "us-west-2"):
        self.aws_credentials = aws_credentials
        self.region = region
        self.session = None
        self.clients = {}
        
        # Initialize AWS session and clients
        self._initialize_aws_session()
        
        # Initialize template generators
        self.template_generator = TemplateGenerator()
        self.security_templates = EnhancedSecurityTemplates()
        
        # Working directories
        self.work_dir = Path(tempfile.mkdtemp(prefix="aws_deployment_"))
        self.terraform_dir = self.work_dir / "terraform"
        self.cloudformation_dir = self.work_dir / "cloudformation"
        
        # Create working directories
        self.terraform_dir.mkdir(parents=True, exist_ok=True)
        self.cloudformation_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Production deployment service initialized with working directory: {self.work_dir}")
    
    def _initialize_aws_session(self):
        """Initialize AWS session with provided credentials"""
        try:
            self.session = boto3.Session(
                aws_access_key_id=self.aws_credentials.get("access_key_id"),
                aws_secret_access_key=self.aws_credentials.get("secret_access_key"),
                aws_session_token=self.aws_credentials.get("session_token"),
                region_name=self.region
            )
            
            # Initialize commonly used clients
            self.clients = {
                "ec2": self.session.client("ec2"),
                "s3": self.session.client("s3"),
                "iam": self.session.client("iam"),
                "cloudformation": self.session.client("cloudformation"),
                "sts": self.session.client("sts"),
                "organizations": self.session.client("organizations"),
                "config": self.session.client("config"),
                "cloudtrail": self.session.client("cloudtrail"),
                "guardduty": self.session.client("guardduty"),
                "securityhub": self.session.client("securityhub"),
                "pricing": self.session.client("pricing", region_name="us-east-1")  # Pricing API only in us-east-1
            }
            
            # Validate credentials
            caller_identity = self.clients["sts"].get_caller_identity()
            logger.info(f"AWS credentials validated for account: {caller_identity.get('Account')}")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS session: {str(e)}")
            raise ValueError(f"Invalid AWS credentials: {str(e)}")
    
    async def create_architecture_from_scratch(
        self, 
        project_data: Dict[str, Any], 
        questionnaire: Dict[str, Any],
        deployment_tool: DeploymentTool = DeploymentTool.TERRAFORM,
        dry_run: bool = True
    ) -> DeploymentResult:
        """Create new architecture from scratch with full security implementation"""
        
        deployment_id = str(uuid.uuid4())
        project_name = project_data.get("project_name", "unknown")
        
        logger.info(f"Creating architecture from scratch - Deployment ID: {deployment_id}")
        
        try:
            # Generate comprehensive templates with security
            templates = await self._generate_production_templates(project_data, questionnaire)
            
            # Validate templates
            validation_result = await self._validate_templates(templates, deployment_tool)
            if not validation_result["valid"]:
                raise ValueError(f"Template validation failed: {validation_result['errors']}")
            
            # Create deployment record
            deployment_result = DeploymentResult(
                deployment_id=deployment_id,
                status=DeploymentStatus.INITIALIZING,
                tool=deployment_tool,
                resources_created=[],
                resources_failed=[],
                output_variables={},
                estimated_cost=0.0,
                actual_cost=None,
                logs=[],
                errors=[],
                stack_outputs={},
                state_file_path=None,
                created_at=datetime.now(),
                completed_at=None
            )
            
            # Save templates to working directory
            template_path = await self._save_templates(templates, deployment_tool, project_name)
            deployment_result.logs.append(f"Templates saved to: {template_path}")
            
            # Plan deployment
            deployment_result.status = DeploymentStatus.PLANNING
            plan_result = await self._plan_deployment(template_path, deployment_tool, dry_run)
            deployment_result.logs.extend(plan_result["logs"])
            deployment_result.estimated_cost = plan_result["estimated_cost"]
            
            if not dry_run:
                # Apply deployment
                deployment_result.status = DeploymentStatus.APPLYING
                apply_result = await self._apply_deployment(template_path, deployment_tool)
                
                deployment_result.resources_created = apply_result["resources_created"]
                deployment_result.resources_failed = apply_result["resources_failed"]
                deployment_result.output_variables = apply_result["outputs"]
                deployment_result.stack_outputs = apply_result["stack_outputs"]
                deployment_result.state_file_path = apply_result.get("state_file_path")
                deployment_result.logs.extend(apply_result["logs"])
                deployment_result.errors.extend(apply_result["errors"])
                
                if apply_result["success"]:
                    deployment_result.status = DeploymentStatus.COMPLETE
                    
                    # Validate security policies post-deployment
                    security_validation = await self._validate_deployed_security(deployment_result)
                    deployment_result.logs.extend(security_validation["logs"])
                    
                else:
                    deployment_result.status = DeploymentStatus.FAILED
                    deployment_result.errors.extend(apply_result["errors"])
            else:
                deployment_result.status = DeploymentStatus.COMPLETE
                deployment_result.logs.append("Dry run completed successfully")
            
            deployment_result.completed_at = datetime.now()
            
            # Save deployment to database
            await self._save_deployment_record(deployment_result, project_data)
            
            return deployment_result
            
        except Exception as e:
            logger.error(f"Architecture creation failed: {str(e)}")
            deployment_result.status = DeploymentStatus.FAILED
            deployment_result.errors.append(str(e))
            deployment_result.completed_at = datetime.now()
            
            await self._save_deployment_record(deployment_result, project_data)
            raise
    
    async def _generate_production_templates(
        self, 
        project_data: Dict[str, Any], 
        questionnaire: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate production-ready templates with comprehensive security"""
        
        project_name = project_data.get("project_name", "aws-project")
        services = questionnaire.get("services", {})
        compliance_requirements = questionnaire.get("compliance_requirements", [])
        security_level = questionnaire.get("security_level", "medium")
        
        # Generate base architecture
        base_architecture = self.template_generator.generate_terraform_template(
            project_name=project_name,
            services=services,
            questionnaire=questionnaire
        )
        
        # Generate enhanced security configurations
        enhanced_security = self.security_templates.generate_enhanced_security(
            project_name=project_name,
            services=services,
            security_level=security_level,
            compliance_requirements=compliance_requirements
        )
        
        # Generate IAM policies with least privilege
        iam_policies = self.security_templates.generate_enhanced_iam_policies(
            project_name=project_name,
            services=services,
            security_level=security_level
        )
        
        # Generate network security
        network_security = self.security_templates.generate_enhanced_network_security(
            project_name=project_name,
            services=services,
            security_level=security_level
        )
        
        # Generate monitoring and logging
        monitoring = self.security_templates.generate_enhanced_monitoring(
            project_name=project_name,
            services=services,
            compliance_requirements=compliance_requirements
        )
        
        # Generate encryption configuration
        encryption = self.security_templates.generate_enhanced_encryption(
            project_name=project_name,
            security_level=security_level,
            compliance_requirements=compliance_requirements
        )
        
        # Combine all templates
        combined_terraform = f"""
# AWS Architecture Generator - Production Deployment
# Project: {project_name}
# Generated: {datetime.now().isoformat()}
# Security Level: {security_level}
# Compliance: {', '.join(compliance_requirements)}

terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
  
  backend "s3" {{
    bucket = "{project_name}-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "{self.region}"
    encrypt = true
    dynamodb_table = "{project_name}-terraform-locks"
  }}
}}

provider "aws" {{
  region = "{self.region}"
  
  default_tags {{
    tags = {{
      Project     = "{project_name}"
      Environment = var.environment
      ManagedBy   = "AWS-Architecture-Generator"
      CreatedAt   = "{datetime.now().isoformat()}"
    }}
  }}
}}

# Variables
variable "environment" {{
  description = "Environment name"
  type        = string
  default     = "production"
}}

variable "domain_name" {{
  description = "Domain name for the application"
  type        = string
  default     = "{project_name}.com"
}}

variable "security_features" {{
  description = "List of security features to enable"
  type        = list(string)
  default     = {json.dumps(compliance_requirements)}
}}

{base_architecture}

{enhanced_security}

{iam_policies}

{network_security}

{monitoring}

{encryption}

# Outputs
output "deployment_info" {{
  description = "Deployment information"
  value = {{
    project_name = "{project_name}"
    region      = "{self.region}"
    environment = var.environment
    created_at  = "{datetime.now().isoformat()}"
  }}
}}

output "security_endpoints" {{
  description = "Security service endpoints"
  value = {{
    cloudtrail_arn = aws_cloudtrail.main.arn
    config_arn     = aws_config_configuration_recorder.main.name
    guardduty_detector = aws_guardduty_detector.main[0].id
  }}
  sensitive = false
}}

output "application_endpoints" {{
  description = "Application endpoints"
  value = {{
    load_balancer_dns = aws_lb.main.dns_name
    cloudfront_domain = aws_cloudfront_distribution.main.domain_name
  }}
}}
"""
        
        # Generate CloudFormation template as alternative
        cloudformation_template = self.template_generator.generate_cloudformation_template(
            project_name=project_name,
            services=services,
            questionnaire=questionnaire
        )
        
        return {
            "terraform": combined_terraform,
            "cloudformation": cloudformation_template,
            "terraform_vars": self._generate_terraform_vars(project_name, questionnaire),
            "terraform_backend": self._generate_terraform_backend_config(project_name)
        }
    
    def _generate_terraform_vars(self, project_name: str, questionnaire: Dict[str, Any]) -> str:
        """Generate terraform.tfvars file"""
        
        return f"""
# Terraform Variables for {project_name}
# Generated: {datetime.now().isoformat()}

environment = "production"
domain_name = "{project_name}.com"

# Security Configuration
security_features = {json.dumps(questionnaire.get("compliance_requirements", []))}

# Network Configuration
vpc_cidr = "10.0.0.0/16"
availability_zones = ["{self.region}a", "{self.region}b", "{self.region}c"]

# Instance Configuration
ec2_instance_type = "{questionnaire.get('preferences', {}).get('ec2_instance_type', 't3.medium')}"
rds_instance_class = "{questionnaire.get('preferences', {}).get('rds_instance_class', 'db.t3.micro')}"
rds_storage_gb = {questionnaire.get('preferences', {}).get('rds_storage_gb', 20)}

# Lambda Configuration
lambda_memory_mb = {questionnaire.get('preferences', {}).get('lambda_memory_mb', 512)}

# S3 Configuration
s3_storage_class = "{questionnaire.get('preferences', {}).get('s3_storage_class', 'STANDARD')}"

# CloudFront Configuration
cloudfront_price_class = "{questionnaire.get('preferences', {}).get('cloudfront_price_class', 'PriceClass_All')}"
"""
    
    def _generate_terraform_backend_config(self, project_name: str) -> str:
        """Generate backend configuration for Terraform state"""
        
        return f"""
# Terraform Backend Configuration
# This file configures remote state storage in S3

terraform {{
  backend "s3" {{
    bucket         = "{project_name}-terraform-state-{self.region}"
    key            = "infrastructure/terraform.tfstate"
    region         = "{self.region}"
    encrypt        = true
    dynamodb_table = "{project_name}-terraform-locks"
    
    # Enable versioning and lifecycle
    versioning = true
    
    # Server-side encryption
    server_side_encryption_configuration {{
      rule {{
        apply_server_side_encryption_by_default {{
          sse_algorithm = "AES256"
        }}
      }}
    }}
  }}
}}
"""
    
    async def _validate_templates(
        self, 
        templates: Dict[str, str], 
        deployment_tool: DeploymentTool
    ) -> Dict[str, Any]:
        """Validate generated templates for correctness"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "resource_count": 0,
            "estimated_cost": 0.0
        }
        
        try:
            if deployment_tool == DeploymentTool.TERRAFORM:
                # Save terraform template temporarily
                temp_tf_file = self.terraform_dir / "main.tf"
                temp_tf_file.write_text(templates["terraform"])
                
                # Run terraform validate
                result = subprocess.run(
                    ["terraform", "init", "-backend=false"],
                    cwd=self.terraform_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Terraform init failed: {result.stderr}")
                    return validation_result
                
                result = subprocess.run(
                    ["terraform", "validate"],
                    cwd=self.terraform_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Terraform validation failed: {result.stderr}")
                else:
                    validation_result["warnings"].append("Terraform template validation passed")
                
                # Count resources
                terraform_content = templates["terraform"]
                resource_count = terraform_content.count('resource "')
                validation_result["resource_count"] = resource_count
                
            elif deployment_tool == DeploymentTool.CLOUDFORMATION:
                # Validate CloudFormation template
                try:
                    cf_template = json.loads(templates["cloudformation"])
                    
                    # Use AWS CloudFormation validate-template API
                    response = self.clients["cloudformation"].validate_template(
                        TemplateBody=templates["cloudformation"]
                    )
                    
                    validation_result["resource_count"] = len(cf_template.get("Resources", {}))
                    validation_result["warnings"].append("CloudFormation template validation passed")
                    
                except json.JSONDecodeError as e:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Invalid JSON in CloudFormation template: {str(e)}")
                except Exception as e:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"CloudFormation validation failed: {str(e)}")
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Template validation error: {str(e)}")
        
        return validation_result
    
    async def _save_templates(
        self, 
        templates: Dict[str, str], 
        deployment_tool: DeploymentTool, 
        project_name: str
    ) -> str:
        """Save templates to working directory"""
        
        try:
            if deployment_tool == DeploymentTool.TERRAFORM:
                # Save main terraform file
                main_tf = self.terraform_dir / "main.tf"
                main_tf.write_text(templates["terraform"])
                
                # Save variables file
                vars_tf = self.terraform_dir / "terraform.tfvars"
                vars_tf.write_text(templates["terraform_vars"])
                
                # Save backend config
                backend_tf = self.terraform_dir / "backend.tf"
                backend_tf.write_text(templates["terraform_backend"])
                
                # Create terraform init script
                init_script = self.terraform_dir / "init.sh"
                init_script.write_text(f"""#!/bin/bash
# Terraform initialization script for {project_name}

set -e

echo "Initializing Terraform for {project_name}..."

# Initialize Terraform
terraform init

echo "Terraform initialization complete!"
""")
                init_script.chmod(0o755)
                
                return str(self.terraform_dir)
                
            elif deployment_tool == DeploymentTool.CLOUDFORMATION:
                # Save CloudFormation template
                cf_template = self.cloudformation_dir / f"{project_name}-template.json"
                cf_template.write_text(templates["cloudformation"])
                
                # Create parameters file
                params_file = self.cloudformation_dir / f"{project_name}-parameters.json"
                params_file.write_text(json.dumps([
                    {
                        "ParameterKey": "Environment",
                        "ParameterValue": "production"
                    },
                    {
                        "ParameterKey": "ProjectName",
                        "ParameterValue": project_name
                    }
                ], indent=2))
                
                return str(self.cloudformation_dir)
                
        except Exception as e:
            logger.error(f"Failed to save templates: {str(e)}")
            raise
    
    async def _plan_deployment(
        self, 
        template_path: str, 
        deployment_tool: DeploymentTool, 
        dry_run: bool
    ) -> Dict[str, Any]:
        """Plan deployment and estimate resources/costs"""
        
        plan_result = {
            "success": True,
            "logs": [],
            "errors": [],
            "estimated_cost": 0.0,
            "resources_to_create": [],
            "resources_to_modify": [],
            "resources_to_destroy": []
        }
        
        try:
            if deployment_tool == DeploymentTool.TERRAFORM:
                # Create state backend infrastructure first
                await self._create_terraform_backend()
                
                # Run terraform plan
                result = subprocess.run(
                    ["terraform", "plan", "-out=tfplan", "-detailed-exitcode"],
                    cwd=template_path,
                    capture_output=True,
                    text=True,
                    env={**os.environ, 
                         "AWS_ACCESS_KEY_ID": self.aws_credentials["access_key_id"],
                         "AWS_SECRET_ACCESS_KEY": self.aws_credentials["secret_access_key"],
                         "AWS_DEFAULT_REGION": self.region}
                )
                
                plan_result["logs"].append(f"Terraform plan output: {result.stdout}")
                
                if result.returncode == 0:
                    plan_result["logs"].append("No changes required")
                elif result.returncode == 2:
                    plan_result["logs"].append("Changes planned successfully")
                    
                    # Parse plan output for resource changes
                    plan_output = result.stdout
                    if "Plan:" in plan_output:
                        # Extract resource counts from plan
                        lines = plan_output.split('\n')
                        for line in lines:
                            if "to add" in line:
                                plan_result["resources_to_create"].append(line.strip())
                            elif "to change" in line:
                                plan_result["resources_to_modify"].append(line.strip())
                            elif "to destroy" in line:
                                plan_result["resources_to_destroy"].append(line.strip())
                else:
                    plan_result["success"] = False
                    plan_result["errors"].append(f"Terraform plan failed: {result.stderr}")
                
            elif deployment_tool == DeploymentTool.CLOUDFORMATION:
                # Use CloudFormation change set for planning
                stack_name = f"{Path(template_path).parent.name}-stack"
                
                try:
                    with open(Path(template_path) / f"{stack_name}-template.json", 'r') as f:
                        template_body = f.read()
                    
                    # Create change set
                    response = self.clients["cloudformation"].create_change_set(
                        StackName=stack_name,
                        TemplateBody=template_body,
                        ChangeSetName=f"{stack_name}-changeset-{int(datetime.now().timestamp())}",
                        Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
                    )
                    
                    plan_result["logs"].append(f"CloudFormation change set created: {response['Id']}")
                    
                except Exception as e:
                    plan_result["success"] = False
                    plan_result["errors"].append(f"CloudFormation planning failed: {str(e)}")
            
            # Estimate costs (basic implementation)
            if plan_result["success"]:
                estimated_cost = await self._estimate_deployment_cost(
                    len(plan_result["resources_to_create"]) + len(plan_result["resources_to_modify"])
                )
                plan_result["estimated_cost"] = estimated_cost
                
        except Exception as e:
            plan_result["success"] = False
            plan_result["errors"].append(f"Planning error: {str(e)}")
        
        return plan_result
    
    async def _create_terraform_backend(self):
        """Create S3 bucket and DynamoDB table for Terraform state"""
        
        project_name = "aws-arch-gen"  # Use a default project name for backend
        bucket_name = f"{project_name}-terraform-state-{self.region}"
        table_name = f"{project_name}-terraform-locks"
        
        try:
            # Create S3 bucket for state
            try:
                if self.region == "us-east-1":
                    self.clients["s3"].create_bucket(Bucket=bucket_name)
                else:
                    self.clients["s3"].create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )
                
                # Enable versioning
                self.clients["s3"].put_bucket_versioning(
                    Bucket=bucket_name,
                    VersioningConfiguration={'Status': 'Enabled'}
                )
                
                # Enable encryption
                self.clients["s3"].put_bucket_encryption(
                    Bucket=bucket_name,
                    ServerSideEncryptionConfiguration={
                        'Rules': [{
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }]
                    }
                )
                
                logger.info(f"Created Terraform state bucket: {bucket_name}")
                
            except self.clients["s3"].exceptions.BucketAlreadyOwnedByYou:
                logger.info(f"Terraform state bucket already exists: {bucket_name}")
            except Exception as e:
                logger.warning(f"Failed to create state bucket: {str(e)}")
            
            # Create DynamoDB table for locks
            try:
                dynamodb = self.session.client("dynamodb")
                dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {'AttributeName': 'LockID', 'KeyType': 'HASH'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'LockID', 'AttributeType': 'S'}
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                
                # Wait for table to be active
                waiter = dynamodb.get_waiter('table_exists')
                waiter.wait(TableName=table_name)
                
                logger.info(f"Created Terraform locks table: {table_name}")
                
            except dynamodb.exceptions.ResourceInUseException:
                logger.info(f"Terraform locks table already exists: {table_name}")
            except Exception as e:
                logger.warning(f"Failed to create locks table: {str(e)}")
                
        except Exception as e:
            logger.error(f"Failed to create Terraform backend: {str(e)}")
            # Continue anyway - Terraform can work with local state
    
    async def _apply_deployment(
        self, 
        template_path: str, 
        deployment_tool: DeploymentTool
    ) -> Dict[str, Any]:
        """Apply the deployment to AWS"""
        
        apply_result = {
            "success": True,
            "logs": [],
            "errors": [],
            "resources_created": [],
            "resources_failed": [],
            "outputs": {},
            "stack_outputs": {},
            "state_file_path": None
        }
        
        try:
            if deployment_tool == DeploymentTool.TERRAFORM:
                # Apply terraform plan
                result = subprocess.run(
                    ["terraform", "apply", "-auto-approve", "tfplan"],
                    cwd=template_path,
                    capture_output=True,
                    text=True,
                    env={**os.environ,
                         "AWS_ACCESS_KEY_ID": self.aws_credentials["access_key_id"],
                         "AWS_SECRET_ACCESS_KEY": self.aws_credentials["secret_access_key"],
                         "AWS_DEFAULT_REGION": self.region}
                )
                
                apply_result["logs"].append(f"Terraform apply output: {result.stdout}")
                
                if result.returncode == 0:
                    apply_result["logs"].append("Terraform apply completed successfully")
                    
                    # Get outputs
                    output_result = subprocess.run(
                        ["terraform", "output", "-json"],
                        cwd=template_path,
                        capture_output=True,
                        text=True
                    )
                    
                    if output_result.returncode == 0:
                        try:
                            outputs = json.loads(output_result.stdout)
                            apply_result["outputs"] = {k: v.get("value") for k, v in outputs.items()}
                        except json.JSONDecodeError:
                            apply_result["logs"].append("Failed to parse Terraform outputs")
                    
                    # Set state file path
                    apply_result["state_file_path"] = str(Path(template_path) / "terraform.tfstate")
                    
                    # Parse created resources
                    apply_output = result.stdout
                    for line in apply_output.split('\n'):
                        if ": Creating..." in line or ": Creation complete" in line:
                            apply_result["resources_created"].append({
                                "type": "terraform_resource",
                                "status": "created",
                                "details": line.strip()
                            })
                else:
                    apply_result["success"] = False
                    apply_result["errors"].append(f"Terraform apply failed: {result.stderr}")
                    
                    # Parse failed resources
                    error_output = result.stderr
                    for line in error_output.split('\n'):
                        if "Error:" in line:
                            apply_result["resources_failed"].append({
                                "type": "terraform_resource",
                                "status": "failed",
                                "error": line.strip()
                            })
                
            elif deployment_tool == DeploymentTool.CLOUDFORMATION:
                # Deploy CloudFormation stack
                stack_name = f"{Path(template_path).parent.name}-stack"
                
                try:
                    with open(Path(template_path) / f"{stack_name}-template.json", 'r') as f:
                        template_body = f.read()
                    
                    # Create or update stack
                    try:
                        response = self.clients["cloudformation"].create_stack(
                            StackName=stack_name,
                            TemplateBody=template_body,
                            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
                            OnFailure='ROLLBACK'
                        )
                        
                        apply_result["logs"].append(f"CloudFormation stack creation started: {response['StackId']}")
                        
                    except self.clients["cloudformation"].exceptions.AlreadyExistsException:
                        # Stack exists, update it
                        response = self.clients["cloudformation"].update_stack(
                            StackName=stack_name,
                            TemplateBody=template_body,
                            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
                        )
                        
                        apply_result["logs"].append(f"CloudFormation stack update started: {response['StackId']}")
                    
                    # Wait for stack completion
                    waiter = self.clients["cloudformation"].get_waiter('stack_create_complete')
                    waiter.wait(StackName=stack_name)
                    
                    # Get stack outputs
                    stack_info = self.clients["cloudformation"].describe_stacks(StackName=stack_name)
                    stack = stack_info["Stacks"][0]
                    
                    if "Outputs" in stack:
                        for output in stack["Outputs"]:
                            apply_result["stack_outputs"][output["OutputKey"]] = output["OutputValue"]
                    
                    apply_result["logs"].append("CloudFormation deployment completed successfully")
                    
                except Exception as e:
                    apply_result["success"] = False
                    apply_result["errors"].append(f"CloudFormation deployment failed: {str(e)}")
            
        except Exception as e:
            apply_result["success"] = False
            apply_result["errors"].append(f"Deployment error: {str(e)}")
        
        return apply_result
    
    async def _estimate_deployment_cost(self, resource_count: int) -> float:
        """Estimate deployment cost based on resources"""
        
        # Basic cost estimation - in production, this would use the AWS Pricing API
        base_cost_per_resource = 10.0  # $10 per resource per month (rough estimate)
        estimated_cost = resource_count * base_cost_per_resource
        
        logger.info(f"Estimated monthly cost for {resource_count} resources: ${estimated_cost}")
        
        return estimated_cost
    
    async def _validate_deployed_security(self, deployment_result: DeploymentResult) -> Dict[str, Any]:
        """Validate that security policies are properly implemented post-deployment"""
        
        validation_result = {
            "logs": [],
            "security_policies": [],
            "compliance_status": {},
            "gaps_identified": []
        }
        
        try:
            # Check CloudTrail
            trails = self.clients["cloudtrail"].describe_trails()
            active_trails = [t for t in trails["trailList"] if t.get("IsLogging", False)]
            
            if active_trails:
                validation_result["logs"].append(f"CloudTrail validation passed: {len(active_trails)} active trails")
                validation_result["security_policies"].append({
                    "policy": "CloudTrail Logging",
                    "status": "implemented",
                    "resources": [t["Name"] for t in active_trails]
                })
            else:
                validation_result["gaps_identified"].append("CloudTrail logging is not enabled")
            
            # Check GuardDuty
            try:
                detectors = self.clients["guardduty"].list_detectors()
                if detectors["DetectorIds"]:
                    validation_result["logs"].append("GuardDuty validation passed")
                    validation_result["security_policies"].append({
                        "policy": "GuardDuty Threat Detection",
                        "status": "implemented",
                        "resources": detectors["DetectorIds"]
                    })
                else:
                    validation_result["gaps_identified"].append("GuardDuty is not enabled")
            except Exception:
                validation_result["gaps_identified"].append("GuardDuty service not available")
            
            # Check Config
            try:
                recorders = self.clients["config"].describe_configuration_recorders()
                if recorders["ConfigurationRecorders"]:
                    validation_result["logs"].append("AWS Config validation passed")
                    validation_result["security_policies"].append({
                        "policy": "AWS Config Compliance",
                        "status": "implemented",
                        "resources": [r["name"] for r in recorders["ConfigurationRecorders"]]
                    })
                else:
                    validation_result["gaps_identified"].append("AWS Config is not enabled")
            except Exception:
                validation_result["gaps_identified"].append("AWS Config service not available")
            
            # Check VPC Security Groups
            try:
                security_groups = self.clients["ec2"].describe_security_groups()
                open_groups = []
                
                for sg in security_groups["SecurityGroups"]:
                    for rule in sg.get("IpPermissions", []):
                        for ip_range in rule.get("IpRanges", []):
                            if ip_range.get("CidrIp") == "0.0.0.0/0":
                                open_groups.append(sg["GroupId"])
                                break
                
                if open_groups:
                    validation_result["gaps_identified"].append(
                        f"Security groups with open access found: {', '.join(open_groups)}"
                    )
                else:
                    validation_result["logs"].append("Security group validation passed")
                    validation_result["security_policies"].append({
                        "policy": "Network Security Groups",
                        "status": "implemented",
                        "resources": [sg["GroupId"] for sg in security_groups["SecurityGroups"]]
                    })
            except Exception as e:
                validation_result["gaps_identified"].append(f"Security group validation failed: {str(e)}")
            
        except Exception as e:
            validation_result["logs"].append(f"Security validation error: {str(e)}")
        
        return validation_result
    
    async def _save_deployment_record(self, deployment_result: DeploymentResult, project_data: Dict[str, Any]):
        """Save deployment record to database"""
        
        try:
            db = next(get_db())
            
            deployment_record = DeploymentDB(
                id=deployment_result.deployment_id,
                project_id=project_data.get("id", "unknown"),
                aws_account_id=self.aws_credentials.get("account_id", "unknown"),
                template_type=deployment_result.tool.value,
                status=deployment_result.status.value,
                dry_run=deployment_result.status == DeploymentStatus.COMPLETE and not deployment_result.resources_created,
                output=json.dumps({
                    "logs": deployment_result.logs,
                    "outputs": deployment_result.output_variables,
                    "resources_created": deployment_result.resources_created
                }),
                error=json.dumps(deployment_result.errors) if deployment_result.errors else None,
                stack_name=f"{project_data.get('project_name', 'unknown')}-stack",
                terraform_state_path=deployment_result.state_file_path
            )
            
            db.add(deployment_record)
            db.commit()
            
            logger.info(f"Deployment record saved: {deployment_result.deployment_id}")
            
        except Exception as e:
            logger.error(f"Failed to save deployment record: {str(e)}")
    
    async def destroy_deployment(self, deployment_id: str) -> DeploymentResult:
        """Destroy a deployed infrastructure"""
        
        logger.info(f"Destroying deployment: {deployment_id}")
        
        try:
            # Get deployment record
            db = next(get_db())
            deployment_record = db.query(DeploymentDB).filter(DeploymentDB.id == deployment_id).first()
            
            if not deployment_record:
                raise ValueError(f"Deployment {deployment_id} not found")
            
            if deployment_record.template_type == "terraform":
                return await self._destroy_terraform_deployment(deployment_record)
            elif deployment_record.template_type == "cloudformation":
                return await self._destroy_cloudformation_deployment(deployment_record)
            else:
                raise ValueError(f"Unknown deployment type: {deployment_record.template_type}")
                
        except Exception as e:
            logger.error(f"Failed to destroy deployment: {str(e)}")
            raise
    
    async def _destroy_terraform_deployment(self, deployment_record: DeploymentDB) -> DeploymentResult:
        """Destroy Terraform deployment"""
        
        destroy_result = DeploymentResult(
            deployment_id=deployment_record.id,
            status=DeploymentStatus.DESTROYING,
            tool=DeploymentTool.TERRAFORM,
            resources_created=[],
            resources_failed=[],
            output_variables={},
            estimated_cost=0.0,
            actual_cost=None,
            logs=[],
            errors=[],
            stack_outputs={},
            state_file_path=deployment_record.terraform_state_path,
            created_at=datetime.now(),
            completed_at=None
        )
        
        try:
            # Run terraform destroy
            if deployment_record.terraform_state_path and Path(deployment_record.terraform_state_path).exists():
                state_dir = Path(deployment_record.terraform_state_path).parent
                
                result = subprocess.run(
                    ["terraform", "destroy", "-auto-approve"],
                    cwd=state_dir,
                    capture_output=True,
                    text=True,
                    env={**os.environ,
                         "AWS_ACCESS_KEY_ID": self.aws_credentials["access_key_id"],
                         "AWS_SECRET_ACCESS_KEY": self.aws_credentials["secret_access_key"],
                         "AWS_DEFAULT_REGION": self.region}
                )
                
                destroy_result.logs.append(f"Terraform destroy output: {result.stdout}")
                
                if result.returncode == 0:
                    destroy_result.status = DeploymentStatus.DESTROYED
                    destroy_result.logs.append("Terraform destroy completed successfully")
                else:
                    destroy_result.status = DeploymentStatus.FAILED
                    destroy_result.errors.append(f"Terraform destroy failed: {result.stderr}")
            else:
                destroy_result.errors.append("Terraform state file not found")
                destroy_result.status = DeploymentStatus.FAILED
                
        except Exception as e:
            destroy_result.status = DeploymentStatus.FAILED
            destroy_result.errors.append(f"Destroy error: {str(e)}")
        
        destroy_result.completed_at = datetime.now()
        return destroy_result
    
    async def _destroy_cloudformation_deployment(self, deployment_record: DeploymentDB) -> DeploymentResult:
        """Destroy CloudFormation deployment"""
        
        destroy_result = DeploymentResult(
            deployment_id=deployment_record.id,
            status=DeploymentStatus.DESTROYING,
            tool=DeploymentTool.CLOUDFORMATION,
            resources_created=[],
            resources_failed=[],
            output_variables={},
            estimated_cost=0.0,
            actual_cost=None,
            logs=[],
            errors=[],
            stack_outputs={},
            state_file_path=None,
            created_at=datetime.now(),
            completed_at=None
        )
        
        try:
            stack_name = deployment_record.stack_name
            
            # Delete CloudFormation stack
            self.clients["cloudformation"].delete_stack(StackName=stack_name)
            
            # Wait for deletion to complete
            waiter = self.clients["cloudformation"].get_waiter('stack_delete_complete')
            waiter.wait(StackName=stack_name)
            
            destroy_result.status = DeploymentStatus.DESTROYED
            destroy_result.logs.append(f"CloudFormation stack {stack_name} deleted successfully")
            
        except Exception as e:
            destroy_result.status = DeploymentStatus.FAILED
            destroy_result.errors.append(f"CloudFormation destroy error: {str(e)}")
        
        destroy_result.completed_at = datetime.now()
        return destroy_result
    
    def __del__(self):
        """Clean up working directory"""
        try:
            if hasattr(self, 'work_dir') and self.work_dir.exists():
                shutil.rmtree(self.work_dir)
                logger.info(f"Cleaned up working directory: {self.work_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean up working directory: {str(e)}")