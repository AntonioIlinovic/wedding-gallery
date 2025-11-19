# Terraform Infrastructure as Code

This directory contains Terraform modules and environment configurations for provisioning AWS infrastructure for the wedding gallery application.

## Structure

```
terraform/
├── modules/          # Reusable Terraform modules
│   ├── vpc/         # VPC, subnets, NAT gateways, etc.
│   ├── s3/          # S3 bucket for photo storage
│   ├── ecr/         # ECR repositories for container images
│   ├── rds/         # RDS PostgreSQL database
│   └── ec2/         # EC2 instance for compute
└── envs/            # Environment-specific configurations
    └── prod/        # Production environment
```

**Note:** Development is done locally using `docker-compose.yml` at the project root. Only production infrastructure is managed via Terraform.

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** >= 1.0 installed
3. **AWS Account** with appropriate permissions

## Required AWS Permissions

The AWS credentials need permissions to create:
- VPC, Subnets, Internet Gateways, NAT Gateways, Route Tables
- EC2 Instances, Security Groups, Key Pairs
- RDS Instances, DB Subnet Groups
- S3 Buckets
- ECR Repositories
- IAM Roles and Policies
- Secrets Manager Secrets

## Quick Start

### 1. Configure AWS Credentials

```bash
aws configure
```

### 2. Navigate to Production Environment Directory

```bash
cd envs/prod
```

### 3. Configure Variables

Copy the example variables file and edit it:
```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

**Important variables to set:**
- `key_pair_name` or `public_key` for SSH access
- `ssh_allowed_cidrs` (restrict to your IP address!)
- `s3_allowed_origins` (specify your domain)
  - **Production Domain:** [weddinggallery.site](http://weddinggallery.site/)

### 4. Initialize Terraform

```bash
terraform init
```

### 5. Review Plan

```bash
terraform plan
```

### 6. Apply Configuration

```bash
terraform apply
```

## Remote State (Recommended)

Configure remote state in `main.tf` to store Terraform state securely:

```hcl
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

## Modules

### VPC Module

Creates a VPC with public and private subnets, internet gateway, and NAT gateways.

**Outputs:**
- `vpc_id`
- `public_subnet_ids`
- `private_subnet_ids`

### S3 Module

Creates an S3 bucket for photo storage with:
- CORS configuration for direct browser uploads
- Lifecycle rules for cost optimization
- Server-side encryption
- Public access blocked (uses presigned URLs)

**Outputs:**
- `bucket_id`
- `bucket_arn`

### ECR Module

Creates ECR repositories for backend and frontend container images with:
- Image scanning on push
- Lifecycle policies to retain only recent images

**Outputs:**
- `backend_repository_url`
- `frontend_repository_url`

### RDS Module

Creates a managed PostgreSQL database with:
- Automatic backups
- Encryption at rest
- Secrets Manager integration for password storage
- Configurable Multi-AZ and Performance Insights

**Outputs:**
- `db_instance_endpoint`
- `db_password_secret_arn`

### EC2 Module

Creates an EC2 instance with:
- IAM role for S3, ECR, and Secrets Manager access
- Security group allowing HTTP/HTTPS and SSH
- Elastic IP (optional)

**Outputs:**
- `instance_id`
- `instance_public_ip`
- `security_group_id`

## Production Environment Configuration

The production environment (`envs/prod`) is configured with:
- Instance sizes: t3.medium (EC2), db.t3.small (RDS)
- Multi-AZ RDS for high availability
- Deletion protection enabled
- Restricted CORS to specific domains
  - **Production Domain:** [weddinggallery.site](http://weddinggallery.site/)
- Image retention: 20 images per repository in ECR
- S3 versioning and Glacier transitions enabled for cost optimization

**Note:** For local development, use `docker-compose.yml` at the project root. No separate dev infrastructure is needed.

## Accessing Resources

After applying, you can access outputs:

```bash
terraform output
```

### Database Password

The database password is stored in AWS Secrets Manager. Retrieve it:

```bash
aws secretsmanager get-secret-value \
  --secret-id $(terraform output -raw db_password_secret_arn) \
  --query SecretString --output text | jq -r .password
```

### ECR Login

To push images to ECR:

```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  $(terraform output -raw ecr_backend_repository_url | cut -d'/' -f1)
```

## Cost Considerations

- **NAT Gateways**: ~$32/month each (2 NAT gateways for high availability)
- **RDS**: Multi-AZ doubles the cost but provides high availability
- **EC2**: Instance costs vary by size and usage
- **S3**: Pay for storage and requests. Lifecycle rules help reduce costs over time

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will delete all resources including databases. Make sure you have backups!

## Troubleshooting

### Common Issues

1. **"Insufficient permissions"**: Check your AWS credentials and IAM permissions
2. **"Key pair not found"**: Create the key pair in AWS Console or provide `public_key`
3. **"RDS creation timeout"**: RDS instances can take 10-15 minutes to create
4. **"Bucket name already exists"**: S3 bucket names are globally unique. The bucket name includes your AWS account ID to avoid conflicts.

## Next Steps

After infrastructure is provisioned:

1. Configure your application to use the RDS endpoint
2. Set up CI/CD to push images to ECR
3. Deploy your application to EC2 using docker-compose
4. Configure Cloudflare DNS to point [weddinggallery.site](http://weddinggallery.site/) to your EC2 instance
5. Set up monitoring and alerting

## Production Domain

**Domain:** [weddinggallery.site](http://weddinggallery.site/)

When configuring production environment:
- Set `s3_allowed_origins` to include `https://weddinggallery.site` and `https://www.weddinggallery.site`
- Point Cloudflare DNS A record to the EC2 instance's public IP
- Ensure SSL/TLS is configured via Cloudflare

