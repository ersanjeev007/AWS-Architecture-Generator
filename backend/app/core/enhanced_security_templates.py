from typing import Dict, List
import json

class EnhancedSecurityTemplates:
    """Enhanced security templates with comprehensive IAM, encryption, monitoring and compliance features"""
    
    def __init__(self):
        self.security_levels = {
            "basic": ["encryption", "vpc", "iam_least_privilege"],
            "medium": ["encryption", "vpc", "iam_least_privilege", "security_groups", "monitoring", "backup", "mfa_enforcement"],
            "high": ["encryption", "vpc", "iam_least_privilege", "security_groups", "monitoring", "backup", "waf", "secrets", "multi_az", "logging", "mfa_enforcement", "guard_duty", "security_hub", "config", "macie", "inspector"]
        }
        
        self.compliance_frameworks = {
            "hipaa": ["encryption_cmk", "logging_cloudtrail", "access_control", "data_classification", "backup_retention"],
            "pci-dss": ["encryption_transit", "network_segmentation", "access_logging", "vulnerability_scanning", "penetration_testing"],
            "sox": ["audit_logging", "change_management", "access_reviews", "data_integrity", "retention_policies"],
            "gdpr": ["data_encryption", "access_controls", "data_portability", "deletion_capabilities", "consent_management"],
            "fedramp": ["encryption_fips", "continuous_monitoring", "incident_response", "access_control", "audit_logging"]
        }
    
    def generate_enhanced_iam_policies(self, project_name: str, services: Dict[str, str], security_level: str) -> str:
        """Generate comprehensive IAM policies with least privilege principle"""
        
        policies = {
            "ec2_role_policy": self._generate_ec2_iam_policy(services, security_level),
            "lambda_role_policy": self._generate_lambda_iam_policy(services, security_level),
            "ecs_role_policy": self._generate_ecs_iam_policy(services, security_level),
            "cross_account_policy": self._generate_cross_account_policy(security_level),
            "security_audit_policy": self._generate_security_audit_policy(),
            "backup_policy": self._generate_backup_iam_policy(services),
            "monitoring_policy": self._generate_monitoring_iam_policy(),
        }
        
        terraform_iam = f'''
# Enhanced IAM Policies and Roles with Least Privilege
# Generated for security level: {security_level}

# IAM Password Policy
resource "aws_iam_account_password_policy" "main" {{
  minimum_password_length        = 14
  require_lowercase_characters   = true
  require_numbers                = true
  require_uppercase_characters   = true
  require_symbols                = true
  allow_users_to_change_password = true
  max_password_age              = 90
  password_reuse_prevention     = 12
  hard_expiry                   = false
}}

# IAM Access Analyzer
resource "aws_accessanalyzer_analyzer" "main" {{
  analyzer_name = "{project_name}-access-analyzer"
  type         = "ACCOUNT"
  
  tags = {{
    Name        = "{project_name}-access-analyzer"
    Environment = var.environment
  }}
}}

# Service Control Policy for Organization (if applicable)
resource "aws_organizations_policy" "security_scp" {{
  count       = var.enable_scp ? 1 : 0
  name        = "{project_name}-security-scp"
  description = "Security Service Control Policy"
  type        = "SERVICE_CONTROL_POLICY"
  
  content = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Sid    = "DenyUnencryptedObjectUploads"
        Effect = "Deny"
        Action = "s3:PutObject"
        Resource = "*"
        Condition = {{
          StringNotEquals = {{
            "s3:x-amz-server-side-encryption" = "AES256"
          }}
        }}
      }},
      {{
        Sid    = "DenyInsecureConnections"
        Effect = "Deny"
        Action = "s3:*"
        Resource = "*"
        Condition = {{
          Bool = {{
            "aws:SecureTransport" = "false"
          }}
        }}
      }},
      {{
        Sid    = "DenyRootAccountUsage"
        Effect = "Deny"
        NotAction = [
          "iam:CreateVirtualMFADevice",
          "iam:EnableMFADevice",
          "iam:GetUser",
          "iam:ListMFADevices",
          "iam:ListVirtualMFADevices",
          "iam:ResyncMFADevice",
          "sts:GetSessionToken"
        ]
        Resource = "*"
        Condition = {{
          StringEquals = {{
            "aws:PrincipalType" = "Root"
          }}
        }}
      }}
    ]
  }})
}}

# Enhanced EC2 IAM Role with Least Privilege
{policies["ec2_role_policy"]}

# Enhanced Lambda IAM Role 
{policies["lambda_role_policy"]}

# Enhanced ECS IAM Roles
{policies["ecs_role_policy"]}

# Cross-Account Access Role (if needed)
{policies["cross_account_policy"]}

# Security Audit Role
{policies["security_audit_policy"]}

# Backup Service Role
{policies["backup_policy"]}

# CloudWatch and Monitoring Role
{policies["monitoring_policy"]}

# IAM Role for AWS Config
resource "aws_iam_role" "config" {{
  count = contains(var.security_features, "config") ? 1 : 0
  name  = "{project_name}-config-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "config.amazonaws.com"
        }}
      }}
    ]
  }})
  
  tags = {{
    Name        = "{project_name}-config-role"
    Environment = var.environment
  }}
}}

resource "aws_iam_role_policy_attachment" "config" {{
  count      = contains(var.security_features, "config") ? 1 : 0
  role       = aws_iam_role.config[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/ConfigRole"
}}

# IAM Role for GuardDuty
resource "aws_iam_role" "guardduty" {{
  count = contains(var.security_features, "guard_duty") ? 1 : 0
  name  = "{project_name}-guardduty-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "guardduty.amazonaws.com"
        }}
      }}
    ]
  }})
  
  tags = {{
    Name        = "{project_name}-guardduty-role"
    Environment = var.environment
  }}
}}

# IAM Role for Security Hub
resource "aws_iam_role" "security_hub" {{
  count = contains(var.security_features, "security_hub") ? 1 : 0
  name  = "{project_name}-security-hub-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "securityhub.amazonaws.com"
        }}
      }}
    ]
  }})
  
  tags = {{
    Name        = "{project_name}-security-hub-role"
    Environment = var.environment
  }}
}}

# IAM Role for Inspector
resource "aws_iam_role" "inspector" {{
  count = contains(var.security_features, "inspector") ? 1 : 0
  name  = "{project_name}-inspector-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "inspector2.amazonaws.com"
        }}
      }}
    ]
  }})
  
  tags = {{
    Name        = "{project_name}-inspector-role"
    Environment = var.environment
  }}
}}

# IAM Role for Macie
resource "aws_iam_role" "macie" {{
  count = contains(var.security_features, "macie") ? 1 : 0
  name  = "{project_name}-macie-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "macie.amazonaws.com"
        }}
      }}
    ]
  }})
  
  tags = {{
    Name        = "{project_name}-macie-role"
    Environment = var.environment
  }}
}}
'''
        return terraform_iam
    
    def _generate_ec2_iam_policy(self, services: Dict[str, str], security_level: str) -> str:
        """Generate EC2 IAM policy with least privilege"""
        base_actions = [
            "ec2:DescribeInstances",
            "ec2:DescribeInstanceStatus",
            "ec2:DescribeTags"
        ]
        
        if security_level in ["medium", "high"]:
            base_actions.extend([
                "ssm:GetParameter",
                "ssm:GetParameters",
                "ssm:GetParametersByPath",
                "kms:Decrypt",
                "kms:DescribeKey"
            ])
        
        if "database" in services:
            base_actions.extend([
                "rds:DescribeDBInstances",
                "rds:DescribeDBClusters"
            ])
        
        if security_level == "high":
            base_actions.extend([
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams",
                "cloudwatch:PutMetricData",
                "ec2:CreateTags"
            ])
        
        return f'''
resource "aws_iam_role" "app" {{
  name = "${{var.project_name}}-app-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "ec2.amazonaws.com"
        }}
        Condition = {{
          StringEquals = {{
            "aws:RequestedRegion" = "${{data.aws_region.current.name}}"
          }}
        }}
      }}
    ]
  }})
  
  tags = {{
    Name        = "${{var.project_name}}-app-role"
    Environment = var.environment
  }}
}}

resource "aws_iam_instance_profile" "app" {{
  name = "${{var.project_name}}-app-profile"
  role = aws_iam_role.app.name
}}

resource "aws_iam_role_policy" "app" {{
  name = "${{var.project_name}}-app-policy"
  role = aws_iam_role.app.id
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Effect = "Allow"
        Action = {json.dumps(base_actions)}
        Resource = "*"
        Condition = {{
          StringEquals = {{
            "aws:RequestedRegion" = "${{data.aws_region.current.name}}"
          }}
        }}
      }},
      {{
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = [
          "${{aws_s3_bucket.main.arn}}",
          "${{aws_s3_bucket.main.arn}}/*"
        ]
        Condition = {{
          StringEquals = {{
            "s3:x-amz-server-side-encryption" = "AES256"
          }}
        }}
      }}
    ]
  }})
}}

# Session Manager access policy (for secure shell access)
resource "aws_iam_role_policy_attachment" "app_ssm" {{
  role       = aws_iam_role.app.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}}

# CloudWatch Agent policy
resource "aws_iam_role_policy_attachment" "app_cloudwatch" {{
  count      = var.security_level == "high" ? 1 : 0
  role       = aws_iam_role.app.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}}
'''
    
    def _generate_lambda_iam_policy(self, services: Dict[str, str], security_level: str) -> str:
        """Generate Lambda IAM policy with least privilege"""
        return f'''
resource "aws_iam_role" "lambda" {{
  name = "${{var.project_name}}-lambda-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "lambda.amazonaws.com"
        }}
        Condition = {{
          StringEquals = {{
            "aws:RequestedRegion" = "${{data.aws_region.current.name}}"
          }}
        }}
      }}
    ]
  }})
  
  tags = {{
    Name        = "${{var.project_name}}-lambda-role"
    Environment = var.environment
  }}
}}

resource "aws_iam_role_policy" "lambda" {{
  name = "${{var.project_name}}-lambda-policy"
  role = aws_iam_role.lambda.id
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${{data.aws_region.current.name}}:${{data.aws_caller_identity.current.account_id}}:log-group:/aws/lambda/${{var.project_name}}-*"
      }},
      {{
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = aws_kms_key.main.arn
        Condition = {{
          StringEquals = {{
            "kms:ViaService" = "s3.${{data.aws_region.current.name}}.amazonaws.com"
          }}
        }}
      }}
    ]
  }})
}}

# VPC access for Lambda (if needed)
resource "aws_iam_role_policy_attachment" "lambda_vpc" {{
  count      = var.lambda_in_vpc ? 1 : 0
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}}
'''
    
    def _generate_ecs_iam_policy(self, services: Dict[str, str], security_level: str) -> str:
        """Generate ECS IAM policies with least privilege"""
        return f'''
# ECS Execution Role
resource "aws_iam_role" "ecs_execution" {{
  name = "${{var.project_name}}-ecs-execution-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "ecs-tasks.amazonaws.com"
        }}
      }}
    ]
  }})
  
  tags = {{
    Name        = "${{var.project_name}}-ecs-execution-role"
    Environment = var.environment
  }}
}}

# ECS Task Role
resource "aws_iam_role" "ecs_task" {{
  name = "${{var.project_name}}-ecs-task-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "ecs-tasks.amazonaws.com"
        }}
      }}
    ]
  }})
  
  tags = {{
    Name        = "${{var.project_name}}-ecs-task-role"
    Environment = var.environment
  }}
}}

# Enhanced ECS Execution Policy
resource "aws_iam_role_policy" "ecs_execution" {{
  name = "${{var.project_name}}-ecs-execution-policy"
  role = aws_iam_role.ecs_execution.id
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      }},
      {{
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${{data.aws_region.current.name}}:${{data.aws_caller_identity.current.account_id}}:log-group:/ecs/${{var.project_name}}"
      }},
      {{
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.db_password.arn
        ]
      }}
    ]
  }})
}}

# ECS Task Policy
resource "aws_iam_role_policy" "ecs_task" {{
  name = "${{var.project_name}}-ecs-task-policy"
  role = aws_iam_role.ecs_task.id
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = [
          "${{aws_s3_bucket.main.arn}}",
          "${{aws_s3_bucket.main.arn}}/*"
        ]
      }}
    ]
  }})
}}
'''
    
    def _generate_cross_account_policy(self, security_level: str) -> str:
        """Generate cross-account access policy for high security environments"""
        if security_level != "high":
            return ""
        
        return f'''
# Cross-Account Access Role (for high security environments)
resource "aws_iam_role" "cross_account" {{
  count = var.enable_cross_account_access ? 1 : 0
  name  = "${{var.project_name}}-cross-account-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          AWS = var.trusted_account_ids
        }}
        Condition = {{
          StringEquals = {{
            "sts:ExternalId" = var.external_id
          }}
          Bool = {{
            "aws:MultiFactorAuthPresent" = "true"
          }}
        }}
      }}
    ]
  }})
  
  tags = {{
    Name        = "${{var.project_name}}-cross-account-role"
    Environment = var.environment
  }}
}}

resource "aws_iam_role_policy" "cross_account" {{
  count = var.enable_cross_account_access ? 1 : 0
  name  = "${{var.project_name}}-cross-account-policy"
  role  = aws_iam_role.cross_account[0].id
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetObject"
        ]
        Resource = [
          "${{aws_s3_bucket.main.arn}}",
          "${{aws_s3_bucket.main.arn}}/*"
        ]
      }}
    ]
  }})
}}
'''
    
    def _generate_security_audit_policy(self) -> str:
        """Generate security audit role with read-only permissions"""
        return f'''
# Security Audit Role (Read-only access for security assessments)
resource "aws_iam_role" "security_audit" {{
  name = "${{var.project_name}}-security-audit-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          AWS = var.security_audit_principals
        }}
        Condition = {{
          Bool = {{
            "aws:MultiFactorAuthPresent" = "true"
          }}
          StringEquals = {{
            "sts:ExternalId" = var.security_audit_external_id
          }}
        }}
      }}
    ]
  }})
  
  tags = {{
    Name        = "${{var.project_name}}-security-audit-role"
    Environment = var.environment
  }}
}}

resource "aws_iam_role_policy_attachment" "security_audit_readonly" {{
  role       = aws_iam_role.security_audit.name
  policy_arn = "arn:aws:iam::aws:policy/SecurityAudit"
}}

resource "aws_iam_role_policy_attachment" "security_audit_access_analyzer" {{
  role       = aws_iam_role.security_audit.name
  policy_arn = "arn:aws:iam::aws:policy/AccessAnalyzerReadOnlyAccess"
}}
'''
    
    def _generate_backup_iam_policy(self, services: Dict[str, str]) -> str:
        """Generate IAM policy for AWS Backup service"""
        return f'''
# AWS Backup Service Role
resource "aws_iam_role" "backup" {{
  count = contains(var.security_features, "backup") ? 1 : 0
  name  = "${{var.project_name}}-backup-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "backup.amazonaws.com"
        }}
      }}
    ]
  }})
  
  tags = {{
    Name        = "${{var.project_name}}-backup-role"
    Environment = var.environment
  }}
}}

resource "aws_iam_role_policy_attachment" "backup" {{
  count      = contains(var.security_features, "backup") ? 1 : 0
  role       = aws_iam_role.backup[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"
}}

resource "aws_iam_role_policy_attachment" "backup_restore" {{
  count      = contains(var.security_features, "backup") ? 1 : 0
  role       = aws_iam_role.backup[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores"
}}
'''
    
    def _generate_monitoring_iam_policy(self) -> str:
        """Generate IAM policy for monitoring and logging services"""
        return f'''
# CloudWatch and Monitoring Role
resource "aws_iam_role" "monitoring" {{
  count = contains(var.security_features, "monitoring") ? 1 : 0
  name  = "${{var.project_name}}-monitoring-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = [
            "events.amazonaws.com",
            "monitoring.amazonaws.com"
          ]
        }}
      }}
    ]
  }})
  
  tags = {{
    Name        = "${{var.project_name}}-monitoring-role"
    Environment = var.environment
  }}
}}

resource "aws_iam_role_policy" "monitoring" {{
  count = contains(var.security_features, "monitoring") ? 1 : 0
  name  = "${{var.project_name}}-monitoring-policy"
  role  = aws_iam_role.monitoring[0].id
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:${{data.aws_region.current.name}}:${{data.aws_caller_identity.current.account_id}}:*"
      }},
      {{
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics"
        ]
        Resource = "*"
      }}
    ]
  }})
}}
'''
    
    def generate_enhanced_security_groups(self, project_name: str, services: Dict[str, str], security_level: str) -> str:
        """Generate enhanced security groups with least privilege access"""
        
        # Determine which ports are needed based on services
        ports_needed = []
        if 'web_server' in services or 'load_balancer' in services:
            ports_needed.extend([80, 443])
        if 'database' in services:
            ports_needed.extend([3306, 5432])  # MySQL, PostgreSQL
        if 'redis' in services:
            ports_needed.append(6379)
        if 'ssh_access' in services:
            ports_needed.append(22)
        
        terraform_sg = f'''
# Enhanced Security Groups with Least Privilege Access
# Generated for security level: {security_level}

# Web tier security group
resource "aws_security_group" "web_tier" {{
  name_prefix = "{project_name}-web-"
  description = "Security group for web tier with enhanced controls"
  vpc_id      = data.aws_vpc.main.id

  # HTTPS traffic
  ingress {{
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  # HTTP traffic (redirect to HTTPS)
  ingress {{
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  # Outbound traffic
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  tags = {{
    Name        = "{project_name}-web-sg"
    Environment = var.environment
    Tier        = "web"
  }}
}}

# Application tier security group
resource "aws_security_group" "app_tier" {{
  name_prefix = "{project_name}-app-"
  description = "Security group for application tier"
  vpc_id      = data.aws_vpc.main.id

  # Allow traffic from web tier
  ingress {{
    description     = "App traffic from web tier"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.web_tier.id]
  }}

  # Allow traffic from ALB (using VPC CIDR to avoid circular dependency)
  ingress {{
    description = "App traffic from ALB"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.main.cidr_block]
  }}

  # Outbound traffic
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  tags = {{
    Name        = "{project_name}-app-sg"
    Environment = var.environment
    Tier        = "application"
  }}
}}

# Database tier security group
resource "aws_security_group" "db_tier" {{
  name_prefix = "{project_name}-db-"
  description = "Security group for database tier"
  vpc_id      = data.aws_vpc.main.id

  # MySQL/Aurora
  ingress {{
    description     = "MySQL/Aurora"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.app_tier.id]
  }}

  # PostgreSQL
  ingress {{
    description     = "PostgreSQL"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app_tier.id]
  }}

  # Redis
  ingress {{
    description     = "Redis"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.app_tier.id]
  }}

  # No outbound rules - databases shouldn't initiate connections
  tags = {{
    Name        = "{project_name}-db-sg"
    Environment = var.environment
    Tier        = "database"
  }}
}}

# ALB security group
resource "aws_security_group" "alb" {{
  name_prefix = "{project_name}-alb-"
  description = "Security group for Application Load Balancer"
  vpc_id      = data.aws_vpc.main.id

  # HTTPS traffic
  ingress {{
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  # HTTP traffic
  ingress {{
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  # Outbound traffic
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  tags = {{
    Name        = "{project_name}-alb-sg"
    Environment = var.environment
    Type        = "load-balancer"
  }}
}}


# Lambda security group (if using VPC Lambda)
resource "aws_security_group" "lambda" {{
  count       = length(keys(var.services)) > 0 && contains(keys(var.services), "lambda") ? 1 : 0
  name_prefix = "{project_name}-lambda-"
  description = "Security group for Lambda functions"
  vpc_id      = data.aws_vpc.main.id

  # Outbound traffic for Lambda
  egress {{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS outbound"
  }}

  egress {{
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.db_tier.id]
    description     = "MySQL access"
  }}

  egress {{
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.db_tier.id]
    description     = "PostgreSQL access"
  }}

  tags = {{
    Name        = "{project_name}-lambda-sg"
    Environment = var.environment
    Type        = "lambda"
  }}
}}

# Bastion host security group (for secure access)
resource "aws_security_group" "bastion" {{
  count       = try(var.enable_bastion, false) ? 1 : 0
  name_prefix = "{project_name}-bastion-"
  description = "Security group for bastion host"
  vpc_id      = data.aws_vpc.main.id

  # SSH access from specific IP ranges
  ingress {{
    description = "SSH from office"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = try(var.allowed_ssh_cidrs, ["10.0.0.0/8"])
  }}

  # Outbound SSH to private subnets
  egress {{
    description = "SSH to private instances"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [for subnet in data.aws_subnet.default : subnet.cidr_block]
  }}

  tags = {{
    Name        = "{project_name}-bastion-sg"
    Environment = var.environment
    Type        = "bastion"
  }}
}}
'''
        
        return terraform_sg
    
    def generate_network_acls(self, project_name: str, security_level: str) -> str:
        """Generate Network ACLs for additional layer of security"""
        
        terraform_nacls = f'''
# Network ACLs - Using Default VPC's Existing Network ACLs
# Default VPC already has a default network ACL that allows all traffic
# For production use, consider adding custom network ACL rules
# Security Level: {security_level}

# Note: Default VPC subnets already have network ACL associations
# Custom network ACLs are disabled to avoid conflicts with existing associations
'''
        
        return terraform_nacls
    
    def generate_enhanced_waf_configuration(self, project_name: str, security_level: str) -> str:
        """Generate enhanced WAF configuration with comprehensive protection rules"""
        
        terraform_waf = f'''
# Enhanced AWS WAF Configuration
# Security Level: {security_level}

# WAF Web ACL for comprehensive web application protection
resource "aws_wafv2_web_acl" "main" {{
  name        = "{project_name}-waf"
  description = "Enhanced WAF protection for {project_name}"
  scope       = "REGIONAL"
  
  default_action {{
    allow {{}}
  }}
  
  # AWS Managed Rules - Core Rule Set (OWASP Top 10)
  rule {{
    name     = "AWSManagedRulesCore"
    priority = 1
    
    override_action {{
      none {{}}
    }}
    
    statement {{
      managed_rule_group_statement {{
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
        
        # Exclude rules that might cause false positives
        excluded_rule {{
          name = "SizeRestrictions_BODY"
        }}
        
        excluded_rule {{
          name = "GenericRFI_BODY"
        }}
      }}
    }}
    
    visibility_config {{
      cloudwatch_metrics_enabled = true
      metric_name                = "{project_name}-waf-core-rules"
      sampled_requests_enabled   = true
    }}
  }}
  
  # AWS Managed Rules - Known Bad Inputs
  rule {{
    name     = "AWSManagedRulesKnownBadInputs"
    priority = 2
    
    override_action {{
      none {{}}
    }}
    
    statement {{
      managed_rule_group_statement {{
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }}
    }}
    
    visibility_config {{
      cloudwatch_metrics_enabled = true
      metric_name                = "{project_name}-waf-bad-inputs"
      sampled_requests_enabled   = true
    }}
  }}
  
  # AWS Managed Rules - SQL Database Protection
  rule {{
    name     = "AWSManagedRulesSQLi"
    priority = 3
    
    override_action {{
      none {{}}
    }}
    
    statement {{
      managed_rule_group_statement {{
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }}
    }}
    
    visibility_config {{
      cloudwatch_metrics_enabled = true
      metric_name                = "{project_name}-waf-sqli"
      sampled_requests_enabled   = true
    }}
  }}
  
  # AWS Managed Rules - Linux Operating System Protection
  rule {{
    name     = "AWSManagedRulesLinux"
    priority = 4
    
    override_action {{
      none {{}}
    }}
    
    statement {{
      managed_rule_group_statement {{
        name        = "AWSManagedRulesLinuxRuleSet"
        vendor_name = "AWS"
      }}
    }}
    
    visibility_config {{
      cloudwatch_metrics_enabled = true
      metric_name                = "{project_name}-waf-linux"
      sampled_requests_enabled   = true
    }}
  }}
  
  # AWS Managed Rules - Windows Operating System Protection
  rule {{
    name     = "AWSManagedRulesWindows"
    priority = 5
    
    override_action {{
      none {{}}
    }}
    
    statement {{
      managed_rule_group_statement {{
        name        = "AWSManagedRulesWindowsRuleSet"
        vendor_name = "AWS"
      }}
    }}
    
    visibility_config {{
      cloudwatch_metrics_enabled = true
      metric_name                = "{project_name}-waf-windows"
      sampled_requests_enabled   = true
    }}
  }}
  
  # Rate Limiting Rule
  rule {{
    name     = "RateLimitRule"
    priority = 6
    
    action {{
      block {{}}
    }}
    
    statement {{
      rate_based_statement {{
        limit              = 2000
        aggregate_key_type = "IP"
        
        scope_down_statement {{
          geo_match_statement {{
            country_codes = ["US", "CA", "GB", "DE", "FR", "AU", "JP"]
          }}
        }}
      }}
    }}
    
    visibility_config {{
      cloudwatch_metrics_enabled = true
      metric_name                = "{project_name}-waf-rate-limit"
      sampled_requests_enabled   = true
    }}
  }}
  
  # Geographic Blocking Rule (block high-risk countries)
  rule {{
    name     = "GeoBlockRule"
    priority = 7
    
    action {{
      block {{}}
    }}
    
    statement {{
      geo_match_statement {{
        country_codes = ["CN", "RU", "KP", "IR"]  # Customize based on your needs
      }}
    }}
    
    visibility_config {{
      cloudwatch_metrics_enabled = true
      metric_name                = "{project_name}-waf-geo-block"
      sampled_requests_enabled   = true
    }}
  }}
  
  # IP Reputation Rule
  rule {{
    name     = "IPReputationRule"
    priority = 8
    
    override_action {{
      none {{}}
    }}
    
    statement {{
      managed_rule_group_statement {{
        name        = "AWSManagedRulesAmazonIpReputationList"
        vendor_name = "AWS"
      }}
    }}
    
    visibility_config {{
      cloudwatch_metrics_enabled = true
      metric_name                = "{project_name}-waf-ip-reputation"
      sampled_requests_enabled   = true
    }}
  }}
  
  # Bot Control Rule (if security level is high)
  dynamic "rule" {{
    for_each = var.security_level == "high" ? [1] : []
    content {{
      name     = "BotControlRule"
      priority = 9
      
      override_action {{
        none {{}}
      }}
      
      statement {{
        managed_rule_group_statement {{
          name        = "AWSManagedRulesBotControlRuleSet"
          vendor_name = "AWS"
        }}
      }}
      
      visibility_config {{
        cloudwatch_metrics_enabled = true
        metric_name                = "{project_name}-waf-bot-control"
        sampled_requests_enabled   = true
      }}
    }}
  }}
  
  tags = {{
    Name        = "{project_name}-waf"
    Environment = var.environment
    Purpose     = "web-application-firewall"
  }}
  
  visibility_config {{
    cloudwatch_metrics_enabled = true
    metric_name                = "{project_name}-waf"
    sampled_requests_enabled   = true
  }}
}}

# WAF Logging Configuration
resource "aws_wafv2_web_acl_logging_configuration" "main" {{
  resource_arn            = aws_wafv2_web_acl.main.arn
  log_destination_configs = [aws_cloudwatch_log_group.waf_logs.arn]
  
  redacted_fields {{
    single_header {{
      name = "authorization"
    }}
  }}
  
  redacted_fields {{
    single_header {{
      name = "cookie"
    }}
  }}
  
  depends_on = [aws_cloudwatch_log_group.waf_logs]
}}

# CloudWatch Log Group for WAF Logs
resource "aws_cloudwatch_log_group" "waf_logs" {{
  name              = "/aws/wafv2/{project_name}"
  retention_in_days = 30
  
  tags = {{
    Name        = "{project_name}-waf-logs"
    Environment = var.environment
  }}
}}

# WAF IP Set for Allowed IPs (can be customized)
resource "aws_wafv2_ip_set" "allowed_ips" {{
  name               = "{project_name}-allowed-ips"
  description        = "Allowed IP addresses for {project_name}"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"
  
  addresses = var.allowed_ip_addresses
  
  tags = {{
    Name        = "{project_name}-allowed-ips"
    Environment = var.environment
  }}
}}

# WAF IP Set for Blocked IPs
resource "aws_wafv2_ip_set" "blocked_ips" {{
  name               = "{project_name}-blocked-ips"
  description        = "Blocked IP addresses for {project_name}"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"
  
  addresses = var.blocked_ip_addresses
  
  tags = {{
    Name        = "{project_name}-blocked-ips"
    Environment = var.environment
  }}
}}

# CloudWatch Dashboard for WAF Metrics
resource "aws_cloudwatch_dashboard" "waf_dashboard" {{
  dashboard_name = "{project_name}-waf-dashboard"
  
  dashboard_body = jsonencode({{
    widgets = [
      {{
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        
        properties = {{
          metrics = [
            ["AWS/WAFV2", "AllowedRequests", "WebACL", "{project_name}-waf", "Region", "us-east-1", "Rule", "ALL"],
            [".", "BlockedRequests", ".", ".", ".", ".", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = "us-east-1"
          title   = "WAF Requests Overview"
          period  = 300
        }}
      }},
      {{
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        
        properties = {{
          metrics = [
            ["AWS/WAFV2", "BlockedRequests", "WebACL", "{project_name}-waf", "Region", "us-east-1", "Rule", "RateLimitRule"],
            [".", ".", ".", ".", ".", ".", ".", "GeoBlockRule"],
            [".", ".", ".", ".", ".", ".", ".", "IPReputationRule"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = "us-east-1"
          title   = "WAF Rule Blocks"
          period  = 300
        }}
      }}
    ]
  }})
}}
'''
        
        return terraform_waf
    
    def generate_enhanced_security_services(self, project_name: str, security_level: str) -> str:
        """Generate enhanced AWS security services configuration"""
        
        terraform_security = f'''
# Enhanced AWS Security Services Configuration
# Security Level: {security_level}

# AWS Config for Configuration Management
resource "aws_config_configuration_recorder" "main" {{
  count    = contains(var.security_features, "config") ? 1 : 0
  name     = "{project_name}-config-recorder"
  role_arn = aws_iam_role.config[0].arn
  depends_on = [aws_iam_role_policy_attachment.config]
  
  recording_group {{
    all_supported = true
    include_global_resource_types = true
    
    exclusion_by_resource_types {{
      resource_types = ["AWS::Config::ResourceCompliance"]
    }}
  }}
}}

resource "aws_config_delivery_channel" "main" {{
  count           = contains(var.security_features, "config") ? 1 : 0
  name            = "{project_name}-config-delivery"
  s3_bucket_name  = aws_s3_bucket.config_logs[0].bucket
  depends_on      = [aws_s3_bucket_policy.config_logs]
}}

# GuardDuty for Threat Detection
resource "aws_guardduty_detector" "main" {{
  count  = contains(var.security_features, "guard_duty") ? 1 : 0
  enable = true
  
  datasources {{
    s3_logs {{
      enable = true
    }}
    kubernetes {{
      audit_logs {{
        enable = true
      }}
    }}
    malware_protection {{
      scan_ec2_instance_with_findings {{
        ebs_volumes {{
          enable = true
        }}
      }}
    }}
  }}
  
  tags = {{
    Name        = "{project_name}-guardduty"
    Environment = var.environment
  }}
}}

# Security Hub for Centralized Security Management
resource "aws_securityhub_account" "main" {{
  count                    = contains(var.security_features, "security_hub") ? 1 : 0
  enable_default_standards = true
}}

# Enable AWS Foundational Security Standard
resource "aws_securityhub_standards_subscription" "aws_foundational" {{
  count         = contains(var.security_features, "security_hub") ? 1 : 0
  standards_arn = "arn:aws:securityhub:::ruleset/finding-format/aws-foundational-security-standard/v/1.0.0"
  depends_on    = [aws_securityhub_account.main]
}}

# Enable CIS AWS Foundations Benchmark
resource "aws_securityhub_standards_subscription" "cis" {{
  count         = contains(var.security_features, "security_hub") ? 1 : 0
  standards_arn = "arn:aws:securityhub:::ruleset/finding-format/cis-aws-foundations-benchmark/v/1.2.0"
  depends_on    = [aws_securityhub_account.main]
}}

# Inspector for Vulnerability Assessment
resource "aws_inspector2_enabler" "main" {{
  count           = contains(var.security_features, "inspector") ? 1 : 0
  account_ids     = [data.aws_caller_identity.current.account_id]
  resource_types  = ["ECR", "EC2"]
}}

# Macie for Data Classification and Protection
resource "aws_macie2_account" "main" {{
  count  = contains(var.security_features, "macie") ? 1 : 0
  status = "ENABLED"
}}

resource "aws_macie2_classification_job" "s3_classification" {{
  count        = contains(var.security_features, "macie") ? 1 : 0
  job_type     = "ONE_TIME"
  name         = "{project_name}-s3-classification"
  description  = "Classify sensitive data in S3 buckets"
  
  s3_job_definition {{
    bucket_definitions {{
      account_id = data.aws_caller_identity.current.account_id
      buckets    = [aws_s3_bucket.main.bucket]
    }}
  }}
  
  depends_on = [aws_macie2_account.main]
}}

# AWS CloudTrail for API Logging
resource "aws_cloudtrail" "main" {{
  count                         = contains(var.security_features, "logging") ? 1 : 0
  name                         = "{project_name}-trail"
  s3_bucket_name              = aws_s3_bucket.logs.bucket
  include_global_service_events = true
  is_multi_region_trail       = true
  enable_logging              = true
  
  insight_selector {{
    insight_type = "ApiCallRateInsight"
  }}
  
  event_selector {{
    read_write_type           = "All"
    include_management_events = true
    
    data_resource {{
      type   = "AWS::S3::Object"
      values = ["${{aws_s3_bucket.main.arn}}/*"]
    }}
  }}
  
  tags = {{
    Name        = "{project_name}-trail"
    Environment = var.environment
  }}
  
  depends_on = [aws_s3_bucket_policy.cloudtrail_logs]
}}

# VPC Flow Logs for Network Monitoring
resource "aws_flow_log" "vpc" {{
  count           = contains(var.security_features, "logging") ? 1 : 0
  iam_role_arn   = aws_iam_role.flow_log[0].arn
  log_destination = aws_cloudwatch_log_group.vpc_flow_logs[0].arn
  traffic_type   = "ALL"
  vpc_id         = data.aws_vpc.main.id
  
  tags = {{
    Name        = "{project_name}-vpc-flow-logs"
    Environment = var.environment
  }}
}}

resource "aws_cloudwatch_log_group" "vpc_flow_logs" {{
  count             = contains(var.security_features, "logging") ? 1 : 0
  name              = "/aws/vpc/flowlogs"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.main.arn
  
  tags = {{
    Name        = "{project_name}-vpc-flow-logs"
    Environment = var.environment
  }}
}}

resource "aws_iam_role" "flow_log" {{
  count = contains(var.security_features, "logging") ? 1 : 0
  name  = "{project_name}-flow-log-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "vpc-flow-logs.amazonaws.com"
        }}
      }}
    ]
  }})
}}

resource "aws_iam_role_policy" "flow_log" {{
  count = contains(var.security_features, "logging") ? 1 : 0
  name  = "{project_name}-flow-log-policy"
  role  = aws_iam_role.flow_log[0].id
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Effect   = "Allow"
        Resource = "*"
      }}
    ]
  }})
}}

# AWS WAF v2 for Web Application Protection
resource "aws_wafv2_web_acl" "main" {{
  count       = contains(var.security_features, "waf") ? 1 : 0
  name        = "{project_name}-waf"
  description = "Web ACL for {project_name}"
  scope       = "REGIONAL"
  
  default_action {{
    allow {{}}
  }}
  
  # AWS Managed Rules - Core Rule Set
  rule {{
    name     = "AWSManagedRulesCore"
    priority = 1
    
    override_action {{
      none {{}}
    }}
    
    statement {{
      managed_rule_group_statement {{
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }}
    }}
    
    visibility_config {{
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCoreMetric"
      sampled_requests_enabled   = true
    }}
  }}
  
  # AWS Managed Rules - Known Bad Inputs
  rule {{
    name     = "AWSManagedRulesKnownBadInputs"
    priority = 2
    
    override_action {{
      none {{}}
    }}
    
    statement {{
      managed_rule_group_statement {{
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }}
    }}
    
    visibility_config {{
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesKnownBadInputsMetric"
      sampled_requests_enabled   = true
    }}
  }}
  
  # Rate limiting rule
  rule {{
    name     = "RateLimitRule"
    priority = 3
    
    action {{
      block {{}}
    }}
    
    statement {{
      rate_based_statement {{
        limit              = 2000
        aggregate_key_type = "IP"
      }}
    }}
    
    visibility_config {{
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRuleMetric"
      sampled_requests_enabled   = true
    }}
  }}
  
  tags = {{
    Name        = "{project_name}-waf"
    Environment = var.environment
  }}
  
  visibility_config {{
    cloudwatch_metrics_enabled = true
    metric_name                = "{project_name}WAF"
    sampled_requests_enabled   = true
  }}
}}

# Associate WAF with ALB
resource "aws_wafv2_web_acl_association" "main" {{
  count        = contains(var.security_features, "waf") ? 1 : 0
  resource_arn = aws_lb.main.arn
  web_acl_arn  = aws_wafv2_web_acl.main[0].arn
}}
'''
        return terraform_security
    
    def generate_enhanced_encryption(self, project_name: str, security_level: str, compliance_requirements: List[str]) -> str:
        """Generate comprehensive encryption configuration"""
        
        # Determine if FIPS 140-2 Level 3 is required for compliance
        fips_required = any(req.lower() in ['fedramp', 'dod'] for req in compliance_requirements)
        
        terraform_encryption = f'''
# Enhanced Encryption Configuration
# Security Level: {security_level}
# Compliance Requirements: {', '.join(compliance_requirements)}

# Customer Managed KMS Key with Advanced Configuration
resource "aws_kms_key" "main" {{
  description              = "Customer managed key for {project_name}"
  key_usage               = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  key_rotation_enabled    = true
  deletion_window_in_days = 30
  
  {"multi_region = true" if security_level == "high" else ""}
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {{
          AWS = "arn:aws:iam::${{data.aws_caller_identity.current.account_id}}:root"
        }}
        Action   = "kms:*"
        Resource = "*"
      }},
      {{
        Sid    = "Allow CloudTrail to encrypt logs"
        Effect = "Allow"
        Principal = {{
          Service = "cloudtrail.amazonaws.com"
        }}
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {{
          StringEquals = {{
            "kms:EncryptionContext:aws:cloudtrail:arn" = "arn:aws:cloudtrail:${{data.aws_region.current.name}}:${{data.aws_caller_identity.current.account_id}}:trail/{project_name}-trail"
          }}
        }}
      }},
      {{
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {{
          Service = "logs.${{data.aws_region.current.name}}.amazonaws.com"
        }}
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {{
          ArnEquals = {{
            "kms:EncryptionContext:aws:logs:arn" = "arn:aws:logs:${{data.aws_region.current.name}}:${{data.aws_caller_identity.current.account_id}}:*"
          }}
        }}
      }}
    ]
  }})
  
  tags = {{
    Name        = "{project_name}-kms-key"
    Environment = var.environment
    Purpose     = "General encryption"
  }}
}}

resource "aws_kms_alias" "main" {{
  name          = "alias/{project_name}-key"
  target_key_id = aws_kms_key.main.key_id
}}

# Separate KMS Key for Database Encryption (high security)
resource "aws_kms_key" "database" {{
  count                   = var.security_level == "high" ? 1 : 0
  description             = "Database encryption key for {project_name}"
  key_usage              = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  key_rotation_enabled   = true
  deletion_window_in_days = 30
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {{
          AWS = "arn:aws:iam::${{data.aws_caller_identity.current.account_id}}:root"
        }}
        Action   = "kms:*"
        Resource = "*"
      }},
      {{
        Sid    = "Allow RDS Service"
        Effect = "Allow"
        Principal = {{
          Service = "rds.amazonaws.com"
        }}
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }}
    ]
  }})
  
  tags = {{
    Name        = "{project_name}-database-kms-key"
    Environment = var.environment
    Purpose     = "Database encryption"
  }}
}}

resource "aws_kms_alias" "database" {{
  count         = var.security_level == "high" ? 1 : 0
  name          = "alias/{project_name}-database-key"
  target_key_id = aws_kms_key.database[0].key_id
}}

# KMS Key for Secrets Manager
resource "aws_kms_key" "secrets" {{
  count                   = contains(var.security_features, "secrets") ? 1 : 0
  description             = "Secrets Manager encryption key for {project_name}"
  key_usage              = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  key_rotation_enabled   = true
  deletion_window_in_days = 10
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {{
          AWS = "arn:aws:iam::${{data.aws_caller_identity.current.account_id}}:root"
        }}
        Action   = "kms:*"
        Resource = "*"
      }},
      {{
        Sid    = "Allow Secrets Manager"
        Effect = "Allow"
        Principal = {{
          Service = "secretsmanager.amazonaws.com"
        }}
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }}
    ]
  }})
  
  tags = {{
    Name        = "{project_name}-secrets-kms-key"
    Environment = var.environment
    Purpose     = "Secrets encryption"
  }}
}}

resource "aws_kms_alias" "secrets" {{
  count         = contains(var.security_features, "secrets") ? 1 : 0
  name          = "alias/{project_name}-secrets-key"
  target_key_id = aws_kms_key.secrets[0].key_id
}}

# CloudHSM Cluster for FIPS 140-2 Level 3 Compliance (if required)
{"" if not fips_required else f"""
resource "aws_cloudhsm_v2_cluster" "main" {{
  hsm_type   = "hsm1.medium"
  subnet_ids = length(data.aws_subnet.default) > 1 ? [data.aws_subnet.default[0].id, data.aws_subnet.default[1].id] : [data.aws_subnet.default[0].id]
  
  tags = {{
    Name        = "{project_name}-cloudhsm"
    Environment = var.environment
    Compliance  = "FIPS-140-2-Level-3"
  }}
}}

resource "aws_cloudhsm_v2_hsm" "main" {{
  count      = 2
  cluster_id = aws_cloudhsm_v2_cluster.main.cluster_id
  subnet_id  = data.aws_subnet.default[count.index].id
  
  tags = {{
    Name        = "{project_name}-hsm-${{count.index + 1}}"
    Environment = var.environment
  }}
}}
"""}

# Certificate Manager for TLS/SSL
resource "aws_acm_certificate" "main" {{
  domain_name       = var.domain_name
  validation_method = "DNS"
  
  subject_alternative_names = [
    "*.{project_name}.com"
  ]
  
  key_algorithm = "RSA_2048"
  
  lifecycle {{
    create_before_destroy = true
  }}
  
  tags = {{
    Name        = "{project_name}-cert"
    Environment = var.environment
  }}
}}

# Certificate validation
resource "aws_acm_certificate_validation" "main" {{
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
  
  timeouts {{
    create = "5m"
  }}
}}
'''
        return terraform_encryption
    
    def generate_compliance_controls(self, project_name: str, compliance_requirements: List[str]) -> str:
        """Generate compliance-specific controls"""
        
        controls = []
        
        for framework in compliance_requirements:
            if framework.lower() == 'hipaa':
                controls.append(self._generate_hipaa_controls(project_name))
            elif framework.lower() == 'pci-dss':
                controls.append(self._generate_pci_controls(project_name))
            elif framework.lower() == 'sox':
                controls.append(self._generate_sox_controls(project_name))
            elif framework.lower() == 'gdpr':
                controls.append(self._generate_gdpr_controls(project_name))
            elif framework.lower() == 'fedramp':
                controls.append(self._generate_fedramp_controls(project_name))
        
        return '\n'.join(controls)
    
    def _generate_hipaa_controls(self, project_name: str) -> str:
        """Generate HIPAA compliance controls"""
        return f'''
# HIPAA Compliance Controls
# Reference: HIPAA Security Rule (45 CFR Part 164)

# Access Control (§164.312(a)(1))
resource "aws_iam_policy" "hipaa_access_control" {{
  name        = "{project_name}-hipaa-access-control"
  description = "HIPAA compliant access control policy"
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Effect = "Deny"
        Action = "*"
        Resource = "*"
        Condition = {{
          Bool = {{
            "aws:MultiFactorAuthPresent" = "false"
          }}
        }}
      }}
    ]
  }})
}}

# Audit Controls (§164.312(b))
resource "aws_cloudwatch_log_group" "hipaa_audit" {{
  name              = "/aws/hipaa/{project_name}/audit"
  retention_in_days = 2555  # 7 years retention for HIPAA
  kms_key_id        = aws_kms_key.main.arn
  
  tags = {{
    Name       = "{project_name}-hipaa-audit-logs"
    Compliance = "HIPAA"
    Purpose    = "Audit Trail"
  }}
}}

# Data Backup and Recovery (§164.308(a)(7)(ii)(A))
resource "aws_backup_vault" "hipaa" {{
  name        = "{project_name}-hipaa-backup"
  kms_key_arn = aws_kms_key.main.arn
  
  tags = {{
    Name       = "{project_name}-hipaa-backup"
    Compliance = "HIPAA"
  }}
}}

resource "aws_backup_plan" "hipaa" {{
  name = "{project_name}-hipaa-backup-plan"
  
  rule {{
    rule_name         = "hipaa_daily_backup"
    target_vault_name = aws_backup_vault.hipaa.name
    schedule          = "cron(0 5 ? * * *)"
    
    recovery_point_tags = {{
      Compliance = "HIPAA"
    }}
    
    lifecycle {{
      cold_storage_after = 30
      delete_after       = 2555  # 7 years
    }}
    
    copy_action {{
      destination_vault_arn = aws_backup_vault.hipaa.arn
      
      lifecycle {{
        cold_storage_after = 30
        delete_after       = 2555
      }}
    }}
  }}
}}
'''
    
    def _generate_pci_controls(self, project_name: str) -> str:
        """Generate PCI-DSS compliance controls"""
        return f'''
# PCI-DSS Compliance Controls
# Reference: PCI DSS v4.0

# Network Segmentation (Requirement 1)
resource "aws_security_group" "pci_cardholder_data" {{
  name_prefix = "{project_name}-pci-chd-"
  vpc_id      = data.aws_vpc.main.id
  description = "PCI-DSS cardholder data environment security group"
  
  # Restrict all traffic by default
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  tags = {{
    Name       = "{project_name}-pci-chd-sg"
    Compliance = "PCI-DSS"
    Purpose    = "Cardholder Data Environment"
  }}
}}

# Strong Cryptography (Requirement 3)
resource "aws_kms_key" "pci_encryption" {{
  description              = "PCI-DSS compliant encryption key"
  key_usage               = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  key_rotation_enabled    = true
  deletion_window_in_days = 30
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {{
          AWS = "arn:aws:iam::${{data.aws_caller_identity.current.account_id}}:root"
        }}
        Action   = "kms:*"
        Resource = "*"
      }}
    ]
  }})
  
  tags = {{
    Name       = "{project_name}-pci-encryption-key"
    Compliance = "PCI-DSS"
    Purpose    = "Cardholder Data Encryption"
  }}
}}

# Logging and Monitoring (Requirement 10)
resource "aws_cloudwatch_log_group" "pci_audit" {{
  name              = "/aws/pci/{project_name}/audit"
  retention_in_days = 365  # Minimum 1 year for PCI-DSS
  kms_key_id        = aws_kms_key.pci_encryption.arn
  
  tags = {{
    Name       = "{project_name}-pci-audit-logs"
    Compliance = "PCI-DSS"
    Purpose    = "Security Audit Trail"
  }}
}}

# Vulnerability Management (Requirement 11)
resource "aws_inspector2_enabler" "pci" {{
  account_ids    = [data.aws_caller_identity.current.account_id]
  resource_types = ["ECR", "EC2"]
}}
'''
    
    def _generate_sox_controls(self, project_name: str) -> str:
        """Generate SOX compliance controls"""
        return f'''
# SOX Compliance Controls
# Reference: Sarbanes-Oxley Act Section 404

# Change Management Controls
resource "aws_config_configuration_recorder" "sox" {{
  name     = "{project_name}-sox-config-recorder"
  role_arn = aws_iam_role.config[0].arn
  
  recording_group {{
    all_supported = true
    include_global_resource_types = true
  }}
}}

# Financial Data Protection
resource "aws_s3_bucket" "sox_financial_data" {{
  bucket = "{project_name}-sox-financial-data"
  
  tags = {{
    Name       = "{project_name}-sox-financial-data"
    Compliance = "SOX"
    DataType   = "Financial"
  }}
}}

resource "aws_s3_bucket_versioning" "sox_financial_data" {{
  bucket = aws_s3_bucket.sox_financial_data.id
  versioning_configuration {{
    status = "Enabled"
  }}
}}

resource "aws_s3_bucket_object_lock_configuration" "sox_financial_data" {{
  bucket = aws_s3_bucket.sox_financial_data.id
  
  rule {{
    default_retention {{
      mode = "GOVERNANCE"
      years = 7
    }}
  }}
}}

# Audit Trail Retention
resource "aws_cloudwatch_log_group" "sox_audit" {{
  name              = "/aws/sox/{project_name}/audit"
  retention_in_days = 2555  # 7 years retention
  kms_key_id        = aws_kms_key.main.arn
  
  tags = {{
    Name       = "{project_name}-sox-audit-logs"
    Compliance = "SOX"
    Purpose    = "Financial Audit Trail"
  }}
}}
'''
    
    def _generate_gdpr_controls(self, project_name: str) -> str:
        """Generate GDPR compliance controls"""
        return f'''
# GDPR Compliance Controls
# Reference: General Data Protection Regulation (EU) 2016/679

# Data Encryption (Article 32)
resource "aws_kms_key" "gdpr_personal_data" {{
  description              = "GDPR personal data encryption key"
  key_usage               = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  key_rotation_enabled    = true
  deletion_window_in_days = 30
  
  tags = {{
    Name       = "{project_name}-gdpr-encryption-key"
    Compliance = "GDPR"
    Purpose    = "Personal Data Protection"
  }}
}}

# Data Processing Records (Article 30)
resource "aws_cloudwatch_log_group" "gdpr_processing" {{
  name              = "/aws/gdpr/{project_name}/processing"
  retention_in_days = 2190  # 6 years retention
  kms_key_id        = aws_kms_key.gdpr_personal_data.arn
  
  tags = {{
    Name       = "{project_name}-gdpr-processing-logs"
    Compliance = "GDPR"
    Purpose    = "Data Processing Records"
  }}
}}

# Data Subject Rights (Articles 15-22)
resource "aws_lambda_function" "gdpr_data_subject_rights" {{
  filename         = "gdpr_handler.zip"
  function_name    = "{project_name}-gdpr-rights-handler"
  role            = aws_iam_role.lambda.arn
  handler         = "index.handler"
  runtime         = "python3.9"
  timeout         = 300
  
  environment {{
    variables = {{
      ENCRYPTION_KEY_ARN = aws_kms_key.gdpr_personal_data.arn
    }}
  }}
  
  tags = {{
    Name       = "{project_name}-gdpr-rights-handler"
    Compliance = "GDPR"
    Purpose    = "Data Subject Rights Management"
  }}
}}

# Data Breach Notification (Article 33)
resource "aws_sns_topic" "gdpr_breach_notification" {{
  name            = "{project_name}-gdpr-breach-alerts"
  kms_master_key_id = aws_kms_key.gdpr_personal_data.arn
  
  tags = {{
    Name       = "{project_name}-gdpr-breach-alerts"
    Compliance = "GDPR"
    Purpose    = "Breach Notification"
  }}
}}
'''
    
    def _generate_fedramp_controls(self, project_name: str) -> str:
        """Generate FedRAMP compliance controls"""
        return f'''
# FedRAMP Compliance Controls
# Reference: FedRAMP Security Controls Baseline

# FIPS 140-2 Encryption (SC-13)
resource "aws_cloudhsm_v2_cluster" "fedramp" {{
  hsm_type   = "hsm1.medium"
  subnet_ids = length(data.aws_subnet.default) > 1 ? [data.aws_subnet.default[0].id, data.aws_subnet.default[1].id] : [data.aws_subnet.default[0].id]
  
  tags = {{
    Name       = "{project_name}-fedramp-hsm"
    Compliance = "FedRAMP"
    Purpose    = "FIPS 140-2 Level 3"
  }}
}}

# Continuous Monitoring (CA-7)
resource "aws_config_configuration_recorder" "fedramp" {{
  name     = "{project_name}-fedramp-config"
  role_arn = aws_iam_role.config[0].arn
  
  recording_group {{
    all_supported = true
    include_global_resource_types = true
    
    recording_mode {{
      recording_frequency = "CONTINUOUS"
    }}
  }}
}}

# Incident Response (IR-4)
resource "aws_sns_topic" "fedramp_incident_response" {{
  name = "{project_name}-fedramp-incident-response"
  
  tags = {{
    Name       = "{project_name}-fedramp-incident-response"
    Compliance = "FedRAMP"
    Purpose    = "Incident Response"
  }}
}}

# Access Control (AC-2)
resource "aws_iam_policy" "fedramp_access_control" {{
  name        = "{project_name}-fedramp-access-control"
  description = "FedRAMP compliant access control policy"
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Effect = "Deny"
        Action = "*"
        Resource = "*"
        Condition = {{
          Bool = {{
            "aws:MultiFactorAuthPresent" = "false"
          }}
        }}
      }},
      {{
        Effect = "Deny"
        Action = "*"
        Resource = "*"
        Condition = {{
          DateGreaterThan = {{
            "aws:TokenIssueTime" = "${{timeadd(timestamp(), "4h")}}"
          }}
        }}
      }}
    ]
  }})
}}
'''
        
        controls = {
            "terraform": terraform_controls,
            "cloudformation": [
                "# CloudFormation compliance controls would be generated here"
            ]
        }

        return {"terraform": "\n".join(terraform_controls), "cloudformation": "\n".join(controls["cloudformation"]), "compliance_frameworks": compliance_frameworks}
    
    def generate_guardduty_configuration(self, project_name: str) -> str:
        """Generate GuardDuty threat detection configuration"""
        return f'''# Amazon GuardDuty - Threat Detection
resource "aws_guardduty_detector" "main" {{
  enable = true
  
  datasources {{
    s3_logs {{
      enable = true
    }}
    kubernetes {{
      audit_logs {{
        enable = true
      }}
    }}
    malware_protection {{
      scan_ec2_instance_with_findings {{
        ebs_volumes {{
          enable = true
        }}
      }}
    }}
  }}
  
  tags = {{
    Name = "${{var.project_name}}-guardduty"
  }}
}}

# GuardDuty S3 Protection
resource "aws_guardduty_s3_detector" "main" {{
  detector_id = aws_guardduty_detector.main.id
  enable      = true
}}'''
    
    def generate_security_hub_configuration(self, project_name: str) -> str:
        """Generate Security Hub configuration"""
        return f'''# AWS Security Hub - Central Security Dashboard
resource "aws_securityhub_account" "main" {{
  enable_default_standards = true
}}

# Security Standards Subscriptions
resource "aws_securityhub_standards_subscription" "aws_foundational" {{
  standards_arn = "arn:aws:securityhub:::ruleset/finding-format/aws-foundational-security-standard/v/1.0.0"
  depends_on    = [aws_securityhub_account.main]
}}

resource "aws_securityhub_standards_subscription" "cis" {{
  standards_arn = "arn:aws:securityhub:::ruleset/finding-format/cis-aws-foundations-benchmark/v/1.2.0"
  depends_on    = [aws_securityhub_account.main]
}}

resource "aws_securityhub_standards_subscription" "pci_dss" {{
  standards_arn = "arn:aws:securityhub:::ruleset/finding-format/pci-dss/v/3.2.1"
  depends_on    = [aws_securityhub_account.main]
}}'''
    
    def generate_config_configuration(self, project_name: str) -> str:
        """Generate AWS Config for compliance monitoring"""
        return f'''# AWS Config - Compliance Monitoring
resource "aws_config_configuration_recorder" "main" {{
  name     = "${{var.project_name}}-config-recorder"
  role_arn = aws_iam_role.config.arn
  
  recording_group {{
    all_supported                 = true
    include_global_resource_types = true
  }}
}}

resource "aws_config_delivery_channel" "main" {{
  name           = "${{var.project_name}}-config-delivery-channel"
  s3_bucket_name = aws_s3_bucket.config.bucket
  depends_on     = [aws_config_configuration_recorder.main]
}}

# Config S3 Bucket
resource "aws_s3_bucket" "config" {{
  bucket        = "${{var.project_name}}-config-${{random_id.config_suffix.hex}}"
  force_destroy = true
  
  tags = {{
    Name = "${{var.project_name}}-config-bucket"
  }}
}}

# Config IAM Role
resource "aws_iam_role" "config" {{
  name = "${{var.project_name}}-config-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "config.amazonaws.com"
        }}
      }}
    ]
  }})
}}

resource "aws_iam_role_policy_attachment" "config" {{
  role       = aws_iam_role.config.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/ConfigRole"
}}'''
    
    def generate_inspector_configuration(self, project_name: str) -> str:
        """Generate Inspector for vulnerability assessments"""
        return f'''# Amazon Inspector - Vulnerability Assessments
resource "aws_inspector2_enabler" "main" {{
  account_ids    = [data.aws_caller_identity.current.account_id]
  resource_types = ["EC2", "ECR"]
}}

# Inspector Assessment Target
resource "aws_inspector_assessment_target" "main" {{
  name = "${{var.project_name}}-assessment-target"
}}

# Inspector Assessment Template
resource "aws_inspector_assessment_template" "main" {{
  name       = "${{var.project_name}}-assessment-template"
  target_arn = aws_inspector_assessment_target.main.arn
  duration   = 3600
  
  rules_package_arns = [
    "arn:aws:inspector:${{data.aws_region.current.name}}:316112463485:rulespackage/0-R01qwB5Q", # Security Best Practices
    "arn:aws:inspector:${{data.aws_region.current.name}}:316112463485:rulespackage/0-gEjTy7T7", # Runtime Behavior Analysis
    "arn:aws:inspector:${{data.aws_region.current.name}}:316112463485:rulespackage/0-rExsr2X8", # Common Vulnerabilities
    "arn:aws:inspector:${{data.aws_region.current.name}}:316112463485:rulespackage/0-SnojL3Z6"  # Network Reachability
  ]
  
  tags = {{
    Name = "${{var.project_name}}-inspector-template"
  }}
}}'''
    
    def generate_macie_configuration(self, project_name: str) -> str:
        """Generate Macie for data security"""
        return f'''# Amazon Macie - Data Security and Privacy
resource "aws_macie2_account" "main" {{
  finding_publishing_frequency = "FIFTEEN_MINUTES"
  status                       = "ENABLED"
}}

# Macie S3 Bucket Classification Job
resource "aws_macie2_classification_job" "s3_scan" {{
  job_type = "ONE_TIME"
  name     = "${{var.project_name}}-s3-classification"
  
  s3_job_definition {{
    bucket_definitions {{
      account_id = data.aws_caller_identity.current.account_id
      buckets    = [aws_s3_bucket.main.bucket]
    }}
  }}
  
  depends_on = [aws_macie2_account.main]
  
  tags = {{
    Name = "${{var.project_name}}-macie-job"
  }}
}}'''
    
    def generate_cloudhsm_configuration(self, project_name: str) -> str:
        """Generate CloudHSM for FIPS compliance"""
        return f'''# AWS CloudHSM - FIPS 140-2 Level 3 Compliance
resource "aws_cloudhsm_v2_cluster" "main" {{
  hsm_type   = "hsm1.medium"
  subnet_ids = data.aws_subnet.default[*].id
  
  tags = {{
    Name = "${{var.project_name}}-hsm-cluster"
  }}
}}

resource "aws_cloudhsm_v2_hsm" "main" {{
  cluster_id        = aws_cloudhsm_v2_cluster.main.cluster_id
  subnet_id         = data.aws_subnet.default[0].id
  availability_zone = data.aws_availability_zones.available.names[0]
  
  tags = {{
    Name = "${{var.project_name}}-hsm"
  }}
}}

# CloudHSM Client Security Group
resource "aws_security_group" "cloudhsm_client" {{
  name_prefix = "${{var.project_name}}-hsm-client-"
  vpc_id      = data.aws_vpc.main.id
  description = "Security group for CloudHSM client"
  
  egress {{
    description = "CloudHSM NTLS"
    from_port   = 2223
    to_port     = 2225
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }}
  
  tags = {{
    Name = "${{var.project_name}}-hsm-client-sg"
  }}
}}'''
    
    def generate_enhanced_monitoring_configuration(self, project_name: str, security_level: str) -> str:
        """Generate enhanced monitoring with comprehensive security metrics"""
        advanced_monitoring = ""
        if security_level == "high":
            advanced_monitoring = f'''

# Custom Security Metrics
resource "aws_cloudwatch_log_metric_filter" "failed_logins" {{
  name           = "${{var.project_name}}-failed-logins"
  log_group_name = aws_cloudwatch_log_group.app.name
  pattern        = "[timestamp, request_id, ip, status_code=401, ...]"
  
  metric_transformation {{
    name      = "FailedLogins"
    namespace = "${{var.project_name}}/Security"
    value     = "1"
  }}
}}

resource "aws_cloudwatch_metric_alarm" "failed_login_threshold" {{
  alarm_name          = "${{var.project_name}}-excessive-failed-logins"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "FailedLogins"
  namespace           = "${{var.project_name}}/Security"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors excessive failed login attempts"
  alarm_actions       = [aws_sns_topic.security_alerts.arn]
  
  tags = {{
    Name = "${{var.project_name}}-failed-login-alarm"
  }}
}}

# Anomaly Detection
resource "aws_cloudwatch_anomaly_detector" "api_traffic" {{
  metric_math_anomaly_detector {{
    metric_data_queries {{
      id = "m1"
      return_data = true
      metric_stat {{
        metric {{
          metric_name = "RequestCount"
          namespace   = "AWS/ApplicationELB"
          
          dimensions = {{
            LoadBalancer = aws_lb.main.arn_suffix
          }}
        }}
        period = 300
        stat   = "Average"
      }}
    }}
  }}
}}'''
        
        return f'''# Enhanced CloudWatch Monitoring
resource "aws_cloudwatch_log_group" "app" {{
  name              = "/aws/application/${{var.project_name}}"
  retention_in_days = 90
  kms_key_id        = aws_kms_key.main.arn
  
  tags = {{
    Name = "${{var.project_name}}-app-logs"
    SecurityLevel = "{security_level}"
  }}
}}

# Security-focused CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "security" {{
  dashboard_name = "${{var.project_name}}-security-dashboard"
  
  dashboard_body = jsonencode({{
    widgets = [
      {{
        type   = "metric"
        width  = 12
        height = 6
        properties = {{
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.main.arn_suffix],
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", aws_lb.main.arn_suffix],
            ["AWS/ApplicationELB", "HTTPCode_ELB_4XX_Count", "LoadBalancer", aws_lb.main.arn_suffix],
            ["AWS/ApplicationELB", "HTTPCode_ELB_5XX_Count", "LoadBalancer", aws_lb.main.arn_suffix]
          ]
          period = 300
          stat   = "Sum"
          region = data.aws_region.current.name
          title  = "Load Balancer Metrics"
        }}
      }}
    ]
  }})
}}

# SNS Topic for Security Alerts
resource "aws_sns_topic" "security_alerts" {{
  name = "${{var.project_name}}-security-alerts"
  
  tags = {{
    Name = "${{var.project_name}}-security-alerts"
  }}
}}

# CloudWatch Alarms for Security Events
resource "aws_cloudwatch_metric_alarm" "high_cpu" {{
  alarm_name          = "${{var.project_name}}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_sns_topic.security_alerts.arn]
  
  tags = {{
    Name = "${{var.project_name}}-cpu-alarm"
  }}
}}

resource "aws_cloudwatch_metric_alarm" "disk_usage" {{
  alarm_name          = "${{var.project_name}}-high-disk-usage"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DiskSpaceUtilization"
  namespace           = "System/Linux"
  period              = "300"
  statistic           = "Average"
  threshold           = "85"
  alarm_description   = "This metric monitors disk space utilization"
  alarm_actions       = [aws_sns_topic.security_alerts.arn]
  
  tags = {{
    Name = "${{var.project_name}}-disk-alarm"
  }}
}}{advanced_monitoring}'''
    
    def generate_enhanced_logging_configuration(self, project_name: str, security_level: str) -> str:
        """Generate enhanced logging with comprehensive audit capabilities"""
        return f'''# Enhanced CloudTrail Configuration
resource "aws_cloudtrail" "main" {{
  name                          = "${{var.project_name}}-trail-enhanced"
  s3_bucket_name               = aws_s3_bucket.cloudtrail_logs.id
  s3_key_prefix                = "cloudtrail"
  include_global_service_events = true
  is_multi_region_trail        = true
  enable_logging               = true
  enable_log_file_validation   = true
  kms_key_id                   = aws_kms_key.main.arn
  
  # Enhanced data events
  event_selector {{
    read_write_type                 = "All"
    include_management_events       = true
    
    data_resource {{
      type   = "AWS::S3::Object"
      values = ["${{aws_s3_bucket.main.arn}}/*"]
    }}
    
    data_resource {{
      type   = "AWS::Lambda::Function"
      values = ["arn:aws:lambda:*"]
    }}
  }}
  
  # Insights for anomaly detection
  insight_selector {{
    insight_type = "ApiCallRateInsight"
  }}
  
  tags = {{
    Name = "${{var.project_name}}-trail-enhanced"
    SecurityLevel = "{security_level}"
  }}
}}

# VPC Flow Logs
resource "aws_flow_log" "vpc" {{
  iam_role_arn    = aws_iam_role.flow_logs.arn
  log_destination = aws_cloudwatch_log_group.vpc_flow_logs.arn
  traffic_type    = "ALL"
  vpc_id          = data.aws_vpc.main.id
  
  tags = {{
    Name = "${{var.project_name}}-vpc-flow-logs"
  }}
}}

resource "aws_cloudwatch_log_group" "vpc_flow_logs" {{
  name              = "/aws/vpc/flowlogs/${{var.project_name}}"
  retention_in_days = 90
  kms_key_id        = aws_kms_key.main.arn
  
  tags = {{
    Name = "${{var.project_name}}-vpc-flow-logs"
  }}
}}

# Enhanced S3 Bucket for CloudTrail Logs
resource "aws_s3_bucket" "cloudtrail_logs" {{
  bucket        = "${{var.project_name}}-cloudtrail-logs-${{random_id.logs_suffix.hex}}"
  force_destroy = false
  
  tags = {{
    Name = "${{var.project_name}}-cloudtrail-logs"
    SecurityLevel = "{security_level}"
  }}
}}

resource "aws_s3_bucket_encryption_configuration" "cloudtrail_logs" {{
  bucket = aws_s3_bucket.cloudtrail_logs.id
  
  rule {{
    apply_server_side_encryption_by_default {{
      kms_master_key_id = aws_kms_key.main.arn
      sse_algorithm     = "aws:kms"
    }}
    bucket_key_enabled = true
  }}
}}

resource "aws_s3_bucket_public_access_block" "cloudtrail_logs" {{
  bucket = aws_s3_bucket.cloudtrail_logs.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}

# IAM Role for Flow Logs
resource "aws_iam_role" "flow_logs" {{
  name = "${{var.project_name}}-flow-logs-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "vpc-flow-logs.amazonaws.com"
        }}
      }}
    ]
  }})
}}

resource "aws_iam_role_policy" "flow_logs" {{
  name = "${{var.project_name}}-flow-logs-policy"
  role = aws_iam_role.flow_logs.id
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Effect   = "Allow"
        Resource = "*"
      }}
    ]
  }})
}}

resource "random_id" "logs_suffix" {{
  byte_length = 4
}}'''