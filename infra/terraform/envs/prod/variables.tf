variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.1.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.1.1.0/24", "10.1.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.1.10.0/24", "10.1.20.0/24"]
}

variable "s3_allowed_origins" {
  description = "Allowed origins for S3 CORS (should be your domain in production)"
  type        = list(string)
  # Example: ["https://yourdomain.com", "https://www.yourdomain.com"]
}

variable "ec2_instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.small"
}

variable "rds_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 100
}

variable "rds_max_allocated_storage" {
  description = "RDS maximum allocated storage in GB (for autoscaling)"
  type        = number
  default     = 500
}

variable "key_pair_name" {
  description = "Name of existing AWS key pair for SSH access"
  type        = string
}

variable "public_key" {
  description = "Public SSH key (required if key_pair_name is null)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "ssh_allowed_cidrs" {
  description = "CIDR blocks allowed to SSH to EC2 instance (restrict in production!)"
  type        = list(string)
}

variable "ec2_user_data" {
  description = "User data script for EC2 instance"
  type        = string
  default     = ""
}

