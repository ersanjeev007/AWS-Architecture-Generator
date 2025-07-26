import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import openai
import boto3
from app.schemas.questionnaire import QuestionnaireRequest
from app.core.enhanced_security_templates import EnhancedSecurityTemplates
import aiohttp
import hashlib

logger = logging.getLogger(__name__)

class SecurityRecommendationType(Enum):
    NEW_FEATURE = "new_feature"
    VULNERABILITY_FIX = "vulnerability_fix"
    COMPLIANCE_UPDATE = "compliance_update"
    BEST_PRACTICE = "best_practice"
    COST_OPTIMIZATION = "cost_optimization"

@dataclass
class SecurityRecommendation:
    id: str
    title: str
    description: str
    recommendation_type: SecurityRecommendationType
    affected_services: List[str]
    priority: str  # "critical", "high", "medium", "low"
    implementation_effort: str  # "low", "medium", "high"
    cost_impact: str  # "none", "low", "medium", "high"
    compliance_frameworks: List[str]
    aws_documentation_url: str
    implementation_steps: List[str]
    terraform_snippet: Optional[str] = None
    cloudformation_snippet: Optional[str] = None
    created_at: datetime = None
    applicable_until: Optional[datetime] = None

@dataclass
class ProjectAnalysis:
    project_id: str
    services_used: List[str]
    security_level: str
    compliance_requirements: List[str]
    last_analyzed: datetime
    security_posture_score: float  # 0-100
    vulnerabilities_count: int
    recommendations_applied: List[str]

class AISecurityAdvisor:
    """AI-powered security advisor for AWS architectures"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key
        if openai_api_key:
            openai.api_key = openai_api_key
        
        # Initialize enhanced security templates
        self.enhanced_security = EnhancedSecurityTemplates()
        
        # AWS Security service announcements and features tracking
        self.aws_security_features_db = {
            "2024": [
                {
                    "service": "aws-waf",
                    "feature": "Bot Control Intelligent Threat Mitigation",
                    "announcement_date": "2024-01-15",
                    "description": "Advanced bot detection using ML to identify and block sophisticated bots",
                    "impact": "Reduces false positives by 90% compared to traditional bot detection",
                    "applicable_services": ["CloudFront", "ALB", "API Gateway"]
                },
                {
                    "service": "amazon-guardduty",
                    "feature": "Runtime Monitoring for ECS and EKS",
                    "announcement_date": "2024-02-20",
                    "description": "Real-time threat detection for containerized workloads",
                    "impact": "Detects container escape attempts and suspicious runtime activities",
                    "applicable_services": ["ECS", "EKS", "Fargate"]
                },
                {
                    "service": "aws-config",
                    "feature": "Security Hub Integration Enhancement",
                    "announcement_date": "2024-03-10",
                    "description": "Improved integration with Security Hub for centralized compliance monitoring",
                    "impact": "Consolidated view of compliance across all AWS services",
                    "applicable_services": ["All AWS Services"]
                },
                {
                    "service": "amazon-inspector",
                    "feature": "Lambda Function Vulnerability Assessment",
                    "announcement_date": "2024-04-05",
                    "description": "Automated vulnerability scanning for Lambda functions and dependencies",
                    "impact": "Identifies vulnerabilities in Lambda code and packages",
                    "applicable_services": ["Lambda"]
                }
            ]
        }
        
        # Security best practices knowledge base
        self.security_knowledge_base = {
            "encryption": {
                "in_transit": {
                    "required_services": ["ALB", "CloudFront", "API Gateway"],
                    "implementation": "Enable HTTPS/TLS 1.2+ encryption",
                    "aws_services": ["Certificate Manager", "CloudFront"]
                },
                "at_rest": {
                    "required_services": ["S3", "RDS", "EBS", "DynamoDB"],
                    "implementation": "Enable encryption using AWS KMS",
                    "aws_services": ["KMS", "CloudHSM"]
                }
            },
            "access_control": {
                "iam": {
                    "principle": "Least privilege access",
                    "implementation": "Use IAM roles and policies with minimal permissions",
                    "aws_services": ["IAM", "STS"]
                },
                "network": {
                    "principle": "Defense in depth",
                    "implementation": "Use VPC, security groups, NACLs, and WAF",
                    "aws_services": ["VPC", "WAF", "Security Groups"]
                }
            },
            "monitoring": {
                "logging": {
                    "required_services": ["All services"],
                    "implementation": "Enable CloudTrail and VPC Flow Logs",
                    "aws_services": ["CloudTrail", "CloudWatch", "VPC Flow Logs"]
                },
                "threat_detection": {
                    "required_services": ["All services"],
                    "implementation": "Enable GuardDuty and Security Hub",
                    "aws_services": ["GuardDuty", "Security Hub", "Inspector"]
                }
            }
        }
        
        # Compliance framework requirements
        self.compliance_requirements = {
            "hipaa": {
                "required_controls": [
                    "encryption_at_rest", "encryption_in_transit", "access_logging",
                    "audit_trails", "data_backup", "access_controls"
                ],
                "recommended_services": [
                    "CloudTrail", "CloudWatch", "KMS", "Secrets Manager", "Config"
                ]
            },
            "pci-dss": {
                "required_controls": [
                    "network_segmentation", "encryption", "access_monitoring",
                    "vulnerability_scanning", "secure_coding"
                ],
                "recommended_services": [
                    "WAF", "GuardDuty", "Inspector", "Security Hub", "KMS"
                ]
            },
            "sox": {
                "required_controls": [
                    "audit_trails", "change_management", "access_controls",
                    "data_integrity", "backup_procedures"
                ],
                "recommended_services": [
                    "CloudTrail", "Config", "Backup", "IAM", "Organizations"
                ]
            }
        }
    
    async def analyze_project_security(self, project_data: Dict, questionnaire: QuestionnaireRequest, services: Dict[str, str]) -> ProjectAnalysis:
        """Analyze a project's current security posture"""
        
        project_id = project_data.get("id", "unknown")
        services_used = list(services.values())
        
        # Determine security level
        security_level = self._determine_security_level(questionnaire)
        
        # Get compliance requirements
        compliance_requirements = getattr(questionnaire, 'compliance_requirements', [])
        if isinstance(compliance_requirements, str):
            compliance_requirements = [compliance_requirements]
        
        # Calculate security posture score
        security_score = await self._calculate_security_score(services_used, security_level, compliance_requirements)
        
        # Count potential vulnerabilities
        vulnerabilities = await self._identify_vulnerabilities(services_used, security_level)
        
        return ProjectAnalysis(
            project_id=project_id,
            services_used=services_used,
            security_level=security_level,
            compliance_requirements=compliance_requirements,
            last_analyzed=datetime.now(),
            security_posture_score=security_score,
            vulnerabilities_count=len(vulnerabilities),
            recommendations_applied=[]
        )
    
    async def get_security_recommendations(self, project_analysis: ProjectAnalysis, include_new_features: bool = True) -> List[SecurityRecommendation]:
        """Generate security recommendations for a project"""
        
        recommendations = []
        
        # Get recommendations based on current security gaps
        gap_recommendations = await self._analyze_security_gaps(project_analysis)
        recommendations.extend(gap_recommendations)
        
        # Get recommendations for new AWS security features
        if include_new_features:
            feature_recommendations = await self._get_new_feature_recommendations(project_analysis)
            recommendations.extend(feature_recommendations)
        
        # Get compliance-specific recommendations
        compliance_recommendations = await self._get_compliance_recommendations(project_analysis)
        recommendations.extend(compliance_recommendations)
        
        # Use AI to generate additional context-aware recommendations
        if self.openai_api_key:
            ai_recommendations = await self._get_ai_recommendations(project_analysis)
            recommendations.extend(ai_recommendations)
        
        # Sort by priority and filter duplicates
        unique_recommendations = self._deduplicate_recommendations(recommendations)
        return sorted(unique_recommendations, key=lambda x: self._priority_score(x.priority), reverse=True)
    
    async def _analyze_security_gaps(self, project_analysis: ProjectAnalysis) -> List[SecurityRecommendation]:
        """Analyze security gaps in the current architecture using enhanced security templates"""
        recommendations = []
        services_used = project_analysis.services_used
        security_level = project_analysis.security_level
        compliance_requirements = project_analysis.compliance_requirements
        
        # Enhanced encryption recommendations using enhanced security templates
        if any(service in ["S3", "RDS", "DynamoDB"] for service in services_used):
            if security_level in ["medium", "high"]:
                enhanced_encryption = self.enhanced_security.generate_enhanced_encryption_configuration(
                    "project", services_used, security_level, compliance_requirements
                )
                
                recommendations.append(SecurityRecommendation(
                    id="enhanced_encryption_at_rest",
                    title="Enable Enhanced Encryption at Rest with Compliance Controls",
                    description="Implement comprehensive encryption at rest with KMS, CloudHSM integration, and compliance-specific controls for data protection",
                    recommendation_type=SecurityRecommendationType.BEST_PRACTICE,
                    affected_services=["S3", "RDS", "DynamoDB", "EBS", "KMS"],
                    priority="critical" if any(req in ["hipaa", "pci-dss", "fedramp"] for req in compliance_requirements) else "high",
                    implementation_effort="medium",
                    cost_impact="low",
                    compliance_frameworks=compliance_requirements or ["HIPAA", "PCI-DSS", "SOX", "GDPR"],
                    aws_documentation_url="https://docs.aws.amazon.com/kms/latest/developerguide/",
                    implementation_steps=[
                        "Create KMS keys with automatic rotation",
                        "Configure CloudHSM for FIPS compliance (if required)",
                        "Enable encryption on all storage services",
                        "Implement envelope encryption for sensitive data",
                        "Set up key usage monitoring and alerting",
                        "Configure cross-region key replication",
                        "Update IAM policies with least privilege access"
                    ],
                    terraform_snippet=enhanced_encryption.get("terraform", ""),
                    cloudformation_snippet=enhanced_encryption.get("cloudformation", "")
                ))
        
        # Enhanced WAF protection recommendations
        if any(service in ["ALB", "CloudFront", "API Gateway"] for service in services_used):
            if security_level in ["medium", "high"]:
                enhanced_waf = self.enhanced_security.generate_enhanced_waf_configuration(
                    "project", security_level
                )
                
                recommendations.append(SecurityRecommendation(
                    id="enhanced_waf_protection",
                    title="Deploy Enhanced AWS WAF with Advanced Threat Protection",
                    description="Implement comprehensive WAF protection with managed rule groups, rate limiting, geo-blocking, and advanced bot detection for maximum security",
                    recommendation_type=SecurityRecommendationType.BEST_PRACTICE,
                    affected_services=["ALB", "CloudFront", "API Gateway"],
                    priority="high",
                    implementation_effort="medium",
                    cost_impact="medium",
                    compliance_frameworks=["PCI-DSS"],
                    aws_documentation_url="https://docs.aws.amazon.com/waf/latest/developerguide/",
                    implementation_steps=[
                        "Create WAF Web ACL",
                        "Configure managed rule groups",
                        "Associate WAF with load balancer/CloudFront",
                        "Set up monitoring and alerting"
                    ]
                ))
        
        # Check for missing monitoring
        if project_analysis.security_posture_score < 80:
            recommendations.append(SecurityRecommendation(
                id="enable_guardduty",
                title="Enable Amazon GuardDuty",
                description="Detect threats and malicious activity using machine learning",
                recommendation_type=SecurityRecommendationType.BEST_PRACTICE,
                affected_services=["All Services"],
                priority="medium",
                implementation_effort="low",
                cost_impact="low",
                compliance_frameworks=["All"],
                aws_documentation_url="https://docs.aws.amazon.com/guardduty/latest/ug/",
                implementation_steps=[
                    "Enable GuardDuty in AWS console",
                    "Configure finding types",
                    "Set up SNS notifications",
                    "Integrate with Security Hub"
                ],
                terraform_snippet=self.enhanced_security.generate_guardduty_configuration("project")
            ))
        
        # Enhanced Security Hub recommendations
        if security_level in ["medium", "high"]:
            recommendations.append(SecurityRecommendation(
                id="enhanced_security_hub",
                title="Deploy AWS Security Hub with Compliance Standards",
                description="Centralize security findings and enable comprehensive compliance monitoring across AWS Foundational, CIS, and PCI DSS standards",
                recommendation_type=SecurityRecommendationType.BEST_PRACTICE,
                affected_services=["All Services"],
                priority="high",
                implementation_effort="low",
                cost_impact="low",
                compliance_frameworks=compliance_requirements or ["AWS Foundational", "CIS", "PCI-DSS"],
                aws_documentation_url="https://docs.aws.amazon.com/securityhub/latest/userguide/",
                implementation_steps=[
                    "Enable Security Hub",
                    "Subscribe to security standards",
                    "Configure automated remediation",
                    "Set up cross-account findings aggregation",
                    "Create custom insights and dashboards"
                ],
                terraform_snippet=self.enhanced_security.generate_security_hub_configuration("project")
            ))
        
        # AWS Config compliance monitoring
        if compliance_requirements and security_level in ["medium", "high"]:
            recommendations.append(SecurityRecommendation(
                id="aws_config_compliance",
                title="Enable AWS Config for Compliance Monitoring",
                description="Deploy AWS Config to continuously monitor resource configurations and ensure compliance with organizational policies",
                recommendation_type=SecurityRecommendationType.COMPLIANCE_UPDATE,
                affected_services=["All Services"],
                priority="high",
                implementation_effort="medium",
                cost_impact="medium",
                compliance_frameworks=compliance_requirements,
                aws_documentation_url="https://docs.aws.amazon.com/config/latest/developerguide/",
                implementation_steps=[
                    "Create S3 bucket for Config delivery",
                    "Set up Config recorder and delivery channel",
                    "Enable compliance-specific Config rules",
                    "Configure automated remediation actions",
                    "Set up compliance reporting"
                ],
                terraform_snippet=self.enhanced_security.generate_config_configuration("project")
            ))
        
        # Macie for data protection
        if any(service in ["S3"] for service in services_used) and security_level == "high":
            recommendations.append(SecurityRecommendation(
                id="amazon_macie_data_protection",
                title="Deploy Amazon Macie for Data Discovery and Protection",
                description="Use Macie to automatically discover, classify, and protect sensitive data in S3 buckets with machine learning-powered data security",
                recommendation_type=SecurityRecommendationType.BEST_PRACTICE,
                affected_services=["S3"],
                priority="high",
                implementation_effort="medium",
                cost_impact="medium",
                compliance_frameworks=["GDPR", "HIPAA", "PCI-DSS"],
                aws_documentation_url="https://docs.aws.amazon.com/macie/latest/user/",
                implementation_steps=[
                    "Enable Macie service",
                    "Configure S3 bucket scanning",
                    "Set up sensitive data discovery jobs",
                    "Configure finding notifications",
                    "Create data classification policies"
                ],
                terraform_snippet=self.enhanced_security.generate_macie_configuration("project")
            ))
        
        # Inspector for vulnerability assessments
        if any(service in ["EC2", "ECS", "Lambda"] for service in services_used):
            recommendations.append(SecurityRecommendation(
                id="amazon_inspector_vulnerability_assessment",
                title="Enable Amazon Inspector for Continuous Vulnerability Assessment",
                description="Deploy Inspector to automatically assess EC2 instances and container images for vulnerabilities and security best practices",
                recommendation_type=SecurityRecommendationType.BEST_PRACTICE,
                affected_services=["EC2", "ECS", "ECR", "Lambda"],
                priority="high",
                implementation_effort="low",
                cost_impact="low",
                compliance_frameworks=["All"],
                aws_documentation_url="https://docs.aws.amazon.com/inspector/latest/user/",
                implementation_steps=[
                    "Enable Inspector service",
                    "Configure assessment targets",
                    "Set up automated scanning schedules",
                    "Configure finding notifications",
                    "Integrate with CI/CD pipeline"
                ],
                terraform_snippet=self.enhanced_security.generate_inspector_configuration("project")
            ))
        
        # CloudHSM for FIPS compliance
        if any(req in ["fedramp", "fips"] for req in compliance_requirements) and security_level == "high":
            recommendations.append(SecurityRecommendation(
                id="cloudhsm_fips_compliance",
                title="Deploy AWS CloudHSM for FIPS 140-2 Level 3 Compliance",
                description="Implement CloudHSM to meet FIPS 140-2 Level 3 compliance requirements for cryptographic operations",
                recommendation_type=SecurityRecommendationType.COMPLIANCE_UPDATE,
                affected_services=["KMS", "CloudHSM"],
                priority="critical",
                implementation_effort="high",
                cost_impact="high",
                compliance_frameworks=["FedRAMP", "FIPS 140-2"],
                aws_documentation_url="https://docs.aws.amazon.com/cloudhsm/latest/userguide/",
                implementation_steps=[
                    "Design CloudHSM cluster architecture",
                    "Create CloudHSM cluster and HSMs",
                    "Configure high availability setup",
                    "Initialize and configure HSM users",
                    "Integrate with applications and KMS",
                    "Set up monitoring and backup procedures"
                ],
                terraform_snippet=self.enhanced_security.generate_cloudhsm_configuration("project")
            ))
        
        # Enhanced Security Groups and NACLs
        recommendations.append(SecurityRecommendation(
            id="enhanced_network_security",
            title="Implement Enhanced Security Groups and Network ACLs",
            description="Deploy defense-in-depth network security with enhanced security groups using zero-trust principles and network ACLs for additional protection layers",
            recommendation_type=SecurityRecommendationType.BEST_PRACTICE,
            affected_services=["VPC", "EC2", "RDS", "ELB"],
            priority="high",
            implementation_effort="medium",
            cost_impact="none",
            compliance_frameworks=["All"],
            aws_documentation_url="https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Security.html",
            implementation_steps=[
                "Review current security group rules",
                "Implement least privilege access",
                "Add network ACL layers",
                "Configure logging and monitoring",
                "Set up automated rule management"
            ],
            terraform_snippet=self.enhanced_security.generate_enhanced_security_groups("project", dict(services), security_level)
        ))
        
        return recommendations
    
    async def _get_new_feature_recommendations(self, project_analysis: ProjectAnalysis) -> List[SecurityRecommendation]:
        """Get recommendations for new AWS security features"""
        recommendations = []
        services_used = project_analysis.services_used
        
        # Check AWS security features database for relevant new features
        current_year = datetime.now().year
        for year_features in self.aws_security_features_db.get(str(current_year), []):
            applicable_services = year_features.get("applicable_services", [])
            
            # Check if any of the project's services can benefit from this feature
            if (any(service in services_used for service in applicable_services) or 
                "All AWS Services" in applicable_services):
                
                feature_id = hashlib.md5(f"{year_features['service']}_{year_features['feature']}".encode()).hexdigest()[:8]
                
                recommendations.append(SecurityRecommendation(
                    id=f"new_feature_{feature_id}",
                    title=f"Adopt {year_features['feature']}",
                    description=f"{year_features['description']} - {year_features['impact']}",
                    recommendation_type=SecurityRecommendationType.NEW_FEATURE,
                    affected_services=applicable_services,
                    priority="medium",
                    implementation_effort="medium",
                    cost_impact="low",
                    compliance_frameworks=["All"],
                    aws_documentation_url=f"https://docs.aws.amazon.com/{year_features['service']}/",
                    implementation_steps=[
                        f"Review {year_features['feature']} documentation",
                        "Assess compatibility with current architecture",
                        "Plan implementation and testing",
                        "Deploy and monitor new feature"
                    ],
                    created_at=datetime.strptime(year_features['announcement_date'], "%Y-%m-%d")
                ))
        
        return recommendations
    
    async def _get_compliance_recommendations(self, project_analysis: ProjectAnalysis) -> List[SecurityRecommendation]:
        """Get compliance-specific recommendations"""
        recommendations = []
        
        for compliance_framework in project_analysis.compliance_requirements:
            framework = compliance_framework.lower()
            if framework in self.compliance_requirements:
                
                required_controls = self.compliance_requirements[framework]["required_controls"]
                recommended_services = self.compliance_requirements[framework]["recommended_services"]
                
                # Check if recommended services are missing
                missing_services = [service for service in recommended_services 
                                  if service not in project_analysis.services_used]
                
                if missing_services:
                    recommendations.append(SecurityRecommendation(
                        id=f"compliance_{framework}_services",
                        title=f"Add {framework.upper()} Required Services",
                        description=f"Implement missing services required for {framework.upper()} compliance",
                        recommendation_type=SecurityRecommendationType.COMPLIANCE_UPDATE,
                        affected_services=missing_services,
                        priority="high",
                        implementation_effort="high",
                        cost_impact="medium",
                        compliance_frameworks=[framework.upper()],
                        aws_documentation_url=f"https://aws.amazon.com/compliance/{framework}/",
                        implementation_steps=[
                            f"Review {framework.upper()} requirements",
                            "Implement missing security controls",
                            "Configure compliance monitoring",
                            "Document compliance measures"
                        ]
                    ))
        
        return recommendations
    
    async def _get_ai_recommendations(self, project_analysis: ProjectAnalysis) -> List[SecurityRecommendation]:
        """Use AI to generate contextual security recommendations"""
        if not self.openai_api_key:
            return []
        
        try:
            # Prepare context for AI
            context = {
                "services": project_analysis.services_used,
                "security_level": project_analysis.security_level,
                "compliance": project_analysis.compliance_requirements,
                "security_score": project_analysis.security_posture_score,
                "vulnerabilities": project_analysis.vulnerabilities_count
            }
            
            prompt = f"""
            As an AWS security expert, analyze this architecture and provide specific security recommendations:
            
            Architecture Context:
            - Services used: {', '.join(context['services'])}
            - Security level: {context['security_level']}
            - Compliance requirements: {', '.join(context['compliance'])}
            - Current security score: {context['security_score']}/100
            - Vulnerabilities identified: {context['vulnerabilities']}
            
            Please provide 2-3 specific, actionable security recommendations that:
            1. Address the most critical security gaps
            2. Consider the specific AWS services in use
            3. Are appropriate for the stated compliance requirements
            4. Include implementation complexity assessment
            
            Format each recommendation as:
            Title: [Clear, specific title]
            Priority: [critical/high/medium/low]
            Description: [Detailed explanation]
            Implementation: [Specific steps]
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_text = response.choices[0].message.content
            
            # Parse AI response into recommendations
            ai_recommendations = self._parse_ai_recommendations(ai_text, project_analysis)
            return ai_recommendations
            
        except Exception as e:
            logger.error(f"Error getting AI recommendations: {e}")
            return []
    
    def _parse_ai_recommendations(self, ai_text: str, project_analysis: ProjectAnalysis) -> List[SecurityRecommendation]:
        """Parse AI-generated recommendations into structured format"""
        recommendations = []
        
        # Simple parsing logic (could be enhanced with more sophisticated NLP)
        sections = ai_text.split("Title:")
        
        for i, section in enumerate(sections[1:], 1):  # Skip first empty section
            try:
                lines = section.strip().split("\n")
                title = lines[0].strip()
                
                priority = "medium"
                description = ""
                implementation_steps = []
                
                for line in lines[1:]:
                    line = line.strip()
                    if line.startswith("Priority:"):
                        priority = line.split(":", 1)[1].strip().lower()
                    elif line.startswith("Description:"):
                        description = line.split(":", 1)[1].strip()
                    elif line.startswith("Implementation:"):
                        implementation_steps.append(line.split(":", 1)[1].strip())
                    elif line and not any(line.startswith(prefix) for prefix in ["Title:", "Priority:", "Description:", "Implementation:"]):
                        if description:
                            description += " " + line
                        else:
                            implementation_steps.append(line)
                
                if title and description:
                    recommendations.append(SecurityRecommendation(
                        id=f"ai_rec_{i}",
                        title=title,
                        description=description,
                        recommendation_type=SecurityRecommendationType.BEST_PRACTICE,
                        affected_services=project_analysis.services_used,
                        priority=priority if priority in ["critical", "high", "medium", "low"] else "medium",
                        implementation_effort="medium",
                        cost_impact="low",
                        compliance_frameworks=project_analysis.compliance_requirements,
                        aws_documentation_url="https://docs.aws.amazon.com/security/",
                        implementation_steps=implementation_steps if implementation_steps else ["Review recommendation", "Plan implementation", "Execute changes", "Monitor results"],
                        created_at=datetime.now()
                    ))
            except Exception as e:
                logger.warning(f"Error parsing AI recommendation {i}: {e}")
                continue
        
        return recommendations
    
    def _determine_security_level(self, questionnaire: QuestionnaireRequest) -> str:
        """Determine security level based on questionnaire"""
        compliance = getattr(questionnaire, 'compliance_requirements', [])
        data_sensitivity = getattr(questionnaire, 'data_sensitivity', '').lower()
        
        if any(req in ['hipaa', 'pci-dss', 'sox'] for req in compliance) or 'high' in data_sensitivity:
            return "high"
        elif 'medium' in data_sensitivity or len(compliance) > 0:
            return "medium"
        else:
            return "basic"
    
    async def _calculate_security_score(self, services_used: List[str], security_level: str, compliance_requirements: List[str]) -> float:
        """Calculate security posture score (0-100)"""
        base_score = 50  # Starting baseline
        
        # Add points for security services
        security_services = ["WAF", "GuardDuty", "Security Hub", "Config", "CloudTrail", "KMS"]
        security_services_used = [s for s in services_used if s in security_services]
        service_score = len(security_services_used) * 8  # 8 points per security service
        
        # Add points based on security level
        level_score = {"basic": 10, "medium": 25, "high": 40}.get(security_level, 10)
        
        # Add points for compliance frameworks
        compliance_score = len(compliance_requirements) * 5
        
        # Deduct points for missing critical services
        critical_missing = 0
        if security_level == "high":
            required_services = ["CloudTrail", "KMS", "WAF"]
            critical_missing = len([s for s in required_services if s not in services_used]) * 10
        
        final_score = min(100, base_score + service_score + level_score + compliance_score - critical_missing)
        return max(0, final_score)
    
    async def _identify_vulnerabilities(self, services_used: List[str], security_level: str) -> List[Dict]:
        """Identify potential vulnerabilities in the architecture"""
        vulnerabilities = []
        
        # Check for common misconfigurations
        if "S3" in services_used and security_level != "high":
            vulnerabilities.append({
                "type": "misconfiguration",
                "service": "S3",
                "description": "S3 bucket may not have encryption enabled",
                "severity": "medium"
            })
        
        if "RDS" in services_used and security_level == "basic":
            vulnerabilities.append({
                "type": "misconfiguration",
                "service": "RDS",
                "description": "Database encryption not enabled",
                "severity": "high"
            })
        
        if "ALB" in services_used and "WAF" not in services_used:
            vulnerabilities.append({
                "type": "missing_protection",
                "service": "ALB",
                "description": "Application Load Balancer not protected by WAF",
                "severity": "medium"
            })
        
        return vulnerabilities
    
    def _deduplicate_recommendations(self, recommendations: List[SecurityRecommendation]) -> List[SecurityRecommendation]:
        """Remove duplicate recommendations"""
        seen_ids = set()
        unique_recommendations = []
        
        for rec in recommendations:
            if rec.id not in seen_ids:
                seen_ids.add(rec.id)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def _priority_score(self, priority: str) -> int:
        """Convert priority to numeric score for sorting"""
        return {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(priority, 1)
    
    async def monitor_aws_security_updates(self) -> List[Dict]:
        """Monitor AWS security updates and new features"""
        try:
            # This would integrate with AWS RSS feeds, blogs, or security bulletins
            # For now, return simulated updates
            updates = [
                {
                    "title": "New AWS Config Managed Rules for Container Security",
                    "date": "2024-12-01",
                    "description": "New managed rules for ECS and EKS security compliance",
                    "impact": "Enhanced container security monitoring",
                    "services": ["ECS", "EKS", "Fargate"]
                },
                {
                    "title": "Enhanced GuardDuty Machine Learning Models",
                    "date": "2024-11-15", 
                    "description": "Improved threat detection accuracy for suspicious activities",
                    "impact": "Reduced false positives by 30%",
                    "services": ["GuardDuty"]
                }
            ]
            
            return updates
            
        except Exception as e:
            logger.error(f"Error monitoring AWS security updates: {e}")
            return []
    
    def get_recommendation_implementation_plan(self, recommendation: SecurityRecommendation, project_analysis: ProjectAnalysis) -> Dict:
        """Generate detailed implementation plan for a recommendation"""
        
        # Estimate implementation timeline
        effort_timeline = {
            "low": "1-2 days",
            "medium": "1-2 weeks", 
            "high": "2-4 weeks"
        }
        
        # Estimate cost impact
        cost_estimates = {
            "none": "$0",
            "low": "$10-50/month",
            "medium": "$50-200/month",
            "high": "$200+/month"
        }
        
        return {
            "recommendation_id": recommendation.id,
            "implementation_timeline": effort_timeline.get(recommendation.implementation_effort, "Unknown"),
            "estimated_cost": cost_estimates.get(recommendation.cost_impact, "Unknown"),
            "prerequisites": self._get_prerequisites(recommendation, project_analysis),
            "testing_plan": self._get_testing_plan(recommendation),
            "rollback_plan": self._get_rollback_plan(recommendation),
            "success_metrics": self._get_success_metrics(recommendation)
        }
    
    def _get_prerequisites(self, recommendation: SecurityRecommendation, project_analysis: ProjectAnalysis) -> List[str]:
        """Get prerequisites for implementing a recommendation"""
        prerequisites = []
        
        if "KMS" in recommendation.title or "encryption" in recommendation.description.lower():
            prerequisites.extend([
                "IAM permissions for KMS operations",
                "Key management policy defined",
                "Backup plan for existing data"
            ])
        
        if "WAF" in recommendation.title:
            prerequisites.extend([
                "Application Load Balancer deployed",
                "Understanding of application traffic patterns",
                "Monitoring and alerting setup"
            ])
        
        return prerequisites
    
    def _get_testing_plan(self, recommendation: SecurityRecommendation) -> List[str]:
        """Get testing plan for a recommendation"""
        return [
            "Deploy changes in development environment",
            "Conduct security testing and validation",
            "Performance impact assessment",
            "User acceptance testing if applicable",
            "Gradual rollout to production"
        ]
    
    def _get_rollback_plan(self, recommendation: SecurityRecommendation) -> List[str]:
        """Get rollback plan for a recommendation"""
        return [
            "Document current configuration",
            "Create infrastructure snapshots/backups",
            "Define rollback triggers and criteria",
            "Test rollback procedures in development",
            "Prepare emergency rollback scripts"
        ]
    
    def _get_success_metrics(self, recommendation: SecurityRecommendation) -> List[str]:
        """Get success metrics for a recommendation"""
        metrics = [
            "Improved security posture score",
            "Reduced vulnerability count",
            "Compliance status improvement"
        ]
        
        if recommendation.recommendation_type == SecurityRecommendationType.NEW_FEATURE:
            metrics.append("Feature adoption and usage metrics")
        
        return metrics