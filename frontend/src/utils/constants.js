// utils/constants.js

export const QUESTIONNAIRE_QUESTIONS = [
  {
    id: 'project_name',
    title: 'Project Setup',
    question: 'What would you like to name your project?',
    type: 'text',
    placeholder: 'e.g., My E-commerce Platform',
    category: 'Basic Info',
    explanation: 'This name will help you identify and organize your architecture project. It will be used in your AWS resource naming and project documentation.',
    examples: [
      'E-commerce Platform',
      'Company Blog',
      'Data Analytics Dashboard',
      'Mobile App Backend'
    ],
    impact: {
      services: 'Used in resource naming',
      cost: 'No direct impact',
      security: 'No direct impact'
    }
  },
  {
    id: 'description',
    title: 'Project Description',
    question: 'Briefly describe what your project does',
    type: 'textarea',
    placeholder: 'Describe the main purpose and functionality of your application...',
    category: 'Basic Info',
    explanation: 'A clear description helps our AI understand your project context and suggest more relevant AWS services and configurations.',
    examples: [
      'An online store selling handmade crafts with user accounts and payment processing',
      'A blog platform where users can create and share articles with comment functionality',
      'A data dashboard that processes customer analytics and generates reports',
      'A mobile app backend handling user authentication and real-time messaging'
    ]
  },
  {
    id: 'compute_preference',
    title: 'Compute Strategy',
    question: 'How would you prefer to run your application?',
    type: 'radio',
    category: 'Technical',
    explanation: 'Different compute options offer various benefits in terms of cost, scalability, and management overhead. Your choice affects which AWS services we recommend.',
    impact: {
      services: 'Lambda, ECS, or EC2',
      cost: 'Serverless can be cheaper for low traffic',
      security: 'Managed services include built-in security'
    },
    options: [
      {
        value: 'serverless',
        label: 'Serverless',
        description: 'No server management, pay only for what you use',
        recommended: true,
        detailedInfo: {
          awsServices: 'AWS Lambda, API Gateway, DynamoDB',
          costRange: '$5-50/month for small to medium apps',
          useCase: 'Event-driven apps, APIs, microservices with variable traffic'
        }
      },
      {
        value: 'containers',
        label: 'Containers',
        description: 'Docker containers with managed orchestration',
        popular: true,
        detailedInfo: {
          awsServices: 'Amazon ECS, AWS Fargate, Application Load Balancer',
          costRange: '$30-200/month depending on usage',
          useCase: 'Microservices, applications requiring consistent runtime environment'
        }
      },
      {
        value: 'vms',
        label: 'Virtual Machines',
        description: 'Traditional servers with full control',
        detailedInfo: {
          awsServices: 'Amazon EC2, Auto Scaling Groups, Elastic Load Balancer',
          costRange: '$50-500+/month depending on instance sizes',
          useCase: 'Legacy applications, applications requiring specific OS configurations'
        }
      }
    ]
  },
  {
    id: 'database_type',
    title: 'Data Storage',
    question: 'What type of database does your application need?',
    type: 'radio',
    category: 'Technical',
    explanation: 'Database choice affects performance, scalability, and cost. SQL databases are great for structured data with relationships, while NoSQL excels at flexible, scalable applications.',
    impact: {
      services: 'RDS, DynamoDB, or DocumentDB',
      cost: 'NoSQL can be more cost-effective at scale',
      security: 'Both offer encryption and access controls'
    },
    options: [
      {
        value: 'sql',
        label: 'SQL Database (Relational)',
        description: 'Structured data with relationships between tables',
        popular: true,
        detailedInfo: {
          awsServices: 'Amazon RDS (MySQL, PostgreSQL, SQL Server)',
          costRange: '$15-100+/month depending on size',
          useCase: 'E-commerce, CRM, financial applications, complex queries'
        }
      },
      {
        value: 'nosql',
        label: 'NoSQL Database (Document/Key-Value)',
        description: 'Flexible schema for rapid development and scaling',
        recommended: true,
        detailedInfo: {
          awsServices: 'Amazon DynamoDB, DocumentDB',
          costRange: '$1-50+/month based on usage',
          useCase: 'Social media, gaming, IoT, content management, real-time apps'
        }
      },
      {
        value: 'none',
        label: 'No Database Needed',
        description: 'Static sites or applications using external data sources',
        detailedInfo: {
          awsServices: 'Amazon S3 for static content',
          costRange: '$1-10/month for static hosting',
          useCase: 'Static websites, documentation sites, landing pages'
        }
      }
    ]
  },
  {
    id: 'storage_needs',
    title: 'Storage Requirements',
    question: 'How much file storage do you expect to need?',
    type: 'radio',
    category: 'Technical',
    explanation: 'Storage requirements help us determine the right combination of AWS storage services and estimate costs for your file storage needs.',
    impact: {
      services: 'S3, EFS, or EBS volumes',
      cost: 'Storage costs scale with data volume',
      security: 'All options include encryption capabilities'
    },
    options: [
      {
        value: 'minimal',
        label: 'Minimal (< 100GB)',
        description: 'Small files, basic document storage',
        detailedInfo: {
          awsServices: 'Amazon S3 Standard',
          costRange: '$2-10/month',
          useCase: 'Profile images, documents, small media files'
        }
      },
      {
        value: 'moderate',
        label: 'Moderate (100GB - 1TB)',
        description: 'Regular file uploads, media content',
        popular: true,
        detailedInfo: {
          awsServices: 'Amazon S3 with Intelligent Tiering',
          costRange: '$10-50/month',
          useCase: 'User-generated content, product images, video content'
        }
      },
      {
        value: 'extensive',
        label: 'Extensive (> 1TB)',
        description: 'Large datasets, media libraries, backups',
        detailedInfo: {
          awsServices: 'Amazon S3 with multiple storage classes, EFS',
          costRange: '$50-500+/month depending on access patterns',
          useCase: 'Data lakes, large media libraries, enterprise backups'
        }
      }
    ]
  },
  {
    id: 'traffic_volume',
    title: 'Expected Traffic',
    question: 'How many users do you expect to visit your application daily?',
    type: 'radio',
    category: 'Scale',
    explanation: 'Traffic expectations help us size your infrastructure appropriately and recommend auto-scaling configurations to handle load efficiently.',
    impact: {
      services: 'Load balancers, CDN, auto-scaling',
      cost: 'Higher traffic requires more resources',
      security: 'More traffic needs DDoS protection'
    },
    options: [
      {
        value: 'low',
        label: 'Low (< 1,000 users/day)',
        description: 'Personal projects, small business sites',
        detailedInfo: {
          awsServices: 'Basic compute and storage, CloudFront optional',
          costRange: '$10-50/month',
          useCase: 'Personal blogs, small business websites, prototypes'
        }
      },
      {
        value: 'medium',
        label: 'Medium (1K - 10K users/day)',
        description: 'Growing applications, small to medium businesses',
        popular: true,
        detailedInfo: {
          awsServices: 'Load balancers, auto-scaling, CloudFront CDN',
          costRange: '$50-200/month',
          useCase: 'Company websites, small e-commerce sites, SaaS applications'
        }
      },
      {
        value: 'high',
        label: 'High (> 10K users/day)',
        description: 'Popular applications, enterprise level',
        detailedInfo: {
          awsServices: 'Multi-AZ deployment, advanced load balancing, CDN',
          costRange: '$200-1000+/month',
          useCase: 'Popular web apps, large e-commerce, enterprise applications'
        }
      }
    ]
  },
  {
    id: 'geographical_reach',
    title: 'Geographic Distribution',
    question: 'Where are your users located?',
    type: 'radio',
    category: 'Scale',
    explanation: 'User location affects latency and compliance requirements. Global reach requires CDN and multi-region deployment for optimal performance.',
    impact: {
      services: 'CloudFront CDN, Route 53, multi-region setup',
      cost: 'Global deployment increases costs',
      security: 'Multi-region requires distributed security controls'
    },
    options: [
      {
        value: 'single_region',
        label: 'Single Region',
        description: 'Users primarily in one geographic area',
        detailedInfo: {
          awsServices: 'Single AWS region deployment',
          costRange: 'Base cost for chosen region',
          useCase: 'Local businesses, region-specific applications'
        }
      },
      {
        value: 'multi_region',
        label: 'Multiple Regions',
        description: 'Users spread across several countries/continents',
        popular: true,
        detailedInfo: {
          awsServices: 'CloudFront CDN, Route 53 DNS, multi-region deployment',
          costRange: '1.5-2x single region cost',
          useCase: 'International businesses, global applications'
        }
      },
      {
        value: 'global',
        label: 'Global',
        description: 'Users worldwide requiring optimal performance everywhere',
        detailedInfo: {
          awsServices: 'Global CDN, edge locations, disaster recovery',
          costRange: '2-3x single region cost',
          useCase: 'Social media platforms, gaming, global SaaS'
        }
      }
    ]
  },
  {
    id: 'data_sensitivity',
    title: 'Data Security',
    question: 'How sensitive is the data your application will handle?',
    type: 'radio',
    category: 'Security',
    explanation: 'Data sensitivity determines the security controls, encryption requirements, and compliance measures we need to implement in your architecture.',
    impact: {
      services: 'KMS, GuardDuty, Security Hub, WAF',
      cost: 'Enhanced security increases costs',
      security: 'Higher sensitivity requires more security layers'
    },
    options: [
      {
        value: 'public',
        label: 'Public',
        description: 'Publicly available information, no privacy concerns',
        detailedInfo: {
          awsServices: 'Basic S3 security, standard encryption',
          costRange: 'No additional security costs',
          useCase: 'Marketing websites, public documentation, blogs'
        }
      },
      {
        value: 'internal',
        label: 'Internal',
        description: 'Business data that should remain within organization',
        popular: true,
        detailedInfo: {
          awsServices: 'VPC, Security Groups, IAM roles, CloudTrail',
          costRange: '+$10-30/month for security services',
          useCase: 'Company intranets, business applications, internal tools'
        }
      },
      {
        value: 'confidential',
        label: 'Confidential',
        description: 'Highly sensitive data requiring strict protection',
        detailedInfo: {
          awsServices: 'KMS encryption, GuardDuty, Security Hub, WAF, VPC Flow Logs',
          costRange: '+$50-200/month for comprehensive security',
          useCase: 'Financial data, healthcare records, personal information'
        }
      }
    ]
  },
  {
    id: 'budget_range',
    title: 'Budget Planning',
    question: 'What is your expected monthly budget for AWS infrastructure?',
    type: 'radio',
    category: 'Business',
    explanation: 'Budget constraints help us recommend cost-effective solutions and suggest Reserved Instances or Savings Plans for long-term cost optimization.',
    impact: {
      services: 'Instance sizes, managed vs self-managed services',
      cost: 'Directly affects service selection',
      security: 'Budget affects security service options'
    },
    options: [
      {
        value: 'startup',
        label: 'Startup (< $500/month)',
        description: 'Cost-conscious, essential services only',
        popular: true,
        detailedInfo: {
          awsServices: 'Free tier eligible services, serverless, minimal instances',
          costRange: '$50-500/month',
          useCase: 'Startups, MVPs, small applications, development environments'
        }
      },
      {
        value: 'small_business',
        label: 'Small Business ($500-2K/month)',
        description: 'Balanced performance and cost considerations',
        detailedInfo: {
          awsServices: 'Mix of managed and self-managed services, reserved instances',
          costRange: '$500-2000/month',
          useCase: 'Growing businesses, production applications, moderate scale'
        }
      },
      {
        value: 'enterprise',
        label: 'Enterprise (> $2K/month)',
        description: 'Performance and reliability prioritized over cost',
        detailedInfo: {
          awsServices: 'Premium support, enterprise services, multi-AZ deployment',
          costRange: '$2000+/month',
          useCase: 'Large organizations, mission-critical applications, high availability'
        }
      }
    ]
  },
  {
    id: 'compliance_requirements',
    title: 'Compliance & Regulations',
    question: 'Which compliance standards does your application need to meet?',
    type: 'checkbox',
    category: 'Security',
    explanation: 'Compliance requirements determine specific security controls, data handling procedures, and audit trails that must be implemented in your AWS architecture.',
    impact: {
      services: 'Compliance-specific AWS services and configurations',
      cost: 'Compliance can add 20-50% to infrastructure costs',
      security: 'Strict security controls and monitoring required'
    },
    options: [
      {
        value: 'hipaa',
        label: 'HIPAA',
        description: 'Healthcare data protection (US)',
        detailedInfo: {
          awsServices: 'HIPAA-eligible services, KMS, CloudTrail, dedicated instances',
          costRange: '+30-50% for compliance controls',
          useCase: 'Healthcare applications, medical records, health data processing'
        }
      },
      {
        value: 'pci',
        label: 'PCI DSS',
        description: 'Payment card industry data security',
        detailedInfo: {
          awsServices: 'WAF, Inspector, Config, dedicated networking',
          costRange: '+25-40% for security requirements',
          useCase: 'E-commerce, payment processing, financial transactions'
        }
      },
      {
        value: 'gdpr',
        label: 'GDPR',
        description: 'European data protection regulation',
        detailedInfo: {
          awsServices: 'Data residency controls, encryption, audit logging',
          costRange: '+15-25% for data protection measures',
          useCase: 'Applications serving European users, personal data processing'
        }
      },
      {
        value: 'sox',
        label: 'SOX',
        description: 'Sarbanes-Oxley financial compliance (US)',
        detailedInfo: {
          awsServices: 'Comprehensive logging, access controls, audit trails',
          costRange: '+20-35% for financial controls',
          useCase: 'Financial reporting, public company applications, accounting systems'
        }
      },
      {
        value: 'none',
        label: 'None',
        description: 'No specific compliance requirements',
        recommended: true,
        detailedInfo: {
          awsServices: 'Standard AWS security best practices',
          costRange: 'No additional compliance costs',
          useCase: 'General applications, internal tools, non-regulated industries'
        }
      }
    ]
  }
];