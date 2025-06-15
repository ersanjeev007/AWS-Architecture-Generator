from typing import Dict
from app.schemas.questionnaire import QuestionnaireRequest

class TemplateGenerator:
    """Generate Infrastructure as Code templates"""
    
    def generate_terraform_template(self, questionnaire: QuestionnaireRequest, services: Dict[str, str]) -> str:
        project_name_clean = questionnaire.project_name.lower().replace(' ', '-').replace('_', '-')
        
        template = f'''# Terraform configuration for {questionnaire.project_name}
terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = var.aws_region
}}

variable "aws_region" {{
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}}

variable "environment" {{
  description = "Environment name"
  type        = string
  default     = "dev"
}}

# VPC
resource "aws_vpc" "main" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = {{
    Name = "{project_name_clean}-vpc"
    Environment = var.environment
  }}
}}

# Internet Gateway
resource "aws_internet_gateway" "main" {{
  vpc_id = aws_vpc.main.id
  tags = {{
    Name = "{project_name_clean}-igw"
  }}
}}

# Public Subnets
resource "aws_subnet" "public" {{
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${{count.index + 1}}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags = {{
    Name = "{project_name_clean}-public-${{count.index + 1}}"
  }}
}}

# Security Group
resource "aws_security_group" "web" {{
  name_prefix = "{project_name_clean}-web-"
  vpc_id      = aws_vpc.main.id

  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  ingress {{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
}}

# S3 Bucket
resource "aws_s3_bucket" "main" {{
  bucket = "{project_name_clean}-storage-${{random_id.bucket_suffix.hex}}"
}}

resource "random_id" "bucket_suffix" {{
  byte_length = 4
}}

resource "aws_s3_bucket_encryption_configuration" "main" {{
  bucket = aws_s3_bucket.main.id
  rule {{
    apply_server_side_encryption_by_default {{
      sse_algorithm = "AES256"
    }}
  }}
}}

resource "aws_s3_bucket_public_access_block" "main" {{
  bucket = aws_s3_bucket.main.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}

data "aws_availability_zones" "available" {{
  state = "available"
}}

# Outputs
output "vpc_id" {{
  value = aws_vpc.main.id
}}

output "s3_bucket_name" {{
  value = aws_s3_bucket.main.bucket
}}'''

        return template

    def generate_cloudformation_template(self, questionnaire: QuestionnaireRequest, services: Dict[str, str]) -> str:
        project_name_clean = questionnaire.project_name.replace(' ', '')
        
        template = f'''AWSTemplateFormatVersion: '2010-09-09'
Description: 'CloudFormation template for {questionnaire.project_name}'

Parameters:
  Environment:
    Type: String
    Default: dev
    Description: Environment name

Resources:
  MainVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: {project_name_clean}VPC

  MainIGW:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: {project_name_clean}IGW

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref MainVPC
      InternetGatewayId: !Ref MainIGW

  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MainVPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: {project_name_clean}PublicSubnet1

  WebSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for {questionnaire.project_name}
      VpcId: !Ref MainVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0

  MainS3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref MainVPC
  
  S3BucketName:
    Description: S3 Bucket Name
    Value: !Ref MainS3Bucket'''

        return template