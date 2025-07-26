import os
import json
import boto3
import asyncio
import subprocess
import tempfile
import shutil
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import uuid
from dataclasses import dataclass, asdict
from enum import Enum

from app.core.dynamic_security_analyzer import DynamicSecurityAnalyzer, SecurityThreat, ComplianceResult
from app.services.production_deployment_service import SecurityPolicyStatus

logger = logging.getLogger(__name__)

class ImportStatus(Enum):
    PENDING = "pending"
    SCANNING = "scanning"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    COMPLETE = "complete"
    FAILED = "failed"

@dataclass
class ImportedResource:
    resource_type: str
    resource_name: str
    resource_id: str
    region: str
    tags: Dict[str, str]
    security_compliant: bool
    security_issues: List[str]
    terraform_code: str
    estimated_monthly_cost: float
    
@dataclass
class SecurityGap:
    gap_id: str
    resource_id: str
    resource_type: str
    gap_type: str  # missing_encryption, open_security_group, etc.
    severity: str  # critical, high, medium, low
    description: str
    current_configuration: Dict[str, Any]
    recommended_configuration: Dict[str, Any]
    remediation_terraform: str
    compliance_frameworks_affected: List[str]
    estimated_fix_time: str

@dataclass
class InfrastructureImportResult:
    import_id: str
    status: ImportStatus
    aws_account_id: str
    region: str
    imported_resources: List[ImportedResource]
    security_gaps: List[SecurityGap]
    compliance_status: Dict[str, Any]
    terraform_code: str
    diagram_data: Dict[str, Any]
    total_estimated_cost: float
    security_score: float
    recommendations: List[str]
    created_at: datetime
    completed_at: Optional[datetime]

class TerraformerService:
    """Production-ready service for importing existing AWS infrastructure using Terraformer"""
    
    def __init__(self, aws_credentials: Dict[str, str], region: str = "us-west-2"):
        self.aws_credentials = aws_credentials
        self.region = region
        self.session = None
        self.clients = {}
        
        # Initialize AWS session
        self._initialize_aws_session()
        
        # Initialize security analyzer
        self.security_analyzer = DynamicSecurityAnalyzer(aws_credentials)
        
        # Working directory for Terraformer
        self.work_dir = Path(tempfile.mkdtemp(prefix="terraformer_import_"))
        self.terraformer_dir = self.work_dir / "terraformer_output"
        self.terraformer_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported AWS services for import
        self.supported_services = [
            "vpc", "subnet", "internet_gateway", "nat_gateway", "route_table",
            "security_group", "network_acl", "vpc_endpoint",
            "ec2_instance", "launch_template", "autoscaling_group", "load_balancer",
            "rds", "elasticache", "s3", "cloudfront",
            "lambda", "api_gateway", "ecs", "eks",
            "iam", "kms", "acm", "route53",
            "cloudtrail", "cloudwatch", "config", "guardduty"
        ]
        
        logger.info(f"Terraformer service initialized with working directory: {self.work_dir}")
    
    def _initialize_aws_session(self):
        """Initialize AWS session with provided credentials"""
        try:
            self.session = boto3.Session(
                aws_access_key_id=self.aws_credentials.get("access_key_id"),
                aws_secret_access_key=self.aws_credentials.get("secret_access_key"),
                aws_session_token=self.aws_credentials.get("session_token"),
                region_name=self.region
            )
            
            # Initialize clients
            self.clients = {
                "ec2": self.session.client("ec2"),
                "s3": self.session.client("s3"),
                "rds": self.session.client("rds"),
                "lambda": self.session.client("lambda"),
                "iam": self.session.client("iam"),
                "sts": self.session.client("sts"),
                "pricing": self.session.client("pricing", region_name="us-east-1"),
                "cloudformation": self.session.client("cloudformation"),
                "resource_groups": self.session.client("resource-groups-tagging-api")
            }
            
            # Validate credentials
            caller_identity = self.clients["sts"].get_caller_identity()
            self.aws_account_id = caller_identity.get("Account")
            logger.info(f"AWS credentials validated for account: {self.aws_account_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS session: {str(e)}")
            raise ValueError(f"Invalid AWS credentials: {str(e)}")
    
    async def import_existing_infrastructure(
        self, 
        project_name: str,
        services_to_import: Optional[List[str]] = None,
        resource_filters: Optional[Dict[str, Any]] = None
    ) -> InfrastructureImportResult:
        """Import existing AWS infrastructure and analyze security posture"""
        
        import_id = str(uuid.uuid4())
        
        logger.info(f"Starting infrastructure import - Import ID: {import_id}")
        
        import_result = InfrastructureImportResult(
            import_id=import_id,
            status=ImportStatus.PENDING,
            aws_account_id=self.aws_account_id,
            region=self.region,
            imported_resources=[],
            security_gaps=[],
            compliance_status={},
            terraform_code="",
            diagram_data={},
            total_estimated_cost=0.0,
            security_score=0.0,
            recommendations=[],
            created_at=datetime.now(),
            completed_at=None
        )
        
        try:
            # Step 1: Scan existing infrastructure
            import_result.status = ImportStatus.SCANNING
            discovered_resources = await self._discover_aws_resources(services_to_import, resource_filters)
            
            if not discovered_resources:
                import_result.status = ImportStatus.FAILED
                import_result.recommendations.append("No resources found to import. Check your AWS account and permissions.")
                return import_result
            
            # Step 2: Generate Terraform code using Terraformer
            import_result.status = ImportStatus.GENERATING
            terraform_result = await self._run_terraformer_import(discovered_resources, project_name)
            import_result.terraform_code = terraform_result["terraform_code"]
            
            # Step 3: Analyze security posture
            import_result.status = ImportStatus.ANALYZING
            security_analysis = await self._analyze_imported_security(discovered_resources)
            
            # Step 4: Process imported resources
            processed_resources = await self._process_imported_resources(
                discovered_resources, 
                terraform_result["resource_mapping"]
            )
            import_result.imported_resources = processed_resources
            
            # Step 5: Identify security gaps
            security_gaps = await self._identify_security_gaps(processed_resources, security_analysis)
            import_result.security_gaps = security_gaps
            
            # Step 6: Generate compliance status
            compliance_status = await self._assess_imported_compliance(security_analysis)
            import_result.compliance_status = compliance_status
            
            # Step 7: Generate architecture diagram
            diagram_data = await self._generate_architecture_diagram(processed_resources)
            import_result.diagram_data = diagram_data
            
            # Step 8: Calculate costs and scores
            import_result.total_estimated_cost = sum(r.estimated_monthly_cost for r in processed_resources)
            import_result.security_score = self._calculate_security_score(security_gaps, processed_resources)
            
            # Step 9: Generate recommendations
            recommendations = await self._generate_import_recommendations(
                security_gaps, compliance_status, processed_resources
            )
            import_result.recommendations = recommendations
            
            import_result.status = ImportStatus.COMPLETE
            import_result.completed_at = datetime.now()
            
            logger.info(f"Infrastructure import completed successfully: {import_id}")
            
        except Exception as e:
            logger.error(f"Infrastructure import failed: {str(e)}")
            import_result.status = ImportStatus.FAILED
            import_result.recommendations.append(f"Import failed: {str(e)}")
            import_result.completed_at = datetime.now()
        
        return import_result
    
    async def _discover_aws_resources(
        self, 
        services_to_import: Optional[List[str]], 
        resource_filters: Optional[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Discover existing AWS resources across services"""
        
        discovered_resources = {}
        services = services_to_import or self.supported_services
        
        try:
            # Use Resource Groups Tagging API for comprehensive discovery
            paginator = self.clients["resource_groups"].get_paginator("get_resources")
            
            # Build resource type filters
            resource_type_filters = []
            for service in services:
                resource_type_filters.extend(self._get_resource_types_for_service(service))
            
            page_iterator = paginator.paginate(
                ResourceTypeFilters=resource_type_filters,
                ResourcesPerPage=100
            )
            
            for page in page_iterator:
                for resource in page.get("ResourceTagMappingList", []):
                    resource_arn = resource["ResourceARN"]
                    resource_type = self._extract_resource_type_from_arn(resource_arn)
                    service_name = self._extract_service_from_arn(resource_arn)
                    
                    if service_name not in discovered_resources:
                        discovered_resources[service_name] = []
                    
                    # Get detailed resource information
                    resource_details = await self._get_resource_details(resource_arn, resource_type)
                    
                    if resource_details:
                        discovered_resources[service_name].append({
                            "arn": resource_arn,
                            "type": resource_type,
                            "id": self._extract_resource_id_from_arn(resource_arn),
                            "region": self._extract_region_from_arn(resource_arn),
                            "tags": {tag["Key"]: tag["Value"] for tag in resource.get("Tags", [])},
                            "details": resource_details
                        })
            
            # Also discover resources not tagged (common case)
            additional_resources = await self._discover_untagged_resources(services)
            
            # Merge additional resources
            for service, resources in additional_resources.items():
                if service in discovered_resources:
                    # Avoid duplicates
                    existing_ids = {r["id"] for r in discovered_resources[service]}
                    new_resources = [r for r in resources if r["id"] not in existing_ids]
                    discovered_resources[service].extend(new_resources)
                else:
                    discovered_resources[service] = resources
            
            logger.info(f"Discovered {sum(len(resources) for resources in discovered_resources.values())} resources across {len(discovered_resources)} services")
            
        except Exception as e:
            logger.error(f"Resource discovery failed: {str(e)}")
            raise
        
        return discovered_resources
    
    def _get_resource_types_for_service(self, service: str) -> List[str]:
        """Get AWS resource types for a given service"""
        
        service_resource_types = {
            "ec2": ["AWS::EC2::Instance", "AWS::EC2::Volume", "AWS::EC2::SecurityGroup"],
            "vpc": ["AWS::EC2::VPC", "AWS::EC2::Subnet", "AWS::EC2::InternetGateway", "AWS::EC2::NatGateway"],
            "s3": ["AWS::S3::Bucket"],
            "rds": ["AWS::RDS::DBInstance", "AWS::RDS::DBCluster"],
            "lambda": ["AWS::Lambda::Function"],
            "iam": ["AWS::IAM::Role", "AWS::IAM::Policy", "AWS::IAM::User"],
            "load_balancer": ["AWS::ElasticLoadBalancing::LoadBalancer", "AWS::ElasticLoadBalancingV2::LoadBalancer"],
            "cloudtrail": ["AWS::CloudTrail::Trail"],
            "kms": ["AWS::KMS::Key"]
        }
        
        return service_resource_types.get(service, [])
    
    def _extract_resource_type_from_arn(self, arn: str) -> str:
        """Extract resource type from ARN"""
        parts = arn.split(":")
        if len(parts) >= 6:
            resource_part = parts[5]
            if "/" in resource_part:
                return resource_part.split("/")[0]
            return resource_part
        return "unknown"
    
    def _extract_service_from_arn(self, arn: str) -> str:
        """Extract service name from ARN"""
        parts = arn.split(":")
        if len(parts) >= 3:
            return parts[2]
        return "unknown"
    
    def _extract_region_from_arn(self, arn: str) -> str:
        """Extract region from ARN"""
        parts = arn.split(":")
        if len(parts) >= 4:
            return parts[3] or self.region
        return self.region
    
    def _extract_resource_id_from_arn(self, arn: str) -> str:
        """Extract resource ID from ARN"""
        parts = arn.split(":")
        if len(parts) >= 6:
            resource_part = parts[5]
            if "/" in resource_part:
                return resource_part.split("/")[-1]
            return resource_part
        return "unknown"
    
    async def _get_resource_details(self, resource_arn: str, resource_type: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific resource"""
        
        try:
            service = self._extract_service_from_arn(resource_arn)
            resource_id = self._extract_resource_id_from_arn(resource_arn)
            
            if service == "ec2":
                if resource_type == "instance":
                    response = self.clients["ec2"].describe_instances(InstanceIds=[resource_id])
                    instances = response.get("Reservations", [])
                    if instances and instances[0].get("Instances"):
                        return instances[0]["Instances"][0]
                elif resource_type == "security-group":
                    response = self.clients["ec2"].describe_security_groups(GroupIds=[resource_id])
                    if response.get("SecurityGroups"):
                        return response["SecurityGroups"][0]
            
            elif service == "s3":
                try:
                    response = self.clients["s3"].get_bucket_location(Bucket=resource_id)
                    encryption = self.clients["s3"].get_bucket_encryption(Bucket=resource_id)
                    return {
                        "Name": resource_id,
                        "Region": response.get("LocationConstraint") or "us-east-1",
                        "Encryption": encryption
                    }
                except Exception:
                    return {"Name": resource_id, "Region": self.region}
            
            elif service == "rds":
                try:
                    response = self.clients["rds"].describe_db_instances(DBInstanceIdentifier=resource_id)
                    if response.get("DBInstances"):
                        return response["DBInstances"][0]
                except Exception:
                    # Try as cluster
                    response = self.clients["rds"].describe_db_clusters(DBClusterIdentifier=resource_id)
                    if response.get("DBClusters"):
                        return response["DBClusters"][0]
            
            elif service == "lambda":
                response = self.clients["lambda"].get_function(FunctionName=resource_id)
                return response.get("Configuration", {})
            
        except Exception as e:
            logger.warning(f"Failed to get details for resource {resource_arn}: {str(e)}")
        
        return None
    
    async def _discover_untagged_resources(self, services: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Discover resources that don't have tags (common case)"""
        
        untagged_resources = {}
        
        try:
            # EC2 Instances
            if "ec2" in services:
                response = self.clients["ec2"].describe_instances()
                ec2_resources = []
                
                for reservation in response.get("Reservations", []):
                    for instance in reservation.get("Instances", []):
                        ec2_resources.append({
                            "arn": f"arn:aws:ec2:{self.region}:{self.aws_account_id}:instance/{instance['InstanceId']}",
                            "type": "instance",
                            "id": instance["InstanceId"],
                            "region": self.region,
                            "tags": {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])},
                            "details": instance
                        })
                
                if ec2_resources:
                    untagged_resources["ec2"] = ec2_resources
            
            # S3 Buckets
            if "s3" in services:
                response = self.clients["s3"].list_buckets()
                s3_resources = []
                
                for bucket in response.get("Buckets", []):
                    bucket_name = bucket["Name"]
                    try:
                        # Get bucket region
                        location = self.clients["s3"].get_bucket_location(Bucket=bucket_name)
                        bucket_region = location.get("LocationConstraint") or "us-east-1"
                        
                        # Get bucket tags
                        try:
                            tags_response = self.clients["s3"].get_bucket_tagging(Bucket=bucket_name)
                            tags = {tag["Key"]: tag["Value"] for tag in tags_response.get("TagSet", [])}
                        except:
                            tags = {}
                        
                        s3_resources.append({
                            "arn": f"arn:aws:s3:::{bucket_name}",
                            "type": "bucket",
                            "id": bucket_name,
                            "region": bucket_region,
                            "tags": tags,
                            "details": bucket
                        })
                    except Exception as e:
                        logger.warning(f"Failed to get details for S3 bucket {bucket_name}: {str(e)}")
                
                if s3_resources:
                    untagged_resources["s3"] = s3_resources
            
            # RDS Instances
            if "rds" in services:
                response = self.clients["rds"].describe_db_instances()
                rds_resources = []
                
                for db_instance in response.get("DBInstances", []):
                    rds_resources.append({
                        "arn": db_instance["DBInstanceArn"],
                        "type": "db-instance",
                        "id": db_instance["DBInstanceIdentifier"],
                        "region": self.region,
                        "tags": {tag["Key"]: tag["Value"] for tag in db_instance.get("TagList", [])},
                        "details": db_instance
                    })
                
                if rds_resources:
                    untagged_resources["rds"] = rds_resources
            
            # Lambda Functions
            if "lambda" in services:
                response = self.clients["lambda"].list_functions()
                lambda_resources = []
                
                for function in response.get("Functions", []):
                    function_name = function["FunctionName"]
                    function_arn = function["FunctionArn"]
                    
                    # Get function tags
                    try:
                        tags_response = self.clients["lambda"].list_tags(Resource=function_arn)
                        tags = tags_response.get("Tags", {})
                    except:
                        tags = {}
                    
                    lambda_resources.append({
                        "arn": function_arn,
                        "type": "function",
                        "id": function_name,
                        "region": self.region,
                        "tags": tags,
                        "details": function
                    })
                
                if lambda_resources:
                    untagged_resources["lambda"] = lambda_resources
            
        except Exception as e:
            logger.error(f"Failed to discover untagged resources: {str(e)}")
        
        return untagged_resources
    
    async def _run_terraformer_import(
        self, 
        discovered_resources: Dict[str, List[Dict[str, Any]]], 
        project_name: str
    ) -> Dict[str, Any]:
        """Run Terraformer to generate Terraform code for discovered resources"""
        
        logger.info("Starting Terraformer import process")
        
        terraform_result = {
            "terraform_code": "",
            "resource_mapping": {}
        }
        
        try:
            # Create Terraformer configuration
            terraformer_config = self._create_terraformer_config(discovered_resources, project_name)
            
            # Run Terraformer for each service
            all_terraform_files = []
            resource_mapping = {}
            
            for service, resources in discovered_resources.items():
                if not resources:
                    continue
                
                logger.info(f"Running Terraformer for {service} ({len(resources)} resources)")
                
                # Create resource IDs list for Terraformer
                resource_ids = [resource["id"] for resource in resources]
                
                # Run Terraformer command
                terraformer_cmd = [
                    "terraformer",
                    "import", "aws",
                    "--services", service,
                    "--regions", self.region,
                    "--profile", "default",  # We'll set env vars instead
                    "--output", str(self.terraformer_dir),
                    "--verbose"
                ]
                
                # Add resource filters if available
                if resource_ids and service in ["ec2", "s3", "rds", "lambda"]:
                    terraformer_cmd.extend(["--filter", f"{service}={','.join(resource_ids)}"])
                
                # Set AWS credentials as environment variables
                env = {
                    **os.environ,
                    "AWS_ACCESS_KEY_ID": self.aws_credentials["access_key_id"],
                    "AWS_SECRET_ACCESS_KEY": self.aws_credentials["secret_access_key"],
                    "AWS_DEFAULT_REGION": self.region
                }
                
                if self.aws_credentials.get("session_token"):
                    env["AWS_SESSION_TOKEN"] = self.aws_credentials["session_token"]
                
                try:
                    result = subprocess.run(
                        terraformer_cmd,
                        cwd=self.work_dir,
                        capture_output=True,
                        text=True,
                        env=env,
                        timeout=300  # 5 minutes timeout
                    )
                    
                    logger.info(f"Terraformer output for {service}: {result.stdout}")
                    
                    if result.returncode != 0:
                        logger.warning(f"Terraformer failed for {service}: {result.stderr}")
                        # Continue with other services
                        continue
                    
                    # Read generated Terraform files
                    service_tf_files = list(self.terraformer_dir.glob(f"**/{service}/*.tf"))
                    for tf_file in service_tf_files:
                        terraform_content = tf_file.read_text()
                        all_terraform_files.append(terraform_content)
                        
                        # Map resources to their Terraform representation
                        resource_mapping[service] = {
                            "terraform_file": str(tf_file),
                            "resources": resources
                        }
                    
                except subprocess.TimeoutExpired:
                    logger.error(f"Terraformer timeout for service {service}")
                    continue
                except Exception as e:
                    logger.error(f"Terraformer execution failed for {service}: {str(e)}")
                    continue
            
            # If Terraformer fails, generate basic Terraform manually
            if not all_terraform_files:
                logger.warning("Terraformer failed, generating basic Terraform manually")
                manual_terraform = await self._generate_manual_terraform(discovered_resources, project_name)
                all_terraform_files.append(manual_terraform)
            
            # Combine all Terraform files
            combined_terraform = self._combine_terraform_files(all_terraform_files, project_name)
            terraform_result["terraform_code"] = combined_terraform
            terraform_result["resource_mapping"] = resource_mapping
            
        except Exception as e:
            logger.error(f"Terraformer import failed: {str(e)}")
            # Generate basic Terraform as fallback
            manual_terraform = await self._generate_manual_terraform(discovered_resources, project_name)
            terraform_result["terraform_code"] = manual_terraform
        
        return terraform_result
    
    def _create_terraformer_config(
        self, 
        discovered_resources: Dict[str, List[Dict[str, Any]]], 
        project_name: str
    ) -> Dict[str, Any]:
        """Create Terraformer configuration"""
        
        return {
            "version": "1.0",
            "project_name": project_name,
            "region": self.region,
            "services": list(discovered_resources.keys()),
            "output_directory": str(self.terraformer_dir)
        }
    
    async def _generate_manual_terraform(
        self, 
        discovered_resources: Dict[str, List[Dict[str, Any]]], 
        project_name: str
    ) -> str:
        """Generate basic Terraform code manually when Terraformer fails"""
        
        terraform_blocks = [
            f'# Generated Terraform for imported infrastructure',
            f'# Project: {project_name}',
            f'# Generated: {datetime.now().isoformat()}',
            f'',
            f'terraform {{',
            f'  required_version = ">= 1.0"',
            f'  required_providers {{',
            f'    aws = {{',
            f'      source  = "hashicorp/aws"',
            f'      version = "~> 5.0"',
            f'    }}',
            f'  }}',
            f'}}',
            f'',
            f'provider "aws" {{',
            f'  region = "{self.region}"',
            f'}}',
            f''
        ]
        
        # Generate resources for each service
        for service, resources in discovered_resources.items():
            if not resources:
                continue
                
            terraform_blocks.append(f'# {service.upper()} Resources')
            
            for resource in resources:
                resource_tf = self._generate_resource_terraform(service, resource)
                if resource_tf:
                    terraform_blocks.append(resource_tf)
                    terraform_blocks.append('')
        
        return '\n'.join(terraform_blocks)
    
    def _generate_resource_terraform(self, service: str, resource: Dict[str, Any]) -> str:
        """Generate Terraform code for a single resource"""
        
        resource_id = resource["id"]
        resource_type = resource["type"]
        details = resource.get("details", {})
        
        if service == "ec2" and resource_type == "instance":
            return f'''resource "aws_instance" "{resource_id.replace('-', '_')}" {{
  # Imported EC2 instance
  ami           = "{details.get('ImageId', 'ami-12345678')}"
  instance_type = "{details.get('InstanceType', 't3.micro')}"
  
  tags = {{
    Name = "{details.get('Tags', {}).get('Name', resource_id)}"
    ImportedBy = "AWS-Architecture-Generator"
  }}
}}'''
        
        elif service == "s3":
            bucket_name = resource_id
            return f'''resource "aws_s3_bucket" "{bucket_name.replace('-', '_').replace('.', '_')}" {{
  bucket = "{bucket_name}"
  
  tags = {{
    ImportedBy = "AWS-Architecture-Generator"
  }}
}}'''
        
        elif service == "rds":
            return f'''resource "aws_db_instance" "{resource_id.replace('-', '_')}" {{
  identifier = "{resource_id}"
  engine     = "{details.get('Engine', 'mysql')}"
  
  tags = {{
    ImportedBy = "AWS-Architecture-Generator"
  }}
}}'''
        
        elif service == "lambda":
            return f'''resource "aws_lambda_function" "{resource_id.replace('-', '_')}" {{
  function_name = "{resource_id}"
  runtime       = "{details.get('Runtime', 'python3.9')}"
  handler       = "{details.get('Handler', 'index.handler')}"
  
  tags = {{
    ImportedBy = "AWS-Architecture-Generator"
  }}
}}'''
        
        return f'# {service} resource {resource_id} - manual definition needed'
    
    def _combine_terraform_files(self, terraform_files: List[str], project_name: str) -> str:
        """Combine multiple Terraform files into one cohesive configuration"""
        
        combined_terraform = f'''# Combined Terraform Configuration for {project_name}
# Generated from imported AWS infrastructure
# Generated: {datetime.now().isoformat()}

terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "{self.region}"
  
  default_tags {{
    tags = {{
      Project     = "{project_name}"
      ImportedBy  = "AWS-Architecture-Generator"
      ImportedAt  = "{datetime.now().isoformat()}"
    }}
  }}
}}

'''
        
        # Add all Terraform content
        for tf_content in terraform_files:
            # Remove duplicate provider blocks
            lines = tf_content.split('\n')
            filtered_lines = []
            skip_provider = False
            
            for line in lines:
                if line.strip().startswith('terraform {') or line.strip().startswith('provider "'):
                    skip_provider = True
                    continue
                elif skip_provider and line.strip() == '}':
                    skip_provider = False
                    continue
                elif not skip_provider:
                    filtered_lines.append(line)
            
            combined_terraform += '\n'.join(filtered_lines) + '\n\n'
        
        return combined_terraform
    
    async def _analyze_imported_security(self, discovered_resources: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Analyze security posture of imported infrastructure"""
        
        logger.info("Analyzing security posture of imported infrastructure")
        
        # Use our dynamic security analyzer
        project_data = {"id": "imported_infrastructure"}
        questionnaire = {"compliance_requirements": ["SOC2", "GDPR", "PCI-DSS"]}
        services = {f"{service}_{i}": service for service, resources in discovered_resources.items() for i in range(len(resources))}
        
        try:
            security_analysis = await self.security_analyzer.analyze_project_security(
                project_data, questionnaire, services
            )
            return security_analysis
        except Exception as e:
            logger.error(f"Security analysis failed: {str(e)}")
            return {
                "security_metrics": {"overall_score": 0},
                "threats": [],
                "compliance_results": {},
                "recommendations": []
            }
    
    async def _process_imported_resources(
        self, 
        discovered_resources: Dict[str, List[Dict[str, Any]]], 
        resource_mapping: Dict[str, Any]
    ) -> List[ImportedResource]:
        """Process discovered resources into ImportedResource objects"""
        
        processed_resources = []
        
        for service, resources in discovered_resources.items():
            for resource in resources:
                # Estimate cost
                estimated_cost = await self._estimate_resource_cost(service, resource)
                
                # Check security compliance
                security_issues = await self._check_resource_security(service, resource)
                
                # Get Terraform code for this resource
                terraform_code = self._get_resource_terraform_code(service, resource, resource_mapping)
                
                processed_resource = ImportedResource(
                    resource_type=service,
                    resource_name=resource.get("tags", {}).get("Name", resource["id"]),
                    resource_id=resource["id"],
                    region=resource["region"],
                    tags=resource["tags"],
                    security_compliant=len(security_issues) == 0,
                    security_issues=security_issues,
                    terraform_code=terraform_code,
                    estimated_monthly_cost=estimated_cost
                )
                
                processed_resources.append(processed_resource)
        
        return processed_resources
    
    async def _estimate_resource_cost(self, service: str, resource: Dict[str, Any]) -> float:
        """Estimate monthly cost for a resource"""
        
        # Basic cost estimation - in production, use AWS Pricing API
        cost_estimates = {
            "ec2": 50.0,  # Average EC2 instance
            "s3": 5.0,    # Small S3 bucket
            "rds": 100.0, # Small RDS instance
            "lambda": 10.0, # Light Lambda usage
        }
        
        base_cost = cost_estimates.get(service, 25.0)
        
        # Adjust based on resource details
        details = resource.get("details", {})
        
        if service == "ec2":
            instance_type = details.get("InstanceType", "t3.micro")
            if "large" in instance_type:
                base_cost *= 4
            elif "medium" in instance_type:
                base_cost *= 2
        
        elif service == "rds":
            instance_class = details.get("DBInstanceClass", "db.t3.micro")
            if "large" in instance_class:
                base_cost *= 3
            elif "medium" in instance_class:
                base_cost *= 1.5
        
        return base_cost
    
    async def _check_resource_security(self, service: str, resource: Dict[str, Any]) -> List[str]:
        """Check security issues for a specific resource"""
        
        security_issues = []
        details = resource.get("details", {})
        
        if service == "ec2":
            # Check for public IP
            if details.get("PublicIpAddress"):
                security_issues.append("Instance has public IP address")
            
            # Check security groups (would need additional API calls)
            security_issues.append("Security group review needed")
        
        elif service == "s3":
            # Check for public access (simplified)
            security_issues.append("Bucket public access configuration needs review")
            
            # Check encryption
            if "Encryption" not in details:
                security_issues.append("Bucket encryption not configured")
        
        elif service == "rds":
            # Check for public accessibility
            if details.get("PubliclyAccessible"):
                security_issues.append("Database is publicly accessible")
            
            # Check encryption
            if not details.get("StorageEncrypted"):
                security_issues.append("Database storage not encrypted")
        
        return security_issues
    
    def _get_resource_terraform_code(
        self, 
        service: str, 
        resource: Dict[str, Any], 
        resource_mapping: Dict[str, Any]
    ) -> str:
        """Get Terraform code for a specific resource"""
        
        if service in resource_mapping:
            # Try to extract from Terraformer output
            return f"# Terraform code for {service} resource {resource['id']}"
        else:
            # Generate basic Terraform
            return self._generate_resource_terraform(service, resource)
    
    async def _identify_security_gaps(
        self, 
        processed_resources: List[ImportedResource], 
        security_analysis: Dict[str, Any]
    ) -> List[SecurityGap]:
        """Identify security gaps in imported infrastructure"""
        
        security_gaps = []
        
        # Analyze each resource for security gaps
        for resource in processed_resources:
            if not resource.security_compliant:
                for issue in resource.security_issues:
                    gap = SecurityGap(
                        gap_id=str(uuid.uuid4()),
                        resource_id=resource.resource_id,
                        resource_type=resource.resource_type,
                        gap_type=self._categorize_security_issue(issue),
                        severity=self._assess_security_severity(issue),
                        description=issue,
                        current_configuration={"status": "non_compliant"},
                        recommended_configuration={"status": "compliant"},
                        remediation_terraform=self._generate_remediation_terraform(resource, issue),
                        compliance_frameworks_affected=["SOC2", "GDPR"],
                        estimated_fix_time="2-4 hours"
                    )
                    security_gaps.append(gap)
        
        # Add gaps from security analysis
        threats = security_analysis.get("threats", [])
        for threat in threats:
            if isinstance(threat, dict):
                gap = SecurityGap(
                    gap_id=str(uuid.uuid4()),
                    resource_id=threat.get("affected_resources", ["unknown"])[0],
                    resource_type="infrastructure",
                    gap_type="security_threat",
                    severity=threat.get("severity", "medium"),
                    description=threat.get("description", "Security threat detected"),
                    current_configuration={"threat_detected": True},
                    recommended_configuration={"threat_mitigated": True},
                    remediation_terraform=self._generate_threat_remediation_terraform(threat),
                    compliance_frameworks_affected=["SOC2", "PCI-DSS"],
                    estimated_fix_time="1-2 days"
                )
                security_gaps.append(gap)
        
        return security_gaps
    
    def _categorize_security_issue(self, issue: str) -> str:
        """Categorize a security issue"""
        
        issue_lower = issue.lower()
        
        if "encryption" in issue_lower:
            return "missing_encryption"
        elif "public" in issue_lower:
            return "public_access"
        elif "security group" in issue_lower:
            return "network_security"
        else:
            return "security_misconfiguration"
    
    def _assess_security_severity(self, issue: str) -> str:
        """Assess severity of a security issue"""
        
        issue_lower = issue.lower()
        
        if "public" in issue_lower or "exposed" in issue_lower:
            return "high"
        elif "encryption" in issue_lower:
            return "medium"
        else:
            return "low"
    
    def _generate_remediation_terraform(self, resource: ImportedResource, issue: str) -> str:
        """Generate Terraform code to fix a security issue"""
        
        if "encryption" in issue.lower():
            return f'''# Enable encryption for {resource.resource_type}
resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {{
  bucket = aws_s3_bucket.{resource.resource_id.replace('-', '_')}.id
  
  rule {{
    apply_server_side_encryption_by_default {{
      sse_algorithm = "AES256"
    }}
  }}
}}'''
        
        elif "public" in issue.lower():
            return f'''# Block public access for {resource.resource_type}
resource "aws_s3_bucket_public_access_block" "block_public" {{
  bucket = aws_s3_bucket.{resource.resource_id.replace('-', '_')}.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}'''
        
        return f"# Remediation needed for: {issue}"
    
    def _generate_threat_remediation_terraform(self, threat: Dict[str, Any]) -> str:
        """Generate Terraform code to remediate a security threat"""
        
        return f'''# Remediation for threat: {threat.get('title', 'Unknown threat')}
# Steps: {', '.join(threat.get('remediation_steps', ['Manual review required']))}

# Additional security controls may be needed
# Please review and implement appropriate measures'''
    
    async def _assess_imported_compliance(self, security_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess compliance status of imported infrastructure"""
        
        compliance_results = security_analysis.get("compliance_results", {})
        
        # Format compliance status
        compliance_status = {}
        
        for framework, result in compliance_results.items():
            if isinstance(result, dict):
                compliance_status[framework] = {
                    "status": result.get("status", "unknown"),
                    "score": result.get("score", 0),
                    "total_controls": result.get("total_controls", 0),
                    "passed_controls": result.get("passed_controls", 0),
                    "failed_controls": result.get("failed_controls", 0)
                }
        
        return compliance_status
    
    async def _generate_architecture_diagram(self, processed_resources: List[ImportedResource]) -> Dict[str, Any]:
        """Generate architecture diagram data for imported resources"""
        
        nodes = []
        edges = []
        
        # Create nodes for each resource
        for i, resource in enumerate(processed_resources):
            node = {
                "id": resource.resource_id,
                "type": "default",
                "data": {
                    "label": f"{resource.resource_name}\n({resource.resource_type})",
                    "resource_type": resource.resource_type,
                    "security_compliant": resource.security_compliant,
                    "estimated_cost": resource.estimated_monthly_cost
                },
                "position": {
                    "x": (i % 4) * 200 + 100,
                    "y": (i // 4) * 150 + 100
                }
            }
            nodes.append(node)
        
        # Create basic edges (would need more sophisticated logic for real connections)
        for i in range(len(nodes) - 1):
            edge = {
                "id": f"edge_{i}",
                "source": nodes[i]["id"],
                "target": nodes[i + 1]["id"],
                "type": "default"
            }
            edges.append(edge)
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def _calculate_security_score(self, security_gaps: List[SecurityGap], processed_resources: List[ImportedResource]) -> float:
        """Calculate overall security score"""
        
        if not processed_resources:
            return 0.0
        
        # Count security issues by severity
        critical_gaps = len([g for g in security_gaps if g.severity == "critical"])
        high_gaps = len([g for g in security_gaps if g.severity == "high"])
        medium_gaps = len([g for g in security_gaps if g.severity == "medium"])
        
        # Calculate score (100 - penalties)
        total_penalty = (critical_gaps * 20) + (high_gaps * 10) + (medium_gaps * 5)
        security_score = max(0, 100 - total_penalty)
        
        return security_score
    
    async def _generate_import_recommendations(
        self, 
        security_gaps: List[SecurityGap], 
        compliance_status: Dict[str, Any], 
        processed_resources: List[ImportedResource]
    ) -> List[str]:
        """Generate recommendations for imported infrastructure"""
        
        recommendations = []
        
        # Security recommendations
        if security_gaps:
            critical_gaps = [g for g in security_gaps if g.severity == "critical"]
            high_gaps = [g for g in security_gaps if g.severity == "high"]
            
            if critical_gaps:
                recommendations.append(f"🚨 URGENT: Address {len(critical_gaps)} critical security gaps immediately")
            
            if high_gaps:
                recommendations.append(f"⚠️ HIGH PRIORITY: Fix {len(high_gaps)} high-severity security issues")
            
            # Group recommendations by type
            gap_types = {}
            for gap in security_gaps:
                if gap.gap_type not in gap_types:
                    gap_types[gap.gap_type] = 0
                gap_types[gap.gap_type] += 1
            
            for gap_type, count in gap_types.items():
                recommendations.append(f"🔧 Fix {count} instances of {gap_type.replace('_', ' ')}")
        
        # Compliance recommendations
        for framework, status in compliance_status.items():
            if status.get("status") == "non_compliant":
                recommendations.append(f"📋 Improve {framework} compliance (currently {status.get('score', 0)}%)")
        
        # Cost optimization recommendations
        total_cost = sum(r.estimated_monthly_cost for r in processed_resources)
        if total_cost > 1000:
            recommendations.append(f"💰 Review high monthly costs (${total_cost:.2f}) for optimization opportunities")
        
        # General recommendations
        recommendations.extend([
            "🔍 Review and apply the generated Terraform code to manage infrastructure as code",
            "📊 Implement monitoring and alerting for all imported resources",
            "🔄 Set up automated compliance scanning",
            "💾 Create backup and disaster recovery plans for critical resources"
        ])
        
        return recommendations
    
    def __del__(self):
        """Clean up working directory"""
        try:
            if hasattr(self, 'work_dir') and self.work_dir.exists():
                shutil.rmtree(self.work_dir)
                logger.info(f"Cleaned up working directory: {self.work_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean up working directory: {str(e)}")