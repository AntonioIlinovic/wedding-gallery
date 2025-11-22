output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "s3_bucket_id" {
  description = "S3 bucket ID for photos"
  value       = module.s3.bucket_id
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = module.s3.bucket_arn
}

output "ecr_backend_repository_url" {
  description = "ECR backend repository URL"
  value       = module.ecr.backend_repository_url
}

output "ecr_frontend_repository_url" {
  description = "ECR frontend repository URL"
  value       = module.ecr.frontend_repository_url
}

output "ec2_instance_id" {
  description = "EC2 instance ID"
  value       = module.ec2.instance_id
}

output "ec2_public_ip" {
  description = "EC2 instance Elastic IP (public IP)"
  value       = module.ec2.elastic_ip
}

output "ec2_public_dns" {
  description = "EC2 instance public DNS"
  value       = module.ec2.instance_public_dns
}

# RDS Outputs (disabled while RDS module is turned off)
# TODO: When re-enabling the RDS module in main.tf, also uncomment these
#       outputs so that the database connection details and password secret
#       ARN are available in terraform outputs.
/*
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.db_instance_endpoint
}

output "rds_address" {
  description = "RDS instance address"
  value       = module.rds.db_instance_address
}

output "db_password_secret_arn" {
  description = "ARN of the secret containing the database password"
  value       = module.rds.db_password_secret_arn
  sensitive   = true
}
*/

