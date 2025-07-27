import uuid
from typing import Dict, List
from app.schemas.questionnaire import QuestionnaireRequest
from app.schemas.architecture import ArchitectureResponse, DiagramData, CostBreakdown
from app.core.aws_services import AWSServicesConfig
from app.core.cost_calculator import CostCalculator
from app.core.diagram_generator import DiagramGenerator
from app.core.template_generator import TemplateGenerator

class ArchitectureGenerator:
    """Main class for generating AWS architectures"""
    
    def __init__(self):
        self.aws_services = AWSServicesConfig()
        self.cost_calculator = CostCalculator()
        self.diagram_generator = DiagramGenerator()
        self.template_generator = TemplateGenerator()
    
    def generate(self, questionnaire: QuestionnaireRequest, user_preferences: Dict = None) -> ArchitectureResponse:
        """Generate complete AWS architecture from questionnaire with user preferences"""
        
        architecture_id = str(uuid.uuid4())
        
        # Select services
        selected_services = self._select_services(questionnaire)
        
        # Generate security features
        security_features = self._generate_security_features(questionnaire)
        
        # Calculate costs
        cost_estimate, cost_breakdown = self._calculate_costs(questionnaire, selected_services)
        
        # Generate diagram
        diagram_data = self._generate_diagram(selected_services, questionnaire)
        
        # Generate templates
        terraform_template = self._generate_terraform(questionnaire, selected_services)
        cloudformation_template = self._generate_cloudformation(questionnaire, selected_services)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(questionnaire, selected_services)
        
        return ArchitectureResponse(
            id=architecture_id,
            project_name=questionnaire.project_name,
            services=selected_services,
            security_features=security_features,
            estimated_cost=cost_estimate,
            cost_breakdown=cost_breakdown,
            diagram_data=diagram_data,
            terraform_template=terraform_template,
            cloudformation_template=cloudformation_template,
            recommendations=recommendations
        )
    
    def generate_architecture(self, questionnaire: QuestionnaireRequest, user_preferences: Dict = None) -> Dict:
        """Generate architecture data as dictionary for storage"""
        response = self.generate(questionnaire, user_preferences)
        return {
            "id": response.id,
            "project_name": response.project_name,
            "services": response.services,
            "security_features": response.security_features,
            "estimated_cost": response.estimated_cost,
            "cost_breakdown": [item.model_dump() if hasattr(item, 'model_dump') else item for item in response.cost_breakdown],
            "diagram_data": response.diagram_data.model_dump() if hasattr(response.diagram_data, 'model_dump') else response.diagram_data,
            "terraform_template": response.terraform_template,
            "cloudformation_template": response.cloudformation_template,
            "recommendations": response.recommendations,
            "user_preferences": user_preferences or {}
        }
    
    def _select_services(self, questionnaire: QuestionnaireRequest) -> Dict[str, str]:
        """Select appropriate AWS services based on requirements and user preferences"""
        
        # If user has provided specific service selections, use those preferentially
        if questionnaire.services:
            return self._process_user_selected_services(questionnaire.services, questionnaire)
        
        # Use default selection logic
        services = {}
        
        # Get string values (handle both enum and string inputs), with defaults for None values
        compute_pref = self._get_preference_value(questionnaire.compute_preference, "serverless")
        database_type = self._get_preference_value(questionnaire.database_type, "nosql")
        storage_needs = self._get_preference_value(questionnaire.storage_needs, "moderate")
        traffic_volume = self._get_preference_value(questionnaire.traffic_volume, "medium")
        geographical_reach = self._get_preference_value(questionnaire.geographical_reach, "single_region")
        
        # Compute services
        if compute_pref == "serverless":
            services["compute"] = "AWS Lambda"
        elif compute_pref == "containers":
            services["compute"] = "Amazon ECS/Fargate"
        else:  # vms
            services["compute"] = "Amazon EC2"
        
        # Database services
        if database_type != "none":
            if database_type == "sql":
                services["database"] = "Amazon RDS"
            else:  # nosql
                services["database"] = "Amazon DynamoDB"
        
        # Storage services
        if storage_needs == "minimal":
            services["storage"] = "Amazon S3"
        elif storage_needs == "moderate":
            services["storage"] = "Amazon S3"
        else:  # extensive
            services["storage"] = "Amazon S3 + EFS"
        
        # Networking services
        if traffic_volume in ["medium", "high"]:
            services["load_balancer"] = "Application Load Balancer"
        
        if geographical_reach in ["multi_region", "global"]:
            services["cdn"] = "Amazon CloudFront"
            services["dns"] = "Amazon Route 53"
        
        # Monitoring
        services["monitoring"] = "Amazon CloudWatch"
        
        return services
    
    def _process_user_selected_services(self, user_services: Dict[str, List[str]], questionnaire: QuestionnaireRequest) -> Dict[str, str]:
        """Process user-selected services and convert to the expected format"""
        services = {}
        
        # Map service categories to primary services
        service_mapping = {
            'compute': {
                'Lambda': 'AWS Lambda',
                'EC2': 'Amazon EC2', 
                'ECS': 'Amazon ECS/Fargate',
                'Fargate': 'Amazon ECS/Fargate',
                'Batch': 'AWS Batch',
                'SageMaker': 'Amazon SageMaker'
            },
            'database': {
                'DynamoDB': 'Amazon DynamoDB',
                'RDS': 'Amazon RDS',
                'Aurora': 'Amazon Aurora',
                'ElastiCache': 'Amazon ElastiCache',
                'Redshift': 'Amazon Redshift',
                'DocumentDB': 'Amazon DocumentDB',
                'Neptune': 'Amazon Neptune'
            },
            'storage': {
                'S3': 'Amazon S3',
                'EBS': 'Amazon EBS',
                'EFS': 'Amazon EFS',
                'FSx': 'Amazon FSx',
                'Data Lake': 'AWS Data Lake'
            },
            'networking': {
                'VPC': 'Amazon VPC',
                'CloudFront': 'Amazon CloudFront',
                'Route 53': 'Amazon Route 53',
                'API Gateway': 'Amazon API Gateway',
                'Load Balancer': 'Application Load Balancer',
                'ALB': 'Application Load Balancer',
                'NLB': 'Network Load Balancer'
            },
            'security': {
                'IAM': 'AWS IAM',
                'KMS': 'AWS KMS',
                'WAF': 'AWS WAF',
                'GuardDuty': 'Amazon GuardDuty',
                'Security Hub': 'AWS Security Hub',
                'Certificate Manager': 'AWS Certificate Manager'
            },
            'monitoring': {
                'CloudWatch': 'Amazon CloudWatch',
                'CloudTrail': 'AWS CloudTrail',
                'X-Ray': 'AWS X-Ray'
            }
        }
        
        # Process each category of user-selected services
        for category, selected_services in user_services.items():
            if selected_services and len(selected_services) > 0:
                # Use the first selected service as primary
                primary_service = selected_services[0]
                
                # Map to AWS service name if mapping exists
                if category in service_mapping and primary_service in service_mapping[category]:
                    services[category] = service_mapping[category][primary_service]
                else:
                    # Use the service name directly if no mapping found
                    services[category] = primary_service
        
        # Ensure essential services are included if not specified - fall back to questionnaire preferences
        if 'compute' not in services:
            compute_pref = self._get_preference_value(questionnaire.compute_preference, "serverless")
            if compute_pref == "serverless":
                services["compute"] = "AWS Lambda"
            elif compute_pref == "containers":
                services["compute"] = "Amazon ECS/Fargate"
            else:  # vms
                services["compute"] = "Amazon EC2"
        
        if 'database' not in services:
            database_type = self._get_preference_value(questionnaire.database_type, "nosql")
            if database_type != "none":
                if database_type == "sql":
                    services["database"] = "Amazon RDS"
                else:  # nosql
                    services["database"] = "Amazon DynamoDB"
        
        if 'storage' not in services:
            storage_needs = self._get_preference_value(questionnaire.storage_needs, "moderate")
            if storage_needs == "minimal":
                services["storage"] = "Amazon S3"
            elif storage_needs == "moderate":
                services["storage"] = "Amazon S3"
            else:  # extensive
                services["storage"] = "Amazon S3 + EFS"
        
        if 'monitoring' not in services:
            services['monitoring'] = 'Amazon CloudWatch'
            
        # Add networking services based on traffic volume if not specified
        traffic_volume = self._get_preference_value(questionnaire.traffic_volume, "medium")
        geographical_reach = self._get_preference_value(questionnaire.geographical_reach, "single_region")
        
        if 'load_balancer' not in services and traffic_volume in ["medium", "high"]:
            services["load_balancer"] = "Application Load Balancer"
        
        if 'cdn' not in services and geographical_reach in ["multi_region", "global"]:
            services["cdn"] = "Amazon CloudFront"
            
        if 'dns' not in services and geographical_reach in ["multi_region", "global"]:
            services["dns"] = "Amazon Route 53"
        
        return services
    
    def _get_preference_value(self, preference, default_value: str) -> str:
        """Get preference value with fallback to default if None or missing"""
        if preference is None:
            return default_value
        
        if isinstance(preference, str):
            return preference
        else:
            # Handle enum values
            return preference.value if hasattr(preference, 'value') else default_value
    
    def _generate_security_features(self, questionnaire: QuestionnaireRequest) -> List[str]:
        """Generate security features based on requirements"""
        security_features = [
            "VPC with private subnets",
            "Security Groups", 
            "IAM roles and policies",
            "CloudTrail logging",
            "S3 bucket encryption",
            "S3 public access block"
        ]
        
        # Get string value for data sensitivity
        data_sensitivity = questionnaire.data_sensitivity if isinstance(questionnaire.data_sensitivity, str) else questionnaire.data_sensitivity.value
        
        if data_sensitivity == "confidential":
            security_features.extend([
                "Amazon GuardDuty",
                "AWS Config", 
                "AWS Security Hub",
                "VPC Flow Logs"
            ])
        
        security_features.append("Amazon Macie for S3 monitoring")
        
        # Handle compliance requirements
        compliance_reqs = []
        if questionnaire.compliance_requirements:
            for req in questionnaire.compliance_requirements:
                req_value = req if isinstance(req, str) else req.value
                if req_value != "none":
                    compliance_reqs.append(req_value)
        # If no compliance requirements or only "none" selected, compliance_reqs will be empty
        
        # Add compliance-specific security
        if "hipaa" in compliance_reqs:
            security_features.extend(["AWS KMS", "CloudHSM"])
        if "pci" in compliance_reqs:
            security_features.extend(["AWS Inspector", "Certificate Manager", "WAF"])
        
        return list(set(security_features))  # Remove duplicates
    
    def _calculate_costs(self, questionnaire: QuestionnaireRequest, services: Dict[str, str]):
        """Calculate costs using the cost calculator"""
        return self.cost_calculator.calculate_costs(questionnaire, services)
    
    def _generate_diagram(self, services: Dict[str, str], questionnaire: QuestionnaireRequest) -> DiagramData:
        """Generate diagram using the diagram generator"""
        return self.diagram_generator.generate_diagram(services, questionnaire)
    
    def _generate_terraform(self, questionnaire: QuestionnaireRequest, services: Dict[str, str]) -> str:
        """Generate Terraform template"""
        return self.template_generator.generate_terraform_template(questionnaire, services)
    
    def _generate_cloudformation(self, questionnaire: QuestionnaireRequest, services: Dict[str, str]) -> str:
        """Generate CloudFormation template"""
        return self.template_generator.generate_cloudformation_template(questionnaire, services)
    
    def _generate_recommendations(self, questionnaire: QuestionnaireRequest, services: Dict[str, str]) -> List[str]:
        """Generate architecture recommendations"""
        recommendations = []
        
        # Get string values
        traffic_volume = questionnaire.traffic_volume if isinstance(questionnaire.traffic_volume, str) else questionnaire.traffic_volume.value
        data_sensitivity = questionnaire.data_sensitivity if isinstance(questionnaire.data_sensitivity, str) else questionnaire.data_sensitivity.value
        budget_range = questionnaire.budget_range if isinstance(questionnaire.budget_range, str) else questionnaire.budget_range.value
        database_type = questionnaire.database_type if isinstance(questionnaire.database_type, str) else questionnaire.database_type.value
        geographical_reach = questionnaire.geographical_reach if isinstance(questionnaire.geographical_reach, str) else questionnaire.geographical_reach.value
        
        if traffic_volume == "high":
            recommendations.extend([
                "Consider implementing auto-scaling for your compute resources",
                "Set up CloudWatch monitoring and alerting for performance metrics"
            ])
        
        if data_sensitivity == "confidential":
            recommendations.extend([
                "Implement encryption for all data at rest and in transit",
                "Set up AWS GuardDuty for threat detection"
            ])
        
        if budget_range == "startup":
            recommendations.extend([
                "Use AWS Cost Explorer to monitor and optimize spending",
                "Consider Reserved Instances for predictable workloads"
            ])
        
        if database_type == "sql":
            recommendations.append("Consider using RDS Multi-AZ for high availability")
        elif database_type == "nosql":
            recommendations.append("Configure DynamoDB on-demand billing for variable workloads")
        
        if geographical_reach == "global":
            recommendations.extend([
                "Implement CloudFront for global content delivery",
                "Consider multi-region deployment for disaster recovery"
            ])
        
        return recommendations