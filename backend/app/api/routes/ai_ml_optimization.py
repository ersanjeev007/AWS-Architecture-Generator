from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging
from datetime import datetime

from app.core.ai_ml_optimizer import IntelligentArchitectureOptimizer, AIRecommendation, ArchitectureMetrics
from app.core.ai_architecture_assistant import IntelligentArchitectureAssistant, ConversationContext
from app.schemas.architecture import ProjectResponse
from app.schemas.questionnaire import QuestionnaireRequest
from app.api.routes.auth import get_current_user
from app.schemas.auth import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-ml", tags=["AI/ML Optimization"])

# Pydantic models for API
class AIAnalysisRequest(BaseModel):
    project_id: str
    questionnaire: Dict[str, Any]
    services: Dict[str, str]
    historical_metrics: Optional[Dict[str, Any]] = None
    include_predictions: bool = True

class AIRecommendationResponse(BaseModel):
    id: str
    title: str
    description: str
    optimization_type: str
    affected_services: List[str]
    priority: str
    confidence_score: float
    predicted_cost_savings: Optional[float] = None
    predicted_performance_improvement: Optional[str] = None
    implementation_complexity: str
    ml_model_used: str
    data_points_analyzed: int
    created_at: datetime

class AIInsightsResponse(BaseModel):
    total_recommendations: int
    optimization_types: Dict[str, int]
    confidence_stats: Dict[str, float]
    cost_impact: Dict[str, Any]
    ai_readiness_score: float
    priority_breakdown: Dict[str, int]

class ChatRequest(BaseModel):
    message: str
    project_id: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message: str
    suggestions: List[str]
    intent: str
    ai_recommendations: Optional[List[AIRecommendationResponse]] = None
    cost_savings: Optional[float] = None
    security_score: Optional[float] = None
    conversation_id: str

class ArchitectureOptimizationRequest(BaseModel):
    project_id: str
    optimization_focus: List[str]  # ["cost", "performance", "security", "scalability"]
    current_architecture: Dict[str, Any]
    constraints: Optional[Dict[str, Any]] = None

# Initialize AI services
ai_optimizer = IntelligentArchitectureOptimizer()
ai_assistant = IntelligentArchitectureAssistant()

@router.post("/analyze-architecture", response_model=Dict[str, Any])
async def analyze_architecture_with_ai(
    request: AIAnalysisRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Analyze architecture using AI/ML and provide comprehensive optimization recommendations
    """
    try:
        logger.info(f"Starting AI analysis for project {request.project_id}")
        
        # Convert request to appropriate format
        project_data = {"id": request.project_id}
        questionnaire = QuestionnaireRequest(**request.questionnaire)
        
        # Perform AI analysis
        recommendations = await ai_optimizer.analyze_architecture_with_ai(
            project_data, questionnaire, request.services, request.historical_metrics
        )
        
        # Generate insights
        insights = await ai_optimizer.generate_ai_architecture_insights(recommendations)
        
        # Convert recommendations to response format
        recommendation_responses = [
            AIRecommendationResponse(
                id=rec.id,
                title=rec.title,
                description=rec.description,
                optimization_type=rec.optimization_type.value,
                affected_services=rec.affected_services,
                priority=rec.priority,
                confidence_score=rec.confidence_score,
                predicted_cost_savings=rec.predicted_cost_savings,
                predicted_performance_improvement=rec.predicted_performance_improvement,
                implementation_complexity=rec.implementation_complexity,
                ml_model_used=rec.ml_model_used,
                data_points_analyzed=rec.data_points_analyzed,
                created_at=rec.created_at or datetime.now()
            )
            for rec in recommendations
        ]
        
        return {
            "analysis_id": f"ai_analysis_{request.project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "project_id": request.project_id,
            "recommendations": recommendation_responses,
            "insights": insights,
            "analysis_timestamp": datetime.now(),
            "ml_models_used": list(set([rec.ml_model_used for rec in recommendations])),
            "total_data_points": sum([rec.data_points_analyzed for rec in recommendations])
        }
        
    except Exception as e:
        logger.error(f"Error in AI architecture analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai_assistant(
    request: ChatRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Chat with AI architecture assistant for personalized guidance
    """
    try:
        # Create conversation context
        context = ConversationContext(
            project_id=request.project_id,
            user_intent="",
            architecture_state=request.context or {},
            conversation_history=[],
            recommendations=[]
        )
        
        # Get response from AI assistant
        response = await ai_assistant.chat_with_assistant(request.message, context)
        
        # Convert AI recommendations if present
        ai_recommendations = None
        if response.get("ai_recommendations"):
            ai_recommendations = [
                AIRecommendationResponse(
                    id=rec.id,
                    title=rec.title,
                    description=rec.description,
                    optimization_type=rec.optimization_type.value,
                    affected_services=rec.affected_services,
                    priority=rec.priority,
                    confidence_score=rec.confidence_score,
                    predicted_cost_savings=rec.predicted_cost_savings,
                    predicted_performance_improvement=rec.predicted_performance_improvement,
                    implementation_complexity=rec.implementation_complexity,
                    ml_model_used=rec.ml_model_used,
                    data_points_analyzed=rec.data_points_analyzed,
                    created_at=rec.created_at or datetime.now()
                )
                for rec in response["ai_recommendations"]
            ]
        
        return ChatResponse(
            message=response["message"],
            suggestions=response["suggestions"],
            intent=response["intent"],
            ai_recommendations=ai_recommendations,
            cost_savings=response.get("cost_savings"),
            security_score=response.get("security_score"),
            conversation_id=f"chat_{request.project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
    except Exception as e:
        logger.error(f"Error in AI chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI chat failed: {str(e)}")

@router.get("/smart-suggestions/{project_id}")
async def get_smart_suggestions(
    project_id: str,
    context: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get smart suggestions for architecture improvements based on project context
    """
    try:
        # Create context for suggestions
        conversation_context = ConversationContext(
            project_id=project_id,
            user_intent="",
            architecture_state={"project_id": project_id},
            conversation_history=[],
            recommendations=[]
        )
        
        suggestions = await ai_assistant.get_smart_suggestions(conversation_context)
        
        return {
            "project_id": project_id,
            "suggestions": suggestions,
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting smart suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@router.post("/optimize-architecture")
async def optimize_architecture(
    request: ArchitectureOptimizationRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Perform comprehensive architecture optimization based on specified focus areas
    """
    try:
        logger.info(f"Starting architecture optimization for project {request.project_id}")
        
        # Extract services from current architecture
        services = request.current_architecture.get("services", {})
        
        # Create questionnaire from architecture data
        questionnaire_data = {
            "project_name": request.current_architecture.get("project_name", "Unnamed Project"),
            "application_type": request.current_architecture.get("application_type", "web_application"),
            "expected_users": request.current_architecture.get("expected_users", 1000),
            "data_sensitivity": request.current_architecture.get("data_sensitivity", "medium"),
            "compliance_requirements": request.current_architecture.get("compliance_requirements", []),
            "budget_range": request.current_architecture.get("budget_range", "1000-5000"),
            "performance_requirements": request.current_architecture.get("performance_requirements", "standard"),
            "availability_requirements": request.current_architecture.get("availability_requirements", "high"),
            "preferred_regions": request.current_architecture.get("preferred_regions", ["us-west-2"])
        }
        
        questionnaire = QuestionnaireRequest(**questionnaire_data)
        
        # Perform AI optimization
        recommendations = await ai_optimizer.analyze_architecture_with_ai(
            {"id": request.project_id}, questionnaire, services
        )
        
        # Filter recommendations based on optimization focus
        filtered_recommendations = []
        for rec in recommendations:
            opt_type = rec.optimization_type.value.lower()
            if any(focus.lower() in opt_type for focus in request.optimization_focus):
                filtered_recommendations.append(rec)
        
        # Generate optimization plan
        optimization_plan = {
            "project_id": request.project_id,
            "optimization_focus": request.optimization_focus,
            "recommendations": [
                {
                    "id": rec.id,
                    "title": rec.title,
                    "description": rec.description,
                    "priority": rec.priority,
                    "confidence_score": rec.confidence_score,
                    "implementation_complexity": rec.implementation_complexity,
                    "estimated_savings": rec.predicted_cost_savings,
                    "performance_improvement": rec.predicted_performance_improvement
                }
                for rec in filtered_recommendations
            ],
            "estimated_total_savings": sum([
                rec.predicted_cost_savings for rec in filtered_recommendations 
                if rec.predicted_cost_savings
            ]),
            "high_priority_count": len([
                rec for rec in filtered_recommendations 
                if rec.priority in ["critical", "high"]
            ]),
            "optimization_timeline": "2-4 weeks",
            "generated_at": datetime.now()
        }
        
        # Schedule background task for detailed analysis
        background_tasks.add_task(
            perform_detailed_optimization_analysis,
            request.project_id,
            optimization_plan
        )
        
        return optimization_plan
        
    except Exception as e:
        logger.error(f"Error in architecture optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@router.get("/ai-readiness-assessment/{project_id}")
async def assess_ai_readiness(
    project_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Assess how ready the architecture is for AI/ML integration
    """
    try:
        # This would typically fetch project data from database
        # For now, using mock data
        mock_services = {
            "compute": "EC2",
            "database": "RDS",
            "storage": "S3",
            "api": "API Gateway"
        }
        
        mock_questionnaire_data = {
            "project_name": "AI Readiness Assessment",
            "application_type": "web_application",
            "expected_users": 5000,
            "data_sensitivity": "medium",
            "compliance_requirements": [],
            "budget_range": "5000-10000",
            "performance_requirements": "high",
            "availability_requirements": "high",
            "preferred_regions": ["us-west-2"]
        }
        
        questionnaire = QuestionnaireRequest(**mock_questionnaire_data)
        
        # Analyze for AI/ML opportunities
        recommendations = await ai_optimizer.analyze_architecture_with_ai(
            {"id": project_id}, questionnaire, mock_services
        )
        
        # Calculate AI readiness score
        insights = await ai_optimizer.generate_ai_architecture_insights(recommendations)
        ai_readiness_score = insights["ai_readiness_score"]
        
        # Generate AI/ML integration recommendations
        ai_ml_recommendations = [
            rec for rec in recommendations
            if "ai" in rec.title.lower() or "ml" in rec.title.lower() or "intelligent" in rec.title.lower()
        ]
        
        # Determine readiness level
        if ai_readiness_score >= 80:
            readiness_level = "High - Ready for advanced AI/ML integration"
        elif ai_readiness_score >= 60:
            readiness_level = "Medium - Some preparation needed for AI/ML"
        elif ai_readiness_score >= 40:
            readiness_level = "Low - Significant preparation needed"
        else:
            readiness_level = "Very Low - Foundation work required"
        
        return {
            "project_id": project_id,
            "ai_readiness_score": ai_readiness_score,
            "readiness_level": readiness_level,
            "ai_ml_recommendations": [
                {
                    "id": rec.id,
                    "title": rec.title,
                    "description": rec.description,
                    "confidence_score": rec.confidence_score,
                    "affected_services": rec.affected_services
                }
                for rec in ai_ml_recommendations
            ],
            "next_steps": [
                "Implement data pipeline for ML",
                "Set up Amazon SageMaker environment",
                "Consider Amazon Bedrock for generative AI",
                "Establish ML model deployment pipeline"
            ],
            "recommended_services": [
                "Amazon SageMaker",
                "Amazon Bedrock",
                "AWS Lambda",
                "Amazon S3",
                "Amazon EMR"
            ],
            "assessment_date": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error in AI readiness assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

@router.get("/ml-cost-prediction/{project_id}")
async def predict_ml_costs(
    project_id: str,
    services: Optional[str] = None,  # Comma-separated list
    usage_pattern: Optional[str] = "medium",
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Predict costs for AI/ML services integration
    """
    try:
        # Parse services
        ml_services = services.split(",") if services else ["SageMaker", "Bedrock", "Lambda"]
        
        # Cost prediction model (simplified)
        base_costs = {
            "SageMaker": 200,  # Base monthly cost
            "Bedrock": 150,
            "Lambda": 50,
            "EMR": 300,
            "Comprehend": 100,
            "Rekognition": 80,
            "Textract": 120
        }
        
        usage_multipliers = {
            "low": 0.5,
            "medium": 1.0,
            "high": 2.0,
            "enterprise": 3.5
        }
        
        multiplier = usage_multipliers.get(usage_pattern, 1.0)
        
        # Calculate predicted costs
        predicted_costs = {}
        total_cost = 0
        
        for service in ml_services:
            service = service.strip()
            if service in base_costs:
                cost = base_costs[service] * multiplier
                predicted_costs[service] = cost
                total_cost += cost
        
        # Generate cost optimization recommendations
        cost_optimizations = []
        if total_cost > 500:
            cost_optimizations.extend([
                "Consider Spot instances for SageMaker training",
                "Use SageMaker Serverless Inference for variable workloads",
                "Implement auto-scaling for cost efficiency"
            ])
        
        if "Bedrock" in ml_services:
            cost_optimizations.extend([
                "Use on-demand pricing for development",
                "Consider Provisioned Throughput for production",
                "Implement efficient prompt caching"
            ])
        
        return {
            "project_id": project_id,
            "ml_services": ml_services,
            "usage_pattern": usage_pattern,
            "predicted_monthly_costs": predicted_costs,
            "total_monthly_cost": total_cost,
            "cost_range": {
                "minimum": total_cost * 0.7,
                "maximum": total_cost * 1.5
            },
            "cost_optimizations": cost_optimizations,
            "roi_potential": {
                "automation_savings": total_cost * 0.3,
                "efficiency_gains": "20-40% improvement in decision making",
                "competitive_advantage": "Enhanced user experience and capabilities"
            },
            "prediction_confidence": 0.85,
            "prediction_date": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error in ML cost prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cost prediction failed: {str(e)}")

async def perform_detailed_optimization_analysis(project_id: str, optimization_plan: Dict[str, Any]):
    """
    Background task for detailed optimization analysis
    """
    try:
        logger.info(f"Performing detailed optimization analysis for project {project_id}")
        
        # This would perform more intensive analysis
        # For now, just log the completion
        logger.info(f"Detailed optimization analysis completed for project {project_id}")
        
        # In a real implementation, you might:
        # - Store results in database
        # - Send notifications to users
        # - Generate detailed reports
        # - Update project recommendations
        
    except Exception as e:
        logger.error(f"Error in detailed optimization analysis: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint for AI/ML services"""
    return {
        "status": "healthy",
        "services": {
            "ai_optimizer": "operational",
            "ai_assistant": "operational"
        },
        "timestamp": datetime.now()
    }