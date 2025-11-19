terraform {
  required_version = ">= 1.0"
  
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

  # Uncomment and configure for remote state management
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "prod/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-state-lock"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}

locals {
  project_name = "wedding-gallery"
  environment  = "prod"
  
  common_tags = {
    Project     = local.project_name
    Environment = local.environment
    ManagedBy   = "Terraform"
  }

  # Get availability zones
  availability_zones = data.aws_availability_zones.available.names
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# VPC Module
module "vpc" {
  source = "../../modules/vpc"

  project_name      = local.project_name
  environment       = local.environment
  vpc_cidr          = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones = slice(local.availability_zones, 0, length(var.public_subnet_cidrs))
  tags              = local.common_tags
}

# S3 Module
module "s3" {
  source = "../../modules/s3"

  project_name  = local.project_name
  environment   = local.environment
  allowed_origins = var.s3_allowed_origins
  enable_versioning = true
  enable_glacier = true
  transition_to_ia_days = 90
  transition_to_glacier_days = 365
  tags          = local.common_tags
}

# ECR Module
module "ecr" {
  source = "../../modules/ecr"

  project_name        = local.project_name
  environment         = local.environment
  image_retention_count = 20
  tags                = local.common_tags
}

# EC2 Module (security group created here, used by RDS)
module "ec2" {
  source = "../../modules/ec2"

  project_name           = local.project_name
  environment            = local.environment
  vpc_id                 = module.vpc.vpc_id
  subnet_id              = module.vpc.public_subnet_ids[0]
  ami_id                 = data.aws_ami.ubuntu.id
  instance_type          = var.ec2_instance_type
  s3_bucket_arn          = module.s3.bucket_arn
  key_pair_name          = var.key_pair_name
  public_key             = var.public_key
  ssh_allowed_cidrs      = var.ssh_allowed_cidrs
  associate_public_ip    = true
  user_data              = var.ec2_user_data
  tags                   = local.common_tags
}

# RDS Module
module "rds" {
  source = "../../modules/rds"

  project_name          = local.project_name
  environment           = local.environment
  vpc_id                = module.vpc.vpc_id
  subnet_ids            = module.vpc.private_subnet_ids
  app_security_group_id = module.ec2.security_group_id
  instance_class        = var.rds_instance_class
  allocated_storage     = var.rds_allocated_storage
  max_allocated_storage = var.rds_max_allocated_storage
  skip_final_snapshot   = false
  deletion_protection   = true
  multi_az              = true
  performance_insights_enabled = true
  backup_retention_period = 30
  tags                  = local.common_tags
}

resource "aws_iam_role_policy" "ec2_rds_secret" {
  name = "${local.project_name}-${local.environment}-ec2-rds-secret-policy"
  role = module.ec2.iam_role_name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = module.rds.db_password_secret_arn
      }
    ]
  })
}

