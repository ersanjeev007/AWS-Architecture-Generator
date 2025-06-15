from typing import Dict, List, Tuple
from app.schemas.questionnaire import QuestionnaireRequest
from app.schemas.architecture import CostBreakdown

class CostCalculator:
    """Calculate estimated costs for AWS services"""
    
    # Base monthly costs for different services (in USD)
    BASE_COSTS = {
        "compute": {
            "serverless": {"low": 10, "medium": 50, "high": 200},
            "containers": {"low": 30, "medium": 150, "high": 500},
            "vms": {"low": 20, "medium": 100, "high": 400}
        },
        "database": {
            "sql": {"low": 15, "medium": 75, "high": 300},
            "nosql": {"low": 10, "medium": 50, "high": 200}
        },
        "storage": {"minimal": 5, "moderate": 25, "extensive": 100},
        "networking": {"load_balancer": 20, "cdn": 15, "dns": 5},
        "monitoring": 10
    }
    
    def calculate_costs(self, questionnaire: QuestionnaireRequest, services: Dict[str, str]) -> Tuple[str, List[CostBreakdown]]:
        """Calculate total estimated cost and detailed breakdown"""
        
        breakdown = []
        total_cost = 0
        
        # Get string values (handle both enum and string inputs)
        traffic_level = questionnaire.traffic_volume if isinstance(questionnaire.traffic_volume, str) else questionnaire.traffic_volume.value
        compute_pref = questionnaire.compute_preference if isinstance(questionnaire.compute_preference, str) else questionnaire.compute_preference.value
        database_type = questionnaire.database_type if isinstance(questionnaire.database_type, str) else questionnaire.database_type.value
        storage_needs = questionnaire.storage_needs if isinstance(questionnaire.storage_needs, str) else questionnaire.storage_needs.value
        budget_range = questionnaire.budget_range if isinstance(questionnaire.budget_range, str) else questionnaire.budget_range.value
        
        # Calculate compute costs
        if "compute" in services:
            compute_cost = self.BASE_COSTS["compute"][compute_pref][traffic_level]
            total_cost += compute_cost
            breakdown.append(CostBreakdown(
                service=services["compute"],
                estimated_monthly_cost=f"${compute_cost}",
                description="Application hosting and compute resources"
            ))
        
        # Calculate database costs
        if "database" in services and database_type != "none":
            db_cost = self.BASE_COSTS["database"][database_type][traffic_level]
            total_cost += db_cost
            breakdown.append(CostBreakdown(
                service=services["database"],
                estimated_monthly_cost=f"${db_cost}",
                description="Database storage and compute"
            ))
        
        # Calculate storage costs
        if "storage" in services:
            storage_cost = self.BASE_COSTS["storage"][storage_needs]
            total_cost += storage_cost
            breakdown.append(CostBreakdown(
                service=services["storage"],
                estimated_monthly_cost=f"${storage_cost}",
                description="Object storage and data transfer"
            ))
        
        # Calculate networking costs
        networking_cost = 0
        if "load_balancer" in services:
            networking_cost += self.BASE_COSTS["networking"]["load_balancer"]
        if "cdn" in services:
            networking_cost += self.BASE_COSTS["networking"]["cdn"]
        if "dns" in services:
            networking_cost += self.BASE_COSTS["networking"]["dns"]
        
        if networking_cost > 0:
            total_cost += networking_cost
            breakdown.append(CostBreakdown(
                service="Networking Services",
                estimated_monthly_cost=f"${networking_cost}",
                description="Load balancing, CDN, and DNS services"
            ))
        
        # Add monitoring costs
        monitoring_cost = self.BASE_COSTS["monitoring"]
        total_cost += monitoring_cost
        breakdown.append(CostBreakdown(
            service="CloudWatch Monitoring",
            estimated_monthly_cost=f"${monitoring_cost}",
            description="Monitoring, logging, and alerting"
        ))
        
        # Apply budget adjustments
        if budget_range == "startup":
            total_cost = int(total_cost * 0.8)
        elif budget_range == "enterprise":
            total_cost = int(total_cost * 1.3)
        
        # Format cost range
        min_cost = int(total_cost * 0.8)
        max_cost = int(total_cost * 1.2)
        cost_range = f"${min_cost}-{max_cost}/month"
        
        return cost_range, breakdown