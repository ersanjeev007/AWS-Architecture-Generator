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
        """Select appropriate AWS services based on requirements"""
        services = {}
        
        # Get string values (handle both enum and string inputs)
        compute_pref = questionnaire.compute_preference if isinstance(questionnaire.compute_preference, str) else questionnaire.compute_preference.value
        database_type = questionnaire.database_type if isinstance(questionnaire.database_type, str) else questionnaire.database_type.value
        storage_needs = questionnaire.storage_needs if isinstance(questionnaire.storage_needs, str) else questionnaire.storage_needs.value
        traffic_volume = questionnaire.traffic_volume if isinstance(questionnaire.traffic_volume, str) else questionnaire.traffic_volume.value
        geographical_reach = questionnaire.geographical_reach if isinstance(questionnaire.geographical_reach, str) else questionnaire.geographical_reach.value
        
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
        for req in questionnaire.compliance_requirements:
            req_value = req if isinstance(req, str) else req.value
            if req_value != "none":
                compliance_reqs.append(req_value)
        
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