from typing import Dict, List
from app.schemas.questionnaire import QuestionnaireRequest
from app.core.enhanced_security_templates import EnhancedSecurityTemplates

class TemplateGenerator:
    """Generate Infrastructure as Code templates with enhanced security hardening"""
    
    def __init__(self):
        self.enhanced_security = EnhancedSecurityTemplates()
        self.security_levels = {
            "basic": ["encryption", "vpc", "enhanced_security_groups", "enhanced_nacls"],
            "medium": ["encryption", "vpc", "enhanced_security_groups", "enhanced_nacls", "monitoring", "backup", "guardduty", "cloudtrail"],
            "high": ["encryption", "vpc", "enhanced_security_groups", "enhanced_nacls", "monitoring", "backup", "waf", "secrets", "multi_az", "logging", "guardduty", "security_hub", "config", "inspector", "macie", "cloudhsm", "compliance_controls"]
        }
    
    def _determine_security_level(self, questionnaire: QuestionnaireRequest) -> str:
        """Determine security requirements based on questionnaire"""
        compliance = getattr(questionnaire, 'compliance_requirements', [])
        data_sensitivity = getattr(questionnaire, 'data_sensitivity', '').lower()
        
        # Enhanced security level determination
        if any(req in ['hipaa', 'pci-dss', 'sox', 'fedramp'] for req in compliance) or 'high' in data_sensitivity:
            return "high"
        elif 'medium' in data_sensitivity or len(compliance) > 0 or any(req in ['gdpr'] for req in compliance):
            return "medium"
        else:
            return "basic"
    
    def _determine_architecture_type(self, questionnaire: QuestionnaireRequest) -> str:
        """Determine the type of architecture based on questionnaire responses"""
        app_type = getattr(questionnaire, 'application_type', '').lower()
        
        if 'web' in app_type or 'frontend' in app_type:
            return "web_application"
        elif 'api' in app_type or 'backend' in app_type:
            return "api_backend"
        elif 'analytics' in app_type or 'data' in app_type or 'ml' in app_type:
            return "data_analytics"
        elif 'microservice' in app_type or 'container' in app_type:
            return "microservices"
        else:
            return "web_application"
    
    def generate_terraform_template(self, questionnaire: QuestionnaireRequest, services: Dict[str, str]) -> str:
        """Generate a security-hardened, project-specific Terraform template"""
        project_name_clean = questionnaire.project_name.lower().replace(' ', '-').replace('_', '-')
        security_level = self._determine_security_level(questionnaire)
        arch_type = self._determine_architecture_type(questionnaire)
        security_features = self.security_levels[security_level]
        
        # Build template sections
        template_sections = []
        
        # Header and provider configuration
        template_sections.append(self._generate_terraform_header(project_name_clean))
        
        # Variables
        template_sections.append(self._generate_terraform_variables(security_level))
        
        # Data sources
        template_sections.append(self._generate_terraform_data_sources())
        
        # Security components
        if "encryption" in security_features:
            template_sections.append(self._generate_terraform_kms(project_name_clean))
        
        if "secrets" in security_features:
            template_sections.append(self._generate_terraform_secrets(project_name_clean))
        
        # Networking
        template_sections.append(self._generate_terraform_vpc(project_name_clean, security_level))
        
        # Enhanced security groups and NACLs  
        if "enhanced_security_groups" in security_features:
            template_sections.append(self._generate_enhanced_terraform_security_groups(project_name_clean, services, security_level))
        
        if "enhanced_nacls" in security_features:
            template_sections.append(self._generate_terraform_nacls(project_name_clean, security_level))
        
        # Enhanced WAF with advanced rules
        if "waf" in security_features:
            template_sections.append(self._generate_enhanced_terraform_waf(project_name_clean, security_level))
        
        # Load balancer
        if "load_balancer" in services:
            template_sections.append(self._generate_terraform_alb(project_name_clean, security_level))
        
        # Compute resources based on architecture type
        if arch_type == "web_application":
            template_sections.append(self._generate_terraform_ec2(project_name_clean, services, security_level))
        elif arch_type == "api_backend":
            template_sections.append(self._generate_terraform_lambda(project_name_clean, security_level))
        elif arch_type == "microservices":
            template_sections.append(self._generate_terraform_ecs(project_name_clean, security_level))
        
        # Database
        if "database" in services:
            template_sections.append(self._generate_terraform_database(project_name_clean, services, security_level))
        
        # Storage
        template_sections.append(self._generate_terraform_s3(project_name_clean, security_level))
        
        # Enhanced security services
        if "guardduty" in security_features:
            template_sections.append(self._generate_terraform_guardduty(project_name_clean))
        
        if "security_hub" in security_features:
            template_sections.append(self._generate_terraform_security_hub(project_name_clean))
        
        if "config" in security_features:
            template_sections.append(self._generate_terraform_config(project_name_clean))
        
        if "inspector" in security_features:
            template_sections.append(self._generate_terraform_inspector(project_name_clean))
        
        if "macie" in security_features:
            template_sections.append(self._generate_terraform_macie(project_name_clean))
        
        if "cloudhsm" in security_features:
            template_sections.append(self._generate_terraform_cloudhsm(project_name_clean))
        
        # Enhanced monitoring and logging
        if "monitoring" in security_features:
            template_sections.append(self._generate_enhanced_terraform_monitoring(project_name_clean, security_level))
        
        if "logging" in security_features:
            template_sections.append(self._generate_enhanced_terraform_logging(project_name_clean, security_level))
        
        # Compliance controls
        if "compliance_controls" in security_features:
            compliance_frameworks = getattr(questionnaire, 'compliance_requirements', [])
            template_sections.append(self._generate_terraform_compliance_controls(project_name_clean, compliance_frameworks))
        
        # Outputs
        template_sections.append(self._generate_terraform_outputs())
        
        return "\n\n".join(template_sections)
    
    def _generate_terraform_header(self, project_name: str) -> str:
        return f'''# Terraform configuration for {project_name}
# Generated with security best practices

terraform {{
  required_version = ">= 1.5"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
    random = {{
      source  = "hashicorp/random"
      version = "~> 3.1"
    }}
  }}
}}

provider "aws" {{
  region = var.aws_region
  
  default_tags {{
    tags = {{
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      CreatedBy   = "AWS-Architecture-Generator"
    }}
  }}
}}'''
    
    def _generate_terraform_variables(self, security_level: str) -> str:
        return '''# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for critical resources"
  type        = bool
  default     = true
}'''
    
    def _generate_terraform_data_sources(self) -> str:
        return '''# Data Sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}'''
    
    def _generate_terraform_kms(self, project_name: str) -> str:
        return f'''# KMS Key for encryption
resource "aws_kms_key" "main" {{
  description             = "KMS key for {project_name}"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  
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
    Name = "${{var.project_name}}-kms-key"
  }}
}}

resource "aws_kms_alias" "main" {{
  name          = "alias/${{var.project_name}}-key"
  target_key_id = aws_kms_key.main.key_id
}}'''
    
    def _generate_terraform_secrets(self, project_name: str) -> str:
        return f'''# Secrets Manager
resource "aws_secretsmanager_secret" "db_credentials" {{
  name                    = "${{var.project_name}}-db-credentials"
  description             = "Database credentials for {project_name}"
  kms_key_id              = aws_kms_key.main.arn
  recovery_window_in_days = 7
  
  tags = {{
    Name = "${{var.project_name}}-db-secret"
  }}
}}

resource "aws_secretsmanager_secret_version" "db_credentials" {{
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({{
    username = "admin"
    password = random_password.db_password.result
  }})
}}

resource "random_password" "db_password" {{
  length  = 32
  special = true
}}'''
    
    def _generate_terraform_vpc(self, project_name: str, security_level: str) -> str:
        multi_az = security_level == "high"
        
        vpc_config = f'''# VPC Configuration
resource "aws_vpc" "main" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {{
    Name = "${{var.project_name}}-vpc"
  }}
}}

# Internet Gateway
resource "aws_internet_gateway" "main" {{
  vpc_id = aws_vpc.main.id
  
  tags = {{
    Name = "${{var.project_name}}-igw"
  }}
}}

# Public Subnets
resource "aws_subnet" "public" {{
  count                   = {2 if multi_az else 1}
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${{count.index + 1}}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = {{
    Name = "${{var.project_name}}-public-${{count.index + 1}}"
    Type = "public"
  }}
}}

# Private Subnets
resource "aws_subnet" "private" {{
  count             = {2 if multi_az else 1}
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${{count.index + 10}}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {{
    Name = "${{var.project_name}}-private-${{count.index + 1}}"
    Type = "private"
  }}
}}

# Route Tables
resource "aws_route_table" "public" {{
  vpc_id = aws_vpc.main.id
  
  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }}
  
  tags = {{
    Name = "${{var.project_name}}-public-rt"
  }}
}}

resource "aws_route_table_association" "public" {{
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}}'''

        if multi_az:
            vpc_config += '''

# NAT Gateways for private subnets
resource "aws_eip" "nat" {
  count  = length(aws_subnet.public)
  domain = "vpc"
  
  depends_on = [aws_internet_gateway.main]
  
  tags = {
    Name = "${var.project_name}-nat-eip-${count.index + 1}"
  }
}

resource "aws_nat_gateway" "main" {
  count         = length(aws_subnet.public)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = {
    Name = "${var.project_name}-nat-gw-${count.index + 1}"
  }
}

resource "aws_route_table" "private" {
  count  = length(aws_subnet.private)
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }
  
  tags = {
    Name = "${var.project_name}-private-rt-${count.index + 1}"
  }
}

resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}'''
        
        return vpc_config
    
    def _generate_terraform_security_groups(self, project_name: str, services: Dict[str, str]) -> str:
        return f'''# Security Groups
resource "aws_security_group" "alb" {{
  name_prefix = "${{var.project_name}}-alb-"
  vpc_id      = aws_vpc.main.id
  description = "Security group for Application Load Balancer"
  
  ingress {{
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  ingress {{
    description = "HTTP (redirect to HTTPS)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  tags = {{
    Name = "${{var.project_name}}-alb-sg"
  }}
  
  lifecycle {{
    create_before_destroy = true
  }}
}}

resource "aws_security_group" "app" {{
  name_prefix = "${{var.project_name}}-app-"
  vpc_id      = aws_vpc.main.id
  description = "Security group for application servers"
  
  ingress {{
    description     = "Application traffic from ALB"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }}
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  tags = {{
    Name = "${{var.project_name}}-app-sg"
  }}
}}

resource "aws_security_group" "database" {{
  name_prefix = "${{var.project_name}}-db-"
  vpc_id      = aws_vpc.main.id
  description = "Security group for database"
  
  ingress {{
    description     = "Database access from application"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }}
  
  tags = {{
    Name = "${{var.project_name}}-db-sg"
  }}
}}'''
    
    def _generate_terraform_waf(self, project_name: str) -> str:
        return f'''# WAF v2 Configuration
resource "aws_wafv2_web_acl" "main" {{
  name  = "${{var.project_name}}-waf"
  scope = "REGIONAL"
  
  default_action {{
    allow {{}}
  }}
  
  # AWS Managed Rules
  rule {{
    name     = "AWSManagedRulesCommonRuleSet"
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
      metric_name                 = "CommonRuleSetMetric"
      sampled_requests_enabled    = true
    }}
  }}
  
  rule {{
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
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
      metric_name                 = "KnownBadInputsRuleSetMetric"
      sampled_requests_enabled    = true
    }}
  }}
  
  tags = {{
    Name = "${{var.project_name}}-waf"
  }}
  
  visibility_config {{
    cloudwatch_metrics_enabled = true
    metric_name                 = "${{var.project_name}}-waf"
    sampled_requests_enabled    = true
  }}
}}'''
    
    def _generate_terraform_alb(self, project_name: str, security_level: str) -> str:
        return f'''# Application Load Balancer
resource "aws_lb" "main" {{
  name               = "${{var.project_name}}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
  
  enable_deletion_protection = var.enable_deletion_protection
  
  {"associate_web_acl_arn = aws_wafv2_web_acl.main.arn" if security_level == "high" else ""}
  
  tags = {{
    Name = "${{var.project_name}}-alb"
  }}
}}

resource "aws_lb_target_group" "app" {{
  name     = "${{var.project_name}}-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  
  health_check {{
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }}
  
  tags = {{
    Name = "${{var.project_name}}-tg"
  }}
}}

resource "aws_lb_listener" "app" {{
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate.main.arn
  
  default_action {{
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }}
}}

resource "aws_lb_listener" "redirect" {{
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {{
    type = "redirect"
    
    redirect {{
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }}
  }}
}}

# SSL Certificate
resource "aws_acm_certificate" "main" {{
  domain_name       = "${{var.project_name}}.example.com"
  validation_method = "DNS"
  
  lifecycle {{
    create_before_destroy = true
  }}
  
  tags = {{
    Name = "${{var.project_name}}-cert"
  }}
}}'''
    
    def _generate_terraform_ec2(self, project_name: str, services: Dict[str, str], security_level: str) -> str:
        return f'''# Launch Template
resource "aws_launch_template" "app" {{
  name_prefix   = "${{var.project_name}}-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  
  vpc_security_group_ids = [aws_security_group.app.id]
  
  {"key_name = aws_key_pair.main.key_name" if security_level in ["medium", "high"] else ""}
  
  iam_instance_profile {{
    name = aws_iam_instance_profile.app.name
  }}
  
  block_device_mappings {{
    device_name = "/dev/xvda"
    ebs {{
      volume_size = 20
      volume_type = "gp3"
      encrypted   = true
      {"kms_key_id = aws_kms_key.main.arn" if security_level == "high" else ""}
      delete_on_termination = true
    }}
  }}
  
  metadata_options {{
    http_endpoint = "enabled"
    http_tokens   = "required"
    http_put_response_hop_limit = 1
  }}
  
  tag_specifications {{
    resource_type = "instance"
    tags = {{
      Name = "${{var.project_name}}-instance"
    }}
  }}
  
  user_data = base64encode(templatefile("${{path.module}}/user_data.sh", {{
    project_name = var.project_name
  }}))
}}

# Auto Scaling Group
resource "aws_autoscaling_group" "app" {{
  name                = "${{var.project_name}}-asg"
  vpc_zone_identifier = aws_subnet.private[*].id
  target_group_arns   = [aws_lb_target_group.app.arn]
  health_check_type   = "ELB"
  health_check_grace_period = 300
  
  min_size         = 1
  max_size         = {3 if security_level == "high" else 2}
  desired_capacity = {2 if security_level == "high" else 1}
  
  launch_template {{
    id      = aws_launch_template.app.id
    version = "$Latest"
  }}
  
  tag {{
    key                 = "Name"
    value               = "${{var.project_name}}-asg"
    propagate_at_launch = false
  }}
}}

# IAM Role for EC2 instances
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
      }}
    ]
  }})
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
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${{aws_s3_bucket.main.arn}}/*"
      }},
      {{
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.db_credentials.arn
      }}
    ]
  }})
}}

# AMI Data Source
data "aws_ami" "amazon_linux" {{
  most_recent = true
  owners      = ["amazon"]
  
  filter {{
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }}
}}'''

        ec2_config = f'''# Launch Template
resource "aws_launch_template" "app" {{
  name_prefix   = "${{var.project_name}}-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  
  vpc_security_group_ids = [aws_security_group.app.id]
  
  {"key_name = aws_key_pair.main.key_name" if security_level in ["medium", "high"] else ""}
  
  iam_instance_profile {{
    name = aws_iam_instance_profile.app.name
  }}
  
  block_device_mappings {{
    device_name = "/dev/xvda"
    ebs {{
      volume_size = 20
      volume_type = "gp3"
      encrypted   = true
      {"kms_key_id = aws_kms_key.main.arn" if security_level == "high" else ""}
      delete_on_termination = true
    }}
  }}
  
  metadata_options {{
    http_endpoint = "enabled"
    http_tokens   = "required"
    http_put_response_hop_limit = 1
  }}
  
  tag_specifications {{
    resource_type = "instance"
    tags = {{
      Name = "${{var.project_name}}-instance"
    }}
  }}
  
  user_data = base64encode(templatefile("${{path.module}}/user_data.sh", {{
    project_name = var.project_name
  }}))
}}

# Auto Scaling Group
resource "aws_autoscaling_group" "app" {{
  name                = "${{var.project_name}}-asg"
  vpc_zone_identifier = aws_subnet.private[*].id
  target_group_arns   = [aws_lb_target_group.app.arn]
  health_check_type   = "ELB"
  health_check_grace_period = 300
  
  min_size         = 1
  max_size         = {3 if security_level == "high" else 2}
  desired_capacity = {2 if security_level == "high" else 1}
  
  launch_template {{
    id      = aws_launch_template.app.id
    version = "$Latest"
  }}
  
  tag {{
    key                 = "Name"
    value               = "${{var.project_name}}-asg"
    propagate_at_launch = false
  }}
}}

# IAM Role for EC2 instances
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
      }}
    ]
  }})
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
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${{aws_s3_bucket.main.arn}}/*"
      }},
      {{
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.db_credentials.arn
      }}
    ]
  }})
}}

# AMI Data Source
data "aws_ami" "amazon_linux" {{
  most_recent = true
  owners      = ["amazon"]
  
  filter {{
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }}
}}'''

        if security_level in ["medium", "high"]:
            ec2_config += '''

# Key Pair for SSH access (if needed)
resource "aws_key_pair" "main" {
  key_name   = "${var.project_name}-key"
  public_key = file("${path.module}/public_key.pub")
}'''
        
        return ec2_config
    
    def _generate_terraform_lambda(self, project_name: str, security_level: str) -> str:
        return f'''# Lambda Functions for API Backend
resource "aws_lambda_function" "api" {{
  filename         = "lambda_function.zip"
  function_name    = "${{var.project_name}}-api"
  role            = aws_iam_role.lambda.arn
  handler         = "index.handler"
  runtime         = "python3.9"
  timeout         = 30
  
  {"kms_key_arn = aws_kms_key.main.arn" if security_level == "high" else ""}
  
  environment {{
    variables = {{
      ENVIRONMENT = var.environment
      {"DB_SECRET_ARN = aws_secretsmanager_secret.db_credentials.arn" if security_level in ["medium", "high"] else ""}
    }}
  }}
  
  vpc_config {{
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }}
  
  tags = {{
    Name = "${{var.project_name}}-lambda"
  }}
}}

# API Gateway
resource "aws_api_gateway_rest_api" "main" {{
  name        = "${{var.project_name}}-api"
  description = "API Gateway for {project_name}"
  
  endpoint_configuration {{
    types = ["REGIONAL"]
  }}
}}

resource "aws_api_gateway_resource" "proxy" {{
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "{{proxy+}}"
}}

resource "aws_api_gateway_method" "proxy" {{
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}}

resource "aws_api_gateway_integration" "lambda" {{
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_method.proxy.resource_id
  http_method = aws_api_gateway_method.proxy.http_method
  
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api.invoke_arn
}}

resource "aws_api_gateway_deployment" "main" {{
  depends_on = [
    aws_api_gateway_integration.lambda,
  ]
  
  rest_api_id = aws_api_gateway_rest_api.main.id
  stage_name  = var.environment
}}

# Lambda IAM Role
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
      }}
    ]
  }})
}}

resource "aws_iam_role_policy_attachment" "lambda_basic" {{
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}}

# Lambda Security Group
resource "aws_security_group" "lambda" {{
  name_prefix = "${{var.project_name}}-lambda-"
  vpc_id      = aws_vpc.main.id
  description = "Security group for Lambda functions"
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  tags = {{
    Name = "${{var.project_name}}-lambda-sg"
  }}
}}'''
    
    def _generate_terraform_ecs(self, project_name: str, security_level: str) -> str:
        container_insights = '''setting {
    name  = "containerInsights"
    value = "enabled"
  }''' if security_level in ["medium", "high"] else ""
        
        return f'''# ECS Cluster
resource "aws_ecs_cluster" "main" {{
  name = "${{var.project_name}}-cluster"
  
  {container_insights}
  
  tags = {{
    Name = "${{var.project_name}}-cluster"
  }}
}}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {{
  family                   = "${{var.project_name}}-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn           = aws_iam_role.ecs_task.arn
  
  container_definitions = jsonencode([
    {{
      name  = "${{var.project_name}}-container"
      image = "nginx:latest"
      
      portMappings = [
        {{
          containerPort = 80
          protocol      = "tcp"
        }}
      ]
      
      logConfiguration = {{
        logDriver = "awslogs"
        options = {{
          "awslogs-group"         = aws_cloudwatch_log_group.app.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "ecs"
        }}
      }}
      
      environment = [
        {{
          name  = "ENVIRONMENT"
          value = var.environment
        }}
      ]
    }}
  ])
  
  tags = {{
    Name = "${{var.project_name}}-task"
  }}
}}

# ECS Service
resource "aws_ecs_service" "app" {{
  name            = "${{var.project_name}}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = {2 if security_level == "high" else 1}
  launch_type     = "FARGATE"
  
  network_configuration {{
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }}
  
  load_balancer {{
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "${{var.project_name}}-container"
    container_port   = 80
  }}
  
  depends_on = [aws_lb_listener.app]
  
  tags = {{
    Name = "${{var.project_name}}-service"
  }}
}}

# ECS IAM Roles
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
}}

resource "aws_iam_role_policy_attachment" "ecs_execution" {{
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}}

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
}}

# ECS Security Group
resource "aws_security_group" "ecs" {{
  name_prefix = "${{var.project_name}}-ecs-"
  vpc_id      = aws_vpc.main.id
  description = "Security group for ECS tasks"
  
  ingress {{
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }}
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  tags = {{
    Name = "${{var.project_name}}-ecs-sg"
  }}
}}'''
    
    def _generate_terraform_database(self, project_name: str, services: Dict[str, str], security_level: str) -> str:
        db_engine = services.get('database', 'mysql')
        multi_az = security_level == "high"
        
        cloudwatch_logs = '''enabled_cloudwatch_logs_exports = ["error", "general", "slow-query"]''' if security_level in ["medium", "high"] else ""
        
        return f'''# RDS Database
resource "aws_db_subnet_group" "main" {{
  name       = "${{var.project_name}}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  
  tags = {{
    Name = "${{var.project_name}}-db-subnet-group"
  }}
}}

resource "aws_db_instance" "main" {{
  identifier = "${{var.project_name}}-database"
  
  engine         = "{db_engine.lower()}"
  engine_version = "{self._get_db_version(db_engine)}"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true
  {"kms_key_id = aws_kms_key.main.arn" if security_level == "high" else ""}
  
  db_name  = "${{replace(var.project_name, \"-\", \"\")}}"
  username = "admin"
  manage_master_user_password = true
  {"master_user_secret_kms_key_id = aws_kms_key.main.arn" if security_level == "high" else ""}
  
  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = {7 if security_level in ["medium", "high"] else 1}
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  multi_az               = {str(multi_az).lower()}
  publicly_accessible    = false
  
  skip_final_snapshot = false
  final_snapshot_identifier = "${{var.project_name}}-final-snapshot-${{formatdate("YYYY-MM-DD-hhmm", timestamp())}}"
  
  deletion_protection = var.enable_deletion_protection
  
  {cloudwatch_logs}
  
  tags = {{
    Name = "${{var.project_name}}-database"
  }}
}}'''
    
    def _generate_terraform_s3(self, project_name: str, security_level: str) -> str:
        logging_config = '''resource "aws_s3_bucket_logging" "main" {
  bucket = aws_s3_bucket.main.id
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "access-logs/"
}''' if security_level in ["medium", "high"] else ""
        
        return f'''# S3 Bucket
resource "aws_s3_bucket" "main" {{
  bucket = "${{var.project_name}}-storage-${{random_id.bucket_suffix.hex}}"
  
  tags = {{
    Name = "${{var.project_name}}-storage"
  }}
}}

resource "random_id" "bucket_suffix" {{
  byte_length = 4
}}

# S3 Bucket Configuration
resource "aws_s3_bucket_versioning" "main" {{
  bucket = aws_s3_bucket.main.id
  versioning_configuration {{
    status = "Enabled"
  }}
}}

resource "aws_s3_bucket_encryption_configuration" "main" {{
  bucket = aws_s3_bucket.main.id
  
  rule {{
    apply_server_side_encryption_by_default {{
      {"kms_master_key_id = aws_kms_key.main.arn" if security_level == "high" else ""}
      sse_algorithm     = "{"aws:kms" if security_level == "high" else "AES256"}"
    }}
    bucket_key_enabled = true
  }}
}}

resource "aws_s3_bucket_public_access_block" "main" {{
  bucket = aws_s3_bucket.main.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}

resource "aws_s3_bucket_lifecycle_configuration" "main" {{
  bucket = aws_s3_bucket.main.id
  
  rule {{
    id     = "lifecycle"
    status = "Enabled"
    
    expiration {{
      days = 90
    }}
    
    noncurrent_version_expiration {{
      noncurrent_days = 30
    }}
  }}
}}

{logging_config}'''
    
    def _generate_terraform_monitoring(self, project_name: str) -> str:
        return f'''# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "app" {{
  name              = "/aws/application/${{var.project_name}}"
  retention_in_days = 30
  
  tags = {{
    Name = "${{var.project_name}}-logs"
  }}
}}

# CloudWatch Alarms
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
  
  dimensions = {{
    AutoScalingGroupName = aws_autoscaling_group.app.name
  }}
  
  tags = {{
    Name = "${{var.project_name}}-cpu-alarm"
  }}
}}

# SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {{
  name = "${{var.project_name}}-alerts"
  
  tags = {{
    Name = "${{var.project_name}}-alerts"
  }}
}}'''
    
    def _generate_terraform_logging(self, project_name: str) -> str:
        return f'''# CloudTrail for Audit Logging
resource "aws_cloudtrail" "main" {{
  name                          = "${{var.project_name}}-trail"
  s3_bucket_name               = aws_s3_bucket.logs.id
  s3_key_prefix                = "cloudtrail"
  include_global_service_events = true
  is_multi_region_trail        = true
  enable_logging               = true
  
  event_selector {{
    read_write_type                 = "All"
    include_management_events       = true
    data_resource {{
      type   = "AWS::S3::Object"
      values = ["${{aws_s3_bucket.main.arn}}/*"]
    }}
  }}
  
  tags = {{
    Name = "${{var.project_name}}-trail"
  }}
}}

# S3 Bucket for Logs
resource "aws_s3_bucket" "logs" {{
  bucket = "${{var.project_name}}-logs-${{random_id.logs_suffix.hex}}"
  
  tags = {{
    Name = "${{var.project_name}}-logs"
  }}
}}

resource "random_id" "logs_suffix" {{
  byte_length = 4
}}

resource "aws_s3_bucket_policy" "cloudtrail_logs" {{
  bucket = aws_s3_bucket.logs.id
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {{
          Service = "cloudtrail.amazonaws.com"
        }}
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.logs.arn
      }},
      {{
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {{
          Service = "cloudtrail.amazonaws.com"
        }}
        Action   = "s3:PutObject"
        Resource = "${{aws_s3_bucket.logs.arn}}/cloudtrail/*"
        Condition = {{
          StringEquals = {{
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }}
        }}
      }}
    ]
  }})
}}'''
    
    def _generate_terraform_outputs(self) -> str:
        return '''# Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = try(aws_lb.main.dns_name, "")
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.main.bucket
}

output "database_endpoint" {
  description = "Database endpoint"
  value       = try(aws_db_instance.main.endpoint, "")
  sensitive   = true
}

output "api_gateway_url" {
  description = "API Gateway URL"
  value       = try(aws_api_gateway_deployment.main.invoke_url, "")
}'''
    
    def _get_db_version(self, engine: str) -> str:
        """Get appropriate database version"""
        versions = {
            "mysql": "8.0",
            "postgres": "14.9",
            "aurora-mysql": "8.0.mysql_aurora.3.02.0",
            "aurora-postgresql": "14.9"
        }
        return versions.get(engine.lower(), "8.0")

    def generate_cloudformation_template(self, questionnaire: QuestionnaireRequest, services: Dict[str, str]) -> str:
        """Generate a security-hardened, project-specific CloudFormation template"""
        project_name_clean = questionnaire.project_name.lower().replace(' ', '-').replace('_', '-')
        security_level = self._determine_security_level(questionnaire)
        arch_type = self._determine_architecture_type(questionnaire)
        security_features = self.security_levels[security_level]
        
        # Build template sections
        template_sections = []
        
        # Header and metadata
        template_sections.append(self._generate_cf_header(questionnaire.project_name))
        
        # Parameters
        template_sections.append(self._generate_cf_parameters(security_level))
        
        # Mappings
        template_sections.append(self._generate_cf_mappings())
        
        # Resources start
        template_sections.append("Resources:")
        
        # Security components
        if "encryption" in security_features:
            template_sections.append(self._generate_cf_kms(project_name_clean))
        
        if "secrets" in security_features:
            template_sections.append(self._generate_cf_secrets(project_name_clean))
        
        # Networking
        template_sections.append(self._generate_cf_vpc(project_name_clean, security_level))
        
        # Security groups
        if "security_groups" in security_features:
            template_sections.append(self._generate_cf_security_groups(project_name_clean, services))
        
        # WAF (if high security)
        if "waf" in security_features:
            template_sections.append(self._generate_cf_waf(project_name_clean))
        
        # Load balancer
        if "load_balancer" in services:
            template_sections.append(self._generate_cf_alb(project_name_clean, security_level))
        
        # Compute resources based on architecture type
        if arch_type == "web_application":
            template_sections.append(self._generate_cf_ec2(project_name_clean, services, security_level))
        elif arch_type == "api_backend":
            template_sections.append(self._generate_cf_lambda(project_name_clean, security_level))
        elif arch_type == "microservices":
            template_sections.append(self._generate_cf_ecs(project_name_clean, security_level))
        
        # Database
        if "database" in services:
            template_sections.append(self._generate_cf_database(project_name_clean, services, security_level))
        
        # Storage
        template_sections.append(self._generate_cf_s3(project_name_clean, security_level))
        
        # Monitoring and logging
        if "monitoring" in security_features:
            template_sections.append(self._generate_cf_monitoring(project_name_clean))
        
        if "logging" in security_features:
            template_sections.append(self._generate_cf_logging(project_name_clean))
        
        # Outputs
        template_sections.append(self._generate_cf_outputs())
        
        return "\n\n".join(template_sections)
    
    def _generate_cf_header(self, project_name: str) -> str:
        return f'''AWSTemplateFormatVersion: '2010-09-09'
Description: >
  CloudFormation template for {project_name} - Generated with security best practices
  by AWS-Architecture-Generator

Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: "Project Configuration"
        Parameters:
          - ProjectName
          - Environment
      - Label:
          default: "Security Configuration"
        Parameters:
          - EnableDeletionProtection'''
    
    def _generate_cf_parameters(self, security_level: str) -> str:
        return '''Parameters:
  ProjectName:
    Type: String
    Description: Project name for resource naming
    MinLength: 1
    MaxLength: 50
    ConstraintDescription: Project name must be between 1 and 50 characters
  
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod
    Description: Environment name
  
  EnableDeletionProtection:
    Type: String
    Default: 'true'
    AllowedValues:
      - 'true'
      - 'false'
    Description: Enable deletion protection for critical resources'''
    
    def _generate_cf_mappings(self) -> str:
        return '''Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-0c55b159cbfafe1d0
    us-west-2:
      AMI: ami-0cb72367e98845d43
    eu-west-1:
      AMI: ami-0bbc25e23a7640b9b'''
    
    def _generate_cf_kms(self, project_name: str) -> str:
        return f'''  # KMS Key for encryption
  MainKMSKey:
    Type: AWS::KMS::Key
    Properties:
      Description: !Sub "KMS key for ${{ProjectName}}"
      EnableKeyRotation: true
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${{AWS::AccountId}}:root"
            Action: 'kms:*'
            Resource: '*'
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-kms-key"
        - Key: Environment
          Value: !Ref Environment
        - Key: ManagedBy
          Value: CloudFormation
  
  MainKMSKeyAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: !Sub "alias/${{ProjectName}}-key"
      TargetKeyId: !Ref MainKMSKey'''
    
    def _generate_cf_secrets(self, project_name: str) -> str:
        return f'''  # Secrets Manager for database credentials
  DatabaseSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub "${{ProjectName}}-db-credentials"
      Description: !Sub "Database credentials for ${{ProjectName}}"
      KmsKeyId: !Ref MainKMSKey
      GenerateSecretString:
        SecretStringTemplate: '{{"username": "admin"}}'
        GenerateStringKey: password
        PasswordLength: 32
        ExcludeCharacters: '"@/\\'
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-db-secret"
        - Key: Environment
          Value: !Ref Environment'''
    
    def _generate_cf_vpc(self, project_name: str, security_level: str) -> str:
        multi_az = security_level == "high"
        
        vpc_template = f'''  # VPC Configuration
  MainVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-vpc"
        - Key: Environment
          Value: !Ref Environment
  
  # Internet Gateway
  MainIGW:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-igw"
        - Key: Environment
          Value: !Ref Environment
  
  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref MainVPC
      InternetGatewayId: !Ref MainIGW
  
  # Public Subnets
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MainVPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-public-1"
        - Key: Type
          Value: public
        - Key: Environment
          Value: !Ref Environment'''

        if multi_az:
            vpc_template += '''
  
  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MainVPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [1, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub "${ProjectName}-public-2"
        - Key: Type
          Value: public
        - Key: Environment
          Value: !Ref Environment'''

        vpc_template += '''
  
  # Private Subnets
  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MainVPC
      CidrBlock: 10.0.10.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      Tags:
        - Key: Name
          Value: !Sub "${ProjectName}-private-1"
        - Key: Type
          Value: private
        - Key: Environment
          Value: !Ref Environment'''

        if multi_az:
            vpc_template += '''
  
  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MainVPC
      CidrBlock: 10.0.11.0/24
      AvailabilityZone: !Select [1, !GetAZs '']
      Tags:
        - Key: Name
          Value: !Sub "${ProjectName}-private-2"
        - Key: Type
          Value: private
        - Key: Environment
          Value: !Ref Environment'''

        vpc_template += '''
  
  # Route Tables
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref MainVPC
      Tags:
        - Key: Name
          Value: !Sub "${ProjectName}-public-rt"
        - Key: Environment
          Value: !Ref Environment
  
  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref MainIGW
  
  PublicSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet1
      RouteTableId: !Ref PublicRouteTable'''

        if multi_az:
            vpc_template += '''
  
  PublicSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet2
      RouteTableId: !Ref PublicRouteTable
  
  # NAT Gateways for high security
  NATGateway1EIP:
    Type: AWS::EC2::EIP
    DependsOn: AttachGateway
    Properties:
      Domain: vpc
      Tags:
        - Key: Name
          Value: !Sub "${ProjectName}-nat-eip-1"
  
  NATGateway2EIP:
    Type: AWS::EC2::EIP
    DependsOn: AttachGateway
    Properties:
      Domain: vpc
      Tags:
        - Key: Name
          Value: !Sub "${ProjectName}-nat-eip-2"
  
  NATGateway1:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NATGateway1EIP.AllocationId
      SubnetId: !Ref PublicSubnet1
      Tags:
        - Key: Name
          Value: !Sub "${ProjectName}-nat-gw-1"
  
  NATGateway2:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NATGateway2EIP.AllocationId
      SubnetId: !Ref PublicSubnet2
      Tags:
        - Key: Name
          Value: !Sub "${ProjectName}-nat-gw-2"
  
  PrivateRouteTable1:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref MainVPC
      Tags:
        - Key: Name
          Value: !Sub "${ProjectName}-private-rt-1"
  
  PrivateRouteTable2:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref MainVPC
      Tags:
        - Key: Name
          Value: !Sub "${ProjectName}-private-rt-2"
  
  PrivateRoute1:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NATGateway1
  
  PrivateRoute2:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable2
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NATGateway2
  
  PrivateSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet1
      RouteTableId: !Ref PrivateRouteTable1
  
  PrivateSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet2
      RouteTableId: !Ref PrivateRouteTable2'''

        return vpc_template
    
    def _generate_cf_security_groups(self, project_name: str, services: Dict[str, str]) -> str:
        return f'''  # Security Groups
  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${{ProjectName}}-alb-sg"
      GroupDescription: Security group for Application Load Balancer
      VpcId: !Ref MainVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: HTTPS
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
          Description: HTTP (redirect to HTTPS)
      SecurityGroupEgress:
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0
          Description: All outbound traffic
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-alb-sg"
        - Key: Environment
          Value: !Ref Environment
  
  AppSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${{ProjectName}}-app-sg"
      GroupDescription: Security group for application servers
      VpcId: !Ref MainVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 8080
          ToPort: 8080
          SourceSecurityGroupId: !Ref ALBSecurityGroup
          Description: Application traffic from ALB
      SecurityGroupEgress:
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0
          Description: All outbound traffic
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-app-sg"
        - Key: Environment
          Value: !Ref Environment
  
  DatabaseSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${{ProjectName}}-db-sg"
      GroupDescription: Security group for database
      VpcId: !Ref MainVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref AppSecurityGroup
          Description: Database access from application
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-db-sg"
        - Key: Environment
          Value: !Ref Environment'''
    
    def _generate_cf_waf(self, project_name: str) -> str:
        return f'''  # WAF v2 Configuration
  MainWebACL:
    Type: AWS::WAFv2::WebACL
    Properties:
      Name: !Sub "${{ProjectName}}-waf"
      Scope: REGIONAL
      DefaultAction:
        Allow: {{}}
      Rules:
        - Name: AWSManagedRulesCommonRuleSet
          Priority: 1
          OverrideAction:
            None: {{}}
          Statement:
            ManagedRuleGroupStatement:
              VendorName: AWS
              Name: AWSManagedRulesCommonRuleSet
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: CommonRuleSetMetric
        - Name: AWSManagedRulesKnownBadInputsRuleSet
          Priority: 2
          OverrideAction:
            None: {{}}
          Statement:
            ManagedRuleGroupStatement:
              VendorName: AWS
              Name: AWSManagedRulesKnownBadInputsRuleSet
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: KnownBadInputsRuleSetMetric
      VisibilityConfig:
        SampledRequestsEnabled: true
        CloudWatchMetricsEnabled: true
        MetricName: !Sub "${{ProjectName}}-waf"
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-waf"
        - Key: Environment
          Value: !Ref Environment'''
    
    def _generate_cf_alb(self, project_name: str, security_level: str) -> str:
        waf_association = '''
      WebAclArn: !GetAtt MainWebACL.Arn''' if security_level == "high" else ""
        
        subnet_config = '''
        - !Ref PublicSubnet2''' if security_level == "high" else ""
        
        return f'''  # Application Load Balancer
  MainALB:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub "${{ProjectName}}-alb"
      Type: application
      Scheme: internet-facing
      SecurityGroups:
        - !Ref ALBSecurityGroup
      Subnets:
        - !Ref PublicSubnet1{subnet_config}
      LoadBalancerAttributes:
        - Key: deletion_protection.enabled
          Value: !Ref EnableDeletionProtection{waf_association}
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-alb"
        - Key: Environment
          Value: !Ref Environment
  
  ALBTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub "${{ProjectName}}-tg"
      Port: 8080
      Protocol: HTTP
      VpcId: !Ref MainVPC
      HealthCheckEnabled: true
      HealthCheckIntervalSeconds: 30
      HealthCheckPath: /health
      HealthCheckPort: traffic-port
      HealthCheckProtocol: HTTP
      HealthCheckTimeoutSeconds: 5
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 2
      Matcher:
        HttpCode: 200
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-tg"
        - Key: Environment
          Value: !Ref Environment
  
  ALBListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref MainALB
      Port: 443
      Protocol: HTTPS
      SslPolicy: ELBSecurityPolicy-TLS-1-2-2017-01
      Certificates:
        - CertificateArn: !Ref SSLCertificate
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref ALBTargetGroup
  
  ALBListenerRedirect:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref MainALB
      Port: 80
      Protocol: HTTP
      DefaultActions:
        - Type: redirect
          RedirectConfig:
            Port: 443
            Protocol: HTTPS
            StatusCode: HTTP_301
  
  # SSL Certificate
  SSLCertificate:
    Type: AWS::CertificateManager::Certificate
    Properties:
      DomainName: !Sub "${{ProjectName}}.example.com"
      ValidationMethod: DNS
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-cert"
        - Key: Environment
          Value: !Ref Environment'''
    
    def _generate_cf_ec2(self, project_name: str, services: Dict[str, str], security_level: str) -> str:
        key_name = '''
      KeyName: !Ref EC2KeyPair''' if security_level in ["medium", "high"] else ""
        
        kms_encryption = '''
            KmsKeyId: !Ref MainKMSKey''' if security_level == "high" else ""
        
        subnet_config = '''
        - !Ref PrivateSubnet2''' if security_level == "high" else ""
        
        ec2_template = f'''  # Launch Template
  AppLaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: !Sub "${{ProjectName}}-lt"
      LaunchTemplateData:
        ImageId: !FindInMap [RegionMap, !Ref "AWS::Region", AMI]
        InstanceType: t3.micro
        SecurityGroupIds:
          - !Ref AppSecurityGroup
        IamInstanceProfile:
          Arn: !GetAtt AppInstanceProfile.Arn{key_name}
        BlockDeviceMappings:
          - DeviceName: /dev/xvda
            Ebs:
              VolumeSize: 20
              VolumeType: gp3
              Encrypted: true{kms_encryption}
              DeleteOnTermination: true
        MetadataOptions:
          HttpEndpoint: enabled
          HttpTokens: required
          HttpPutResponseHopLimit: 1
        TagSpecifications:
          - ResourceType: instance
            Tags:
              - Key: Name
                Value: !Sub "${{ProjectName}}-instance"
              - Key: Environment
                Value: !Ref Environment
        UserData:
          Fn::Base64: !Sub |
            #!/bin/bash
            yum update -y
            # Application setup commands here
  
  # Auto Scaling Group
  AppAutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub "${{ProjectName}}-asg"
      VPCZoneIdentifier:
        - !Ref PrivateSubnet1{subnet_config}
      LaunchTemplate:
        LaunchTemplateId: !Ref AppLaunchTemplate
        Version: !GetAtt AppLaunchTemplate.LatestVersionNumber
      MinSize: 1
      MaxSize: {3 if security_level == "high" else 2}
      DesiredCapacity: {2 if security_level == "high" else 1}
      TargetGroupARNs:
        - !Ref ALBTargetGroup
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-asg"
          PropagateAtLaunch: false
        - Key: Environment
          Value: !Ref Environment
          PropagateAtLaunch: false
  
  # IAM Role for EC2 instances
  AppInstanceRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${{ProjectName}}-app-role"
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: !Sub "${{ProjectName}}-app-policy"
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                  - s3:DeleteObject
                Resource: !Sub "${{MainS3Bucket}}/*"
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                Resource: !Ref DatabaseSecret
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-app-role"
        - Key: Environment
          Value: !Ref Environment
  
  AppInstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      InstanceProfileName: !Sub "${{ProjectName}}-app-profile"
      Roles:
        - !Ref AppInstanceRole'''

        if security_level in ["medium", "high"]:
            ec2_template += '''
  
  # Key Pair for SSH access
  EC2KeyPair:
    Type: AWS::EC2::KeyPair
    Properties:
      KeyName: !Sub "${ProjectName}-key"
      # Note: You'll need to provide the public key material
      Tags:
        - Key: Name
          Value: !Sub "${ProjectName}-key"
        - Key: Environment
          Value: !Ref Environment'''
        
        return ec2_template
    
    def _generate_cf_ecs(self, project_name: str, security_level: str) -> str:
        container_insights = '''
      ClusterSettings:
        - Name: containerInsights
          Value: enabled''' if security_level in ["medium", "high"] else ""
        
        subnet_config = '''
            - !Ref PrivateSubnet2''' if security_level == "high" else ""
        
        return f'''  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub "${{ProjectName}}-cluster"{container_insights}
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-cluster"
        - Key: Environment
          Value: !Ref Environment
  
  # ECS Task Definition
  ECSTaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub "${{ProjectName}}-app"
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      Cpu: 256
      Memory: 512
      ExecutionRoleArn: !GetAtt ECSExecutionRole.Arn
      TaskRoleArn: !GetAtt ECSTaskRole.Arn
      ContainerDefinitions:
        - Name: !Sub "${{ProjectName}}-container"
          Image: nginx:latest
          PortMappings:
            - ContainerPort: 80
              Protocol: tcp
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref ECSLogGroup
              awslogs-region: !Ref "AWS::Region"
              awslogs-stream-prefix: ecs
          Environment:
            - Name: ENVIRONMENT
              Value: !Ref Environment
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-task"
        - Key: Environment
          Value: !Ref Environment
  
  # ECS Service
  ECSService:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: !Sub "${{ProjectName}}-service"
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref ECSTaskDefinition
      DesiredCount: {2 if security_level == "high" else 1}
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets:
            - !Ref PrivateSubnet1{subnet_config}
          SecurityGroups:
            - !Ref ECSSecurityGroup
          AssignPublicIp: DISABLED
      LoadBalancers:
        - TargetGroupArn: !Ref ALBTargetGroup
          ContainerName: !Sub "${{ProjectName}}-container"
          ContainerPort: 80
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-service"
        - Key: Environment
          Value: !Ref Environment
  
  # ECS IAM Roles
  ECSExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${{ProjectName}}-ecs-execution-role"
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-ecs-execution-role"
        - Key: Environment
          Value: !Ref Environment
  
  ECSTaskRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${{ProjectName}}-ecs-task-role"
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-ecs-task-role"
        - Key: Environment
          Value: !Ref Environment
  
  # ECS Security Group
  ECSSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${{ProjectName}}-ecs-sg"
      GroupDescription: Security group for ECS tasks
      VpcId: !Ref MainVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref ALBSecurityGroup
          Description: Container port from ALB
      SecurityGroupEgress:
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0
          Description: All outbound traffic
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-ecs-sg"
        - Key: Environment
          Value: !Ref Environment
  
  # CloudWatch Log Group for ECS
  ECSLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/ecs/${{ProjectName}}"
      RetentionInDays: 30
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-ecs-logs"
        - Key: Environment
          Value: !Ref Environment'''
    
    def _generate_cf_database(self, project_name: str, services: Dict[str, str], security_level: str) -> str:
        db_engine = services.get('database', 'mysql')
        multi_az = security_level == "high"
        
        kms_encryption = '''
      KmsKeyId: !Ref MainKMSKey''' if security_level == "high" else ""
        
        backup_retention = 7 if security_level in ["medium", "high"] else 1
        
        monitoring_config = '''
      EnableCloudwatchLogsExports:
        - error
        - general
        - slow-query''' if security_level in ["medium", "high"] else ""
        
        subnet_config = '''
        - !Ref PrivateSubnet2''' if multi_az else ""
        
        return f'''  # RDS Database
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupName: !Sub "${{ProjectName}}-db-subnet-group"
      DBSubnetGroupDescription: Subnet group for database
      SubnetIds:
        - !Ref PrivateSubnet1{subnet_config}
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-db-subnet-group"
        - Key: Environment
          Value: !Ref Environment
  
  MainDatabase:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    Properties:
      DBInstanceIdentifier: !Sub "${{ProjectName}}-database"
      Engine: {db_engine.lower()}
      EngineVersion: {self._get_db_version(db_engine)}
      DBInstanceClass: db.t3.micro
      AllocatedStorage: 20
      MaxAllocatedStorage: 100
      StorageType: gp2
      StorageEncrypted: true{kms_encryption}
      DBName: !Sub "${{ProjectName}}"
      MasterUsername: admin
      ManageMasterUserPassword: true
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup
      DBSubnetGroupName: !Ref DBSubnetGroup
      BackupRetentionPeriod: {backup_retention}
      PreferredBackupWindow: "03:00-04:00"
      PreferredMaintenanceWindow: "sun:04:00-sun:05:00"
      MultiAZ: {str(multi_az).lower()}
      PubliclyAccessible: false
      DeletionProtection: !Ref EnableDeletionProtection{monitoring_config}
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-database"
        - Key: Environment
          Value: !Ref Environment'''
    
    def _generate_cf_s3(self, project_name: str, security_level: str) -> str:
        kms_encryption = '''
            KMSMasterKeyID: !Ref MainKMSKey
            SSEAlgorithm: aws:kms''' if security_level == "high" else '''
            SSEAlgorithm: AES256'''
        
        logging_config = '''
  
  MainS3BucketLogging:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${ProjectName}-logs-${AWS::AccountId}-${AWS::Region}"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:''' + kms_encryption + '''
            BucketKeyEnabled: true
      Tags:
        - Key: Name
          Value: !Sub "${ProjectName}-logs"
        - Key: Environment
          Value: !Ref Environment
  
  S3BucketLoggingConfig:
    Type: AWS::S3::Bucket
    Properties:
      LoggingConfiguration:
        DestinationBucketName: !Ref MainS3BucketLogging
        LogFilePrefix: access-logs/''' if security_level in ["medium", "high"] else ""
        
        return f'''  # S3 Bucket
  MainS3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${{ProjectName}}-storage-${{AWS::AccountId}}-${{AWS::Region}}"
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:{kms_encryption}
            BucketKeyEnabled: true
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      VersioningConfiguration:
        Status: Enabled
      LifecycleConfiguration:
        Rules:
          - Id: lifecycle
            Status: Enabled
            ExpirationInDays: 90
            NoncurrentVersionExpirationInDays: 30
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-storage"
        - Key: Environment
          Value: !Ref Environment{logging_config}'''
    
    def _generate_cf_monitoring(self, project_name: str) -> str:
        return f'''  # CloudWatch Log Group
  AppLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/aws/application/${{ProjectName}}"
      RetentionInDays: 30
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-logs"
        - Key: Environment
          Value: !Ref Environment
  
  # CloudWatch Alarms
  HighCPUAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${{ProjectName}}-high-cpu"
      AlarmDescription: This metric monitors high CPU utilization
      ComparisonOperator: GreaterThanThreshold
      EvaluationPeriods: 2
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Period: 120
      Statistic: Average
      Threshold: 80
      Dimensions:
        - Name: AutoScalingGroupName
          Value: !Ref AppAutoScalingGroup
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-cpu-alarm"
        - Key: Environment
          Value: !Ref Environment
  
  # SNS Topic for Alerts
  AlertsTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub "${{ProjectName}}-alerts"
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-alerts"
        - Key: Environment
          Value: !Ref Environment'''
    
    def _generate_cf_logging(self, project_name: str) -> str:
        return f'''  # CloudTrail for Audit Logging
  MainCloudTrail:
    Type: AWS::CloudTrail::Trail
    Properties:
      TrailName: !Sub "${{ProjectName}}-trail"
      S3BucketName: !Ref CloudTrailLogsBucket
      S3KeyPrefix: cloudtrail
      IncludeGlobalServiceEvents: true
      IsMultiRegionTrail: true
      EnableLogFileValidation: true
      EventSelectors:
        - ReadWriteType: All
          IncludeManagementEvents: true
          DataResources:
            - Type: AWS::S3::Object
              Values:
                - !Sub "${{MainS3Bucket}}/*"
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-trail"
        - Key: Environment
          Value: !Ref Environment
  
  # S3 Bucket for CloudTrail Logs
  CloudTrailLogsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${{ProjectName}}-cloudtrail-${{AWS::AccountId}}-${{AWS::Region}}"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-cloudtrail-logs"
        - Key: Environment
          Value: !Ref Environment
  
  CloudTrailBucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref CloudTrailLogsBucket
      PolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Sid: AWSCloudTrailAclCheck
            Effect: Allow
            Principal:
              Service: cloudtrail.amazonaws.com
            Action: s3:GetBucketAcl
            Resource: !GetAtt CloudTrailLogsBucket.Arn
          - Sid: AWSCloudTrailWrite
            Effect: Allow
            Principal:
              Service: cloudtrail.amazonaws.com
            Action: s3:PutObject
            Resource: !Sub "${{CloudTrailLogsBucket.Arn}}/cloudtrail/*"
            Condition:
              StringEquals:
                's3:x-amz-acl': bucket-owner-full-control'''
    
    def _generate_cf_outputs(self) -> str:
        return '''Outputs:
  VPCId:
    Description: ID of the VPC
    Value: !Ref MainVPC
    Export:
      Name: !Sub "${AWS::StackName}-VPC-ID"
  
  LoadBalancerDNS:
    Description: DNS name of the load balancer
    Value: !GetAtt MainALB.DNSName
    Export:
      Name: !Sub "${AWS::StackName}-ALB-DNS"
    Condition: LoadBalancerExists
  
  S3BucketName:
    Description: Name of the S3 bucket
    Value: !Ref MainS3Bucket
    Export:
      Name: !Sub "${AWS::StackName}-S3-Bucket"
  
  DatabaseEndpoint:
    Description: Database endpoint
    Value: !GetAtt MainDatabase.Endpoint.Address
    Export:
      Name: !Sub "${AWS::StackName}-DB-Endpoint"
    Condition: DatabaseExists
  
  ApiGatewayURL:
    Description: API Gateway URL
    Value: !Sub "https://${ApiGateway}.execute-api.${AWS::Region}.amazonaws.com/${Environment}"
    Export:
      Name: !Sub "${AWS::StackName}-API-URL"
    Condition: ApiGatewayExists

Conditions:
  LoadBalancerExists: !Not [!Equals [!Ref MainALB, ""]]
  DatabaseExists: !Not [!Equals [!Ref MainDatabase, ""]]
  ApiGatewayExists: !Not [!Equals [!Ref ApiGateway, ""]]'''
    
    def _generate_cf_lambda(self, project_name: str, security_level: str) -> str:
        kms_config = '''
      KmsKeyArn: !GetAtt MainKMSKey.Arn''' if security_level == "high" else ""
        
        subnet_config = '''
          - !Ref PrivateSubnet2''' if security_level == "high" else ""
        
        lambda_code = '''import json
          def handler(event, context):
              return {
                  'statusCode': 200,
                  'body': json.dumps('Hello from Lambda!')
              }'''
        
        return f'''  # Lambda Function for API Backend
  ApiLambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${{ProjectName}}-api"
      Runtime: python3.9
      Handler: index.handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Code:
        ZipFile: |
          {lambda_code}
      Timeout: 30{kms_config}
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment
      VpcConfig:
        SubnetIds:
          - !Ref PrivateSubnet1{subnet_config}
        SecurityGroupIds:
          - !Ref LambdaSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-lambda"
        - Key: Environment
          Value: !Ref Environment
  
  # API Gateway
  ApiGateway:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: !Sub "${{ProjectName}}-api"
      Description: !Sub "API Gateway for ${{ProjectName}}"
      EndpointConfiguration:
        Types:
          - REGIONAL
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-api"
        - Key: Environment
          Value: !Ref Environment
  
  ApiGatewayResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref ApiGateway
      ParentId: !GetAtt ApiGateway.RootResourceId
      PathPart: "{{proxy+}}"
  
  ApiGatewayMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref ApiGateway
      ResourceId: !Ref ApiGatewayResource
      HttpMethod: ANY
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub "arn:aws:apigateway:${{AWS::Region}}:lambda:path/2015-03-31/functions/${{ApiLambdaFunction.Arn}}/invocations"
  
  ApiGatewayDeployment:
    Type: AWS::ApiGateway::Deployment
    DependsOn:
      - ApiGatewayMethod
    Properties:
      RestApiId: !Ref ApiGateway
      StageName: !Ref Environment
  
  # Lambda IAM Role
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${{ProjectName}}-lambda-role"
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-lambda-role"
        - Key: Environment
          Value: !Ref Environment
  
  # Lambda Security Group
  LambdaSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "${{ProjectName}}-lambda-sg"
      GroupDescription: Security group for Lambda functions
      VpcId: !Ref MainVPC
      SecurityGroupEgress:
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0
          Description: All outbound traffic
      Tags:
        - Key: Name
          Value: !Sub "${{ProjectName}}-lambda-sg"
        - Key: Environment
          Value: !Ref Environment'''
    
    def _generate_enhanced_terraform_security_groups(self, project_name: str, services: Dict[str, str], security_level: str) -> str:
        """Generate enhanced security groups with comprehensive rules"""
        return self.enhanced_security.generate_enhanced_security_groups(project_name, services, security_level)
    
    def _generate_terraform_nacls(self, project_name: str, security_level: str) -> str:
        """Generate Network ACLs for additional layer of security"""
        return self.enhanced_security.generate_network_acls(project_name, security_level)
    
    def _generate_enhanced_terraform_waf(self, project_name: str, security_level: str) -> str:
        """Generate enhanced WAF with advanced rules and protections"""
        return self.enhanced_security.generate_enhanced_waf_configuration(project_name, security_level)
    
    def _generate_enhanced_terraform_monitoring(self, project_name: str, security_level: str) -> str:
        """Generate enhanced monitoring with comprehensive security metrics"""
        return self.enhanced_security.generate_enhanced_monitoring_configuration(project_name, security_level)
    
    def _generate_enhanced_terraform_logging(self, project_name: str, security_level: str) -> str:
        """Generate enhanced logging with comprehensive audit capabilities"""
        return self.enhanced_security.generate_enhanced_logging_configuration(project_name, security_level)
    
    def _generate_terraform_guardduty(self, project_name: str) -> str:
        """Generate GuardDuty threat detection"""
        return self.enhanced_security.generate_guardduty_configuration(project_name)
    
    def _generate_terraform_security_hub(self, project_name: str) -> str:
        """Generate Security Hub configuration"""
        return self.enhanced_security.generate_security_hub_configuration(project_name)
    
    def _generate_terraform_config(self, project_name: str) -> str:
        """Generate AWS Config for compliance monitoring"""
        return self.enhanced_security.generate_config_configuration(project_name)
    
    def _generate_terraform_inspector(self, project_name: str) -> str:
        """Generate Inspector for vulnerability assessments"""
        return self.enhanced_security.generate_inspector_configuration(project_name)
    
    def _generate_terraform_macie(self, project_name: str) -> str:
        """Generate Macie for data security"""
        return self.enhanced_security.generate_macie_configuration(project_name)
    
    def _generate_terraform_cloudhsm(self, project_name: str) -> str:
        """Generate CloudHSM for FIPS compliance"""
        return self.enhanced_security.generate_cloudhsm_configuration(project_name)
    
    def _generate_terraform_compliance_controls(self, project_name: str, compliance_frameworks: List[str]) -> str:
        """Generate compliance-specific controls"""
        return self.enhanced_security.generate_compliance_controls(project_name, compliance_frameworks)