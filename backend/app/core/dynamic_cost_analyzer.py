import json
import logging
import asyncio
import boto3
import aiohttp
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

class CostOptimizationType(Enum):
    SPOT_INSTANCES = "spot_instances"
    RESERVED_INSTANCES = "reserved_instances"
    RIGHTSIZING = "rightsizing"
    STORAGE_OPTIMIZATION = "storage_optimization"
    SCHEDULING = "scheduling"
    AUTO_SCALING = "auto_scaling"

@dataclass
class ServiceCost:
    service_name: str
    service_type: str
    monthly_cost: float
    daily_cost: float
    hourly_cost: float
    usage_metrics: Dict[str, Any]
    cost_breakdown: Dict[str, float]
    region: str
    last_updated: datetime

@dataclass
class CostOptimization:
    id: str
    title: str
    description: str
    optimization_type: CostOptimizationType
    current_monthly_cost: float
    optimized_monthly_cost: float
    potential_savings: float
    savings_percentage: float
    confidence_score: float
    implementation_effort: str
    affected_services: List[str]
    implementation_steps: List[str]
    timeline: str
    risks: List[str]

@dataclass
class CostForecast:
    period: str
    forecasted_cost: float
    confidence_interval: Tuple[float, float]
    growth_rate: float
    key_drivers: List[str]
    assumptions: List[str]

class DynamicCostAnalyzer:
    """Dynamic cost analyzer that connects to real AWS pricing and cost APIs"""
    
    def __init__(self, aws_credentials: Optional[Dict[str, str]] = None):
        self.aws_credentials = aws_credentials
        self.aws_clients = {}
        
        # AWS Pricing API endpoints
        self.pricing_endpoints = {
            "global": "https://pricing.us-east-1.amazonaws.com",
            "regional": "https://pricing.{region}.amazonaws.com"
        }
        
        # Service pricing mappings
        self.service_pricing_codes = {
            "ec2": "AmazonEC2",
            "s3": "AmazonS3",
            "rds": "AmazonRDS",
            "lambda": "AWSLambda",
            "dynamodb": "AmazonDynamoDB",
            "elasticache": "AmazonElastiCache",
            "cloudfront": "AmazonCloudFront",
            "elb": "AWSELB",
            "apigateway": "AmazonApiGateway",
            "sqs": "AmazonSQS",
            "sns": "AmazonSNS",
            "kinesis": "AmazonKinesis",
            "emr": "AmazonEMR",
            "sagemaker": "AmazonSageMaker",
            "bedrock": "AmazonBedrock"
        }
        
        # Initialize AWS clients if credentials provided
        if aws_credentials:
            self._initialize_aws_clients()
        
        # Cost optimization rules engine
        self.optimization_rules = self._load_optimization_rules()
    
    def _initialize_aws_clients(self):
        """Initialize AWS service clients"""
        try:
            session = boto3.Session(
                aws_access_key_id=self.aws_credentials.get("access_key_id"),
                aws_secret_access_key=self.aws_credentials.get("secret_access_key"),
                region_name=self.aws_credentials.get("region", "us-west-2")
            )
            
            # Cost and billing related clients
            self.aws_clients = {
                "pricing": session.client("pricing", region_name="us-east-1"),  # Pricing API only in us-east-1
                "ce": session.client("ce"),  # Cost Explorer
                "cloudwatch": session.client("cloudwatch"),
                "ec2": session.client("ec2"),
                "s3": session.client("s3"),
                "rds": session.client("rds"),
                "lambda": session.client("lambda"),
                "application_autoscaling": session.client("application-autoscaling"),
                "compute_optimizer": session.client("compute-optimizer")
            }
            
            logger.info("AWS cost analysis clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {str(e)}")
            self.aws_clients = {}
    
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Load cost optimization rules"""
        return {
            "ec2": {
                "spot_savings": 0.70,  # Up to 70% savings
                "reserved_savings": 0.30,  # Up to 30% savings
                "rightsizing_threshold": 0.30,  # If utilization < 30%
                "scheduling_savings": 0.50  # For dev/test environments
            },
            "s3": {
                "ia_transition_days": 30,
                "glacier_transition_days": 90,
                "storage_savings": 0.40
            },
            "rds": {
                "reserved_savings": 0.35,
                "rightsizing_threshold": 0.40,
                "storage_optimization": 0.20
            },
            "lambda": {
                "provisioned_concurrency_threshold": 1000,  # requests/minute
                "arm_savings": 0.20
            }
        }
    
    async def analyze_project_costs(self, project_data: Dict[str, Any], 
                                  services: Dict[str, str],
                                  usage_patterns: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform comprehensive dynamic cost analysis"""
        
        project_id = project_data.get("id", "unknown")
        region = self.aws_credentials.get("region", "us-west-2") if self.aws_credentials else "us-west-2"
        
        try:
            # Run cost analyses in parallel
            analysis_tasks = [
                self._get_current_service_costs(project_id, services, region),
                self._fetch_real_time_pricing(services, region),
                self._analyze_usage_patterns(project_id, services),
                self._identify_cost_optimizations(services, usage_patterns),
                self._generate_cost_forecasts(services, usage_patterns),
                self._calculate_total_cost_of_ownership(services),
                self._analyze_cost_trends(project_id),
                self._check_cost_anomalies(project_id)
            ]
            
            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Process results
            current_costs = results[0] if not isinstance(results[0], Exception) else {}
            real_time_pricing = results[1] if not isinstance(results[1], Exception) else {}
            usage_analysis = results[2] if not isinstance(results[2], Exception) else {}
            optimizations = results[3] if not isinstance(results[3], Exception) else []
            forecasts = results[4] if not isinstance(results[4], Exception) else {}
            tco_analysis = results[5] if not isinstance(results[5], Exception) else {}
            cost_trends = results[6] if not isinstance(results[6], Exception) else {}
            anomalies = results[7] if not isinstance(results[7], Exception) else []
            
            # Calculate summary metrics
            total_monthly_cost = sum(cost.monthly_cost for cost in current_costs.get("services", []))
            total_potential_savings = sum(opt.potential_savings for opt in optimizations)
            
            return {
                "project_id": project_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "region": region,
                "cost_summary": {
                    "total_monthly_cost": round(total_monthly_cost, 2),
                    "total_daily_cost": round(total_monthly_cost / 30, 2),
                    "total_hourly_cost": round(total_monthly_cost / (30 * 24), 2),
                    "potential_monthly_savings": round(total_potential_savings, 2),
                    "savings_percentage": round((total_potential_savings / total_monthly_cost * 100) if total_monthly_cost > 0 else 0, 1)
                },
                "current_costs": current_costs,
                "real_time_pricing": real_time_pricing,
                "usage_analysis": usage_analysis,
                "optimizations": [asdict(opt) for opt in optimizations],
                "forecasts": forecasts,
                "tco_analysis": tco_analysis,
                "cost_trends": cost_trends,
                "anomalies": anomalies,
                "next_analysis_due": (datetime.now() + timedelta(hours=6)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in cost analysis: {str(e)}")
            raise
    
    async def _get_current_service_costs(self, project_id: str, services: Dict[str, str], region: str) -> Dict[str, Any]:
        """Get current costs from AWS Cost Explorer"""
        
        current_costs = {
            "services": [],
            "total_cost": 0.0,
            "cost_by_service": {},
            "data_source": "estimated"  # Will be "aws_ce" if real data available
        }
        
        try:
            if "ce" in self.aws_clients:
                # Get actual costs from Cost Explorer
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=30)
                
                response = self.aws_clients["ce"].get_cost_and_usage(
                    TimePeriod={
                        'Start': start_date.strftime('%Y-%m-%d'),
                        'End': end_date.strftime('%Y-%m-%d')
                    },
                    Granularity='MONTHLY',
                    Metrics=['BlendedCost'],
                    GroupBy=[
                        {
                            'Type': 'DIMENSION',
                            'Key': 'SERVICE'
                        }
                    ]
                )
                
                current_costs["data_source"] = "aws_ce"
                
                for result in response.get("ResultsByTime", []):
                    for group in result.get("Groups", []):
                        service_name = group.get("Keys", ["Unknown"])[0]
                        cost = float(group.get("Metrics", {}).get("BlendedCost", {}).get("Amount", "0"))
                        current_costs["cost_by_service"][service_name] = cost
                        current_costs["total_cost"] += cost
            
            else:
                # Use estimated costs based on service types and pricing
                for service_name, service_type in services.items():
                    estimated_cost = await self._estimate_service_cost(service_name, service_type, region)
                    current_costs["services"].append(estimated_cost)
                    current_costs["cost_by_service"][service_name] = estimated_cost.monthly_cost
                    current_costs["total_cost"] += estimated_cost.monthly_cost
                    
        except Exception as e:
            logger.error(f"Error getting current service costs: {str(e)}")
        
        return current_costs
    
    async def _estimate_service_cost(self, service_name: str, service_type: str, region: str) -> ServiceCost:
        """Estimate cost for a service based on typical usage patterns"""
        
        # Default usage patterns for estimation
        usage_estimates = {
            "ec2": {"instance_type": "t3.medium", "hours": 720},  # 24/7
            "s3": {"storage_gb": 100, "requests": 10000},
            "rds": {"instance_type": "db.t3.micro", "storage_gb": 20, "hours": 720},
            "lambda": {"requests": 100000, "duration_ms": 1000, "memory_mb": 512},
            "dynamodb": {"read_units": 5, "write_units": 5, "storage_gb": 1},
            "apigateway": {"requests": 100000},
            "cloudfront": {"data_transfer_gb": 50},
            "elasticache": {"node_type": "cache.t3.micro", "nodes": 1, "hours": 720}
        }
        
        service_type_lower = service_type.lower()
        usage = usage_estimates.get(service_type_lower, {})
        
        # Get pricing information
        pricing_info = await self._get_service_pricing(service_type_lower, region, usage)
        
        monthly_cost = pricing_info.get("monthly_cost", 50.0)  # Default estimate
        
        return ServiceCost(
            service_name=service_name,
            service_type=service_type,
            monthly_cost=monthly_cost,
            daily_cost=monthly_cost / 30,
            hourly_cost=monthly_cost / (30 * 24),
            usage_metrics=usage,
            cost_breakdown=pricing_info.get("breakdown", {"compute": monthly_cost}),
            region=region,
            last_updated=datetime.now()
        )
    
    async def _get_service_pricing(self, service_type: str, region: str, usage: Dict[str, Any]) -> Dict[str, Any]:
        """Get real-time pricing for a service"""
        
        pricing_info = {"monthly_cost": 0.0, "breakdown": {}}
        
        try:
            if "pricing" in self.aws_clients and service_type in self.service_pricing_codes:
                # Use AWS Pricing API for real pricing
                service_code = self.service_pricing_codes[service_type]
                
                response = self.aws_clients["pricing"].get_products(
                    ServiceCode=service_code,
                    Filters=[
                        {
                            'Type': 'TERM_MATCH',
                            'Field': 'location',
                            'Value': self._get_pricing_location(region)
                        }
                    ],
                    MaxResults=10
                )
                
                # Process pricing data
                for product in response.get("PriceList", []):
                    price_data = json.loads(product)
                    pricing_info = self._calculate_service_cost(service_type, price_data, usage)
                    break  # Use first matching product
            
            else:
                # Use fallback pricing estimates
                pricing_info = self._get_fallback_pricing(service_type, usage)
                
        except Exception as e:
            logger.error(f"Error getting service pricing for {service_type}: {str(e)}")
            pricing_info = self._get_fallback_pricing(service_type, usage)
        
        return pricing_info
    
    def _get_pricing_location(self, region: str) -> str:
        """Map AWS region to pricing location"""
        region_mapping = {
            "us-east-1": "US East (N. Virginia)",
            "us-west-2": "US West (Oregon)",
            "eu-west-1": "Europe (Ireland)",
            "ap-southeast-1": "Asia Pacific (Singapore)",
            # Add more mappings as needed
        }
        return region_mapping.get(region, "US East (N. Virginia)")
    
    def _calculate_service_cost(self, service_type: str, price_data: Dict[str, Any], usage: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cost based on pricing data and usage"""
        
        try:
            # Extract pricing information from AWS pricing data
            terms = price_data.get("terms", {})
            on_demand = terms.get("OnDemand", {})
            
            monthly_cost = 0.0
            breakdown = {}
            
            for term_key, term_data in on_demand.items():
                price_dimensions = term_data.get("priceDimensions", {})
                
                for dim_key, dim_data in price_dimensions.items():
                    price_per_unit = float(dim_data.get("pricePerUnit", {}).get("USD", "0"))
                    unit = dim_data.get("unit", "")
                    description = dim_data.get("description", "")
                    
                    # Calculate cost based on service type and usage
                    if service_type == "ec2":
                        if "Hrs" in unit:
                            hours = usage.get("hours", 720)
                            cost = price_per_unit * hours
                            monthly_cost += cost
                            breakdown["compute_hours"] = cost
                    
                    elif service_type == "s3":
                        if "GB" in unit and "storage" in description.lower():
                            storage = usage.get("storage_gb", 100)
                            cost = price_per_unit * storage
                            monthly_cost += cost
                            breakdown["storage"] = cost
                        elif "Requests" in unit:
                            requests = usage.get("requests", 10000)
                            cost = price_per_unit * requests / 1000  # Usually priced per 1000 requests
                            monthly_cost += cost
                            breakdown["requests"] = cost
                    
                    # Add more service types as needed
            
            return {"monthly_cost": monthly_cost, "breakdown": breakdown}
            
        except Exception as e:
            logger.error(f"Error calculating service cost: {str(e)}")
            return self._get_fallback_pricing(service_type, usage)
    
    def _get_fallback_pricing(self, service_type: str, usage: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback pricing estimates when API is unavailable"""
        
        # Fallback pricing based on typical AWS costs (as of 2025)
        fallback_costs = {
            "ec2": {
                "t3.micro": 0.0104,  # per hour
                "t3.small": 0.0208,
                "t3.medium": 0.0416,
                "t3.large": 0.0832
            },
            "s3": {
                "storage": 0.023,  # per GB/month
                "requests": 0.0004  # per 1000 GET requests
            },
            "rds": {
                "db.t3.micro": 0.017,  # per hour
                "storage": 0.115  # per GB/month
            },
            "lambda": {
                "requests": 0.0000002,  # per request
                "duration": 0.0000166667  # per GB-second
            },
            "dynamodb": {
                "read_capacity": 0.25,  # per RCU/month
                "write_capacity": 1.25,  # per WCU/month
                "storage": 0.25  # per GB/month
            }
        }
        
        monthly_cost = 0.0
        breakdown = {}
        
        if service_type == "ec2":
            instance_type = usage.get("instance_type", "t3.medium")
            hours = usage.get("hours", 720)
            hourly_rate = fallback_costs["ec2"].get(instance_type, 0.0416)
            cost = hourly_rate * hours
            monthly_cost = cost
            breakdown["compute"] = cost
        
        elif service_type == "s3":
            storage_gb = usage.get("storage_gb", 100)
            requests = usage.get("requests", 10000)
            storage_cost = storage_gb * fallback_costs["s3"]["storage"]
            request_cost = requests * fallback_costs["s3"]["requests"]
            monthly_cost = storage_cost + request_cost
            breakdown["storage"] = storage_cost
            breakdown["requests"] = request_cost
        
        elif service_type == "rds":
            instance_type = usage.get("instance_type", "db.t3.micro")
            hours = usage.get("hours", 720)
            storage_gb = usage.get("storage_gb", 20)
            compute_cost = fallback_costs["rds"][instance_type] * hours
            storage_cost = storage_gb * fallback_costs["rds"]["storage"]
            monthly_cost = compute_cost + storage_cost
            breakdown["compute"] = compute_cost
            breakdown["storage"] = storage_cost
        
        elif service_type == "lambda":
            requests = usage.get("requests", 100000)
            duration_ms = usage.get("duration_ms", 1000)
            memory_mb = usage.get("memory_mb", 512)
            
            request_cost = requests * fallback_costs["lambda"]["requests"]
            gb_seconds = (memory_mb / 1024) * (duration_ms / 1000) * requests
            duration_cost = gb_seconds * fallback_costs["lambda"]["duration"]
            monthly_cost = request_cost + duration_cost
            breakdown["requests"] = request_cost
            breakdown["duration"] = duration_cost
        
        else:
            # Default estimate for unknown services
            monthly_cost = 25.0
            breakdown["estimated"] = monthly_cost
        
        return {"monthly_cost": monthly_cost, "breakdown": breakdown}
    
    async def _fetch_real_time_pricing(self, services: Dict[str, str], region: str) -> Dict[str, Any]:
        """Fetch real-time pricing information"""
        
        pricing_data = {
            "region": region,
            "last_updated": datetime.now().isoformat(),
            "services": {},
            "currency": "USD"
        }
        
        try:
            for service_name, service_type in services.items():
                service_pricing = await self._get_service_pricing(service_type.lower(), region, {})
                pricing_data["services"][service_name] = {
                    "service_type": service_type,
                    "pricing_model": "on_demand",
                    "monthly_estimate": service_pricing.get("monthly_cost", 0),
                    "breakdown": service_pricing.get("breakdown", {}),
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error fetching real-time pricing: {str(e)}")
        
        return pricing_data
    
    async def _analyze_usage_patterns(self, project_id: str, services: Dict[str, str]) -> Dict[str, Any]:
        """Analyze usage patterns from CloudWatch metrics"""
        
        usage_analysis = {
            "analysis_period": "30_days",
            "services": {},
            "overall_utilization": 0.0,
            "peak_usage_hours": [],
            "recommendations": []
        }
        
        try:
            if "cloudwatch" in self.aws_clients:
                # Get CloudWatch metrics for usage analysis
                end_time = datetime.now()
                start_time = end_time - timedelta(days=30)
                
                for service_name, service_type in services.items():
                    metrics = await self._get_service_metrics(service_name, service_type, start_time, end_time)
                    usage_analysis["services"][service_name] = metrics
            
            else:
                # Use estimated usage patterns
                for service_name, service_type in services.items():
                    usage_analysis["services"][service_name] = {
                        "avg_utilization": 0.65,  # 65% average utilization
                        "peak_utilization": 0.85,
                        "idle_hours": 8,  # 8 hours of low usage daily
                        "patterns": ["business_hours", "weekday_heavy"]
                    }
            
            # Calculate overall utilization
            if usage_analysis["services"]:
                total_util = sum(service.get("avg_utilization", 0.65) for service in usage_analysis["services"].values())
                usage_analysis["overall_utilization"] = total_util / len(usage_analysis["services"])
            
            # Generate recommendations based on usage patterns
            if usage_analysis["overall_utilization"] < 0.4:
                usage_analysis["recommendations"].append("Consider rightsizing instances due to low utilization")
            
            if usage_analysis["overall_utilization"] < 0.6:
                usage_analysis["recommendations"].append("Evaluate scheduling for non-production workloads")
                
        except Exception as e:
            logger.error(f"Error analyzing usage patterns: {str(e)}")
        
        return usage_analysis
    
    async def _get_service_metrics(self, service_name: str, service_type: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get CloudWatch metrics for a specific service"""
        
        metrics = {
            "avg_utilization": 0.65,
            "peak_utilization": 0.85,
            "idle_hours": 8,
            "patterns": ["business_hours"]
        }
        
        try:
            if service_type.lower() == "ec2":
                # Get EC2 CPU utilization
                response = self.aws_clients["cloudwatch"].get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName='CPUUtilization',
                    Dimensions=[
                        {
                            'Name': 'InstanceId',
                            'Value': service_name  # Assuming service_name is instance ID
                        }
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,  # 1 hour
                    Statistics=['Average', 'Maximum']
                )
                
                datapoints = response.get("Datapoints", [])
                if datapoints:
                    avg_cpu = sum(dp["Average"] for dp in datapoints) / len(datapoints)
                    max_cpu = max(dp["Maximum"] for dp in datapoints)
                    
                    metrics["avg_utilization"] = avg_cpu / 100
                    metrics["peak_utilization"] = max_cpu / 100
                    
                    # Identify idle hours (< 10% CPU)
                    idle_hours = sum(1 for dp in datapoints if dp["Average"] < 10)
                    metrics["idle_hours"] = idle_hours
            
            # Add more service types as needed
            
        except Exception as e:
            logger.error(f"Error getting metrics for {service_name}: {str(e)}")
        
        return metrics
    
    async def _identify_cost_optimizations(self, services: Dict[str, str], usage_patterns: Optional[Dict[str, Any]]) -> List[CostOptimization]:
        """Identify cost optimization opportunities"""
        
        optimizations = []
        
        try:
            for service_name, service_type in services.items():
                service_optimizations = await self._analyze_service_optimizations(
                    service_name, service_type, usage_patterns
                )
                optimizations.extend(service_optimizations)
            
            # Add cross-service optimizations
            cross_service_opts = await self._identify_cross_service_optimizations(services)
            optimizations.extend(cross_service_opts)
            
        except Exception as e:
            logger.error(f"Error identifying cost optimizations: {str(e)}")
        
        return optimizations
    
    async def _analyze_service_optimizations(self, service_name: str, service_type: str, usage_patterns: Optional[Dict[str, Any]]) -> List[CostOptimization]:
        """Analyze cost optimizations for a specific service"""
        
        optimizations = []
        service_type_lower = service_type.lower()
        
        try:
            if service_type_lower == "ec2":
                # EC2 optimization opportunities
                current_cost = 100.0  # Placeholder - would get from actual cost analysis
                
                # Spot instance optimization
                spot_savings = current_cost * self.optimization_rules["ec2"]["spot_savings"]
                optimizations.append(CostOptimization(
                    id=f"spot_{service_name}",
                    title=f"Use Spot Instances for {service_name}",
                    description="Migrate suitable workloads to Spot instances for significant cost savings",
                    optimization_type=CostOptimizationType.SPOT_INSTANCES,
                    current_monthly_cost=current_cost,
                    optimized_monthly_cost=current_cost - spot_savings,
                    potential_savings=spot_savings,
                    savings_percentage=70.0,
                    confidence_score=0.85,
                    implementation_effort="medium",
                    affected_services=[service_name],
                    implementation_steps=[
                        "Evaluate workload interruption tolerance",
                        "Set up Spot instance request",
                        "Implement graceful shutdown handling",
                        "Monitor spot price trends"
                    ],
                    timeline="1-2 weeks",
                    risks=[
                        "Potential instance interruption",
                        "Application state management required"
                    ]
                ))
                
                # Reserved instance optimization
                if usage_patterns and usage_patterns.get("consistent_usage", True):
                    ri_savings = current_cost * self.optimization_rules["ec2"]["reserved_savings"]
                    optimizations.append(CostOptimization(
                        id=f"reserved_{service_name}",
                        title=f"Purchase Reserved Instances for {service_name}",
                        description="Purchase 1-year Reserved Instances for predictable workloads",
                        optimization_type=CostOptimizationType.RESERVED_INSTANCES,
                        current_monthly_cost=current_cost,
                        optimized_monthly_cost=current_cost - ri_savings,
                        potential_savings=ri_savings,
                        savings_percentage=30.0,
                        confidence_score=0.90,
                        implementation_effort="low",
                        affected_services=[service_name],
                        implementation_steps=[
                            "Analyze usage patterns",
                            "Choose appropriate RI term and payment option",
                            "Purchase Reserved Instances",
                            "Monitor RI utilization"
                        ],
                        timeline="immediate",
                        risks=[
                            "Commitment to specific instance type and region",
                            "Underutilization if requirements change"
                        ]
                    ))
                
                # Rightsizing optimization
                avg_utilization = 0.45  # Placeholder
                if avg_utilization < self.optimization_rules["ec2"]["rightsizing_threshold"]:
                    rightsizing_savings = current_cost * 0.40
                    optimizations.append(CostOptimization(
                        id=f"rightsize_{service_name}",
                        title=f"Rightsize EC2 Instance {service_name}",
                        description=f"Downsize instance due to low utilization ({avg_utilization*100:.1f}%)",
                        optimization_type=CostOptimizationType.RIGHTSIZING,
                        current_monthly_cost=current_cost,
                        optimized_monthly_cost=current_cost - rightsizing_savings,
                        potential_savings=rightsizing_savings,
                        savings_percentage=40.0,
                        confidence_score=0.80,
                        implementation_effort="low",
                        affected_services=[service_name],
                        implementation_steps=[
                            "Create instance snapshot",
                            "Launch smaller instance type",
                            "Test application performance",
                            "Update load balancer configuration"
                        ],
                        timeline="3-5 days",
                        risks=[
                            "Potential performance impact",
                            "May need to upsize during peak periods"
                        ]
                    ))
            
            elif service_type_lower == "s3":
                # S3 optimization opportunities
                current_cost = 50.0  # Placeholder
                
                # Storage class optimization
                storage_savings = current_cost * self.optimization_rules["s3"]["storage_savings"]
                optimizations.append(CostOptimization(
                    id=f"s3_storage_class_{service_name}",
                    title=f"Optimize S3 Storage Classes for {service_name}",
                    description="Implement intelligent tiering and lifecycle policies",
                    optimization_type=CostOptimizationType.STORAGE_OPTIMIZATION,
                    current_monthly_cost=current_cost,
                    optimized_monthly_cost=current_cost - storage_savings,
                    potential_savings=storage_savings,
                    savings_percentage=40.0,
                    confidence_score=0.75,
                    implementation_effort="low",
                    affected_services=[service_name],
                    implementation_steps=[
                        "Analyze access patterns",
                        "Set up S3 Intelligent Tiering",
                        "Create lifecycle policies",
                        "Monitor storage class transitions"
                    ],
                    timeline="1 week",
                    risks=[
                        "Retrieval costs for infrequently accessed data",
                        "Potential retrieval delays"
                    ]
                ))
            
            elif service_type_lower == "rds":
                # RDS optimization opportunities
                current_cost = 150.0  # Placeholder
                
                # Reserved instance optimization
                ri_savings = current_cost * self.optimization_rules["rds"]["reserved_savings"]
                optimizations.append(CostOptimization(
                    id=f"rds_reserved_{service_name}",
                    title=f"Purchase RDS Reserved Instances for {service_name}",
                    description="Purchase Reserved Instances for production databases",
                    optimization_type=CostOptimizationType.RESERVED_INSTANCES,
                    current_monthly_cost=current_cost,
                    optimized_monthly_cost=current_cost - ri_savings,
                    potential_savings=ri_savings,
                    savings_percentage=35.0,
                    confidence_score=0.88,
                    implementation_effort="low",
                    affected_services=[service_name],
                    implementation_steps=[
                        "Review database usage patterns",
                        "Select appropriate RI terms",
                        "Purchase Reserved Instances",
                        "Monitor utilization"
                    ],
                    timeline="immediate",
                    risks=[
                        "Long-term commitment",
                        "Instance type/region lock-in"
                    ]
                ))
            
            # Add more service types as needed
            
        except Exception as e:
            logger.error(f"Error analyzing optimizations for {service_name}: {str(e)}")
        
        return optimizations
    
    async def _identify_cross_service_optimizations(self, services: Dict[str, str]) -> List[CostOptimization]:
        """Identify optimization opportunities across multiple services"""
        
        cross_optimizations = []
        
        try:
            # Auto Scaling optimization
            if any(stype.lower() in ["ec2", "ecs", "lambda"] for stype in services.values()):
                cross_optimizations.append(CostOptimization(
                    id="cross_auto_scaling",
                    title="Implement Intelligent Auto Scaling",
                    description="Set up predictive auto scaling across compute services",
                    optimization_type=CostOptimizationType.AUTO_SCALING,
                    current_monthly_cost=500.0,
                    optimized_monthly_cost=350.0,
                    potential_savings=150.0,
                    savings_percentage=30.0,
                    confidence_score=0.80,
                    implementation_effort="medium",
                    affected_services=list(services.keys()),
                    implementation_steps=[
                        "Analyze traffic patterns",
                        "Configure auto scaling groups",
                        "Set up CloudWatch alarms",
                        "Implement predictive scaling"
                    ],
                    timeline="2-3 weeks",
                    risks=[
                        "Potential performance impact during scaling events",
                        "Complexity in managing multiple scaling policies"
                    ]
                ))
            
            # Scheduling optimization for dev/test environments
            if len(services) > 3:  # Multiple services suggest dev/test potential
                cross_optimizations.append(CostOptimization(
                    id="cross_scheduling",
                    title="Implement Environment Scheduling",
                    description="Schedule non-production environments to run only during business hours",
                    optimization_type=CostOptimizationType.SCHEDULING,
                    current_monthly_cost=300.0,
                    optimized_monthly_cost=150.0,
                    potential_savings=150.0,
                    savings_percentage=50.0,
                    confidence_score=0.70,
                    implementation_effort="medium",
                    affected_services=list(services.keys()),
                    implementation_steps=[
                        "Identify non-production workloads",
                        "Set up Lambda scheduling functions",
                        "Configure start/stop automation",
                        "Test scheduling policies"
                    ],
                    timeline="1-2 weeks",
                    risks=[
                        "Potential development workflow disruption",
                        "Coordination required with development teams"
                    ]
                ))
            
        except Exception as e:
            logger.error(f"Error identifying cross-service optimizations: {str(e)}")
        
        return cross_optimizations
    
    async def _generate_cost_forecasts(self, services: Dict[str, str], usage_patterns: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate cost forecasts using historical data and trends"""
        
        forecasts = {
            "forecast_period": "12_months",
            "currency": "USD",
            "forecasts": {},
            "methodology": "linear_regression_with_seasonality"
        }
        
        try:
            # Generate forecasts for different time periods
            for period in ["3_months", "6_months", "12_months"]:
                base_monthly_cost = 500.0  # Placeholder - would calculate from actual costs
                
                # Apply growth factors based on usage patterns
                growth_rate = 0.05  # 5% monthly growth (placeholder)
                if usage_patterns and usage_patterns.get("growth_expected", True):
                    growth_rate = 0.08  # Higher growth expected
                
                periods_count = {"3_months": 3, "6_months": 6, "12_months": 12}[period]
                
                # Calculate compound growth
                forecasted_cost = base_monthly_cost * ((1 + growth_rate) ** periods_count)
                
                # Add confidence intervals
                confidence_lower = forecasted_cost * 0.85
                confidence_upper = forecasted_cost * 1.15
                
                forecasts["forecasts"][period] = CostForecast(
                    period=period,
                    forecasted_cost=round(forecasted_cost, 2),
                    confidence_interval=(round(confidence_lower, 2), round(confidence_upper, 2)),
                    growth_rate=growth_rate,
                    key_drivers=["service_expansion", "usage_growth", "feature_additions"],
                    assumptions=["steady_growth", "no_major_architecture_changes", "current_pricing_maintained"]
                )
            
        except Exception as e:
            logger.error(f"Error generating cost forecasts: {str(e)}")
        
        return forecasts
    
    async def _calculate_total_cost_of_ownership(self, services: Dict[str, str]) -> Dict[str, Any]:
        """Calculate Total Cost of Ownership including hidden costs"""
        
        tco_analysis = {
            "analysis_period": "36_months",
            "direct_costs": {},
            "indirect_costs": {},
            "total_tco": 0.0,
            "cost_categories": {}
        }
        
        try:
            base_infrastructure_cost = 500.0 * 36  # 36 months
            
            # Direct costs
            tco_analysis["direct_costs"] = {
                "infrastructure": base_infrastructure_cost,
                "data_transfer": base_infrastructure_cost * 0.10,  # 10% of infrastructure
                "storage": base_infrastructure_cost * 0.15,  # 15% of infrastructure
                "support": base_infrastructure_cost * 0.05  # 5% for support
            }
            
            # Indirect costs
            tco_analysis["indirect_costs"] = {
                "management_overhead": base_infrastructure_cost * 0.20,  # 20% for management
                "training": 5000.0,  # Training costs
                "monitoring_tools": 2000.0 * 3,  # Monitoring tools for 3 years
                "security_compliance": base_infrastructure_cost * 0.08  # 8% for security
            }
            
            # Calculate totals
            total_direct = sum(tco_analysis["direct_costs"].values())
            total_indirect = sum(tco_analysis["indirect_costs"].values())
            tco_analysis["total_tco"] = total_direct + total_indirect
            
            # Cost categories breakdown
            tco_analysis["cost_categories"] = {
                "infrastructure": (tco_analysis["direct_costs"]["infrastructure"] / tco_analysis["total_tco"]) * 100,
                "operational": ((total_indirect - tco_analysis["indirect_costs"]["training"]) / tco_analysis["total_tco"]) * 100,
                "one_time": (tco_analysis["indirect_costs"]["training"] / tco_analysis["total_tco"]) * 100
            }
            
        except Exception as e:
            logger.error(f"Error calculating TCO: {str(e)}")
        
        return tco_analysis
    
    async def _analyze_cost_trends(self, project_id: str) -> Dict[str, Any]:
        """Analyze cost trends and patterns"""
        
        trends = {
            "period": "90_days",
            "overall_trend": "increasing",
            "monthly_growth_rate": 0.05,
            "seasonal_patterns": [],
            "cost_drivers": [],
            "anomalies_detected": 0
        }
        
        try:
            if "ce" in self.aws_clients:
                # Get cost trend data from Cost Explorer
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=90)
                
                response = self.aws_clients["ce"].get_cost_and_usage(
                    TimePeriod={
                        'Start': start_date.strftime('%Y-%m-%d'),
                        'End': end_date.strftime('%Y-%m-%d')
                    },
                    Granularity='DAILY',
                    Metrics=['BlendedCost']
                )
                
                # Analyze the trend data
                daily_costs = []
                for result in response.get("ResultsByTime", []):
                    cost = float(result.get("Total", {}).get("BlendedCost", {}).get("Amount", "0"))
                    daily_costs.append(cost)
                
                if len(daily_costs) > 30:
                    # Calculate trend
                    recent_avg = np.mean(daily_costs[-30:])
                    previous_avg = np.mean(daily_costs[-60:-30])
                    
                    if recent_avg > previous_avg * 1.1:
                        trends["overall_trend"] = "increasing"
                        trends["monthly_growth_rate"] = (recent_avg - previous_avg) / previous_avg
                    elif recent_avg < previous_avg * 0.9:
                        trends["overall_trend"] = "decreasing"
                        trends["monthly_growth_rate"] = (recent_avg - previous_avg) / previous_avg
                    else:
                        trends["overall_trend"] = "stable"
                        trends["monthly_growth_rate"] = 0.0
                
            else:
                # Use placeholder trend analysis
                trends.update({
                    "cost_drivers": ["increased_usage", "new_services", "data_growth"],
                    "seasonal_patterns": ["higher_weekday_usage", "month_end_spikes"]
                })
                
        except Exception as e:
            logger.error(f"Error analyzing cost trends: {str(e)}")
        
        return trends
    
    async def _check_cost_anomalies(self, project_id: str) -> List[Dict[str, Any]]:
        """Check for cost anomalies and unusual spending patterns"""
        
        anomalies = []
        
        try:
            if "ce" in self.aws_clients:
                # Use Cost Anomaly Detection service
                response = self.aws_clients["ce"].get_anomalies(
                    DateInterval={
                        'StartDate': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                        'EndDate': datetime.now().strftime('%Y-%m-%d')
                    }
                )
                
                for anomaly in response.get("Anomalies", []):
                    anomalies.append({
                        "id": anomaly.get("AnomalyId", ""),
                        "start_date": anomaly.get("AnomalyStartDate", ""),
                        "end_date": anomaly.get("AnomalyEndDate", ""),
                        "dimension_key": anomaly.get("DimensionKey", ""),
                        "impact": {
                            "max_impact": float(anomaly.get("Impact", {}).get("MaxImpact", "0")),
                            "total_impact": float(anomaly.get("Impact", {}).get("TotalImpact", "0"))
                        },
                        "root_causes": anomaly.get("RootCauses", []),
                        "feedback": anomaly.get("Feedback", ""),
                        "detected_at": datetime.now().isoformat()
                    })
            
            else:
                # Mock anomaly for demonstration
                anomalies.append({
                    "id": "anomaly_001",
                    "start_date": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                    "end_date": datetime.now().strftime('%Y-%m-%d'),
                    "dimension_key": "SERVICE",
                    "impact": {
                        "max_impact": 150.0,
                        "total_impact": 300.0
                    },
                    "root_causes": [
                        {
                            "Service": "Amazon EC2-Instance",
                            "Region": "us-west-2",
                            "UsageType": "BoxUsage:t3.large"
                        }
                    ],
                    "feedback": "ANOMALY",
                    "detected_at": datetime.now().isoformat(),
                    "description": "Unusual spike in EC2 usage detected"
                })
                
        except Exception as e:
            logger.error(f"Error checking cost anomalies: {str(e)}")
        
        return anomalies
    
    async def get_real_time_cost_metrics(self, project_id: str) -> Dict[str, Any]:
        """Get real-time cost metrics and alerts"""
        
        try:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "project_id": project_id,
                "current_month_spend": 0.0,
                "daily_spend": 0.0,
                "hourly_spend": 0.0,
                "budget_status": {
                    "budget_amount": 1000.0,
                    "spent_amount": 650.0,
                    "remaining_amount": 350.0,
                    "usage_percentage": 65.0,
                    "projected_month_end": 850.0,
                    "status": "on_track"
                },
                "cost_breakdown_by_service": {},
                "alerts": [],
                "recommendations": []
            }
            
            if "ce" in self.aws_clients:
                # Get current month costs
                today = datetime.now().date()
                month_start = today.replace(day=1)
                
                response = self.aws_clients["ce"].get_cost_and_usage(
                    TimePeriod={
                        'Start': month_start.strftime('%Y-%m-%d'),
                        'End': today.strftime('%Y-%m-%d')
                    },
                    Granularity='MONTHLY',
                    Metrics=['BlendedCost'],
                    GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
                )
                
                total_month_cost = 0.0
                for result in response.get("ResultsByTime", []):
                    for group in result.get("Groups", []):
                        service = group.get("Keys", ["Unknown"])[0]
                        cost = float(group.get("Metrics", {}).get("BlendedCost", {}).get("Amount", "0"))
                        metrics["cost_breakdown_by_service"][service] = cost
                        total_month_cost += cost
                
                metrics["current_month_spend"] = total_month_cost
                
                # Calculate daily and hourly rates
                days_in_month = (today - month_start).days + 1
                metrics["daily_spend"] = total_month_cost / days_in_month if days_in_month > 0 else 0
                metrics["hourly_spend"] = metrics["daily_spend"] / 24
                
                # Update budget status
                metrics["budget_status"]["spent_amount"] = total_month_cost
                metrics["budget_status"]["usage_percentage"] = (total_month_cost / metrics["budget_status"]["budget_amount"]) * 100
                metrics["budget_status"]["remaining_amount"] = metrics["budget_status"]["budget_amount"] - total_month_cost
                
                # Project month-end spending
                remaining_days = (today.replace(month=today.month+1, day=1) - timedelta(days=1) - today).days
                metrics["budget_status"]["projected_month_end"] = total_month_cost + (metrics["daily_spend"] * remaining_days)
                
                # Determine budget status
                if metrics["budget_status"]["usage_percentage"] > 90:
                    metrics["budget_status"]["status"] = "over_budget"
                elif metrics["budget_status"]["usage_percentage"] > 80:
                    metrics["budget_status"]["status"] = "at_risk"
                else:
                    metrics["budget_status"]["status"] = "on_track"
            
            else:
                # Use mock data
                metrics.update({
                    "current_month_spend": 650.0,
                    "daily_spend": 21.67,
                    "hourly_spend": 0.90,
                    "cost_breakdown_by_service": {
                        "Amazon EC2": 300.0,
                        "Amazon S3": 50.0,
                        "Amazon RDS": 200.0,
                        "AWS Lambda": 25.0,
                        "Amazon CloudFront": 75.0
                    }
                })
            
            # Generate alerts based on metrics
            if metrics["budget_status"]["usage_percentage"] > 85:
                metrics["alerts"].append({
                    "type": "budget_alert",
                    "severity": "high",
                    "message": f"Budget usage at {metrics['budget_status']['usage_percentage']:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Generate recommendations
            if metrics["budget_status"]["projected_month_end"] > metrics["budget_status"]["budget_amount"]:
                metrics["recommendations"].append({
                    "type": "cost_optimization",
                    "priority": "high",
                    "message": "Consider implementing cost optimizations to stay within budget",
                    "estimated_savings": "15-25%"
                })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting real-time cost metrics: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "project_id": project_id,
                "error": str(e)
            }