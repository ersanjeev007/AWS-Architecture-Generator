from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio
from datetime import datetime

from app.database import get_db, ProjectDB
from app.core.ai_security_advisor import AISecurityAdvisor, SecurityRecommendation, ProjectAnalysis, SecurityRecommendationType
from app.schemas.questionnaire import QuestionnaireRequest
from pydantic import BaseModel

router = APIRouter()

class SecurityAnalysisRequest(BaseModel):
    project_id: str
    questionnaire: QuestionnaireRequest
    services: dict
    include_ai_recommendations: bool = True
    security_level: Optional[str] = None

class SecurityRecommendationResponse(BaseModel):
    id: str
    title: str
    description: str
    recommendation_type: str
    affected_services: List[str]
    priority: str
    implementation_effort: str
    cost_impact: str
    compliance_frameworks: List[str]
    aws_documentation_url: str
    implementation_steps: List[str]
    terraform_snippet: Optional[str] = None
    cloudformation_snippet: Optional[str] = None
    created_at: Optional[datetime] = None

class ProjectSecurityAnalysisResponse(BaseModel):
    project_id: str
    security_posture_score: float
    vulnerabilities_count: int
    recommendations: List[SecurityRecommendationResponse]
    compliance_status: dict
    last_analyzed: datetime

class SecurityMonitoringResponse(BaseModel):
    aws_security_updates: List[dict]
    applicable_updates: List[dict]
    monitoring_status: str
    last_update_check: datetime

@router.post("/analyze-project", response_model=ProjectSecurityAnalysisResponse)
async def analyze_project_security(
    request: SecurityAnalysisRequest,
    openai_api_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Analyze project security and get AI-powered recommendations"""
    try:
        # Initialize AI security advisor
        advisor = AISecurityAdvisor(openai_api_key=openai_api_key)
        
        # Get project data
        project = db.query(ProjectDB).filter(ProjectDB.id == request.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_data = {
            "id": request.project_id,
            "name": project.project_name,
            "created_at": project.created_at
        }
        
        # Analyze project security
        project_analysis = await advisor.analyze_project_security(
            project_data=project_data,
            questionnaire=request.questionnaire,
            services=request.services
        )
        
        # Get security recommendations
        recommendations = await advisor.get_security_recommendations(
            project_analysis=project_analysis,
            include_new_features=True
        )
        
        # Convert to response format
        recommendation_responses = [
            SecurityRecommendationResponse(
                id=rec.id,
                title=rec.title,
                description=rec.description,
                recommendation_type=rec.recommendation_type.value,
                affected_services=rec.affected_services,
                priority=rec.priority,
                implementation_effort=rec.implementation_effort,
                cost_impact=rec.cost_impact,
                compliance_frameworks=rec.compliance_frameworks,
                aws_documentation_url=rec.aws_documentation_url,
                implementation_steps=rec.implementation_steps,
                terraform_snippet=rec.terraform_snippet,
                cloudformation_snippet=rec.cloudformation_snippet,
                created_at=rec.created_at
            )
            for rec in recommendations
        ]
        
        # Calculate compliance status
        compliance_status = _calculate_compliance_status(
            project_analysis.compliance_requirements,
            recommendations
        )
        
        response = ProjectSecurityAnalysisResponse(
            project_id=request.project_id,
            security_posture_score=project_analysis.security_posture_score,
            vulnerabilities_count=project_analysis.vulnerabilities_count,
            recommendations=recommendation_responses,
            compliance_status=compliance_status,
            last_analyzed=project_analysis.last_analyzed
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing project security: {str(e)}")

@router.get("/recommendations/{project_id}", response_model=List[SecurityRecommendationResponse])
async def get_project_recommendations(
    project_id: str,
    priority_filter: Optional[str] = None,
    recommendation_type: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get security recommendations for a specific project"""
    try:
        # Get project from database
        project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Initialize advisor
        advisor = AISecurityAdvisor()
        
        # Recreate project analysis from stored data
        questionnaire_data = project.questionnaire_data
        questionnaire = QuestionnaireRequest(**questionnaire_data)
        
        services_data = project.architecture_data.get("services", {})
        
        project_data = {
            "id": project_id,
            "name": project.project_name,
            "created_at": project.created_at
        }
        
        project_analysis = await advisor.analyze_project_security(
            project_data=project_data,
            questionnaire=questionnaire,
            services=services_data
        )
        
        # Get recommendations
        recommendations = await advisor.get_security_recommendations(
            project_analysis=project_analysis,
            include_new_features=True
        )
        
        # Apply filters
        if priority_filter:
            recommendations = [r for r in recommendations if r.priority == priority_filter]
        
        if recommendation_type:
            recommendations = [r for r in recommendations if r.recommendation_type.value == recommendation_type]
        
        # Limit results
        recommendations = recommendations[:limit]
        
        # Convert to response format
        return [
            SecurityRecommendationResponse(
                id=rec.id,
                title=rec.title,
                description=rec.description,
                recommendation_type=rec.recommendation_type.value,
                affected_services=rec.affected_services,
                priority=rec.priority,
                implementation_effort=rec.implementation_effort,
                cost_impact=rec.cost_impact,
                compliance_frameworks=rec.compliance_frameworks,
                aws_documentation_url=rec.aws_documentation_url,
                implementation_steps=rec.implementation_steps,
                terraform_snippet=rec.terraform_snippet,
                cloudformation_snippet=rec.cloudformation_snippet,
                created_at=rec.created_at
            )
            for rec in recommendations
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@router.get("/aws-security-updates", response_model=SecurityMonitoringResponse)
async def get_aws_security_updates(
    background_tasks: BackgroundTasks,
    filter_by_services: Optional[List[str]] = None
):
    """Get latest AWS security updates and applicable recommendations"""
    try:
        advisor = AISecurityAdvisor()
        
        # Monitor AWS security updates
        updates = await advisor.monitor_aws_security_updates()
        
        # Filter by services if specified
        applicable_updates = updates
        if filter_by_services:
            applicable_updates = [
                update for update in updates
                if any(service in update.get("services", []) for service in filter_by_services)
            ]
        
        response = SecurityMonitoringResponse(
            aws_security_updates=updates,
            applicable_updates=applicable_updates,
            monitoring_status="active",
            last_update_check=datetime.now()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting security updates: {str(e)}")

@router.post("/recommendation-implementation-plan/{recommendation_id}")
async def get_implementation_plan(
    recommendation_id: str,
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed implementation plan for a security recommendation"""
    try:
        # Get project data
        project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        advisor = AISecurityAdvisor()
        
        # Recreate project analysis
        questionnaire_data = project.questionnaire_data
        questionnaire = QuestionnaireRequest(**questionnaire_data)
        
        services_data = project.architecture_data.get("services", {})
        
        project_data = {
            "id": project_id,
            "name": project.project_name,
            "created_at": project.created_at
        }
        
        project_analysis = await advisor.analyze_project_security(
            project_data=project_data,
            questionnaire=questionnaire,
            services=services_data
        )
        
        # Get all recommendations and find the requested one
        recommendations = await advisor.get_security_recommendations(
            project_analysis=project_analysis,
            include_new_features=True
        )
        
        target_recommendation = None
        for rec in recommendations:
            if rec.id == recommendation_id:
                target_recommendation = rec
                break
        
        if not target_recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        # Get implementation plan
        implementation_plan = advisor.get_recommendation_implementation_plan(
            recommendation=target_recommendation,
            project_analysis=project_analysis
        )
        
        return implementation_plan
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting implementation plan: {str(e)}")

@router.post("/bulk-analyze")
async def bulk_analyze_projects(
    project_ids: List[str],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analyze multiple projects for security recommendations"""
    try:
        advisor = AISecurityAdvisor()
        
        # Start background analysis for all projects
        background_tasks.add_task(
            _bulk_analyze_background,
            project_ids,
            advisor,
            db
        )
        
        return {
            "message": f"Bulk analysis started for {len(project_ids)} projects",
            "project_ids": project_ids,
            "status": "processing",
            "estimated_completion": "5-10 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting bulk analysis: {str(e)}")

@router.get("/compliance-dashboard/{project_id}")
async def get_compliance_dashboard(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get compliance dashboard for a project"""
    try:
        project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        advisor = AISecurityAdvisor()
        
        # Recreate project analysis
        questionnaire_data = project.questionnaire_data
        questionnaire = QuestionnaireRequest(**questionnaire_data)
        
        services_data = project.architecture_data.get("services", {})
        
        project_data = {
            "id": project_id,
            "name": project.project_name,
            "created_at": project.created_at
        }
        
        project_analysis = await advisor.analyze_project_security(
            project_data=project_data,
            questionnaire=questionnaire,
            services=services_data
        )
        
        # Get compliance-specific analysis
        compliance_frameworks = project_analysis.compliance_requirements
        
        dashboard = {
            "project_id": project_id,
            "compliance_frameworks": compliance_frameworks,
            "overall_compliance_score": project_analysis.security_posture_score,
            "framework_scores": {},
            "critical_gaps": [],
            "compliance_recommendations": []
        }
        
        # Calculate framework-specific scores
        for framework in compliance_frameworks:
            framework_score = _calculate_framework_score(framework, project_analysis)
            dashboard["framework_scores"][framework] = framework_score
            
            if framework_score < 70:
                dashboard["critical_gaps"].append({
                    "framework": framework,
                    "score": framework_score,
                    "gap": "Below compliance threshold"
                })
        
        # Get compliance recommendations
        recommendations = await advisor.get_security_recommendations(
            project_analysis=project_analysis,
            include_new_features=False
        )
        
        compliance_recs = [
            rec for rec in recommendations
            if rec.recommendation_type == SecurityRecommendationType.COMPLIANCE_UPDATE
        ]
        
        dashboard["compliance_recommendations"] = [
            {
                "id": rec.id,
                "title": rec.title,
                "frameworks": rec.compliance_frameworks,
                "priority": rec.priority
            }
            for rec in compliance_recs
        ]
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting compliance dashboard: {str(e)}")

async def _bulk_analyze_background(project_ids: List[str], advisor: AISecurityAdvisor, db: Session):
    """Background task for bulk project analysis"""
    try:
        for project_id in project_ids:
            project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
            if not project:
                continue
            
            # Analyze project (simplified for background processing)
            questionnaire_data = project.questionnaire_data
            questionnaire = QuestionnaireRequest(**questionnaire_data)
            
            services_data = project.architecture_data.get("services", {})
            
            project_data = {
                "id": project_id,
                "name": project.project_name,
                "created_at": project.created_at
            }
            
            project_analysis = await advisor.analyze_project_security(
                project_data=project_data,
                questionnaire=questionnaire,
                services=services_data
            )
            
            # Store analysis results (would implement storage logic here)
            # For now, just log the completion
            print(f"Completed analysis for project {project_id}")
            
    except Exception as e:
        print(f"Error in bulk analysis: {e}")

def _calculate_compliance_status(compliance_requirements: List[str], recommendations: List[SecurityRecommendation]) -> dict:
    """Calculate compliance status based on requirements and recommendations"""
    status = {}
    
    for framework in compliance_requirements:
        framework_recs = [
            rec for rec in recommendations
            if framework.upper() in rec.compliance_frameworks
        ]
        
        critical_issues = len([rec for rec in framework_recs if rec.priority in ["critical", "high"]])
        total_recommendations = len(framework_recs)
        
        if total_recommendations == 0:
            compliance_score = 100
        else:
            compliance_score = max(0, 100 - (critical_issues * 20) - ((total_recommendations - critical_issues) * 5))
        
        status[framework] = {
            "compliance_score": compliance_score,
            "status": "compliant" if compliance_score >= 80 else "non_compliant",
            "critical_issues": critical_issues,
            "total_recommendations": total_recommendations
        }
    
    return status

def _calculate_framework_score(framework: str, project_analysis: ProjectAnalysis) -> float:
    """Calculate compliance score for a specific framework"""
    base_score = project_analysis.security_posture_score
    
    # Adjust based on framework-specific requirements
    framework_adjustments = {
        "hipaa": -10 if "KMS" not in project_analysis.services_used else 0,
        "pci-dss": -15 if "WAF" not in project_analysis.services_used else 0,
        "sox": -5 if "CloudTrail" not in project_analysis.services_used else 0
    }
    
    adjustment = framework_adjustments.get(framework.lower(), 0)
    return max(0, min(100, base_score + adjustment))