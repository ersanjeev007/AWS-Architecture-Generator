# Terraform configuration for project-1
# Generated with security best practices

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      CreatedBy   = "AWS-Architecture-Generator"
    }
  }
}

# Variables
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
}

variable "services" {
  description = "Map of services to enable"
  type        = map(string)
  default     = {}
}

variable "enable_bastion" {
  description = "Enable bastion host for secure access"
  type        = bool
  default     = false
}

variable "allowed_ssh_cidrs" {
  description = "CIDR blocks allowed for SSH access"
  type        = list(string)
  default     = ["10.0.0.0/8"]
}

variable "enable_scp" {
  description = "Enable Service Control Policies"
  type        = bool
  default     = false
}

# Data Sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# Random ID for unique resource naming
resource "random_id" "suffix" {
  byte_length = 4
}

# KMS Key for encryption
resource "aws_kms_key" "main" {
  description             = "KMS key for project-1"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      }
    ]
  })
  
  tags = {
    Name = "${var.project_name}-kms-key"
  }
}

resource "aws_kms_alias" "main" {
  name          = "alias/${var.project_name}-key-${random_id.suffix.hex}"
  target_key_id = aws_kms_key.main.key_id
}

# Use Default VPC to avoid VPC limits
data "aws_vpc" "main" {
  default = true
}

# Get default subnets
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
}

data "aws_subnet" "default" {
  count = length(data.aws_subnets.default.ids)
  id    = data.aws_subnets.default.ids[count.index]
}

# Use default subnets for both public and private
locals {
  # Use existing default subnets (they're all public by default)
  public_subnet_ids = data.aws_subnets.default.ids
  private_subnet_ids = data.aws_subnets.default.ids  # Same as public for simplicity
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = data.aws_vpc.main.id
  
  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = data.aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "${var.project_name}-public-${count.index + 1}"
    Type = "public"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = data.aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "${var.project_name}-private-${count.index + 1}"
    Type = "private"
  }
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = data.aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Single NAT Gateway for cost efficiency and EIP limit compliance
resource "aws_eip" "nat" {
  domain = "vpc"
  
  depends_on = [aws_internet_gateway.main]
  
  tags = {
    Name = "${var.project_name}-nat-eip"
  }
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id
  
  tags = {
    Name = "${var.project_name}-nat-gw"
  }
}

# Single route table for all private subnets
resource "aws_route_table" "private" {
  vpc_id = data.aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }
  
  tags = {
    Name = "${var.project_name}-private-rt"
  }
}

resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}


# Enhanced Security Groups with Least Privilege Access
# Generated for security level: basic

# Web tier security group
resource "aws_security_group" "web_tier" {
  name_prefix = "project-1-web-"
  description = "Security group for web tier with enhanced controls"
  vpc_id      = data.aws_vpc.main.id

  # HTTPS traffic
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP traffic (redirect to HTTPS)
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "project-1-web-sg"
    Environment = var.environment
    Tier        = "web"
  }
}

# Application tier security group
resource "aws_security_group" "app_tier" {
  name_prefix = "project-1-app-"
  description = "Security group for application tier"
  vpc_id      = data.aws_vpc.main.id

  # Allow traffic from web tier
  ingress {
    description     = "App traffic from web tier"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.web_tier.id]
  }

  # Allow traffic from ALB (using VPC CIDR to avoid circular dependency)
  ingress {
    description = "App traffic from ALB"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.main.cidr_block]
  }

  # Outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "project-1-app-sg"
    Environment = var.environment
    Tier        = "application"
  }
}

# Database tier security group
resource "aws_security_group" "db_tier" {
  name_prefix = "project-1-db-"
  description = "Security group for database tier"
  vpc_id      = data.aws_vpc.main.id

  # MySQL/Aurora
  ingress {
    description     = "MySQL/Aurora"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.app_tier.id]
  }

  # PostgreSQL
  ingress {
    description     = "PostgreSQL"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app_tier.id]
  }

  # Redis
  ingress {
    description     = "Redis"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.app_tier.id]
  }

  # No outbound rules - databases shouldn't initiate connections
  tags = {
    Name        = "project-1-db-sg"
    Environment = var.environment
    Tier        = "database"
  }
}

# ALB security group
resource "aws_security_group" "alb" {
  name_prefix = "project-1-alb-"
  description = "Security group for Application Load Balancer"
  vpc_id      = data.aws_vpc.main.id

  # HTTPS traffic
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP traffic
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "project-1-alb-sg"
    Environment = var.environment
    Type        = "load-balancer"
  }
}


# Lambda security group (if using VPC Lambda)
resource "aws_security_group" "lambda" {
  count       = length(keys(var.services)) > 0 && contains(keys(var.services), "lambda") ? 1 : 0
  name_prefix = "project-1-lambda-"
  description = "Security group for Lambda functions"
  vpc_id      = data.aws_vpc.main.id

  # Outbound traffic for Lambda
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS outbound"
  }

  egress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.db_tier.id]
    description     = "MySQL access"
  }

  egress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.db_tier.id]
    description     = "PostgreSQL access"
  }

  tags = {
    Name        = "project-1-lambda-sg"
    Environment = var.environment
    Type        = "lambda"
  }
}

# Bastion host security group (for secure access)
resource "aws_security_group" "bastion" {
  count       = try(var.enable_bastion, false) ? 1 : 0
  name_prefix = "project-1-bastion-"
  description = "Security group for bastion host"
  vpc_id      = data.aws_vpc.main.id

  # SSH access from specific IP ranges
  ingress {
    description = "SSH from office"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = try(var.allowed_ssh_cidrs, ["10.0.0.0/8"])
  }

  # Outbound SSH to private subnets
  egress {
    description = "SSH to private instances"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [for subnet in aws_subnet.private : subnet.cidr_block]
  }

  tags = {
    Name        = "project-1-bastion-sg"
    Environment = var.environment
    Type        = "bastion"
  }
}



# Network ACLs for Additional Security Layer
# Security Level: basic

# Public subnet NACL (for web tier)
resource "aws_network_acl" "public" {
  vpc_id = data.aws_vpc.main.id
  
  # Allow HTTP inbound
  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 80
    to_port    = 80
  }
  
  # Allow HTTPS inbound
  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }
  
  # Allow ephemeral ports inbound (for return traffic)
  ingress {
    protocol   = "tcp"
    rule_no    = 120
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }
  
  # Allow SSH from management network (if enabled)
  ingress {
    protocol   = "tcp"
    rule_no    = 130
    action     = "allow"
    cidr_block = "10.0.0.0/8"
    from_port  = 22
    to_port    = 22
  }
  
  # Allow all outbound traffic
  egress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 80
    to_port    = 80
  }
  
  egress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }
  
  egress {
    protocol   = "tcp"
    rule_no    = 120
    action     = "allow"
    cidr_block = "10.0.0.0/16"
    from_port  = 8080
    to_port    = 8080
  }
  
  egress {
    protocol   = "tcp"
    rule_no    = 130
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }
  
  tags = {
    Name        = "project-1-public-nacl"
    Environment = var.environment
    Tier        = "public"
  }
}

# Private subnet NACL (for app tier)
resource "aws_network_acl" "private" {
  vpc_id = data.aws_vpc.main.id
  
  # Allow traffic from public subnet
  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = aws_subnet.public[0].cidr_block
    from_port  = 8080
    to_port    = 8080
  }
  
  # Additional ingress rules for multi-AZ if needed
  dynamic "ingress" {
    for_each = length(aws_subnet.public) > 1 ? [aws_subnet.public[1]] : []
    content {
      protocol   = "tcp"
      rule_no    = 110
      action     = "allow"
      cidr_block = ingress.value.cidr_block
      from_port  = 8080
      to_port    = 8080
    }
  }
  
  # Allow HTTPS outbound
  egress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }
  
  # Allow database connections
  egress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = aws_subnet.private[0].cidr_block
    from_port  = 3306
    to_port    = 3306
  }
  
  # Additional egress rules for multi-AZ if needed  
  dynamic "egress" {
    for_each = length(aws_subnet.private) > 1 ? [aws_subnet.private[1]] : []
    content {
      protocol   = "tcp"
      rule_no    = 120
      action     = "allow"
      cidr_block = egress.value.cidr_block
      from_port  = 3306
      to_port    = 3306
    }
  }
  
  egress {
    protocol   = "tcp"
    rule_no    = 130
    action     = "allow"
    cidr_block = aws_subnet.private[0].cidr_block
    from_port  = 5432
    to_port    = 5432
  }
  
  dynamic "egress" {
    for_each = length(aws_subnet.private) > 1 ? [aws_subnet.private[1]] : []
    content {
      protocol   = "tcp"
      rule_no    = 140
      action     = "allow"
      cidr_block = egress.value.cidr_block
      from_port  = 5432
      to_port    = 5432
    }
  }
  
  # Allow ephemeral ports
  egress {
    protocol   = "tcp"
    rule_no    = 150
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }
  
  tags = {
    Name        = "project-1-private-nacl"
    Environment = var.environment
    Tier        = "private"
  }
}

# Associate NACLs with subnets
resource "aws_network_acl_association" "public" {
  count          = length(aws_subnet.public)
  network_acl_id = aws_network_acl.public.id
  subnet_id      = aws_subnet.public[count.index].id
}

resource "aws_network_acl_association" "private" {
  count          = length(aws_subnet.private)
  network_acl_id = aws_network_acl.private.id
  subnet_id      = aws_subnet.private[count.index].id
}


# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb-${random_id.suffix.hex}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = local.public_subnet_ids
  
  enable_deletion_protection = var.enable_deletion_protection
  
  
  
  tags = {
    Name = "${var.project_name}-alb"
  }
}

resource "aws_lb_target_group" "app" {
  name     = "${var.project_name}-tg-${random_id.suffix.hex}"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.main.id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
  
  tags = {
    Name = "${var.project_name}-tg"
  }
}

resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# Launch Template
resource "aws_launch_template" "app" {
  name_prefix   = "${var.project_name}-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  
  vpc_security_group_ids = [aws_security_group.app_tier.id]
  
  
  
  iam_instance_profile {
    name = aws_iam_instance_profile.app.name
  }
  
  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size = 20
      volume_type = "gp3"
      encrypted   = true
      
      delete_on_termination = true
    }
  }
  
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
    http_put_response_hop_limit = 1
  }
  
  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.project_name}-instance"
    }
  }
  
  user_data = base64encode(<<-EOF
#!/bin/bash
yum update -y
yum install -y amazon-cloudwatch-agent
echo "Project: ${var.project_name}" > /home/ec2-user/project_info.txt
EOF
  )
}

# Auto Scaling Group
resource "aws_autoscaling_group" "app" {
  name                = "${var.project_name}-asg-${random_id.suffix.hex}"
  vpc_zone_identifier = local.private_subnet_ids
  target_group_arns   = [aws_lb_target_group.app.arn]
  health_check_type   = "ELB"
  health_check_grace_period = 300
  
  min_size         = 1
  max_size         = 2
  desired_capacity = 1
  
  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }
  
  tag {
    key                 = "Name"
    value               = "${var.project_name}-asg"
    propagate_at_launch = false
  }
}

# IAM Role for EC2 instances
resource "aws_iam_role" "app" {
  name = "${var.project_name}-app-role-${random_id.suffix.hex}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_instance_profile" "app" {
  name = "${var.project_name}-app-profile-${random_id.suffix.hex}"
  role = aws_iam_role.app.name
}

resource "aws_iam_role_policy" "app" {
  name = "${var.project_name}-app-policy-${random_id.suffix.hex}"
  role = aws_iam_role.app.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.main.arn}/*"
      }
    ]
  })
}

# AMI Data Source
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# RDS Database
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group-${random_id.suffix.hex}"
  subnet_ids = local.private_subnet_ids
  
  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-database-${random_id.suffix.hex}"
  
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true
  
  
  db_name  = "${replace(var.project_name, "-", "")}"
  username = "admin"
  manage_master_user_password = true
  
  
  vpc_security_group_ids = [aws_security_group.db_tier.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 1
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  multi_az               = true
  publicly_accessible    = false
  
  skip_final_snapshot = false
  final_snapshot_identifier = "${var.project_name}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
  
  deletion_protection = var.enable_deletion_protection
  
  
  
  tags = {
    Name = "${var.project_name}-database"
  }
}

# S3 Bucket
resource "aws_s3_bucket" "main" {
  bucket = "${var.project_name}-storage-${random_id.bucket_suffix.hex}"
  
  tags = {
    Name = "${var.project_name}-storage"
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# S3 Bucket Configuration
resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id
  
  rule {
    apply_server_side_encryption_by_default {
      
      sse_algorithm     = "AES256"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "main" {
  bucket = aws_s3_bucket.main.id
  
  rule {
    id     = "lifecycle"
    status = "Enabled"
    
    expiration {
      days = 90
    }
    
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}



# Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = data.aws_vpc.main.id
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

