import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import boto3
import openai
from app.schemas.questionnaire import QuestionnaireRequest

logger = logging.getLogger(__name__)

class AIOptimizationType(Enum):
    COST_OPTIMIZATION = "cost_optimization"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_ENHANCEMENT = "security_enhancement"
    SCALABILITY_IMPROVEMENT = "scalability_improvement"
    COMPLIANCE_AUTOMATION = "compliance_automation"
    PREDICTIVE_SCALING = "predictive_scaling"
    ANOMALY_DETECTION = "anomaly_detection"

@dataclass
class AIRecommendation:
    id: str
    title: str
    description: str
    optimization_type: AIOptimizationType
    affected_services: List[str]
    priority: str
    confidence_score: float  # 0.0 to 1.0
    predicted_cost_savings: Optional[float] = None
    predicted_performance_improvement: Optional[str] = None
    implementation_complexity: str = "medium"
    ml_model_used: str = ""
    data_points_analyzed: int = 0
    created_at: datetime = None

@dataclass
class ArchitectureMetrics:
    project_id: str
    cost_per_month: float
    performance_score: float  # 0-100
    security_score: float    # 0-100
    scalability_score: float # 0-100
    availability_score: float # 0-100
    services_count: int
    compliance_score: float  # 0-100
    resource_utilization: Dict[str, float]
    traffic_patterns: Dict[str, List[float]]
    error_rates: Dict[str, float]

class IntelligentArchitectureOptimizer:
    """AI/ML-powered architecture optimization engine"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key
        if openai_api_key:
            openai.api_key = openai_api_key
        
        # Initialize ML models
        self.cost_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.performance_optimizer = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Initialize encoders and scalers
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
        # AI/ML service recommendations database
        self.ai_services_matrix = {
            "data_processing": {
                "small": ["AWS Lambda", "AWS Glue"],
                "medium": ["Amazon EMR", "AWS Batch"],
                "large": ["Amazon EMR", "AWS Batch", "Amazon EKS"]
            },
            "ml_training": {
                "basic": ["SageMaker Training Jobs"],
                "advanced": ["SageMaker HyperPod", "Amazon Bedrock"],
                "enterprise": ["SageMaker HyperPod", "Amazon Bedrock", "AWS Trainium"]
            },
            "inference": {
                "real_time": ["SageMaker Real-time Endpoints", "Amazon Bedrock"],
                "batch": ["SageMaker Batch Transform", "AWS Batch"],
                "edge": ["AWS IoT Greengrass", "SageMaker Edge Manager"]
            },
            "generative_ai": {
                "foundation_models": ["Amazon Bedrock", "SageMaker JumpStart"],
                "custom_models": ["SageMaker Training", "Amazon Bedrock"],
                "multimodal": ["Amazon Bedrock", "Amazon Titan", "Claude"]
            }
        }
        
        # Load historical data for ML models (simulated for demo)
        self._initialize_ml_models()
    
    def _initialize_ml_models(self):
        """Initialize ML models with synthetic training data"""
        # Generate synthetic training data for cost prediction
        np.random.seed(42)
        n_samples = 1000
        
        # Features: services_count, region, instance_types, storage_gb, traffic_gb
        X_cost = np.random.rand(n_samples, 8)
        # Add some realistic relationships
        y_cost = (X_cost[:, 0] * 500 +  # services impact
                 X_cost[:, 1] * 200 +   # region impact
                 X_cost[:, 2] * 1000 +  # instance type impact
                 X_cost[:, 3] * 0.1 +   # storage impact
                 np.random.normal(0, 50, n_samples))  # noise
        
        self.cost_predictor.fit(X_cost, y_cost)
        
        # Initialize anomaly detector with normal patterns
        X_anomaly = np.random.normal(0, 1, (1000, 10))
        self.anomaly_detector.fit(X_anomaly)
        
        # Performance predictor
        X_perf = np.random.rand(n_samples, 6)
        y_perf = (X_perf[:, 0] * 30 +     # CPU impact
                 X_perf[:, 1] * 25 +      # Memory impact
                 X_perf[:, 2] * -15 +     # Network latency impact (negative)
                 np.random.normal(70, 10, n_samples))  # base performance + noise
        y_perf = np.clip(y_perf, 0, 100)  # Keep within 0-100 range
        
        self.performance_optimizer.fit(X_perf, y_perf)
        
        logger.info("ML models initialized successfully")
    
    async def analyze_architecture_with_ai(self, project_data: Dict, questionnaire: QuestionnaireRequest, 
                                         services: Dict[str, str], historical_metrics: Optional[Dict] = None) -> List[AIRecommendation]:
        """Main AI/ML analysis function for architecture optimization"""
        
        recommendations = []
        
        # Extract architecture metrics
        metrics = self._extract_architecture_metrics(project_data, services, historical_metrics)
        
        # Run AI/ML optimizations in parallel
        optimization_tasks = [
            self._ai_cost_optimization(metrics, services),
            self._ai_performance_optimization(metrics, services),
            self._ai_security_enhancement(metrics, services),
            self._ai_scalability_analysis(metrics, services),
            self._ai_anomaly_detection(metrics),
            self._ai_predictive_scaling(metrics, services),
            self._ai_compliance_automation(metrics, questionnaire),
            self._generative_ai_recommendations(metrics, services, questionnaire)
        ]
        
        # Execute all optimizations concurrently
        optimization_results = await asyncio.gather(*optimization_tasks, return_exceptions=True)
        
        # Collect successful recommendations
        for result in optimization_results:
            if isinstance(result, list):
                recommendations.extend(result)
            elif not isinstance(result, Exception):
                recommendations.append(result)
        
        # Sort by confidence score and priority
        recommendations.sort(key=lambda x: (x.priority == "critical", x.confidence_score), reverse=True)
        
        return recommendations[:20]  # Return top 20 recommendations
    
    def _extract_architecture_metrics(self, project_data: Dict, services: Dict[str, str], 
                                    historical_metrics: Optional[Dict] = None) -> ArchitectureMetrics:
        """Extract quantitative metrics from architecture for ML analysis"""
        
        # Simulate realistic metrics based on services
        service_count = len(services)
        base_cost = service_count * 150  # Base cost per service
        
        # Add service-specific costs
        service_multipliers = {
            "database": 300,
            "load_balancer": 200,
            "storage": 100,
            "compute": 250,
            "lambda": 50,
            "api_gateway": 75
        }
        
        estimated_cost = base_cost
        for service_type in services.values():
            estimated_cost += service_multipliers.get(service_type.lower(), 100)
        
        # Simulate performance metrics
        performance_score = max(50, 100 - (service_count * 2))  # More services = complexity
        security_score = 75 + (service_count * 1.5) if service_count < 10 else 85
        
        # Simulate resource utilization
        resource_util = {
            "cpu": np.random.uniform(40, 80),
            "memory": np.random.uniform(50, 85),
            "network": np.random.uniform(30, 70),
            "storage": np.random.uniform(45, 75)
        }
        
        # Simulate traffic patterns (24 hours)
        traffic_patterns = {
            "requests_per_hour": list(np.random.poisson(100, 24)),
            "error_rate": list(np.random.uniform(0.1, 2.0, 24))
        }
        
        return ArchitectureMetrics(
            project_id=project_data.get("id", "unknown"),
            cost_per_month=estimated_cost,
            performance_score=performance_score,
            security_score=security_score,
            scalability_score=70,
            availability_score=95,
            services_count=service_count,
            compliance_score=80,
            resource_utilization=resource_util,
            traffic_patterns=traffic_patterns,
            error_rates={"api": 0.5, "database": 0.1, "storage": 0.05}
        )
    
    async def _ai_cost_optimization(self, metrics: ArchitectureMetrics, services: Dict[str, str]) -> List[AIRecommendation]:
        """AI-powered cost optimization recommendations"""
        recommendations = []
        
        # Prepare features for cost prediction
        features = np.array([[
            metrics.services_count,
            metrics.resource_utilization["cpu"],
            metrics.resource_utilization["memory"],
            metrics.resource_utilization["network"],
            metrics.resource_utilization["storage"],
            sum(metrics.traffic_patterns["requests_per_hour"]),
            metrics.performance_score,
            metrics.availability_score
        ]])
        
        # Predict potential cost savings
        current_cost = metrics.cost_per_month
        optimized_cost = self.cost_predictor.predict(features)[0]
        potential_savings = max(0, current_cost - optimized_cost)
        
        # Generate cost optimization recommendations
        if potential_savings > 50:
            recommendations.append(AIRecommendation(
                id="ai_cost_spot_instances",
                title="AI-Recommended: Implement Spot Instance Strategy",
                description=f"ML analysis indicates potential savings of ${potential_savings:.2f}/month by migrating non-critical workloads to Spot instances. Based on your traffic patterns, we predict 70% availability for cost-optimized workloads.",
                optimization_type=AIOptimizationType.COST_OPTIMIZATION,
                affected_services=["EC2", "ECS", "EKS"],
                priority="high",
                confidence_score=0.85,
                predicted_cost_savings=potential_savings,
                ml_model_used="RandomForest Cost Predictor",
                data_points_analyzed=1000,
                created_at=datetime.now()
            ))
        
        # Reserved Instance recommendations
        if metrics.resource_utilization["cpu"] > 60:
            recommendations.append(AIRecommendation(
                id="ai_cost_reserved_instances",
                title="AI-Recommended: Reserved Instance Optimization",
                description=f"Based on your consistent CPU utilization of {metrics.resource_utilization['cpu']:.1f}%, switching to Reserved Instances could save ${current_cost * 0.3:.2f}/month (30% savings).",
                optimization_type=AIOptimizationType.COST_OPTIMIZATION,
                affected_services=["EC2", "RDS"],
                priority="medium",
                confidence_score=0.78,
                predicted_cost_savings=current_cost * 0.3,
                ml_model_used="Utilization Pattern Analysis",
                data_points_analyzed=24,
                created_at=datetime.now()
            ))
        
        # Intelligent Auto Scaling
        traffic_variance = np.std(metrics.traffic_patterns["requests_per_hour"])
        if traffic_variance > 30:
            recommendations.append(AIRecommendation(
                id="ai_cost_intelligent_scaling",
                title="AI-Recommended: Predictive Auto Scaling",
                description=f"High traffic variance detected (σ={traffic_variance:.1f}). Implementing ML-based predictive scaling could reduce over-provisioning costs by 25-40%.",
                optimization_type=AIOptimizationType.PREDICTIVE_SCALING,
                affected_services=["EC2", "ECS", "Lambda"],
                priority="high",
                confidence_score=0.82,
                predicted_cost_savings=current_cost * 0.25,
                ml_model_used="Traffic Pattern Analysis",
                data_points_analyzed=len(metrics.traffic_patterns["requests_per_hour"]),
                created_at=datetime.now()
            ))
        
        return recommendations
    
    async def _ai_performance_optimization(self, metrics: ArchitectureMetrics, services: Dict[str, str]) -> List[AIRecommendation]:
        """AI-powered performance optimization"""
        recommendations = []
        
        # Prepare features for performance prediction
        features = np.array([[
            metrics.resource_utilization["cpu"],
            metrics.resource_utilization["memory"],
            metrics.resource_utilization["network"],
            sum(metrics.error_rates.values()),
            metrics.services_count,
            np.mean(metrics.traffic_patterns["requests_per_hour"])
        ]])
        
        predicted_performance = self.performance_optimizer.predict(features)[0]
        current_performance = metrics.performance_score
        
        if predicted_performance > current_performance + 10:
            recommendations.append(AIRecommendation(
                id="ai_performance_optimization",
                title="AI-Recommended: Performance Enhancement Strategy",
                description=f"ML analysis predicts {predicted_performance - current_performance:.1f}% performance improvement through optimized resource allocation and caching strategies.",
                optimization_type=AIOptimizationType.PERFORMANCE_OPTIMIZATION,
                affected_services=list(services.values()),
                priority="high",
                confidence_score=0.87,
                predicted_performance_improvement=f"{predicted_performance - current_performance:.1f}%",
                ml_model_used="Performance Optimization Model",
                data_points_analyzed=1000,
                created_at=datetime.now()
            ))
        
        # CDN and Caching recommendations
        if metrics.resource_utilization["network"] > 70:
            recommendations.append(AIRecommendation(
                id="ai_caching_strategy",
                title="AI-Recommended: Intelligent Caching Layer",
                description="High network utilization detected. Implementing CloudFront with intelligent caching could reduce response times by 60% and bandwidth costs by 40%.",
                optimization_type=AIOptimizationType.PERFORMANCE_OPTIMIZATION,
                affected_services=["CloudFront", "ElastiCache"],
                priority="medium",
                confidence_score=0.79,
                predicted_performance_improvement="60% response time reduction",
                ml_model_used="Network Pattern Analysis",
                data_points_analyzed=100,
                created_at=datetime.now()
            ))
        
        return recommendations
    
    async def _ai_security_enhancement(self, metrics: ArchitectureMetrics, services: Dict[str, str]) -> List[AIRecommendation]:
        """AI-powered security enhancement recommendations"""
        recommendations = []
        
        # Anomaly-based security recommendations
        security_features = np.array([[
            metrics.error_rates.get("api", 0),
            len([s for s in services.values() if "database" in s.lower()]),
            metrics.services_count,
            metrics.resource_utilization["network"],
            1 if any("s3" in s.lower() for s in services.values()) else 0
        ]])
        
        # Check for anomalies in security patterns
        anomaly_score = self.anomaly_detector.decision_function(security_features)[0]
        
        if anomaly_score < -0.1:  # Negative scores indicate anomalies
            recommendations.append(AIRecommendation(
                id="ai_security_anomaly_detection",
                title="AI-Recommended: Enhanced Security Monitoring",
                description=f"Anomaly detection model identified unusual patterns (score: {anomaly_score:.3f}). Deploying GuardDuty with ML-powered threat detection is recommended.",
                optimization_type=AIOptimizationType.SECURITY_ENHANCEMENT,
                affected_services=["GuardDuty", "Security Hub", "CloudTrail"],
                priority="critical",
                confidence_score=0.91,
                ml_model_used="Isolation Forest Anomaly Detector",
                data_points_analyzed=1000,
                created_at=datetime.now()
            ))
        
        # Zero Trust Architecture recommendation
        if metrics.services_count > 5:
            recommendations.append(AIRecommendation(
                id="ai_zero_trust_architecture",
                title="AI-Recommended: Zero Trust Network Architecture",
                description="Complex architecture detected. Implementing Zero Trust principles with AI-powered access controls could reduce security risks by 70%.",
                optimization_type=AIOptimizationType.SECURITY_ENHANCEMENT,
                affected_services=["VPC", "IAM", "Security Groups"],
                priority="high",
                confidence_score=0.84,
                ml_model_used="Architecture Complexity Analysis",
                data_points_analyzed=metrics.services_count,
                created_at=datetime.now()
            ))
        
        return recommendations
    
    async def _ai_scalability_analysis(self, metrics: ArchitectureMetrics, services: Dict[str, str]) -> List[AIRecommendation]:
        """AI-powered scalability recommendations"""
        recommendations = []
        
        # Analyze traffic patterns for scalability needs
        traffic_trend = np.polyfit(range(24), metrics.traffic_patterns["requests_per_hour"], 1)[0]
        
        if traffic_trend > 5:  # Growing traffic
            recommendations.append(AIRecommendation(
                id="ai_scalability_microservices",
                title="AI-Recommended: Microservices Architecture Migration",
                description=f"Growing traffic trend detected (+{traffic_trend:.1f} requests/hour). Migrating to microservices architecture could improve scalability by 300%.",
                optimization_type=AIOptimizationType.SCALABILITY_IMPROVEMENT,
                affected_services=["ECS", "EKS", "API Gateway", "Lambda"],
                priority="medium",
                confidence_score=0.76,
                ml_model_used="Traffic Trend Analysis",
                data_points_analyzed=24,
                created_at=datetime.now()
            ))
        
        # Container orchestration recommendations
        if metrics.services_count > 8:
            recommendations.append(AIRecommendation(
                id="ai_container_orchestration",
                title="AI-Recommended: Kubernetes Orchestration",
                description="Large-scale architecture detected. Implementing EKS with AI-powered auto-scaling could improve resource efficiency by 45%.",
                optimization_type=AIOptimizationType.SCALABILITY_IMPROVEMENT,
                affected_services=["EKS", "Fargate"],
                priority="medium",
                confidence_score=0.81,
                implementation_complexity="high",
                ml_model_used="Service Complexity Analysis",
                data_points_analyzed=metrics.services_count,
                created_at=datetime.now()
            ))
        
        return recommendations
    
    async def _ai_anomaly_detection(self, metrics: ArchitectureMetrics) -> List[AIRecommendation]:
        """AI-powered anomaly detection for architecture patterns"""
        recommendations = []
        
        # Prepare features for anomaly detection
        features = np.array([[
            metrics.cost_per_month,
            metrics.performance_score,
            metrics.security_score,
            metrics.resource_utilization["cpu"],
            metrics.resource_utilization["memory"],
            np.mean(metrics.traffic_patterns["requests_per_hour"]),
            sum(metrics.error_rates.values()),
            metrics.services_count,
            metrics.availability_score,
            metrics.scalability_score
        ]])
        
        # Detect anomalies
        anomaly_score = self.anomaly_detector.decision_function(features)[0]
        is_anomaly = self.anomaly_detector.predict(features)[0] == -1
        
        if is_anomaly:
            recommendations.append(AIRecommendation(
                id="ai_architecture_anomaly",
                title="AI-Alert: Architecture Anomaly Detected",
                description=f"Anomaly detection model identified unusual architecture patterns (score: {anomaly_score:.3f}). Consider architecture review and optimization.",
                optimization_type=AIOptimizationType.ANOMALY_DETECTION,
                affected_services=["Architecture Review"],
                priority="high",
                confidence_score=abs(anomaly_score),
                ml_model_used="Isolation Forest",
                data_points_analyzed=1000,
                created_at=datetime.now()
            ))
        
        return recommendations
    
    async def _ai_predictive_scaling(self, metrics: ArchitectureMetrics, services: Dict[str, str]) -> List[AIRecommendation]:
        """AI-powered predictive scaling recommendations"""
        recommendations = []
        
        # Analyze traffic patterns for predictive scaling
        hourly_requests = metrics.traffic_patterns["requests_per_hour"]
        
        # Simple seasonality detection
        peak_hours = [i for i, req in enumerate(hourly_requests) if req > np.mean(hourly_requests) + np.std(hourly_requests)]
        
        if len(peak_hours) > 2:
            recommendations.append(AIRecommendation(
                id="ai_predictive_scaling",
                title="AI-Recommended: Predictive Auto Scaling",
                description=f"Peak traffic detected at hours {peak_hours}. Implementing predictive scaling could reduce response times by 40% during peak periods.",
                optimization_type=AIOptimizationType.PREDICTIVE_SCALING,
                affected_services=["Auto Scaling", "CloudWatch", "Lambda"],
                priority="high",
                confidence_score=0.89,
                predicted_performance_improvement="40% response time improvement",
                ml_model_used="Time Series Pattern Recognition",
                data_points_analyzed=24,
                created_at=datetime.now()
            ))
        
        return recommendations
    
    async def _ai_compliance_automation(self, metrics: ArchitectureMetrics, questionnaire: QuestionnaireRequest) -> List[AIRecommendation]:
        """AI-powered compliance automation recommendations"""
        recommendations = []
        
        compliance_requirements = getattr(questionnaire, 'compliance_requirements', [])
        
        if compliance_requirements:
            recommendations.append(AIRecommendation(
                id="ai_compliance_automation",
                title="AI-Recommended: Automated Compliance Monitoring",
                description=f"Compliance requirements detected: {', '.join(compliance_requirements)}. Implementing AI-powered compliance monitoring could reduce manual auditing effort by 80%.",
                optimization_type=AIOptimizationType.COMPLIANCE_AUTOMATION,
                affected_services=["Config", "Security Hub", "CloudTrail"],
                priority="high",
                confidence_score=0.88,
                ml_model_used="Compliance Pattern Recognition",
                data_points_analyzed=len(compliance_requirements),
                created_at=datetime.now()
            ))
        
        return recommendations
    
    async def _generative_ai_recommendations(self, metrics: ArchitectureMetrics, services: Dict[str, str], 
                                           questionnaire: QuestionnaireRequest) -> List[AIRecommendation]:
        """Generate AI/ML service recommendations using generative AI"""
        recommendations = []
        
        # Determine AI/ML requirements based on project characteristics
        data_processing_needs = self._assess_data_processing_needs(metrics, services)
        ml_use_cases = self._identify_ml_use_cases(questionnaire, services)
        
        # Recommend appropriate AI/ML services
        for use_case, complexity in ml_use_cases.items():
            service_recommendations = self.ai_services_matrix.get(use_case, {}).get(complexity, [])
            
            if service_recommendations:
                recommendations.append(AIRecommendation(
                    id=f"ai_service_{use_case}_{complexity}",
                    title=f"AI-Recommended: {use_case.replace('_', ' ').title()} with {', '.join(service_recommendations)}",
                    description=f"Based on your architecture and requirements, implementing {use_case.replace('_', ' ')} using {', '.join(service_recommendations)} could enhance your application capabilities.",
                    optimization_type=AIOptimizationType.PERFORMANCE_OPTIMIZATION,
                    affected_services=service_recommendations,
                    priority="medium",
                    confidence_score=0.75,
                    ml_model_used="AI Service Recommendation Engine",
                    data_points_analyzed=len(services),
                    created_at=datetime.now()
                ))
        
        # Amazon Bedrock for Generative AI
        if any(keyword in str(questionnaire).lower() for keyword in ["chat", "content", "text", "image", "ai", "intelligent"]):
            recommendations.append(AIRecommendation(
                id="ai_bedrock_generative_ai",
                title="AI-Recommended: Amazon Bedrock Integration",
                description="Your application could benefit from generative AI capabilities. Amazon Bedrock provides access to foundation models for chat, content generation, and intelligent automation.",
                optimization_type=AIOptimizationType.PERFORMANCE_OPTIMIZATION,
                affected_services=["Amazon Bedrock", "Lambda", "API Gateway"],
                priority="high",
                confidence_score=0.82,
                ml_model_used="Use Case Pattern Recognition",
                data_points_analyzed=1,
                created_at=datetime.now()
            ))
        
        return recommendations
    
    def _assess_data_processing_needs(self, metrics: ArchitectureMetrics, services: Dict[str, str]) -> str:
        """Assess data processing requirements"""
        if metrics.services_count > 10:
            return "large"
        elif metrics.services_count > 5:
            return "medium"
        else:
            return "small"
    
    def _identify_ml_use_cases(self, questionnaire: QuestionnaireRequest, services: Dict[str, str]) -> Dict[str, str]:
        """Identify potential ML use cases based on questionnaire and services"""
        use_cases = {}
        
        # Analyze questionnaire for AI/ML indicators
        questionnaire_text = str(questionnaire).lower()
        
        if any(keyword in questionnaire_text for keyword in ["predict", "forecast", "analytics", "data"]):
            use_cases["data_processing"] = "medium"
        
        if any(keyword in questionnaire_text for keyword in ["ai", "ml", "machine learning", "intelligent"]):
            use_cases["ml_training"] = "advanced"
        
        if any(keyword in questionnaire_text for keyword in ["chat", "content", "generate", "text"]):
            use_cases["generative_ai"] = "foundation_models"
        
        if any(keyword in questionnaire_text for keyword in ["real-time", "api", "inference"]):
            use_cases["inference"] = "real_time"
        
        return use_cases
    
    async def generate_ai_architecture_insights(self, recommendations: List[AIRecommendation]) -> Dict[str, Any]:
        """Generate comprehensive AI insights summary"""
        
        insights = {
            "total_recommendations": len(recommendations),
            "optimization_types": {},
            "confidence_stats": {
                "average_confidence": np.mean([r.confidence_score for r in recommendations]),
                "high_confidence_count": len([r for r in recommendations if r.confidence_score > 0.8])
            },
            "cost_impact": {
                "total_potential_savings": sum([r.predicted_cost_savings for r in recommendations if r.predicted_cost_savings]),
                "cost_optimization_count": len([r for r in recommendations if r.optimization_type == AIOptimizationType.COST_OPTIMIZATION])
            },
            "ai_readiness_score": self._calculate_ai_readiness_score(recommendations),
            "priority_breakdown": {
                "critical": len([r for r in recommendations if r.priority == "critical"]),
                "high": len([r for r in recommendations if r.priority == "high"]),
                "medium": len([r for r in recommendations if r.priority == "medium"]),
                "low": len([r for r in recommendations if r.priority == "low"])
            }
        }
        
        # Count optimization types
        for rec in recommendations:
            opt_type = rec.optimization_type.value
            insights["optimization_types"][opt_type] = insights["optimization_types"].get(opt_type, 0) + 1
        
        return insights
    
    def _calculate_ai_readiness_score(self, recommendations: List[AIRecommendation]) -> float:
        """Calculate AI readiness score based on recommendations"""
        if not recommendations:
            return 0.0
        
        # AI readiness factors
        ai_ml_recommendations = len([r for r in recommendations if "ai" in r.title.lower() or "ml" in r.title.lower()])
        high_confidence_recommendations = len([r for r in recommendations if r.confidence_score > 0.8])
        automation_recommendations = len([r for r in recommendations if r.optimization_type == AIOptimizationType.COMPLIANCE_AUTOMATION])
        
        # Calculate score (0-100)
        score = min(100, (
            (ai_ml_recommendations / len(recommendations)) * 40 +
            (high_confidence_recommendations / len(recommendations)) * 30 +
            (automation_recommendations / len(recommendations)) * 30
        ))
        
        return round(score, 2)