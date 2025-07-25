import boto3
import json
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from app.schemas.questionnaire import QuestionnaireRequest
from app.schemas.architecture import CostBreakdown
import asyncio
import aiohttp
from functools import lru_cache

logger = logging.getLogger(__name__)

@dataclass
class ServiceUsage:
    """Represents usage patterns for AWS services"""
    compute_hours: int = 730  # Default: full month
    storage_gb: int = 100
    requests_per_month: int = 1000000
    data_transfer_gb: int = 50
    database_storage_gb: int = 20
    database_iops: int = 3000

@dataclass
class PricingData:
    """Stores pricing information for AWS services"""
    service: str
    region: str
    instance_type: str
    price_per_hour: float
    price_per_gb_storage: float
    price_per_request: float
    last_updated: datetime

class EnhancedCostCalculator:
    """Enhanced cost calculator with real AWS pricing integration"""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.pricing_client = None
        self.pricing_cache = {}
        self.cache_ttl = timedelta(hours=24)
        
        # Security service base costs (monthly)
        self.security_costs = {
            "waf": {"requests": 0.0006, "rules": 5.0},  # per million requests, per rule
            "guardduty": {"finding": 4.0, "analysis": 0.50},  # per million events
            "config": {"configuration_item": 0.003, "rule_evaluation": 0.001},
            "cloudtrail": {"management_events": 2.0, "data_events": 0.10},  # per 100k events
            "kms": {"api_requests": 0.03, "key": 1.0},  # per 10k requests, per key
            "secrets_manager": {"secret": 0.40, "api_calls": 0.05},  # per secret per month, per 10k calls
            "certificate_manager": 0.0,  # Free for ACM certificates
            "security_hub": {"finding": 0.0030}  # per finding ingested
        }
        
        # Default usage patterns based on traffic levels
        self.usage_patterns = {
            "low": ServiceUsage(
                compute_hours=200,
                storage_gb=50,
                requests_per_month=100000,
                data_transfer_gb=10,
                database_storage_gb=5,
                database_iops=1000
            ),
            "medium": ServiceUsage(
                compute_hours=500,
                storage_gb=200,
                requests_per_month=1000000,
                data_transfer_gb=50,
                database_storage_gb=20,
                database_iops=3000
            ),
            "high": ServiceUsage(
                compute_hours=730,  # Full month
                storage_gb=1000,
                requests_per_month=10000000,
                data_transfer_gb=200,
                database_storage_gb=100,
                database_iops=10000
            )
        }
    
    async def initialize_pricing_client(self):
        """Initialize AWS Pricing API client"""
        try:
            session = boto3.Session()
            self.pricing_client = session.client('pricing', region_name='us-east-1')  # Pricing API only available in us-east-1
        except Exception as e:
            logger.warning(f"Failed to initialize AWS Pricing client: {e}")
            self.pricing_client = None
    
    @lru_cache(maxsize=100)
    def get_cached_pricing(self, service_code: str, instance_type: str) -> Optional[float]:
        """Get cached pricing data with TTL"""
        cache_key = f"{service_code}_{instance_type}_{self.region}"
        
        if cache_key in self.pricing_cache:
            cached_data = self.pricing_cache[cache_key]
            if datetime.now() - cached_data["timestamp"] < self.cache_ttl:
                return cached_data["price"]
        
        return None
    
    async def get_aws_pricing(self, service_code: str, instance_type: str, region: str = None) -> float:
        """Get real-time AWS pricing from Pricing API"""
        if not self.pricing_client:
            return self._get_fallback_pricing(service_code, instance_type)
        
        if not region:
            region = self.region
            
        try:
            # Check cache first
            cached_price = self.get_cached_pricing(service_code, instance_type)
            if cached_price:
                return cached_price
            
            # Build pricing filters
            filters = [
                {"Type": "TERM_MATCH", "Field": "ServiceCode", "Value": service_code},
                {"Type": "TERM_MATCH", "Field": "location", "Value": self._get_region_description(region)},
                {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
                {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
                {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"}
            ]
            
            response = self.pricing_client.get_products(
                ServiceCode=service_code,
                Filters=filters,
                MaxResults=1
            )
            
            if response['PriceList']:
                price_data = json.loads(response['PriceList'][0])
                
                # Extract on-demand pricing
                terms = price_data.get('terms', {})
                on_demand = terms.get('OnDemand', {})
                
                for term_key, term_data in on_demand.items():
                    price_dimensions = term_data.get('priceDimensions', {})
                    for price_key, price_info in price_dimensions.items():
                        price_per_unit = float(price_info['pricePerUnit']['USD'])
                        
                        # Cache the result
                        cache_key = f"{service_code}_{instance_type}_{region}"
                        self.pricing_cache[cache_key] = {
                            "price": price_per_unit,
                            "timestamp": datetime.now()
                        }
                        
                        return price_per_unit
            
        except Exception as e:
            logger.error(f"Error fetching AWS pricing for {service_code}/{instance_type}: {e}")
        
        return self._get_fallback_pricing(service_code, instance_type)
    
    def _get_fallback_pricing(self, service_code: str, instance_type: str) -> float:
        """Fallback pricing when AWS Pricing API is unavailable"""
        fallback_prices = {
            "AmazonEC2": {
                "t3.micro": 0.0104,
                "t3.small": 0.0208,
                "t3.medium": 0.0416,
                "t3.large": 0.0832,
                "m5.large": 0.096,
                "m5.xlarge": 0.192,
                "c5.large": 0.085,
                "r5.large": 0.126
            },
            "AmazonRDS": {
                "db.t3.micro": 0.017,
                "db.t3.small": 0.034,
                "db.t3.medium": 0.068,
                "db.r5.large": 0.24,
                "db.m5.large": 0.192
            },
            "AmazonLambda": {
                "requests": 0.0000002,  # per request
                "duration": 0.0000166667  # per GB-second
            },
            "AmazonS3": {
                "standard": 0.023,  # per GB
                "requests_put": 0.0005,  # per 1000 requests
                "requests_get": 0.0004   # per 1000 requests
            }
        }
        
        return fallback_prices.get(service_code, {}).get(instance_type, 10.0)
    
    def _get_region_description(self, region: str) -> str:
        """Convert region code to AWS pricing region description"""
        region_mapping = {
            "us-east-1": "US East (N. Virginia)",
            "us-west-2": "US West (Oregon)",
            "eu-west-1": "Europe (Ireland)",
            "ap-southeast-1": "Asia Pacific (Singapore)",
            "ap-northeast-1": "Asia Pacific (Tokyo)"
        }
        return region_mapping.get(region, "US East (N. Virginia)")
    
    async def calculate_enhanced_costs(self, questionnaire: QuestionnaireRequest, services: Dict[str, str], security_level: str = "medium") -> Tuple[str, List[CostBreakdown]]:
        """Calculate enhanced cost estimation with real AWS pricing"""
        
        await self.initialize_pricing_client()
        
        breakdown = []
        total_cost = 0
        
        # Get usage patterns based on traffic
        traffic_level = questionnaire.traffic_volume if isinstance(questionnaire.traffic_volume, str) else questionnaire.traffic_volume.value
        usage = self.usage_patterns.get(traffic_level, self.usage_patterns["medium"])
        
        # Calculate compute costs
        if "compute" in services:
            compute_cost = await self._calculate_compute_costs(questionnaire, services, usage)
            total_cost += compute_cost
            breakdown.append(CostBreakdown(
                service=services["compute"],
                estimated_monthly_cost=f"${compute_cost:.2f}",
                description=f"Compute resources ({usage.compute_hours} hours/month)"
            ))
        
        # Calculate database costs
        if "database" in services:
            db_cost = await self._calculate_database_costs(questionnaire, services, usage)
            total_cost += db_cost
            breakdown.append(CostBreakdown(
                service=services["database"],
                estimated_monthly_cost=f"${db_cost:.2f}",
                description=f"Database ({usage.database_storage_gb}GB storage, {usage.database_iops} IOPS)"
            ))
        
        # Calculate storage costs
        if "storage" in services:
            storage_cost = await self._calculate_storage_costs(services, usage)
            total_cost += storage_cost
            breakdown.append(CostBreakdown(
                service=services["storage"],
                estimated_monthly_cost=f"${storage_cost:.2f}",
                description=f"Object storage ({usage.storage_gb}GB) and data transfer ({usage.data_transfer_gb}GB)"
            ))
        
        # Calculate networking costs
        networking_cost = await self._calculate_networking_costs(services, usage)
        if networking_cost > 0:
            total_cost += networking_cost
            breakdown.append(CostBreakdown(
                service="Networking Services",
                estimated_monthly_cost=f"${networking_cost:.2f}",
                description="Load balancer, CloudFront CDN, Route53 DNS"
            ))
        
        # Calculate security costs
        security_cost = self._calculate_security_costs(security_level, usage)
        if security_cost > 0:
            total_cost += security_cost
            breakdown.append(CostBreakdown(
                service="Security Services",
                estimated_monthly_cost=f"${security_cost:.2f}",
                description="WAF, GuardDuty, KMS, Secrets Manager, Config"
            ))
        
        # Calculate monitoring costs
        monitoring_cost = self._calculate_monitoring_costs(usage)
        total_cost += monitoring_cost
        breakdown.append(CostBreakdown(
            service="Monitoring & Logging",
            estimated_monthly_cost=f"${monitoring_cost:.2f}",
            description="CloudWatch, CloudTrail, X-Ray tracing"
        ))
        
        # Apply budget adjustments and add cost optimization recommendations
        budget_range = questionnaire.budget_range if isinstance(questionnaire.budget_range, str) else questionnaire.budget_range.value
        total_cost, optimization_savings = self._apply_cost_optimizations(total_cost, budget_range, questionnaire)
        
        if optimization_savings > 0:
            breakdown.append(CostBreakdown(
                service="Cost Optimizations",
                estimated_monthly_cost=f"-${optimization_savings:.2f}",
                description="Reserved instances, Spot pricing, right-sizing"
            ))
        
        # Format cost range with confidence interval
        confidence = 0.85  # 85% confidence in estimate
        variance = 0.15 if self.pricing_client else 0.25  # Higher variance if using fallback pricing
        
        min_cost = max(0, total_cost * (1 - variance))
        max_cost = total_cost * (1 + variance)
        
        cost_range = f"${min_cost:.0f}-{max_cost:.0f}/month"
        
        # Add confidence and optimization notes
        breakdown.append(CostBreakdown(
            service="Cost Estimate Info",
            estimated_monthly_cost=f"{confidence*100:.0f}% confidence",
            description=f"Based on {traffic_level} traffic, {self.region} region pricing. Includes AWS Free Tier where applicable."
        ))
        
        return cost_range, breakdown
    
    async def _calculate_compute_costs(self, questionnaire: QuestionnaireRequest, services: Dict[str, str], usage: ServiceUsage) -> float:
        """Calculate compute service costs"""
        compute_pref = questionnaire.compute_preference if isinstance(questionnaire.compute_preference, str) else questionnaire.compute_preference.value
        
        if compute_pref == "serverless":
            # Lambda pricing
            lambda_requests = usage.requests_per_month
            lambda_duration_gb_seconds = lambda_requests * 0.5  # Assume 500ms average duration, 128MB memory
            
            request_cost = lambda_requests * 0.0000002
            duration_cost = lambda_duration_gb_seconds * 0.0000166667
            
            # Free tier: 1M requests and 400,000 GB-seconds per month
            request_cost = max(0, request_cost - (1000000 * 0.0000002))
            duration_cost = max(0, duration_cost - (400000 * 0.0000166667))
            
            return request_cost + duration_cost
            
        elif compute_pref == "containers":
            # ECS Fargate pricing
            fargate_cpu_cost = 0.04048  # per vCPU per hour
            fargate_memory_cost = 0.004445  # per GB per hour
            
            # Assume 1 vCPU, 2GB memory
            return (fargate_cpu_cost + (2 * fargate_memory_cost)) * usage.compute_hours
            
        else:  # VMs
            # EC2 pricing
            instance_type = "t3.medium" if usage.compute_hours < 500 else "m5.large"
            hourly_rate = await self.get_aws_pricing("AmazonEC2", instance_type)
            
            # Apply free tier (750 hours t2.micro/t3.micro per month for first 12 months)
            if instance_type == "t3.micro":
                billable_hours = max(0, usage.compute_hours - 750)
            else:
                billable_hours = usage.compute_hours
                
            return hourly_rate * billable_hours
    
    async def _calculate_database_costs(self, questionnaire: QuestionnaireRequest, services: Dict[str, str], usage: ServiceUsage) -> float:
        """Calculate database costs"""
        database_type = questionnaire.database_type if isinstance(questionnaire.database_type, str) else questionnaire.database_type.value
        
        if database_type == "nosql":
            # DynamoDB pricing
            read_units = usage.requests_per_month * 0.5 / (30 * 24 * 3600)  # Average read capacity units
            write_units = usage.requests_per_month * 0.1 / (30 * 24 * 3600)  # Average write capacity units
            
            # On-demand pricing
            read_cost = max(0, (read_units * 30 * 24) - 25) * 0.25  # $0.25 per million read requests (25M free tier)
            write_cost = max(0, (write_units * 30 * 24) - 25) * 1.25  # $1.25 per million write requests (25M free tier)
            storage_cost = max(0, usage.database_storage_gb - 25) * 0.25  # $0.25 per GB (25GB free tier)
            
            return read_cost + write_cost + storage_cost
            
        else:  # SQL
            # RDS pricing
            instance_type = "db.t3.micro" if usage.database_storage_gb < 20 else "db.t3.small"
            hourly_rate = await self.get_aws_pricing("AmazonRDS", instance_type)
            
            # RDS free tier: 750 hours db.t2.micro/db.t3.micro, 20GB storage
            if instance_type == "db.t3.micro":
                billable_hours = max(0, 730 - 750)  # Free tier
                billable_storage = max(0, usage.database_storage_gb - 20)
            else:
                billable_hours = 730
                billable_storage = usage.database_storage_gb
                
            compute_cost = hourly_rate * billable_hours
            storage_cost = billable_storage * 0.115  # GP2 storage pricing
            
            return compute_cost + storage_cost
    
    async def _calculate_storage_costs(self, services: Dict[str, str], usage: ServiceUsage) -> float:
        """Calculate S3 storage costs"""
        # S3 Standard pricing
        storage_cost = max(0, usage.storage_gb - 5) * 0.023  # 5GB free tier
        
        # Request costs
        put_requests = usage.requests_per_month * 0.1  # Assume 10% PUT requests
        get_requests = usage.requests_per_month * 0.9  # Assume 90% GET requests
        
        put_cost = max(0, put_requests - 2000) * 0.0005 / 1000  # 2000 PUT requests free tier
        get_cost = max(0, get_requests - 20000) * 0.0004 / 1000  # 20000 GET requests free tier
        
        # Data transfer out
        transfer_cost = max(0, usage.data_transfer_gb - 1) * 0.09  # 1GB free tier
        
        return storage_cost + put_cost + get_cost + transfer_cost
    
    async def _calculate_networking_costs(self, services: Dict[str, str], usage: ServiceUsage) -> float:
        """Calculate networking service costs"""
        total_cost = 0
        
        if "load_balancer" in services:
            # ALB pricing: $0.0225 per hour + $0.008 per LCU-hour
            total_cost += 0.0225 * 730  # Base cost
            lcu_hours = min(usage.requests_per_month / 1000000, 1) * 730  # Estimate LCU usage
            total_cost += lcu_hours * 0.008
        
        if "cdn" in services:
            # CloudFront pricing
            # First 10TB: $0.085 per GB
            cdn_data = usage.data_transfer_gb * 2  # Assume 2x data transfer for CDN
            total_cost += cdn_data * 0.085
            
            # HTTP/HTTPS requests
            total_cost += (usage.requests_per_month / 10000) * 0.0075  # $0.0075 per 10,000 requests
        
        if "dns" in services:
            # Route53 pricing
            total_cost += 0.50  # $0.50 per hosted zone per month
            total_cost += max(0, (usage.requests_per_month / 1000000) - 1) * 0.40  # $0.40 per million queries (1M free)
        
        return total_cost
    
    def _calculate_security_costs(self, security_level: str, usage: ServiceUsage) -> float:
        """Calculate security service costs based on security level"""
        total_cost = 0
        
        if security_level == "basic":
            # Basic security (mostly free tier)
            total_cost += self.security_costs["cloudtrail"]["management_events"]  # CloudTrail management events
            
        elif security_level == "medium":
            # Medium security
            total_cost += self.security_costs["waf"]["rules"] * 5  # 5 WAF rules
            total_cost += (usage.requests_per_month / 1000000) * self.security_costs["waf"]["requests"]
            total_cost += self.security_costs["config"]["configuration_item"] * 100  # 100 config items
            total_cost += self.security_costs["kms"]["key"] * 2  # 2 KMS keys
            total_cost += self.security_costs["secrets_manager"]["secret"] * 3  # 3 secrets
            
        else:  # high security
            # High security (comprehensive)
            total_cost += self.security_costs["guardduty"]["finding"] * 10  # GuardDuty findings
            total_cost += self.security_costs["waf"]["rules"] * 10  # 10 WAF rules
            total_cost += (usage.requests_per_month / 1000000) * self.security_costs["waf"]["requests"]
            total_cost += self.security_costs["config"]["configuration_item"] * 200  # 200 config items
            total_cost += self.security_costs["kms"]["key"] * 5  # 5 KMS keys
            total_cost += self.security_costs["secrets_manager"]["secret"] * 5  # 5 secrets
            total_cost += self.security_costs["security_hub"]["finding"] * 1000  # Security Hub findings
            
        return total_cost
    
    def _calculate_monitoring_costs(self, usage: ServiceUsage) -> float:
        """Calculate monitoring and logging costs"""
        # CloudWatch metrics (first 10 metrics free)
        metrics_cost = max(0, 20 - 10) * 0.30  # $0.30 per metric per month
        
        # CloudWatch logs (5GB free tier)
        logs_gb = usage.requests_per_month * 0.0001  # Estimate log volume
        logs_cost = max(0, logs_gb - 5) * 0.50  # $0.50 per GB ingested
        
        # CloudWatch alarms (10 free tier)
        alarms_cost = max(0, 5 - 10) * 0.10  # $0.10 per alarm per month
        
        return metrics_cost + logs_cost + alarms_cost
    
    def _apply_cost_optimizations(self, total_cost: float, budget_range: str, questionnaire: QuestionnaireRequest) -> Tuple[float, float]:
        """Apply cost optimizations and return optimized cost and savings"""
        savings = 0
        
        # Reserved Instance savings (10-30% for production workloads)
        if budget_range == "enterprise":
            ri_savings = total_cost * 0.20  # 20% savings with RIs
            savings += ri_savings
            
        # Spot Instance savings for suitable workloads (up to 70% savings)
        elif budget_range == "startup":
            spot_savings = total_cost * 0.15  # Conservative 15% savings with Spot
            savings += spot_savings
        
        # Right-sizing savings (5-15% typical)
        right_sizing_savings = total_cost * 0.10
        savings += right_sizing_savings
        
        # Budget-based adjustments
        if budget_range == "startup":
            # Additional startup optimizations
            total_cost = total_cost * 0.85  # 15% additional optimization
        elif budget_range == "enterprise":
            # Enterprise typically chooses higher availability/performance
            total_cost = total_cost * 1.15  # 15% premium for enterprise features
        
        final_cost = max(0, total_cost - savings)
        return final_cost, savings

    def get_cost_optimization_recommendations(self, questionnaire: QuestionnaireRequest, total_cost: float) -> List[Dict[str, str]]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        traffic_level = questionnaire.traffic_volume if isinstance(questionnaire.traffic_volume, str) else questionnaire.traffic_volume.value
        budget_range = questionnaire.budget_range if isinstance(questionnaire.budget_range, str) else questionnaire.budget_range.value
        
        if total_cost > 100:
            recommendations.append({
                "category": "Reserved Instances",
                "recommendation": "Consider 1-year Reserved Instances for predictable workloads",
                "potential_savings": "10-30% on compute costs",
                "implementation": "Purchase RIs for baseline capacity"
            })
        
        if traffic_level in ["low", "medium"]:
            recommendations.append({
                "category": "Spot Instances",
                "recommendation": "Use Spot Instances for fault-tolerant workloads",
                "potential_savings": "Up to 70% on compute costs",
                "implementation": "Implement Auto Scaling with mixed instance types"
            })
        
        if budget_range == "startup":
            recommendations.append({
                "category": "AWS Free Tier",
                "recommendation": "Maximize AWS Free Tier usage",
                "potential_savings": "$100-300/month for first 12 months",
                "implementation": "Use t3.micro instances, 5GB S3, 25GB DynamoDB"
            })
        
        recommendations.append({
            "category": "Right-sizing",
            "recommendation": "Monitor and right-size resources regularly",
            "potential_savings": "10-15% on overall costs",
            "implementation": "Use CloudWatch and AWS Trusted Advisor"
        })
        
        return recommendations