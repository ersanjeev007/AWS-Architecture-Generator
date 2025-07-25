import { apiClient } from './api';

class SecurityService {
  /**
   * Analyze project security and get AI-powered recommendations
   */
  async analyzeProjectSecurity(projectId, questionnaire, services, includeAI = true, securityLevel = null) {
    try {
      const response = await apiClient.post('/security/analyze-project', {
        project_id: projectId,
        questionnaire,
        services,
        include_ai_recommendations: includeAI,
        security_level: securityLevel
      });
      return response.data;
    } catch (error) {
      console.error('Error analyzing project security:', error);
      throw error;
    }
  }

  /**
   * Get security recommendations for a specific project
   */
  async getProjectRecommendations(projectId, options = {}) {
    try {
      const { priorityFilter, recommendationType, limit = 10 } = options;
      const params = { limit };
      
      if (priorityFilter) params.priority_filter = priorityFilter;
      if (recommendationType) params.recommendation_type = recommendationType;

      const response = await apiClient.get(`/security/recommendations/${projectId}`, { params });
      return response.data;
    } catch (error) {
      console.error('Error getting project recommendations:', error);
      throw error;
    }
  }

  /**
   * Get latest AWS security updates
   */
  async getAWSSecurityUpdates(filterByServices = []) {
    try {
      const params = filterByServices.length > 0 ? { filter_by_services: filterByServices } : {};
      const response = await apiClient.get('/security/aws-security-updates', { params });
      return response.data;
    } catch (error) {
      console.error('Error getting AWS security updates:', error);
      throw error;
    }
  }

  /**
   * Get detailed implementation plan for a security recommendation
   */
  async getImplementationPlan(recommendationId, projectId) {
    try {
      const response = await apiClient.post(`/security/recommendation-implementation-plan/${recommendationId}`, {
        project_id: projectId
      });
      return response.data;
    } catch (error) {
      console.error('Error getting implementation plan:', error);
      throw error;
    }
  }

  /**
   * Get compliance dashboard for a project
   */
  async getComplianceDashboard(projectId) {
    try {
      const response = await apiClient.get(`/security/compliance-dashboard/${projectId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting compliance dashboard:', error);
      throw error;
    }
  }

  /**
   * Start bulk analysis for multiple projects
   */
  async bulkAnalyzeProjects(projectIds) {
    try {
      const response = await apiClient.post('/security/bulk-analyze', {
        project_ids: projectIds
      });
      return response.data;
    } catch (error) {
      console.error('Error starting bulk analysis:', error);
      throw error;
    }
  }

  /**
   * Get mock security data for demo purposes
   */
  async getMockSecurityData(projectId = 'demo') {
    try {
      // Return simulated security data structure similar to real API
      return {
        project_id: projectId,
        security_posture_score: 87,
        vulnerabilities_count: 7,
        last_analyzed: new Date().toISOString(),
        compliance_status: {
          hipaa: { compliance_score: 92, status: 'compliant', critical_issues: 0, total_recommendations: 2 },
          'pci-dss': { compliance_score: 78, status: 'non_compliant', critical_issues: 2, total_recommendations: 5 },
          sox: { compliance_score: 95, status: 'compliant', critical_issues: 0, total_recommendations: 1 }
        },
        recommendations: [
          {
            id: 'encrypt_at_rest',
            title: 'Enable Encryption at Rest',
            description: 'Encrypt sensitive data stored in databases and storage services using AWS KMS',
            recommendation_type: 'best_practice',
            affected_services: ['S3', 'RDS', 'DynamoDB'],
            priority: 'high',
            implementation_effort: 'low',
            cost_impact: 'low',
            compliance_frameworks: ['HIPAA', 'PCI-DSS', 'SOX'],
            aws_documentation_url: 'https://docs.aws.amazon.com/kms/latest/developerguide/',
            implementation_steps: [
              'Create KMS key for encryption',
              'Enable encryption on storage services',
              'Configure automatic key rotation',
              'Update IAM policies for KMS access'
            ],
            created_at: new Date().toISOString()
          },
          {
            id: 'enable_waf',
            title: 'Enable AWS WAF Protection',
            description: 'Protect web applications from common attacks using AWS WAF with managed rule groups',
            recommendation_type: 'best_practice',
            affected_services: ['ALB', 'CloudFront', 'API Gateway'],
            priority: 'high',
            implementation_effort: 'medium',
            cost_impact: 'medium',
            compliance_frameworks: ['PCI-DSS'],
            aws_documentation_url: 'https://docs.aws.amazon.com/waf/latest/developerguide/',
            implementation_steps: [
              'Create WAF Web ACL',
              'Configure managed rule groups',
              'Associate WAF with load balancer/CloudFront',
              'Set up monitoring and alerting'
            ],
            created_at: new Date().toISOString()
          },
          {
            id: 'enable_guardduty',
            title: 'Enable Amazon GuardDuty',
            description: 'Detect threats and malicious activity using machine learning for continuous monitoring',
            recommendation_type: 'best_practice',
            affected_services: ['All Services'],
            priority: 'medium',
            implementation_effort: 'low',
            cost_impact: 'low',
            compliance_frameworks: ['All'],
            aws_documentation_url: 'https://docs.aws.amazon.com/guardduty/latest/ug/',
            implementation_steps: [
              'Enable GuardDuty in AWS console',
              'Configure finding types',
              'Set up SNS notifications',
              'Integrate with Security Hub'
            ],
            created_at: new Date().toISOString()
          }
        ],
        security_metrics: {
          threat_detection_coverage: 85,
          encryption_coverage: 78,
          access_control_score: 92,
          monitoring_coverage: 88,
          compliance_readiness: 85
        },
        threats: [
          {
            id: 1,
            severity: 'critical',
            title: 'S3 Bucket Publicly Accessible',
            description: 'data-backup-bucket has public read access enabled',
            service: 'S3',
            detectedAt: '2 hours ago',
            status: 'active'
          },
          {
            id: 2,
            severity: 'high',
            title: 'EC2 Instance with Open SSH',
            description: 'Security group allows SSH (port 22) from 0.0.0.0/0',
            service: 'EC2',
            detectedAt: '4 hours ago',
            status: 'active'
          },
          {
            id: 3,
            severity: 'medium',
            title: 'RDS Instance Without Encryption',
            description: 'Database instance is not encrypted at rest',
            service: 'RDS',
            detectedAt: '1 day ago',
            status: 'investigating'
          }
        ],
        recent_activity: [
          { action: 'New security policy applied', time: '30 minutes ago', type: 'improvement' },
          { action: 'Suspicious login attempt blocked', time: '2 hours ago', type: 'threat' },
          { action: 'SSL certificate renewed', time: '1 day ago', type: 'maintenance' },
          { action: 'Security scan completed', time: '1 day ago', type: 'scan' }
        ]
      };
    } catch (error) {
      console.error('Error getting mock security data:', error);
      throw error;
    }
  }

  /**
   * Get security score breakdown by category
   */
  getSecurityScoreBreakdown(securityData) {
    const breakdown = {
      threat_detection: {
        score: securityData.security_metrics?.threat_detection_coverage || 85,
        description: 'Coverage of threat detection services',
        status: 'good'
      },
      encryption: {
        score: securityData.security_metrics?.encryption_coverage || 78,
        description: 'Data encryption at rest and in transit',
        status: 'needs_improvement'
      },
      access_control: {
        score: securityData.security_metrics?.access_control_score || 92,
        description: 'IAM policies and access management',
        status: 'excellent'
      },
      monitoring: {
        score: securityData.security_metrics?.monitoring_coverage || 88,
        description: 'Security monitoring and logging',
        status: 'good'
      },
      compliance: {
        score: securityData.security_metrics?.compliance_readiness || 85,
        description: 'Compliance framework adherence',
        status: 'good'
      }
    };

    // Determine status based on score
    Object.keys(breakdown).forEach(category => {
      const score = breakdown[category].score;
      if (score >= 90) breakdown[category].status = 'excellent';
      else if (score >= 80) breakdown[category].status = 'good';
      else if (score >= 70) breakdown[category].status = 'needs_improvement';
      else breakdown[category].status = 'critical';
    });

    return breakdown;
  }

  /**
   * Get recommendations by priority
   */
  getRecommendationsByPriority(recommendations) {
    const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
    return recommendations.sort((a, b) => {
      return (priorityOrder[b.priority] || 0) - (priorityOrder[a.priority] || 0);
    });
  }

  /**
   * Get recommendations by category
   */
  getRecommendationsByCategory(recommendations) {
    const categories = {
      encryption: [],
      access_control: [],
      monitoring: [],
      compliance: [],
      network_security: [],
      other: []
    };

    recommendations.forEach(rec => {
      if (rec.title.toLowerCase().includes('encrypt') || rec.title.toLowerCase().includes('kms')) {
        categories.encryption.push(rec);
      } else if (rec.title.toLowerCase().includes('iam') || rec.title.toLowerCase().includes('access')) {
        categories.access_control.push(rec);
      } else if (rec.title.toLowerCase().includes('guard') || rec.title.toLowerCase().includes('monitor')) {
        categories.monitoring.push(rec);
      } else if (rec.compliance_frameworks.length > 0) {
        categories.compliance.push(rec);
      } else if (rec.title.toLowerCase().includes('waf') || rec.title.toLowerCase().includes('network')) {
        categories.network_security.push(rec);
      } else {
        categories.other.push(rec);
      }
    });

    return categories;
  }

  /**
   * Get threat severity distribution
   */
  getThreatSeverityDistribution(threats) {
    const distribution = { critical: 0, high: 0, medium: 0, low: 0 };
    
    threats.forEach(threat => {
      distribution[threat.severity] = (distribution[threat.severity] || 0) + 1;
    });

    return distribution;
  }

  /**
   * Calculate security improvement impact
   */
  calculateSecurityImprovementImpact(currentScore, recommendations) {
    let potentialImprovement = 0;
    
    recommendations.forEach(rec => {
      switch (rec.priority) {
        case 'critical':
          potentialImprovement += 15;
          break;
        case 'high':
          potentialImprovement += 10;
          break;
        case 'medium':
          potentialImprovement += 5;
          break;
        case 'low':
          potentialImprovement += 2;
          break;
      }
    });

    const projectedScore = Math.min(100, currentScore + potentialImprovement);
    const improvementPercentage = ((projectedScore - currentScore) / currentScore) * 100;

    return {
      current_score: currentScore,
      projected_score: projectedScore,
      improvement_points: potentialImprovement,
      improvement_percentage: Math.round(improvementPercentage),
      recommendations_to_implement: recommendations.length
    };
  }

  /**
   * Format security score for display
   */
  formatSecurityScore(score) {
    if (score >= 90) return { value: score, status: 'excellent', color: 'green' };
    if (score >= 80) return { value: score, status: 'good', color: 'blue' };
    if (score >= 70) return { value: score, status: 'needs improvement', color: 'orange' };
    return { value: score, status: 'critical', color: 'red' };
  }

  /**
   * Get compliance framework details
   */
  getComplianceFrameworkDetails() {
    return {
      hipaa: {
        name: 'HIPAA',
        full_name: 'Health Insurance Portability and Accountability Act',
        description: 'Protects sensitive patient health information',
        key_requirements: ['Data encryption', 'Access controls', 'Audit trails', 'Risk assessments']
      },
      'pci-dss': {
        name: 'PCI DSS',
        full_name: 'Payment Card Industry Data Security Standard',
        description: 'Security standards for organizations that handle payment cards',
        key_requirements: ['Network security', 'Data protection', 'Vulnerability management', 'Access monitoring']
      },
      sox: {
        name: 'SOX',
        full_name: 'Sarbanes-Oxley Act',
        description: 'Financial reporting and corporate governance requirements',
        key_requirements: ['Financial data integrity', 'Change management', 'Access controls', 'Audit trails']
      },
      gdpr: {
        name: 'GDPR',
        full_name: 'General Data Protection Regulation',
        description: 'Data protection and privacy regulation in the EU',
        key_requirements: ['Data consent', 'Right to erasure', 'Data portability', 'Privacy by design']
      }
    };
  }
}

export default new SecurityService();