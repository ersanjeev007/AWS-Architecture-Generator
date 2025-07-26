from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta

from app.core.dynamic_cost_analyzer import DynamicCostAnalyzer

logger = logging.getLogger(__name__)
router = APIRouter()

# Global analyzer instance - would be better with dependency injection
cost_analyzer = None

def get_cost_analyzer(aws_credentials: Optional[Dict[str, str]] = None) -> DynamicCostAnalyzer:
    """Get or create cost analyzer instance"""
    global cost_analyzer
    if cost_analyzer is None:
        cost_analyzer = DynamicCostAnalyzer(aws_credentials=aws_credentials)
    return cost_analyzer

@router.post("/analyze-project-costs")
async def analyze_project_costs(
    project_data: Dict[str, Any],
    services: Dict[str, str],
    usage_patterns: Optional[Dict[str, Any]] = None,
    aws_credentials: Optional[Dict[str, str]] = None
):
    """
    Perform comprehensive dynamic cost analysis for a project
    """
    try:
        analyzer = get_cost_analyzer(aws_credentials)
        result = await analyzer.analyze_project_costs(project_data, services, usage_patterns)
        
        return {
            "status": "success",
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in cost analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cost analysis failed: {str(e)}")

@router.get("/real-time-metrics/{project_id}")
async def get_real_time_cost_metrics(project_id: str):
    """
    Get real-time cost metrics for a project
    """
    try:
        analyzer = get_cost_analyzer()
        metrics = await analyzer.get_real_time_cost_metrics(project_id)
        
        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting real-time cost metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cost metrics: {str(e)}")

@router.get("/service-costs/{project_id}")
async def get_service_costs(
    project_id: str,
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    region: Optional[str] = Query("us-west-2", description="AWS region")
):
    """
    Get detailed cost breakdown by service
    """
    try:
        # Mock service costs - would come from dynamic analyzer
        services_costs = [
            {
                "service_name": "web-server-ec2",
                "service_type": "EC2",
                "monthly_cost": 145.60,
                "daily_cost": 4.85,
                "hourly_cost": 0.20,
                "usage_metrics": {
                    "instance_type": "t3.medium",
                    "hours": 720,
                    "cpu_utilization": 65.2
                },
                "cost_breakdown": {
                    "compute": 120.00,
                    "storage": 25.60
                },
                "region": region,
                "last_updated": datetime.now().isoformat(),
                "optimization_potential": 35.0
            },
            {
                "service_name": "app-data-s3",
                "service_type": "S3",
                "monthly_cost": 23.45,
                "daily_cost": 0.78,
                "hourly_cost": 0.03,
                "usage_metrics": {
                    "storage_gb": 850,
                    "requests": 45000,
                    "data_transfer_gb": 120
                },
                "cost_breakdown": {
                    "storage": 19.55,
                    "requests": 1.80,
                    "data_transfer": 2.10
                },
                "region": region,
                "last_updated": datetime.now().isoformat(),
                "optimization_potential": 40.0
            },
            {
                "service_name": "user-database-rds",
                "service_type": "RDS",
                "monthly_cost": 189.30,
                "daily_cost": 6.31,
                "hourly_cost": 0.26,
                "usage_metrics": {
                    "instance_type": "db.t3.small",
                    "storage_gb": 100,
                    "hours": 720,
                    "connections": 25
                },
                "cost_breakdown": {
                    "compute": 152.64,
                    "storage": 11.50,
                    "backup": 25.16
                },
                "region": region,
                "last_updated": datetime.now().isoformat(),
                "optimization_potential": 30.0
            },
            {
                "service_name": "api-functions-lambda",
                "service_type": "Lambda",
                "monthly_cost": 12.80,
                "daily_cost": 0.43,
                "hourly_cost": 0.02,
                "usage_metrics": {
                    "requests": 250000,
                    "duration_ms": 850,
                    "memory_mb": 512
                },
                "cost_breakdown": {
                    "requests": 0.50,
                    "duration": 12.30
                },
                "region": region,
                "last_updated": datetime.now().isoformat(),
                "optimization_potential": 20.0
            }
        ]
        
        # Filter by service type if provided
        if service_type:
            services_costs = [s for s in services_costs if s["service_type"].lower() == service_type.lower()]
        
        total_monthly_cost = sum(s["monthly_cost"] for s in services_costs)
        total_optimization_potential = sum(s["monthly_cost"] * s["optimization_potential"] / 100 for s in services_costs)
        
        return {
            "status": "success",
            "project_id": project_id,
            "services": services_costs,
            "summary": {
                "total_services": len(services_costs),
                "total_monthly_cost": round(total_monthly_cost, 2),
                "total_daily_cost": round(total_monthly_cost / 30, 2),
                "total_optimization_potential": round(total_optimization_potential, 2),
                "avg_optimization_potential": round(total_optimization_potential / total_monthly_cost * 100, 1) if total_monthly_cost > 0 else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting service costs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get service costs: {str(e)}")

@router.get("/optimizations/{project_id}")
async def get_cost_optimizations(
    project_id: str,
    optimization_type: Optional[str] = Query(None, description="Filter by optimization type"),
    priority: Optional[str] = Query(None, description="Filter by priority (high, medium, low)")
):
    """
    Get cost optimization recommendations for a project
    """
    try:
        # Mock optimization recommendations
        optimizations = [
            {
                "id": "spot_web_server",
                "title": "Use Spot Instances for Web Server",
                "description": "Migrate web server workload to Spot instances for 70% cost savings",
                "optimization_type": "spot_instances",
                "current_monthly_cost": 145.60,
                "optimized_monthly_cost": 43.68,
                "potential_savings": 101.92,
                "savings_percentage": 70.0,
                "confidence_score": 85.0,
                "implementation_effort": "medium",
                "affected_services": ["web-server-ec2"],
                "priority": "high",
                "implementation_steps": [
                    "Evaluate workload interruption tolerance",
                    "Set up Spot instance request with mixed instance types",
                    "Implement graceful shutdown handling",
                    "Configure Auto Scaling with Spot fleet"
                ],
                "timeline": "1-2 weeks",
                "risks": [
                    "Potential instance interruption",
                    "Application state management required"
                ],
                "impact_analysis": {
                    "performance_impact": "minimal",
                    "availability_impact": "low",
                    "complexity": "medium"
                }
            },
            {
                "id": "s3_storage_class",
                "title": "Optimize S3 Storage Classes",
                "description": "Implement intelligent tiering and lifecycle policies for 40% storage savings",
                "optimization_type": "storage_optimization",
                "current_monthly_cost": 23.45,
                "optimized_monthly_cost": 14.07,
                "potential_savings": 9.38,
                "savings_percentage": 40.0,
                "confidence_score": 75.0,
                "implementation_effort": "low",
                "affected_services": ["app-data-s3"],
                "priority": "medium",
                "implementation_steps": [
                    "Analyze access patterns for objects",
                    "Enable S3 Intelligent Tiering",
                    "Create lifecycle policies for archival",
                    "Monitor storage class transitions"
                ],
                "timeline": "3-5 days",
                "risks": [
                    "Retrieval costs for infrequently accessed data",
                    "Potential retrieval delays for archived data"
                ],
                "impact_analysis": {
                    "performance_impact": "minimal",
                    "availability_impact": "none",
                    "complexity": "low"
                }
            },
            {
                "id": "rds_reserved_instances",
                "title": "Purchase RDS Reserved Instances",
                "description": "Purchase 1-year Reserved Instances for production database",
                "optimization_type": "reserved_instances",
                "current_monthly_cost": 189.30,
                "optimized_monthly_cost": 123.05,
                "potential_savings": 66.25,
                "savings_percentage": 35.0,
                "confidence_score": 90.0,
                "implementation_effort": "low",
                "affected_services": ["user-database-rds"],
                "priority": "high",
                "implementation_steps": [
                    "Review database usage patterns",
                    "Select appropriate RI term (1-year vs 3-year)",
                    "Choose payment option (No Upfront, Partial, All Upfront)",
                    "Purchase Reserved Instance"
                ],
                "timeline": "immediate",
                "risks": [
                    "Long-term commitment to instance type",
                    "Regional lock-in",
                    "Underutilization if requirements change"
                ],
                "impact_analysis": {
                    "performance_impact": "none",
                    "availability_impact": "none",
                    "complexity": "low"
                }
            },
            {
                "id": "lambda_arm_migration",
                "title": "Migrate Lambda Functions to ARM Architecture",
                "description": "Migrate Lambda functions to ARM64 (Graviton2) for 20% cost savings",
                "optimization_type": "rightsizing",
                "current_monthly_cost": 12.80,
                "optimized_monthly_cost": 10.24,
                "potential_savings": 2.56,
                "savings_percentage": 20.0,
                "confidence_score": 80.0,
                "implementation_effort": "low",
                "affected_services": ["api-functions-lambda"],
                "priority": "low",
                "implementation_steps": [
                    "Test functions on ARM64 architecture",
                    "Update deployment configuration",
                    "Monitor performance metrics",
                    "Rollback if issues detected"
                ],
                "timeline": "1 week",
                "risks": [
                    "Potential compatibility issues",
                    "Performance variations"
                ],
                "impact_analysis": {
                    "performance_impact": "minimal",
                    "availability_impact": "low",
                    "complexity": "low"
                }
            },
            {
                "id": "cross_auto_scaling",
                "title": "Implement Predictive Auto Scaling",
                "description": "Set up ML-powered predictive scaling across compute services",
                "optimization_type": "auto_scaling",
                "current_monthly_cost": 371.15,
                "optimized_monthly_cost": 259.81,
                "potential_savings": 111.34,
                "savings_percentage": 30.0,
                "confidence_score": 80.0,
                "implementation_effort": "high",
                "affected_services": ["web-server-ec2", "api-functions-lambda"],
                "priority": "high",
                "implementation_steps": [
                    "Analyze historical traffic patterns",
                    "Configure predictive scaling policies",
                    "Set up CloudWatch custom metrics",
                    "Implement gradual rollout",
                    "Monitor scaling behavior"
                ],
                "timeline": "2-3 weeks",
                "risks": [
                    "Over-scaling during unexpected events",
                    "Complexity in tuning scaling parameters",
                    "Potential performance impact during scaling"
                ],
                "impact_analysis": {
                    "performance_impact": "positive",
                    "availability_impact": "positive",
                    "complexity": "high"
                }
            }
        ]
        
        # Filter by optimization type if provided
        if optimization_type:
            optimizations = [opt for opt in optimizations if opt["optimization_type"] == optimization_type]
        
        # Filter by priority if provided
        if priority:
            optimizations = [opt for opt in optimizations if opt["priority"] == priority]
        
        # Calculate summary statistics
        total_current_cost = sum(opt["current_monthly_cost"] for opt in optimizations)
        total_potential_savings = sum(opt["potential_savings"] for opt in optimizations)
        avg_confidence = sum(opt["confidence_score"] for opt in optimizations) / len(optimizations) if optimizations else 0
        
        # Group by priority
        priority_breakdown = {}
        for opt in optimizations:
            priority_key = opt["priority"]
            if priority_key not in priority_breakdown:
                priority_breakdown[priority_key] = {"count": 0, "savings": 0.0}
            priority_breakdown[priority_key]["count"] += 1
            priority_breakdown[priority_key]["savings"] += opt["potential_savings"]
        
        return {
            "status": "success",
            "project_id": project_id,
            "optimizations": optimizations,
            "summary": {
                "total_optimizations": len(optimizations),
                "total_current_cost": round(total_current_cost, 2),
                "total_potential_savings": round(total_potential_savings, 2),
                "average_confidence": round(avg_confidence, 1),
                "priority_breakdown": priority_breakdown
            },
            "filters_applied": {
                "optimization_type": optimization_type,
                "priority": priority
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting cost optimizations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cost optimizations: {str(e)}")

@router.get("/forecasts/{project_id}")
async def get_cost_forecasts(
    project_id: str,
    period: Optional[str] = Query("12_months", description="Forecast period (3_months, 6_months, 12_months)")
):
    """
    Get cost forecasts for a project
    """
    try:
        # Mock forecast data
        forecasts = {
            "project_id": project_id,
            "forecast_period": period,
            "currency": "USD",
            "base_monthly_cost": 371.15,
            "methodology": "linear_regression_with_seasonality",
            "forecasts": {
                "3_months": {
                    "period": "3_months",
                    "forecasted_cost": 1200.25,
                    "confidence_interval": [1020.21, 1380.29],
                    "growth_rate": 0.05,
                    "monthly_breakdown": [
                        {"month": 1, "cost": 389.71, "confidence": [331.25, 448.17]},
                        {"month": 2, "cost": 409.19, "confidence": [347.81, 470.57]},
                        {"month": 3, "cost": 429.65, "confidence": [365.20, 494.10]}
                    ],
                    "key_drivers": ["increased_usage", "service_expansion", "seasonal_growth"],
                    "assumptions": ["steady_growth", "no_major_changes", "current_pricing"]
                },
                "6_months": {
                    "period": "6_months",
                    "forecasted_cost": 2520.48,
                    "confidence_interval": [2142.41, 2898.55],
                    "growth_rate": 0.05,
                    "monthly_breakdown": [
                        {"month": 1, "cost": 389.71, "confidence": [331.25, 448.17]},
                        {"month": 2, "cost": 409.19, "confidence": [347.81, 470.57]},
                        {"month": 3, "cost": 429.65, "confidence": [365.20, 494.10]},
                        {"month": 4, "cost": 451.13, "confidence": [383.46, 518.80]},
                        {"month": 5, "cost": 473.69, "confidence": [402.64, 544.74]},
                        {"month": 6, "cost": 497.37, "confidence": [422.77, 571.97]}
                    ],
                    "key_drivers": ["user_growth", "feature_expansion", "data_growth"],
                    "assumptions": ["consistent_growth", "no_optimization", "stable_pricing"]
                },
                "12_months": {
                    "period": "12_months",
                    "forecasted_cost": 5450.78,
                    "confidence_interval": [4633.16, 6268.40],
                    "growth_rate": 0.05,
                    "monthly_breakdown": [
                        {"month": 1, "cost": 389.71, "confidence": [331.25, 448.17]},
                        {"month": 2, "cost": 409.19, "confidence": [347.81, 470.57]},
                        {"month": 3, "cost": 429.65, "confidence": [365.20, 494.10]},
                        {"month": 4, "cost": 451.13, "confidence": [383.46, 518.80]},
                        {"month": 5, "cost": 473.69, "confidence": [402.64, 544.74]},
                        {"month": 6, "cost": 497.37, "confidence": [422.77, 571.97]},
                        {"month": 7, "cost": 522.24, "confidence": [443.90, 600.58]},
                        {"month": 8, "cost": 548.35, "confidence": [466.10, 630.60]},
                        {"month": 9, "cost": 575.77, "confidence": [489.40, 662.14]},
                        {"month": 10, "cost": 604.56, "confidence": [513.87, 695.25]},
                        {"month": 11, "cost": 634.79, "confidence": [539.57, 730.01]},
                        {"month": 12, "cost": 666.53, "confidence": [566.55, 766.51]}
                    ],
                    "key_drivers": ["business_growth", "service_scaling", "market_expansion"],
                    "assumptions": ["sustained_growth", "technology_evolution", "pricing_stability"]
                }
            },
            "scenarios": {
                "optimistic": {
                    "description": "With cost optimizations implemented",
                    "12_month_cost": 4088.09,  # 25% savings
                    "savings": 1362.69
                },
                "pessimistic": {
                    "description": "Higher than expected growth",
                    "12_month_cost": 6540.94,  # 20% higher
                    "additional_cost": 1090.16
                },
                "baseline": {
                    "description": "Current trend continues",
                    "12_month_cost": 5450.78,
                    "variance": 0.0
                }
            },
            "recommendations": [
                "Implement recommended cost optimizations to achieve 25% savings",
                "Monitor usage patterns monthly to adjust forecasts",
                "Set up budget alerts at 80% and 90% thresholds",
                "Review and update forecasts quarterly"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        # Return specific period if requested
        if period in forecasts["forecasts"]:
            specific_forecast = forecasts["forecasts"][period]
            return {
                "status": "success",
                "project_id": project_id,
                "forecast": specific_forecast,
                "scenarios": forecasts["scenarios"],
                "recommendations": forecasts["recommendations"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "success",
                "project_id": project_id,
                "forecasts": forecasts,
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Error getting cost forecasts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cost forecasts: {str(e)}")

@router.get("/budget-status/{project_id}")
async def get_budget_status(project_id: str):
    """
    Get current budget status and alerts
    """
    try:
        budget_status = {
            "project_id": project_id,
            "budget_period": "monthly",
            "current_period": datetime.now().strftime("%Y-%m"),
            "budget_amount": 500.00,
            "spent_amount": 371.15,
            "remaining_amount": 128.85,
            "usage_percentage": 74.23,
            "projected_month_end": 445.38,
            "days_remaining": (datetime.now().replace(month=datetime.now().month+1, day=1) - timedelta(days=1) - datetime.now()).days,
            "daily_burn_rate": 12.37,
            "status": "on_track",
            "alerts": [
                {
                    "type": "budget_warning",
                    "severity": "medium",
                    "message": "70% of monthly budget consumed with 8 days remaining",
                    "threshold": 70.0,
                    "triggered_at": (datetime.now() - timedelta(hours=2)).isoformat()
                }
            ],
            "cost_breakdown": {
                "compute": {"amount": 245.60, "percentage": 66.2},
                "storage": {"amount": 48.95, "percentage": 13.2},
                "networking": {"amount": 31.20, "percentage": 8.4},
                "database": {"amount": 28.40, "percentage": 7.7},
                "other": {"amount": 17.00, "percentage": 4.5}
            },
            "trends": {
                "vs_last_month": {"change": 15.5, "direction": "increase"},
                "vs_budget": {"variance": -25.77, "direction": "under"},
                "weekly_trend": "increasing"
            },
            "recommendations": [
                "Current spending is on track to finish under budget",
                "Consider implementing spot instances to reduce compute costs",
                "Set up additional budget alerts at 85% and 95%"
            ],
            "next_review_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Determine status based on usage and projections
        if budget_status["projected_month_end"] > budget_status["budget_amount"]:
            budget_status["status"] = "over_budget_risk"
            budget_status["alerts"].append({
                "type": "budget_projection",
                "severity": "high",
                "message": f"Projected to exceed budget by ${budget_status['projected_month_end'] - budget_status['budget_amount']:.2f}",
                "threshold": 100.0,
                "triggered_at": datetime.now().isoformat()
            })
        elif budget_status["usage_percentage"] > 90:
            budget_status["status"] = "at_risk"
        elif budget_status["usage_percentage"] > 80:
            budget_status["status"] = "monitor"
        else:
            budget_status["status"] = "on_track"
        
        return {
            "status": "success",
            "budget_status": budget_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting budget status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get budget status: {str(e)}")

@router.get("/pricing/{service_type}")
async def get_real_time_pricing(
    service_type: str,
    region: str = Query("us-west-2", description="AWS region"),
    instance_type: Optional[str] = Query(None, description="Specific instance type")
):
    """
    Get real-time pricing for a specific service type
    """
    try:
        # Mock pricing data - would come from AWS Pricing API
        pricing_data = {
            "service_type": service_type,
            "region": region,
            "currency": "USD",
            "pricing_model": "on_demand",
            "last_updated": datetime.now().isoformat()
        }
        
        if service_type.lower() == "ec2":
            pricing_data["instances"] = [
                {
                    "instance_type": "t3.micro",
                    "vcpus": 2,
                    "memory_gb": 1,
                    "hourly_rate": 0.0104,
                    "monthly_estimate": 7.49,
                    "storage": "EBS only"
                },
                {
                    "instance_type": "t3.small",
                    "vcpus": 2,
                    "memory_gb": 2,
                    "hourly_rate": 0.0208,
                    "monthly_estimate": 14.98,
                    "storage": "EBS only"
                },
                {
                    "instance_type": "t3.medium",
                    "vcpus": 2,
                    "memory_gb": 4,
                    "hourly_rate": 0.0416,
                    "monthly_estimate": 29.95,
                    "storage": "EBS only"
                },
                {
                    "instance_type": "t3.large",
                    "vcpus": 2,
                    "memory_gb": 8,
                    "hourly_rate": 0.0832,
                    "monthly_estimate": 59.90,
                    "storage": "EBS only"
                }
            ]
            
            # Filter by instance type if provided
            if instance_type:
                pricing_data["instances"] = [
                    inst for inst in pricing_data["instances"] 
                    if inst["instance_type"] == instance_type
                ]
        
        elif service_type.lower() == "s3":
            pricing_data["storage_classes"] = [
                {
                    "class": "Standard",
                    "price_per_gb": 0.023,
                    "retrieval_cost": 0.0,
                    "minimum_duration": "None"
                },
                {
                    "class": "Standard-IA",
                    "price_per_gb": 0.0125,
                    "retrieval_cost": 0.01,
                    "minimum_duration": "30 days"
                },
                {
                    "class": "Glacier",
                    "price_per_gb": 0.004,
                    "retrieval_cost": 0.03,
                    "minimum_duration": "90 days"
                },
                {
                    "class": "Glacier Deep Archive",
                    "price_per_gb": 0.00099,
                    "retrieval_cost": 0.05,
                    "minimum_duration": "180 days"
                }
            ]
            
            pricing_data["requests"] = {
                "put_requests_per_1000": 0.005,
                "get_requests_per_1000": 0.0004,
                "delete_requests": 0.0
            }
        
        elif service_type.lower() == "rds":
            pricing_data["instances"] = [
                {
                    "instance_type": "db.t3.micro",
                    "vcpus": 2,
                    "memory_gb": 1,
                    "hourly_rate": 0.017,
                    "monthly_estimate": 12.24
                },
                {
                    "instance_type": "db.t3.small",
                    "vcpus": 2,
                    "memory_gb": 2,
                    "hourly_rate": 0.034,
                    "monthly_estimate": 24.48
                },
                {
                    "instance_type": "db.t3.medium",
                    "vcpus": 2,
                    "memory_gb": 4,
                    "hourly_rate": 0.068,
                    "monthly_estimate": 48.96
                }
            ]
            
            pricing_data["storage"] = {
                "gp2_per_gb": 0.115,
                "gp3_per_gb": 0.092,
                "io1_per_gb": 0.125,
                "backup_per_gb": 0.095
            }
        
        elif service_type.lower() == "lambda":
            pricing_data["pricing"] = {
                "requests_per_million": 0.20,
                "duration_per_gb_second": 0.0000166667,
                "free_tier": {
                    "requests": 1000000,
                    "gb_seconds": 400000
                }
            }
        
        else:
            pricing_data["message"] = f"Pricing data not available for service type: {service_type}"
        
        return {
            "status": "success",
            "pricing": pricing_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting real-time pricing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get pricing: {str(e)}")

@router.get("/cost-trends/{project_id}")
async def get_cost_trends(
    project_id: str,
    period: str = Query("30_days", description="Trend period (7_days, 30_days, 90_days)")
):
    """
    Get cost trends and patterns for a project
    """
    try:
        # Mock trend data
        trends = {
            "project_id": project_id,
            "period": period,
            "currency": "USD",
            "overall_trend": "increasing",
            "growth_rate": {
                "daily": 0.02,
                "weekly": 0.15,
                "monthly": 0.65
            },
            "cost_history": [],
            "service_trends": {
                "EC2": {"trend": "increasing", "change": 12.5},
                "S3": {"trend": "stable", "change": 2.1},
                "RDS": {"trend": "increasing", "change": 8.3},
                "Lambda": {"trend": "decreasing", "change": -5.2}
            },
            "anomalies": [
                {
                    "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                    "service": "EC2",
                    "impact": 45.60,
                    "description": "Unusual spike in compute usage"
                }
            ],
            "patterns": [
                "Higher usage during weekdays",
                "Peak usage between 9 AM - 5 PM",
                "Month-end processing spikes"
            ],
            "predictions": {
                "next_week": 89.50,
                "next_month": 425.30,
                "confidence": 82.5
            },
            "recommendations": [
                "Consider scheduling non-critical workloads during off-peak hours",
                "Implement auto-scaling to handle usage spikes efficiently",
                "Review month-end processing for optimization opportunities"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        # Generate mock historical data based on period
        days = {"7_days": 7, "30_days": 30, "90_days": 90}[period]
        base_cost = 12.37
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i-1)
            # Add some variation and trend
            daily_cost = base_cost + (i * 0.1) + (np.random.normal(0, 2) if 'numpy' in globals() else 0)
            trends["cost_history"].append({
                "date": date.strftime("%Y-%m-%d"),
                "cost": round(max(0, daily_cost), 2),
                "services": {
                    "EC2": round(daily_cost * 0.6, 2),
                    "S3": round(daily_cost * 0.15, 2),
                    "RDS": round(daily_cost * 0.2, 2),
                    "Lambda": round(daily_cost * 0.05, 2)
                }
            })
        
        return {
            "status": "success",
            "trends": trends,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting cost trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cost trends: {str(e)}")

@router.post("/trigger-cost-analysis")
async def trigger_cost_analysis(
    project_id: str,
    services: Dict[str, str],
    background_tasks: BackgroundTasks,
    aws_credentials: Optional[Dict[str, str]] = None
):
    """
    Trigger a comprehensive cost analysis in the background
    """
    try:
        def run_cost_analysis():
            """Background task to run cost analysis"""
            analyzer = get_cost_analyzer(aws_credentials)
            logger.info(f"Running comprehensive cost analysis for project {project_id}")
            # This would trigger a full analysis including:
            # - Real-time pricing updates
            # - Usage pattern analysis
            # - Optimization recommendations
            # - Forecast updates
        
        background_tasks.add_task(run_cost_analysis)
        
        return {
            "status": "success",
            "message": f"Cost analysis initiated for project {project_id}",
            "analysis_id": f"cost_analysis_{project_id}_{int(datetime.now().timestamp())}",
            "estimated_completion": (datetime.now() + timedelta(minutes=5)).isoformat(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering cost analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger cost analysis: {str(e)}")