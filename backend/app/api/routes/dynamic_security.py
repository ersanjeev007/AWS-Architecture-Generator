from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from app.core.dynamic_security_analyzer import DynamicSecurityAnalyzer
from app.schemas.questionnaire import QuestionnaireRequest

logger = logging.getLogger(__name__)
router = APIRouter()

# Global analyzer instance - would be better with dependency injection
security_analyzer = None

def get_security_analyzer(aws_credentials: Optional[Dict[str, str]] = None) -> DynamicSecurityAnalyzer:
    """Get or create security analyzer instance"""
    global security_analyzer
    if security_analyzer is None:
        security_analyzer = DynamicSecurityAnalyzer(aws_credentials=aws_credentials)
    return security_analyzer

@router.post("/analyze-project-security")
async def analyze_project_security(
    project_data: Dict[str, Any],
    questionnaire: QuestionnaireRequest,
    services: Dict[str, str],
    aws_credentials: Optional[Dict[str, str]] = None
):
    """
    Perform comprehensive dynamic security analysis for a project
    """
    try:
        analyzer = get_security_analyzer(aws_credentials)
        result = await analyzer.analyze_project_security(project_data, questionnaire, services)
        
        return {
            "status": "success",
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in security analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Security analysis failed: {str(e)}")

@router.get("/real-time-status/{project_id}")
async def get_real_time_security_status(project_id: str):
    """
    Get real-time security status for a project
    """
    try:
        analyzer = get_security_analyzer()
        status = await analyzer.get_real_time_security_status(project_id)
        
        return {
            "status": "success",
            "security_status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting real-time security status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get security status: {str(e)}")

@router.get("/security-metrics/{project_id}")
async def get_security_metrics(project_id: str):
    """
    Get security metrics for a project
    """
    try:
        # This would typically fetch from a database or cache
        # For now, return mock metrics
        metrics = {
            "project_id": project_id,
            "overall_score": 85.2,
            "threat_count": 3,
            "critical_threats": 0,
            "high_threats": 1,
            "compliance_score": 78.5,
            "encrypted_resources": 8,
            "total_resources": 10,
            "iam_users": 5,
            "iam_roles": 12,
            "security_groups": 6,
            "open_ports": 2,
            "last_scan": datetime.now().isoformat(),
            "trends": {
                "score_trend": "improving",
                "threat_trend": "stable",
                "compliance_trend": "improving"
            }
        }
        
        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting security metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get security metrics: {str(e)}")

@router.get("/compliance-status/{project_id}")
async def get_compliance_status(project_id: str, framework: Optional[str] = None):
    """
    Get compliance status for specific framework or all frameworks
    """
    try:
        # Mock compliance data - would come from dynamic analyzer
        frameworks = {
            "SOC2": {
                "status": "partial",
                "score": 78.5,
                "total_controls": 6,
                "passed_controls": 4,
                "failed_controls": 2,
                "last_assessed": datetime.now().isoformat()
            },
            "PCI-DSS": {
                "status": "non_compliant",
                "score": 45.2,
                "total_controls": 8,
                "passed_controls": 3,
                "failed_controls": 5,
                "last_assessed": datetime.now().isoformat()
            },
            "HIPAA": {
                "status": "partial",
                "score": 65.8,
                "total_controls": 5,
                "passed_controls": 3,
                "failed_controls": 2,
                "last_assessed": datetime.now().isoformat()
            },
            "GDPR": {
                "status": "compliant",
                "score": 88.9,
                "total_controls": 5,
                "passed_controls": 4,
                "failed_controls": 1,
                "last_assessed": datetime.now().isoformat()
            },
            "NIST": {
                "status": "partial",
                "score": 72.1,
                "total_controls": 5,
                "passed_controls": 3,
                "failed_controls": 2,
                "last_assessed": datetime.now().isoformat()
            }
        }
        
        if framework:
            if framework.upper() in frameworks:
                result = frameworks[framework.upper()]
            else:
                raise HTTPException(status_code=404, detail=f"Framework {framework} not found")
        else:
            result = frameworks
        
        return {
            "status": "success",
            "project_id": project_id,
            "compliance": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting compliance status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get compliance status: {str(e)}")

@router.get("/threat-intelligence/{project_id}")
async def get_threat_intelligence(project_id: str, severity: Optional[str] = None):
    """
    Get threat intelligence for a project
    """
    try:
        # Mock threat intelligence data
        threats = [
            {
                "id": "threat_001",
                "title": "S3 Bucket Potentially Public",
                "description": "S3 bucket may allow public access",
                "severity": "high",
                "service": "S3",
                "category": "Data Exposure",
                "detected_at": datetime.now().isoformat(),
                "status": "active",
                "cvss_score": 7.5,
                "remediation_steps": [
                    "Enable S3 Block Public Access",
                    "Review bucket policies",
                    "Implement least privilege access"
                ]
            },
            {
                "id": "threat_002",
                "title": "Security Group Allows World Access",
                "description": "Security group allows access from 0.0.0.0/0 on port 22",
                "severity": "high",
                "service": "EC2",
                "category": "Network Security",
                "detected_at": datetime.now().isoformat(),
                "status": "active",
                "cvss_score": 8.1,
                "remediation_steps": [
                    "Restrict security group rules to specific IP ranges",
                    "Use bastion hosts for administrative access",
                    "Implement least privilege network access"
                ]
            },
            {
                "id": "threat_003",
                "title": "RDS Instance Not Encrypted",
                "description": "RDS instance is not encrypted at rest",
                "severity": "medium",
                "service": "RDS",
                "category": "Encryption",
                "detected_at": datetime.now().isoformat(),
                "status": "active",
                "cvss_score": 5.3,
                "remediation_steps": [
                    "Enable encryption at rest",
                    "Use AWS KMS for key management",
                    "Enable automated backups with encryption"
                ]
            }
        ]
        
        # Filter by severity if provided
        if severity:
            threats = [t for t in threats if t["severity"].lower() == severity.lower()]
        
        return {
            "status": "success",
            "project_id": project_id,
            "threats": threats,
            "total_threats": len(threats),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting threat intelligence: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get threat intelligence: {str(e)}")

@router.post("/scan/vulnerability")
async def trigger_vulnerability_scan(
    project_id: str,
    services: Dict[str, str],
    background_tasks: BackgroundTasks,
    aws_credentials: Optional[Dict[str, str]] = None
):
    """
    Trigger a vulnerability scan for the project
    """
    try:
        def run_vulnerability_scan():
            """Background task to run vulnerability scan"""
            analyzer = get_security_analyzer(aws_credentials)
            # This would trigger a comprehensive scan
            logger.info(f"Running vulnerability scan for project {project_id}")
        
        background_tasks.add_task(run_vulnerability_scan)
        
        return {
            "status": "success",
            "message": f"Vulnerability scan initiated for project {project_id}",
            "scan_id": f"scan_{project_id}_{int(datetime.now().timestamp())}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering vulnerability scan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger vulnerability scan: {str(e)}")

@router.get("/recommendations/{project_id}")
async def get_security_recommendations(project_id: str, category: Optional[str] = None):
    """
    Get security recommendations for a project
    """
    try:
        # Mock security recommendations
        recommendations = [
            {
                "id": "rec_001",
                "title": "Enable Multi-Factor Authentication",
                "description": "Enable MFA for all IAM users to enhance account security",
                "priority": "high",
                "category": "access_management",
                "effort": "low",
                "impact": "high",
                "implementation_steps": [
                    "Review all IAM users",
                    "Enable MFA for each user",
                    "Provide MFA setup instructions to users",
                    "Monitor MFA compliance"
                ],
                "estimated_time": "2-4 hours",
                "cost_impact": "minimal"
            },
            {
                "id": "rec_002",
                "title": "Implement Network Segmentation",
                "description": "Use VPC and subnets to create network boundaries",
                "priority": "high",
                "category": "network_security",
                "effort": "medium",
                "impact": "high",
                "implementation_steps": [
                    "Design network architecture",
                    "Create private and public subnets",
                    "Configure route tables",
                    "Update security groups",
                    "Test connectivity"
                ],
                "estimated_time": "1-2 days",
                "cost_impact": "low"
            },
            {
                "id": "rec_003",
                "title": "Enable CloudTrail Logging",
                "description": "Enable comprehensive audit logging across all regions",
                "priority": "medium",
                "category": "monitoring",
                "effort": "low",
                "impact": "medium",
                "implementation_steps": [
                    "Create CloudTrail trail",
                    "Configure S3 bucket for logs",
                    "Enable log file validation",
                    "Set up CloudWatch integration",
                    "Configure alerts"
                ],
                "estimated_time": "2-3 hours",
                "cost_impact": "low"
            }
        ]
        
        # Filter by category if provided
        if category:
            recommendations = [r for r in recommendations if r["category"] == category]
        
        return {
            "status": "success",
            "project_id": project_id,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting security recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get security recommendations: {str(e)}")

@router.get("/encryption-status/{project_id}")
async def get_encryption_status(project_id: str):
    """
    Get encryption status for all services in the project
    """
    try:
        # Mock encryption status
        encryption_status = {
            "project_id": project_id,
            "overall_encrypted_percentage": 80.0,
            "total_services": 10,
            "encrypted_services": 8,
            "services": {
                "s3_bucket_data": {
                    "encrypted": True,
                    "encryption_type": "AES-256",
                    "key_management": "AWS KMS"
                },
                "rds_database": {
                    "encrypted": False,
                    "encryption_type": None,
                    "key_management": None,
                    "recommendation": "Enable encryption at rest"
                },
                "ebs_volumes": {
                    "encrypted": True,
                    "encryption_type": "AES-256",
                    "key_management": "AWS KMS"
                },
                "lambda_environment": {
                    "encrypted": True,
                    "encryption_type": "AES-256",
                    "key_management": "AWS KMS"
                }
            },
            "recommendations": [
                "Enable RDS encryption for database instances",
                "Use customer-managed KMS keys for better control",
                "Enable S3 bucket key for cost optimization"
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "encryption_status": encryption_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting encryption status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get encryption status: {str(e)}")