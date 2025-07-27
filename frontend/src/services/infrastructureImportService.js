import { apiClient } from './api';
import { extractApiErrorMessage } from '../utils/errorUtils';

class InfrastructureImportService {
  /**
   * Scan AWS account to discover existing infrastructure
   */
  async scanAWSAccount(credentials) {
    try {
      const response = await apiClient.post('/infrastructure-import/scan-aws-account', credentials);
      return response.data;
    } catch (error) {
      console.error('Error scanning AWS account:', error);
      throw new Error(extractApiErrorMessage(error, 'Failed to scan AWS account'));
    }
  }

  /**
   * Import infrastructure and create a new project
   */
  async importInfrastructure(importRequest) {
    try {
      const response = await apiClient.post('/infrastructure-import/import-infrastructure', importRequest);
      return response.data;
    } catch (error) {
      console.error('Error importing infrastructure:', error);
      throw new Error(extractApiErrorMessage(error, 'Failed to import infrastructure'));
    }
  }

  /**
   * Generate Terraform configuration from scanned infrastructure
   */
  async generateTerraform(infrastructure) {
    try {
      const response = await apiClient.post('/infrastructure-import/generate-terraform', infrastructure);
      return response.data;
    } catch (error) {
      console.error('Error generating Terraform:', error);
      throw new Error(extractApiErrorMessage(error, 'Failed to generate Terraform configuration'));
    }
  }

  /**
   * Generate CloudFormation template from scanned infrastructure
   */
  async generateCloudFormation(infrastructure) {
    try {
      const response = await apiClient.post('/infrastructure-import/generate-cloudformation', infrastructure);
      return response.data;
    } catch (error) {
      console.error('Error generating CloudFormation:', error);
      throw new Error(extractApiErrorMessage(error, 'Failed to generate CloudFormation template'));
    }
  }

  /**
   * Analyze security posture of imported infrastructure
   */
  async analyzeImportedSecurity(infrastructure) {
    try {
      const response = await apiClient.post('/infrastructure-import/analyze-security', infrastructure);
      return response.data;
    } catch (error) {
      console.error('Error analyzing security:', error);
      throw new Error(extractApiErrorMessage(error, 'Failed to analyze infrastructure security'));
    }
  }

  /**
   * Generate architecture diagram from imported infrastructure
   */
  async generateDiagram(infrastructure) {
    try {
      const response = await apiClient.post('/infrastructure-import/generate-diagram', infrastructure);
      return response.data;
    } catch (error) {
      console.error('Error generating diagram:', error);
      throw new Error(extractApiErrorMessage(error, 'Failed to generate architecture diagram'));
    }
  }

  /**
   * Get mock infrastructure data for demo purposes
   */
  getMockInfrastructure() {
    return {
      account_id: "123456789012",
      region: "us-east-1",
      scan_timestamp: new Date().toISOString(),
      services: {
        ec2: {
          instances: [
            {
              instance_id: "i-1234567890abcdef0",
              instance_type: "t3.medium",
              state: "running",
              vpc_id: "vpc-12345678",
              subnet_id: "subnet-12345678",
              security_groups: ["sg-12345678"],
              tags: { Name: "WebServer", Environment: "production" }
            }
          ],
          security_groups: [
            {
              group_id: "sg-12345678",
              group_name: "web-server-sg",
              description: "Security group for web server",
              inbound_rules: [
                { protocol: "tcp", port: 80, source: "0.0.0.0/0" },
                { protocol: "tcp", port: 443, source: "0.0.0.0/0" }
              ]
            }
          ]
        },
        rds: {
          instances: [
            {
              db_instance_identifier: "prod-database",
              db_instance_class: "db.t3.micro",
              engine: "mysql",
              engine_version: "8.0.35",
              allocated_storage: 20,
              vpc_security_groups: ["sg-87654321"]
            }
          ]
        },
        s3: {
          buckets: [
            {
              bucket_name: "my-app-assets-bucket",
              region: "us-east-1",
              encryption: { enabled: true, type: "AES256" },
              versioning: { enabled: true },
              public_access: { blocked: true }
            }
          ]
        },
        lambda: {
          functions: [
            {
              function_name: "process-uploads",
              runtime: "python3.9",
              memory_size: 256,
              timeout: 30,
              environment_variables: { BUCKET_NAME: "my-app-assets-bucket" }
            }
          ]
        },
        vpc: {
          vpcs: [
            {
              vpc_id: "vpc-12345678",
              cidr_block: "10.0.0.0/16",
              state: "available",
              subnets: [
                {
                  subnet_id: "subnet-12345678",
                  cidr_block: "10.0.1.0/24",
                  availability_zone: "us-east-1a",
                  type: "public"
                }
              ]
            }
          ]
        }
      }
    };
  }

  /**
   * Format resource count for display
   */
  formatResourceCount(services) {
    const counts = {};
    
    Object.entries(services).forEach(([serviceName, serviceData]) => {
      if (typeof serviceData === 'object' && serviceData !== null) {
        // Count different resource types within each service
        const resourceTypes = Object.keys(serviceData);
        let totalCount = 0;
        
        resourceTypes.forEach(resourceType => {
          const resources = serviceData[resourceType];
          if (Array.isArray(resources)) {
            totalCount += resources.length;
          }
        });
        
        counts[serviceName] = totalCount;
      }
    });
    
    return counts;
  }

  /**
   * Extract service names from infrastructure
   */
  getDiscoveredServices(infrastructure) {
    const services = infrastructure?.services || {};
    return Object.keys(services).filter(service => {
      const serviceData = services[service];
      return serviceData && Object.keys(serviceData).length > 0;
    });
  }

  /**
   * Calculate total resources discovered
   */
  getTotalResourceCount(infrastructure) {
    const services = infrastructure?.services || {};
    let total = 0;
    
    Object.values(services).forEach(serviceData => {
      if (typeof serviceData === 'object' && serviceData !== null) {
        Object.values(serviceData).forEach(resources => {
          if (Array.isArray(resources)) {
            total += resources.length;
          }
        });
      }
    });
    
    return total;
  }

  /**
   * Get security risk summary from infrastructure
   */
  getSecurityRiskSummary(infrastructure) {
    const risks = {
      high: 0,
      medium: 0,
      low: 0
    };

    // Check for common security issues
    const services = infrastructure?.services || {};

    // Check for open security groups
    if (services.ec2?.security_groups) {
      services.ec2.security_groups.forEach(sg => {
        sg.inbound_rules?.forEach(rule => {
          if (rule.source === "0.0.0.0/0") {
            risks.high++;
          }
        });
      });
    }

    // Check for unencrypted S3 buckets
    if (services.s3?.buckets) {
      services.s3.buckets.forEach(bucket => {
        if (!bucket.encryption?.enabled) {
          risks.medium++;
        }
        if (!bucket.public_access?.blocked) {
          risks.high++;
        }
      });
    }

    // Check for database security
    if (services.rds?.instances) {
      services.rds.instances.forEach(db => {
        // This would check for various RDS security configurations
        risks.low++; // Placeholder for actual security checks
      });
    }

    return risks;
  }

  /**
   * Validate AWS credentials format
   */
  validateCredentials(credentials) {
    const errors = [];

    if (!credentials.access_key_id || credentials.access_key_id.length < 16) {
      errors.push('Valid AWS Access Key ID is required');
    }

    if (!credentials.secret_access_key || credentials.secret_access_key.length < 20) {
      errors.push('Valid AWS Secret Access Key is required');
    }

    if (!credentials.region) {
      errors.push('AWS Region is required');
    }

    return errors;
  }

  /**
   * Get available AWS regions
   */
  getAWSRegions() {
    return [
      { value: 'us-east-1', label: 'US East (N. Virginia)' },
      { value: 'us-east-2', label: 'US East (Ohio)' },
      { value: 'us-west-1', label: 'US West (N. California)' },
      { value: 'us-west-2', label: 'US West (Oregon)' },
      { value: 'eu-west-1', label: 'Europe (Ireland)' },
      { value: 'eu-west-2', label: 'Europe (London)' },
      { value: 'eu-west-3', label: 'Europe (Paris)' },
      { value: 'eu-central-1', label: 'Europe (Frankfurt)' },
      { value: 'ap-southeast-1', label: 'Asia Pacific (Singapore)' },
      { value: 'ap-southeast-2', label: 'Asia Pacific (Sydney)' },
      { value: 'ap-northeast-1', label: 'Asia Pacific (Tokyo)' },
      { value: 'ap-south-1', label: 'Asia Pacific (Mumbai)' },
      { value: 'ca-central-1', label: 'Canada (Central)' }
    ];
  }
}

export default new InfrastructureImportService();