import { apiClient } from './api';

class CostAnalysisService {
  /**
   * Get enhanced cost estimate with real AWS pricing
   */
  async getEnhancedCostEstimate(questionnaire, services, region = 'us-east-1', securityLevel = 'medium') {
    try {
      const response = await apiClient.post('/cost-analysis/enhanced-estimate', {
        questionnaire,
        services,
        region,
        security_level: securityLevel
      });
      return response.data;
    } catch (error) {
      console.error('Error getting enhanced cost estimate:', error);
      throw error;
    }
  }

  /**
   * Get cost optimization recommendations for a project
   */
  async getCostOptimizationRecommendations(projectId, optimizationType = 'all') {
    try {
      const response = await apiClient.get(`/cost-analysis/optimization-recommendations/${projectId}`, {
        params: { optimization_type: optimizationType }
      });
      return response.data;
    } catch (error) {
      console.error('Error getting cost optimization recommendations:', error);
      throw error;
    }
  }

  /**
   * Compare costs across different AWS regions
   */
  async compareRegionalCosts(questionnaire, services, regions = ['us-east-1', 'us-west-2', 'eu-west-1'], securityLevel = 'medium') {
    try {
      const response = await apiClient.post('/cost-analysis/compare-regions', {
        questionnaire,
        services,
        security_level: securityLevel
      }, {
        params: { regions: regions.join(',') }
      });
      return response.data;
    } catch (error) {
      console.error('Error comparing regional costs:', error);
      throw error;
    }
  }

  /**
   * Get historical cost trends and projections
   */
  async getCostTrends(projectId, months = 12) {
    try {
      const response = await apiClient.get(`/cost-analysis/cost-trends/${projectId}`, {
        params: { months }
      });
      return response.data;
    } catch (error) {
      console.error('Error getting cost trends:', error);
      throw error;
    }
  }

  /**
   * Get real-time cost data (mock implementation for demo)
   */
  async getRealTimeCostData(projectId) {
    try {
      // In a real implementation, this would connect to AWS Cost Explorer API
      // For now, return simulated real-time data
      return {
        current_month_spend: 2847.65,
        daily_spend: 94.92,
        projected_month_end: 3200.00,
        cost_alerts: [
          {
            type: 'warning',
            message: 'Monthly spend is 15% higher than last month',
            threshold: 2500,
            current: 2847.65
          }
        ],
        top_services: [
          { service: 'EC2', cost: 1245.80, percentage: 43.7 },
          { service: 'RDS', cost: 678.90, percentage: 23.8 },
          { service: 'S3', cost: 234.50, percentage: 8.2 }
        ]
      };
    } catch (error) {
      console.error('Error getting real-time cost data:', error);
      throw error;
    }
  }

  /**
   * Apply cost optimization recommendation
   */
  async applyCostOptimization(projectId, recommendationType, optimizationData) {
    try {
      const response = await apiClient.post(`/cost-analysis/apply-optimization/${projectId}`, {
        recommendation_type: recommendationType,
        optimization_data: optimizationData
      });
      return response.data;
    } catch (error) {
      console.error('Error applying cost optimization:', error);
      throw error;
    }
  }

  /**
   * Get cost breakdown by service category
   */
  getCostBreakdownByCategory(costBreakdown) {
    const categories = {
      compute: ['EC2', 'Lambda', 'ECS', 'EKS', 'Fargate'],
      storage: ['S3', 'EBS', 'EFS'],
      database: ['RDS', 'DynamoDB', 'ElastiCache'],
      networking: ['CloudFront', 'Load Balancer', 'Route53', 'VPC'],
      security: ['WAF', 'GuardDuty', 'KMS', 'Secrets Manager', 'Config'],
      monitoring: ['CloudWatch', 'CloudTrail', 'X-Ray']
    };

    const breakdown = {};
    
    Object.keys(categories).forEach(category => {
      breakdown[category] = {
        services: [],
        total_cost: 0,
        percentage: 0
      };
    });

    let totalCost = 0;

    costBreakdown.forEach(item => {
      const cost = parseFloat(item.estimated_monthly_cost.replace('$', '').replace(',', ''));
      if (isNaN(cost) || cost < 0) return;

      totalCost += cost;
      let categorized = false;

      Object.keys(categories).forEach(category => {
        categories[category].forEach(service => {
          if (item.service.includes(service)) {
            breakdown[category].services.push({
              name: item.service,
              cost: cost,
              description: item.description
            });
            breakdown[category].total_cost += cost;
            categorized = true;
          }
        });
      });

      if (!categorized) {
        if (!breakdown.other) {
          breakdown.other = { services: [], total_cost: 0, percentage: 0 };
        }
        breakdown.other.services.push({
          name: item.service,
          cost: cost,
          description: item.description
        });
        breakdown.other.total_cost += cost;
      }
    });

    // Calculate percentages
    Object.keys(breakdown).forEach(category => {
      if (totalCost > 0) {
        breakdown[category].percentage = (breakdown[category].total_cost / totalCost) * 100;
      }
    });

    return {
      breakdown,
      total_cost: totalCost
    };
  }

  /**
   * Format cost for display
   */
  formatCost(cost, currency = 'USD') {
    if (typeof cost === 'string') {
      return cost;
    }
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(cost);
  }

  /**
   * Calculate cost savings percentage
   */
  calculateSavingsPercentage(originalCost, optimizedCost) {
    if (originalCost <= 0) return 0;
    return ((originalCost - optimizedCost) / originalCost) * 100;
  }

  /**
   * Get cost efficiency score
   */
  getCostEfficiencyScore(currentCost, benchmarkCost, utilizationRate = 0.7) {
    const costEfficiency = (benchmarkCost / currentCost) * utilizationRate;
    return Math.min(100, Math.max(0, costEfficiency * 100));
  }
}

export default new CostAnalysisService();