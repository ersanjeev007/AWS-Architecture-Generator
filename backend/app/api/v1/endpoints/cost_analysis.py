from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio

from app.database import get_db, ProjectDB
from app.core.enhanced_cost_calculator import EnhancedCostCalculator
from app.schemas.architecture import CostBreakdown, EnhancedCostResponse, CostOptimizationResponse
from app.schemas.questionnaire import QuestionnaireRequest
from pydantic import BaseModel

router = APIRouter()

class CostAnalysisRequest(BaseModel):
    questionnaire: QuestionnaireRequest
    services: dict
    region: str = "us-east-1"
    security_level: str = "medium"

class CostOptimizationRequest(BaseModel):
    project_id: str
    optimization_type: str = "all"  # "reserved_instances", "spot_instances", "right_sizing", "all"

@router.post("/enhanced-estimate", response_model=EnhancedCostResponse)
async def get_enhanced_cost_estimate(
    request: CostAnalysisRequest,
    db: Session = Depends(get_db)
):
    """Get enhanced cost estimation with real AWS pricing"""
    try:
        calculator = EnhancedCostCalculator(region=request.region)
        
        cost_range, breakdown = await calculator.calculate_enhanced_costs(
            questionnaire=request.questionnaire,
            services=request.services,
            security_level=request.security_level
        )
        
        # Get cost optimization recommendations
        total_cost = sum(
            float(item.estimated_monthly_cost.replace('$', '').replace(',', '').split('-')[0]) 
            for item in breakdown 
            if item.estimated_monthly_cost.startswith('$') and not item.estimated_monthly_cost.startswith('-$')
        )
        
        optimizations = calculator.get_cost_optimization_recommendations(
            questionnaire=request.questionnaire,
            total_cost=total_cost
        )
        
        # Calculate pricing confidence
        pricing_confidence = 85 if calculator.pricing_client else 60
        
        response = EnhancedCostResponse(
            estimated_cost=cost_range,
            cost_breakdown=breakdown,
            total_monthly_cost=total_cost,
            pricing_confidence=pricing_confidence,
            region=request.region,
            optimizations=optimizations,
            last_updated=calculator.pricing_cache.get("last_updated", "Live pricing"),
            includes_free_tier=True,
            currency="USD"
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating enhanced costs: {str(e)}")

@router.get("/optimization-recommendations/{project_id}", response_model=CostOptimizationResponse)
async def get_cost_optimization_recommendations(
    project_id: str,
    optimization_type: str = "all",
    db: Session = Depends(get_db)
):
    """Get cost optimization recommendations for a specific project"""
    try:
        # Get project from database
        project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Parse project data
        questionnaire_data = project.questionnaire_data
        services_data = project.architecture_data.get("services", {})
        
        # Create questionnaire object
        questionnaire = QuestionnaireRequest(**questionnaire_data)
        
        calculator = EnhancedCostCalculator(region="us-east-1")
        
        # Calculate current costs
        cost_range, breakdown = await calculator.calculate_enhanced_costs(
            questionnaire=questionnaire,
            services=services_data,
            security_level="medium"
        )
        
        current_cost = sum(
            float(item.estimated_monthly_cost.replace('$', '').replace(',', '').split('-')[0]) 
            for item in breakdown 
            if item.estimated_monthly_cost.startswith('$') and not item.estimated_monthly_cost.startswith('-$')
        )
        
        # Get optimization recommendations
        optimizations = calculator.get_cost_optimization_recommendations(
            questionnaire=questionnaire,
            total_cost=current_cost
        )
        
        # Filter by optimization type if specified
        if optimization_type != "all":
            optimizations = [opt for opt in optimizations if opt["category"].lower().replace(" ", "_") == optimization_type]
        
        # Calculate potential savings
        total_potential_savings = sum(
            float(opt.get("potential_savings", "0%").replace("%", "")) / 100 * current_cost
            for opt in optimizations
            if "%" in opt.get("potential_savings", "")
        )
        
        response = CostOptimizationResponse(
            project_id=project_id,
            current_monthly_cost=current_cost,
            optimization_recommendations=optimizations,
            total_potential_savings=total_potential_savings,
            optimization_impact=f"{(total_potential_savings/current_cost)*100:.1f}%" if current_cost > 0 else "0%",
            implementation_priority=_prioritize_optimizations(optimizations, current_cost)
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting optimization recommendations: {str(e)}")

@router.post("/compare-regions")
async def compare_regional_costs(
    request: CostAnalysisRequest,
    regions: List[str] = ["us-east-1", "us-west-2", "eu-west-1"]
):
    """Compare costs across different AWS regions"""
    try:
        regional_costs = {}
        
        tasks = []
        for region in regions:
            calculator = EnhancedCostCalculator(region=region)
            task = calculator.calculate_enhanced_costs(
                questionnaire=request.questionnaire,
                services=request.services,
                security_level=request.security_level
            )
            tasks.append((region, task))
        
        # Execute all calculations concurrently
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        for i, (region, _) in enumerate(tasks):
            if isinstance(results[i], Exception):
                regional_costs[region] = {"error": str(results[i])}
            else:
                cost_range, breakdown = results[i]
                total_cost = sum(
                    float(item.estimated_monthly_cost.replace('$', '').replace(',', '').split('-')[0]) 
                    for item in breakdown 
                    if item.estimated_monthly_cost.startswith('$') and not item.estimated_monthly_cost.startswith('-$')
                )
                regional_costs[region] = {
                    "cost_range": cost_range,
                    "total_monthly_cost": total_cost,
                    "breakdown": [item.dict() for item in breakdown]
                }
        
        # Find cheapest region
        cheapest_region = min(
            [r for r in regional_costs.keys() if "error" not in regional_costs[r]], 
            key=lambda x: regional_costs[x]["total_monthly_cost"]
        )
        
        return {
            "regional_comparison": regional_costs,
            "cheapest_region": cheapest_region,
            "cost_variance": _calculate_cost_variance(regional_costs),
            "recommendations": _get_regional_recommendations(regional_costs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing regional costs: {str(e)}")

@router.get("/cost-trends/{project_id}")
async def get_cost_trends(
    project_id: str,
    months: int = 12,
    db: Session = Depends(get_db)
):
    """Get historical cost trends and projections for a project"""
    try:
        # This would integrate with AWS Cost Explorer API in a real implementation
        # For now, return simulated trend data
        
        import random
        from datetime import datetime, timedelta
        
        base_cost = 150  # Simulated base monthly cost
        trends = []
        
        for i in range(months):
            date = datetime.now() - timedelta(days=30 * (months - i - 1))
            # Simulate cost variations
            variance = random.uniform(0.85, 1.15)
            growth = 1 + (i * 0.02)  # 2% monthly growth
            cost = base_cost * variance * growth
            
            trends.append({
                "month": date.strftime("%Y-%m"),
                "actual_cost": round(cost, 2),
                "projected_cost": round(cost * 1.1, 2),  # 10% higher projection
                "services_breakdown": {
                    "compute": round(cost * 0.4, 2),
                    "storage": round(cost * 0.2, 2),
                    "networking": round(cost * 0.15, 2),
                    "database": round(cost * 0.15, 2),
                    "security": round(cost * 0.1, 2)
                }
            })
        
        # Calculate trend analysis
        recent_costs = [t["actual_cost"] for t in trends[-3:]]
        trend_direction = "increasing" if recent_costs[-1] > recent_costs[0] else "decreasing"
        trend_percentage = ((recent_costs[-1] - recent_costs[0]) / recent_costs[0]) * 100
        
        return {
            "project_id": project_id,
            "cost_trends": trends,
            "trend_analysis": {
                "direction": trend_direction,
                "percentage_change": round(trend_percentage, 1),
                "average_monthly_cost": round(sum(recent_costs) / len(recent_costs), 2)
            },
            "cost_anomalies": _detect_cost_anomalies(trends),
            "recommendations": _get_trend_recommendations(trends)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cost trends: {str(e)}")

def _prioritize_optimizations(optimizations: List[dict], current_cost: float) -> List[str]:
    """Prioritize optimization recommendations based on impact and effort"""
    priorities = []
    
    for opt in optimizations:
        potential_savings = opt.get("potential_savings", "0%")
        if "%" in potential_savings:
            savings_pct = float(potential_savings.replace("%", ""))
            if savings_pct > 20:
                priorities.append(f"High: {opt['category']} - {potential_savings} savings")
            elif savings_pct > 10:
                priorities.append(f"Medium: {opt['category']} - {potential_savings} savings")
            else:
                priorities.append(f"Low: {opt['category']} - {potential_savings} savings")
    
    return priorities

def _calculate_cost_variance(regional_costs: dict) -> float:
    """Calculate cost variance across regions"""
    costs = [
        data["total_monthly_cost"] 
        for data in regional_costs.values() 
        if "error" not in data
    ]
    
    if len(costs) < 2:
        return 0
    
    min_cost = min(costs)
    max_cost = max(costs)
    return ((max_cost - min_cost) / min_cost) * 100

def _get_regional_recommendations(regional_costs: dict) -> List[str]:
    """Get recommendations based on regional cost comparison"""
    recommendations = []
    
    costs = {
        region: data["total_monthly_cost"] 
        for region, data in regional_costs.items() 
        if "error" not in data
    }
    
    if len(costs) > 1:
        cheapest = min(costs, key=costs.get)
        most_expensive = max(costs, key=costs.get)
        savings = costs[most_expensive] - costs[cheapest]
        
        if savings > 50:
            recommendations.append(f"Consider {cheapest} region for ${savings:.0f}/month savings")
        
        recommendations.append("Factor in data transfer costs for multi-region architectures")
        recommendations.append("Consider compliance and latency requirements when choosing regions")
    
    return recommendations

def _detect_cost_anomalies(trends: List[dict]) -> List[dict]:
    """Detect cost anomalies in trend data"""
    anomalies = []
    
    for i, trend in enumerate(trends[1:], 1):
        prev_cost = trends[i-1]["actual_cost"]
        current_cost = trend["actual_cost"]
        change = ((current_cost - prev_cost) / prev_cost) * 100
        
        if abs(change) > 25:  # More than 25% change
            anomalies.append({
                "month": trend["month"],
                "type": "spike" if change > 0 else "drop",
                "percentage_change": round(change, 1),
                "potential_cause": _guess_anomaly_cause(change, trend)
            })
    
    return anomalies

def _guess_anomaly_cause(change: float, trend: dict) -> str:
    """Guess the potential cause of cost anomaly"""
    if change > 50:
        return "Possible service scaling or new resource deployment"
    elif change > 25:
        return "Increased usage or service configuration change"
    elif change < -25:
        return "Resource optimization or service termination"
    else:
        return "Normal variance"

def _get_trend_recommendations(trends: List[dict]) -> List[str]:
    """Get recommendations based on cost trends"""
    recommendations = []
    
    recent_trends = trends[-3:]
    costs = [t["actual_cost"] for t in recent_trends]
    
    if len(costs) > 1:
        growth_rate = ((costs[-1] - costs[0]) / costs[0]) * 100 / len(costs)
        
        if growth_rate > 10:
            recommendations.append("High cost growth detected - review resource scaling policies")
            recommendations.append("Consider implementing cost budgets and alerts")
        elif growth_rate > 5:
            recommendations.append("Moderate cost growth - monitor and optimize resource usage")
        
        if costs[-1] > 500:
            recommendations.append("Consider Reserved Instances for predictable workloads")
            recommendations.append("Evaluate AWS Savings Plans for additional discounts")
    
    return recommendations