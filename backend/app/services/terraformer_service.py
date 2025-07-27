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
                "resource_groups": self.session.client("resourcegroupstaggingapi")
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
            logger.info("Step 1: Starting infrastructure scanning...")
            import_result.status = ImportStatus.SCANNING
            
            try:
                discovered_resources = await self._discover_aws_resources(services_to_import, resource_filters)
                logger.info(f"Step 1 completed: Found {len(discovered_resources) if discovered_resources else 0} service types")
            except Exception as e:
                logger.error(f"Step 1 failed during resource discovery: {str(e)}")
                import traceback
                logger.error(f"Step 1 traceback: {traceback.format_exc()}")
                raise
            
            if not discovered_resources:
                logger.warning("Step 1: No resources discovered")
                import_result.status = ImportStatus.FAILED
                import_result.recommendations.append("No resources found to import. Check your AWS account and permissions.")
                return import_result
            
            # Step 2: Generate Terraform code using Terraformer
            logger.info("Step 2: Starting Terraform code generation...")
            import_result.status = ImportStatus.GENERATING
            
            try:
                terraform_result = await self._run_terraformer_import(discovered_resources, project_name)
                if terraform_result is None:
                    logger.error("Step 2: Terraform result is None")
                    raise Exception("Terraform import returned None result")
                
                import_result.terraform_code = terraform_result.get("terraform_code", "")
                logger.info("Step 2 completed: Terraform code generated")
            except Exception as e:
                logger.error(f"Step 2 failed during Terraform generation: {str(e)}")
                import traceback
                logger.error(f"Step 2 traceback: {traceback.format_exc()}")
                raise
            
            # Step 3: Analyze security posture
            logger.info("Step 3: Starting security analysis...")
            import_result.status = ImportStatus.ANALYZING
            
            try:
                security_analysis = await self._analyze_imported_security(discovered_resources)
                if security_analysis is None:
                    logger.warning("Step 3: Security analysis returned None, using empty dict")
                    security_analysis = {}
                logger.info("Step 3 completed: Security analysis finished")
            except Exception as e:
                logger.error(f"Step 3 failed during security analysis: {str(e)}")
                import traceback
                logger.error(f"Step 3 traceback: {traceback.format_exc()}")
                raise
            
            # Step 4: Process imported resources
            logger.info("Step 4: Starting resource processing...")
            
            try:
                resource_mapping = terraform_result.get("resource_mapping", {})
                if resource_mapping is None:
                    logger.warning("Step 4: Resource mapping is None, using empty dict")
                    resource_mapping = {}
                
                processed_resources = await self._process_imported_resources(
                    discovered_resources, 
                    resource_mapping
                )
                
                if processed_resources is None:
                    logger.warning("Step 4: Processed resources is None, using empty list")
                    processed_resources = []
                
                import_result.imported_resources = processed_resources
                logger.info(f"Step 4 completed: Processed {len(processed_resources)} resources")
            except Exception as e:
                logger.error(f"Step 4 failed during resource processing: {str(e)}")
                import traceback
                logger.error(f"Step 4 traceback: {traceback.format_exc()}")
                raise
            
            # Step 5: Identify security gaps
            logger.info("Step 5: Starting security gap identification...")
            
            try:
                security_gaps = await self._identify_security_gaps(processed_resources, security_analysis)
                if security_gaps is None:
                    logger.warning("Step 5: Security gaps is None, using empty list")
                    security_gaps = []
                import_result.security_gaps = security_gaps
                logger.info(f"Step 5 completed: Identified {len(security_gaps)} security gaps")
            except Exception as e:
                logger.error(f"Step 5 failed during security gap identification: {str(e)}")
                import traceback
                logger.error(f"Step 5 traceback: {traceback.format_exc()}")
                # Continue with empty list rather than failing
                import_result.security_gaps = []
            
            # Step 6: Generate compliance status
            logger.info("Step 6: Starting compliance assessment...")
            
            try:
                compliance_status = await self._assess_imported_compliance(security_analysis)
                if compliance_status is None:
                    logger.warning("Step 6: Compliance status is None, using empty dict")
                    compliance_status = {}
                import_result.compliance_status = compliance_status
                logger.info("Step 6 completed: Compliance assessment finished")
            except Exception as e:
                logger.error(f"Step 6 failed during compliance assessment: {str(e)}")
                import traceback
                logger.error(f"Step 6 traceback: {traceback.format_exc()}")
                # Continue with empty dict rather than failing
                import_result.compliance_status = {}
            
            # Step 7: Generate architecture diagram
            logger.info("Step 7: Starting diagram generation...")
            
            try:
                diagram_data = await self._generate_architecture_diagram(processed_resources)
                if diagram_data is None:
                    logger.warning("Step 7: Diagram data is None, using empty dict")
                    diagram_data = {}
                import_result.diagram_data = diagram_data
                logger.info("Step 7 completed: Architecture diagram generated")
            except Exception as e:
                logger.error(f"Step 7 failed during diagram generation: {str(e)}")
                import traceback
                logger.error(f"Step 7 traceback: {traceback.format_exc()}")
                # Continue with empty dict rather than failing
                import_result.diagram_data = {}
            
            # Step 8: Calculate costs and scores
            logger.info("Step 8: Starting cost and score calculation...")
            
            try:
                if processed_resources:
                    import_result.total_estimated_cost = sum(r.estimated_monthly_cost for r in processed_resources if r and hasattr(r, 'estimated_monthly_cost') and r.estimated_monthly_cost)
                else:
                    import_result.total_estimated_cost = 0.0
                logger.info(f"Step 8: Total estimated cost: ${import_result.total_estimated_cost}")
            except Exception as e:
                logger.error(f"Step 8 failed during cost calculation: {str(e)}")
                import_result.total_estimated_cost = 0.0
            # Calculate security score
            try:
                import_result.security_score = self._calculate_security_score(security_gaps, processed_resources)
                logger.info(f"Security score calculated: {import_result.security_score}")
            except Exception as e:
                logger.error(f"Failed to calculate security score: {str(e)}")
                import_result.security_score = 0.0
            
            # Step 9: Generate recommendations
            logger.info("Step 9: Starting recommendation generation...")
            
            try:
                recommendations = await self._generate_import_recommendations(
                    security_gaps, compliance_status, processed_resources
                )
                if recommendations is None:
                    logger.warning("Step 9: Recommendations is None, using empty list")
                    recommendations = []
                import_result.recommendations = recommendations
                logger.info(f"Step 9 completed: Generated {len(recommendations)} recommendations")
            except Exception as e:
                logger.error(f"Step 9 failed during recommendation generation: {str(e)}")
                import traceback
                logger.error(f"Step 9 traceback: {traceback.format_exc()}")
                # Continue with empty list rather than failing
                import_result.recommendations = []
            
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
        
        logger.info(f"Starting resource discovery in region: {self.region}")
        logger.info(f"Services to discover: {services}")
        
        try:
            # First, use direct service APIs to discover all resources (more comprehensive)
            # Run discovery methods concurrently for better performance
            logger.info("Starting concurrent resource discovery...")
            
            import asyncio
            discovery_tasks = [
                self._discover_ec2_resources(discovered_resources, services),
                self._discover_s3_resources(discovered_resources, services),
                self._discover_rds_resources(discovered_resources, services)
            ]
            
            # Run all discovery tasks concurrently with timeout
            try:
                await asyncio.wait_for(asyncio.gather(*discovery_tasks), timeout=45.0)
                logger.info("Concurrent resource discovery completed")
            except asyncio.TimeoutError:
                logger.warning("Resource discovery timed out after 45 seconds, continuing with partial results")
            
            # Then use Resource Groups Tagging API for additional tagged resources (with timeout)
            logger.info("Starting Resource Groups API discovery...")
            
            try:
                async def discover_tagged_resources():
                    paginator = self.clients["resource_groups"].get_paginator("get_resources")
                    
                    # Get all resources and filter later (ResourceTypeFilters format is inconsistent)
                    page_iterator = paginator.paginate(
                        ResourcesPerPage=100
                    )
                    
                    resource_count = 0
                    for page in page_iterator:
                        for resource in page.get("ResourceTagMappingList", []):
                            resource_arn = resource["ResourceARN"]
                            resource_type = self._extract_resource_type_from_arn(resource_arn)
                            service_name = self._extract_service_from_arn(resource_arn)
                            
                            # Filter by requested services if specified
                            if services and service_name not in services:
                                continue
                            
                            if service_name not in discovered_resources:
                                discovered_resources[service_name] = []
                            
                            # Check if we already discovered this resource via direct API
                            resource_id = self._extract_resource_id_from_arn(resource_arn)
                            if any(r.get("resource_id") == resource_id or r.get("resource_name") == resource_id for r in discovered_resources[service_name]):
                                continue  # Skip duplicates
                            
                            # Get detailed resource information (skip for performance if too many)
                            resource_details = None
                            if resource_count < 50:  # Limit detailed calls for performance
                                resource_details = await self._get_resource_details(resource_arn, resource_type)
                            
                            discovered_resources[service_name].append({
                                "resource_arn": resource_arn,
                                "resource_name": self._extract_resource_name_from_arn(resource_arn),
                                "resource_id": resource_id,
                                "resource_type": resource_type,
                                "service": service_name,
                                "region": self._extract_region_from_arn(resource_arn),
                                "tags": {tag["Key"]: tag["Value"] for tag in resource.get("Tags", [])},
                                "details": resource_details or {}
                            })
                            
                            resource_count += 1
                            if resource_count >= 100:  # Limit total resources for performance
                                logger.info("Reached resource limit (100), stopping Resource Groups discovery")
                                return
                
                # Run with timeout
                await asyncio.wait_for(discover_tagged_resources(), timeout=30.0)
                logger.info("Resource Groups API discovery completed")
                
            except asyncio.TimeoutError:
                logger.warning("Resource Groups API discovery timed out after 30 seconds")
            except Exception as e:
                logger.warning(f"Resource Groups API discovery failed: {str(e)}")
            
            # Discover additional untagged resources
            try:
                additional_resources = await self._discover_untagged_resources(services)
                
                # Merge additional resources
                for service, resources in additional_resources.items():
                    if service in discovered_resources:
                        # Avoid duplicates - safely handle both dict and non-dict resources
                        existing_ids = set()
                        for r in discovered_resources[service]:
                            if isinstance(r, dict):
                                existing_ids.add(r.get("resource_id", r.get("id", "unknown")))
                            else:
                                logger.warning(f"Non-dict resource found in {service}: {type(r)}")
                        
                        new_resources = []
                        for r in resources:
                            if isinstance(r, dict):
                                resource_id = r.get("resource_id", r.get("id", "unknown"))
                                if resource_id not in existing_ids:
                                    new_resources.append(r)
                            else:
                                logger.warning(f"Skipping non-dict resource in additional {service}: {type(r)}")
                        
                        discovered_resources[service].extend(new_resources)
                    else:
                        # Filter out non-dict resources
                        valid_resources = [r for r in resources if isinstance(r, dict)]
                        if len(valid_resources) < len(resources):
                            logger.warning(f"Filtered out {len(resources) - len(valid_resources)} non-dict resources from {service}")
                        discovered_resources[service] = valid_resources
            except Exception as e:
                logger.warning(f"Failed to discover additional untagged resources: {str(e)}")
            
            total_resources = sum(len(resources) for resources in discovered_resources.values())
            logger.info(f"Discovered {total_resources} resources across {len(discovered_resources)} services")
            
            # Log detailed breakdown by service
            for service, resources in discovered_resources.items():
                logger.info(f"  {service}: {len(resources)} resources")
                for i, resource in enumerate(resources[:3]):  # Log first 3 resources for debugging
                    if isinstance(resource, dict):
                        resource_id = resource.get("resource_id", resource.get("id", f"unknown_{i}"))
                        logger.info(f"    - {resource_id}")
                    else:
                        logger.info(f"    - non-dict resource: {type(resource)}")
            
        except Exception as e:
            logger.error(f"Resource discovery failed: {str(e)}")
            raise
        
        return discovered_resources
    
    def _get_resource_types_for_service(self, service: str) -> List[str]:
        """Get AWS resource types for a given service in the correct format for Resource Groups Tagging API"""
        
        # Resource Groups Tagging API expects service names, not CloudFormation resource types
        service_resource_types = {
            "ec2": ["ec2:instance", "ec2:volume", "ec2:security-group"],
            "vpc": ["ec2:vpc", "ec2:subnet", "ec2:internet-gateway", "ec2:nat-gateway"],
            "s3": ["s3:bucket"],
            "rds": ["rds:db", "rds:cluster"],
            "lambda": ["lambda:function"],
            "iam": ["iam:role", "iam:policy", "iam:user"],
            "load_balancer": ["elasticloadbalancing:loadbalancer"],
            "cloudtrail": ["cloudtrail:trail"],
            "kms": ["kms:key"]
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
            if "ec2" in services or "ec2_instance" in services:
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
                    untagged_resources["ec2_instance"] = ec2_resources
            
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
                resource_ids = [resource.get("resource_id", resource.get("id", "unknown")) for resource in resources]
                
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
                if resource_ids and service in ["ec2", "ec2_instance", "s3", "rds", "lambda"]:
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
        
        resource_id = resource.get("resource_id", resource.get("id", "unknown"))
        resource_type = resource.get("resource_type", resource.get("type", "unknown"))
        details = resource.get("details", {})
        
        if (service == "ec2" or service == "ec2_instance") and (resource_type == "instance" or resource_type == "ec2_instance"):
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
        
        # Create services map with actual resource names for proper security analysis
        services = {}
        logger.info(f"Discovered resources structure: {discovered_resources}")
        
        for service, resources in discovered_resources.items():
            logger.info(f"Processing service: {service}, resources: {len(resources) if isinstance(resources, list) else 'not a list'}")
            if not isinstance(resources, list):
                logger.warning(f"Resources for {service} is not a list: {type(resources)}")
                continue
                
            for i, resource in enumerate(resources):
                logger.info(f"Resource {i}: {resource}")
                if resource is None:
                    logger.warning(f"Resource {i} is None, skipping")
                    continue
                    
                if not isinstance(resource, dict):
                    logger.warning(f"Resource {i} is not a dict: {type(resource)}, using fallback name")
                    resource_name = f"{service}_resource_{i}"
                else:
                    # Use actual resource name/identifier instead of generic service type
                    resource_name = resource.get("resource_name") or resource.get("name") or resource.get("bucket_name") or f"{service}_resource_{i}"
                
                services[resource_name] = service
                logger.info(f"Added to services: {resource_name} -> {service}")
        
        logger.info(f"Final services map for security analysis: {services}")
        
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
            if not isinstance(resources, list):
                logger.error(f"Resources for service {service} is not a list: {type(resources)}")
                continue
                
            for i, resource in enumerate(resources):
                # Validate resource is a dictionary
                if not isinstance(resource, dict):
                    logger.error(f"Resource {i} in service {service} is not a dict: {type(resource)} - {resource}")
                    continue
                
                try:
                    # Estimate cost
                    estimated_cost = await self._estimate_resource_cost(service, resource)
                    
                    # Check security compliance
                    security_issues = await self._check_resource_security(service, resource)
                    
                    # Get Terraform code for this resource
                    terraform_code = self._get_resource_terraform_code(service, resource, resource_mapping)
                    
                    # Safely extract resource fields with proper fallbacks
                    resource_tags = resource.get("tags", {}) if isinstance(resource.get("tags"), dict) else {}
                    resource_name = resource_tags.get("Name") if resource_tags else None
                    if not resource_name:
                        resource_name = resource.get("resource_id") or resource.get("id") or f"{service}_resource_{i}"
                    
                    resource_id = resource.get("resource_id") or resource.get("id") or f"unknown_{service}_{i}"
                    resource_region = resource.get("region") or self.region
                    
                    processed_resource = ImportedResource(
                        resource_type=service,
                        resource_name=resource_name,
                        resource_id=resource_id,
                        region=resource_region,
                        tags=resource_tags,
                        security_compliant=len(security_issues) == 0,
                        security_issues=security_issues,
                        terraform_code=terraform_code,
                        estimated_monthly_cost=estimated_cost
                    )
                except Exception as e:
                    logger.error(f"Failed to process resource {i} in service {service}: {str(e)}")
                    logger.error(f"Resource data: {resource}")
                    continue
                
                processed_resources.append(processed_resource)
        
        return processed_resources
    
    async def _estimate_resource_cost(self, service: str, resource: Dict[str, Any]) -> float:
        """Estimate monthly cost for a resource"""
        
        # Validate input
        if not isinstance(resource, dict):
            logger.warning(f"Cannot estimate cost for non-dict resource in {service}: {type(resource)}")
            return 0.0
        
        # Basic cost estimation - in production, use AWS Pricing API
        cost_estimates = {
            "ec2": 50.0,  # Average EC2 instance
            "ec2_instance": 50.0,  # Average EC2 instance
            "s3": 5.0,    # Small S3 bucket
            "rds": 100.0, # Small RDS instance
            "lambda": 10.0, # Light Lambda usage
        }
        
        base_cost = cost_estimates.get(service, 25.0)
        
        # Adjust based on resource details
        details = resource.get("details", {})
        if not isinstance(details, dict):
            logger.warning(f"Resource details is not a dict for {service}: {type(details)}")
            details = {}
        
        if service == "ec2" or service == "ec2_instance":
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
        
        # Safety check: ensure resource is not None and is a dict
        if not resource or not isinstance(resource, dict):
            logger.warning(f"Invalid resource passed to security check: {resource}")
            return ["Resource security check failed due to invalid data"]
        
        details = resource.get("details", {})
        
        if service == "ec2" or service == "ec2_instance":
            # Check for public IP
            if details.get("PublicIpAddress"):
                security_issues.append("Instance has public IP address")
            
            # Check security groups (would need additional API calls)
            security_issues.append("Security group review needed")
        
        elif service == "s3":
            # Perform actual S3 security checks instead of hardcoded assumptions
            bucket_name = None
            if isinstance(details, dict):
                bucket_name = details.get("resource_name") or details.get("name") or details.get("bucket_name")
            
            # Also try to get bucket name from resource directly
            if not bucket_name and isinstance(resource, dict):
                bucket_name = resource.get("resource_name") or resource.get("name") or resource.get("bucket_name")
            
            if bucket_name:
                # Check public access block configuration
                try:
                    public_access = self.clients["s3"].get_public_access_block(Bucket=bucket_name)
                    config = public_access.get("PublicAccessBlockConfiguration", {})
                    required_settings = ["BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets"]
                    missing_settings = [setting for setting in required_settings if not config.get(setting, False)]
                    
                    if missing_settings:
                        security_issues.append(f"Bucket public access not fully blocked (missing: {', '.join(missing_settings)})")
                except Exception as e:
                    if "NoSuchPublicAccessBlockConfiguration" in str(e):
                        security_issues.append("Bucket public access block not configured")
                
                # Check encryption
                try:
                    encryption = self.clients["s3"].get_bucket_encryption(Bucket=bucket_name)
                    encryption_config = encryption.get("ServerSideEncryptionConfiguration", {})
                    rules = encryption_config.get("Rules", [])
                    
                    if not rules:
                        security_issues.append("Bucket encryption not configured")
                except Exception as e:
                    if "ServerSideEncryptionConfigurationNotFoundError" in str(e) or "NoSuchEncryptionConfiguration" in str(e):
                        security_issues.append("Bucket encryption not configured")
            else:
                # Fallback when bucket name cannot be determined
                logger.warning(f"Could not determine S3 bucket name from resource: {resource}")
                security_issues.append("S3 bucket security check needs manual review")
        
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
        
        # Validate input
        if not isinstance(resource, dict):
            logger.warning(f"Cannot generate Terraform code for non-dict resource in {service}: {type(resource)}")
            return f"# Terraform code generation failed - invalid resource data"
        
        if service in resource_mapping:
            # Try to extract from Terraformer output
            resource_id = resource.get('resource_id') or resource.get('id') or 'unknown'
            return f"# Terraform code for {service} resource {resource_id}"
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

    async def _discover_ec2_resources(self, discovered_resources: Dict[str, List], services: List[str]):
        """Discover EC2 instances using direct EC2 API calls"""
        if not services or "ec2" in services or "ec2_instance" in services:
            try:
                if "ec2" not in self.clients:
                    logger.warning("EC2 client not available - skipping EC2 discovery")
                    return
                
                logger.info(f"Discovering EC2 instances via direct API in region: {self.region}")
                response = self.clients["ec2"].describe_instances()
                
                total_reservations = len(response.get("Reservations", []))
                logger.info(f"Found {total_reservations} reservations")
                
                ec2_resources = []
                for reservation in response.get("Reservations", []):
                    instances_in_reservation = reservation.get("Instances", [])
                    logger.info(f"Processing reservation with {len(instances_in_reservation)} instances")
                    
                    for instance in instances_in_reservation:
                        instance_id = instance.get("InstanceId")
                        instance_state = instance.get("State", {}).get("Name", "unknown")
                        
                        logger.info(f"Found EC2 instance: {instance_id} (State: {instance_state})")
                        
                        if instance_id:
                            # Include all instances regardless of state (running, stopped, etc.)
                            ec2_resources.append({
                                "resource_name": instance_id,
                                "resource_id": instance_id,
                                "resource_type": "ec2_instance",
                                "service": "ec2_instance",
                                "region": self.region,
                                "details": {
                                    "InstanceType": instance.get("InstanceType"),
                                    "State": instance_state,
                                    "PublicIpAddress": instance.get("PublicIpAddress"),
                                    "PrivateIpAddress": instance.get("PrivateIpAddress"),
                                    "LaunchTime": str(instance.get("LaunchTime", "")),
                                    "Platform": instance.get("Platform"),
                                    "VpcId": instance.get("VpcId"),
                                    "SubnetId": instance.get("SubnetId")
                                },
                                "tags": {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
                            })
                
                logger.info(f"Total EC2 instances discovered: {len(ec2_resources)}")
                
                if ec2_resources:
                    discovered_resources["ec2_instance"] = ec2_resources
                    logger.info(f"Added {len(ec2_resources)} EC2 instances to discovered_resources")
                else:
                    logger.warning("No EC2 instances found - this could indicate permission issues or no instances in this region")
                    
            except Exception as e:
                logger.error(f"Failed to discover EC2 resources: {str(e)}")
                logger.error(f"Error type: {type(e).__name__}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")

    async def _discover_s3_resources(self, discovered_resources: Dict[str, List], services: List[str]):
        """Discover S3 buckets using direct S3 API calls"""
        if not services or "s3" in services:
            try:
                if "s3" not in self.clients:
                    return
                
                logger.info("Discovering S3 buckets via direct API")
                response = self.clients["s3"].list_buckets()
                
                s3_resources = []
                for bucket in response.get("Buckets", []):
                    bucket_name = bucket.get("Name")
                    if bucket_name:
                        # Get bucket location
                        try:
                            location_response = self.clients["s3"].get_bucket_location(Bucket=bucket_name)
                            region = location_response.get("LocationConstraint") or "us-east-1"
                        except:
                            region = self.region
                            
                        s3_resources.append({
                            "resource_name": bucket_name,
                            "resource_id": bucket_name,
                            "resource_type": "s3",
                            "service": "s3",
                            "region": region,
                            "details": {
                                "BucketName": bucket_name,
                                "CreationDate": str(bucket.get("CreationDate", ""))
                            },
                            "tags": {}
                        })
                
                if s3_resources:
                    discovered_resources["s3"] = s3_resources
                    logger.info(f"Discovered {len(s3_resources)} S3 buckets")
                    
            except Exception as e:
                logger.error(f"Failed to discover S3 resources: {str(e)}")

    async def _discover_rds_resources(self, discovered_resources: Dict[str, List], services: List[str]):
        """Discover RDS instances using direct RDS API calls"""
        if not services or "rds" in services:
            try:
                if "rds" not in self.clients:
                    return
                
                logger.info("Discovering RDS instances via direct API")
                response = self.clients["rds"].describe_db_instances()
                
                rds_resources = []
                for db_instance in response.get("DBInstances", []):
                    db_id = db_instance.get("DBInstanceIdentifier")
                    if db_id:
                        rds_resources.append({
                            "resource_name": db_id,
                            "resource_id": db_id,
                            "resource_type": "rds",
                            "service": "rds",
                            "region": self.region,
                            "details": {
                                "DBInstanceClass": db_instance.get("DBInstanceClass"),
                                "Engine": db_instance.get("Engine"),
                                "DBInstanceStatus": db_instance.get("DBInstanceStatus"),
                                "AllocatedStorage": db_instance.get("AllocatedStorage"),
                                "PubliclyAccessible": db_instance.get("PubliclyAccessible"),
                                "VpcId": db_instance.get("DBSubnetGroup", {}).get("VpcId")
                            },
                            "tags": {}
                        })
                
                if rds_resources:
                    discovered_resources["rds"] = rds_resources
                    logger.info(f"Discovered {len(rds_resources)} RDS instances")
                    
            except Exception as e:
                logger.error(f"Failed to discover RDS resources: {str(e)}")
    
    def __del__(self):
        """Clean up working directory"""
        try:
            if hasattr(self, 'work_dir') and self.work_dir.exists():
                shutil.rmtree(self.work_dir)
                logger.info(f"Cleaned up working directory: {self.work_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean up working directory: {str(e)}")