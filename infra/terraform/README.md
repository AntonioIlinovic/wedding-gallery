# Terraform Infrastructure as Code

This directory contains Terraform modules and environment configurations for provisioning AWS infrastructure for the wedding gallery application.

## Structure

```
terraform/
├── modules/          # Reusable Terraform modules
│   ├── vpc/         # VPC, subnets, NAT gateways, etc.
│   ├── s3/          # S3 bucket for photo storage
│   ├── ecr/         # ECR repositories for container images
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

### EC2 Module

Creates an EC2 instance with:
- IAM role for S3, ECR, and Secrets Manager access
- Security group allowing HTTP/HTTPS and SSH
- Elastic IP association (references a manually created Elastic IP)

**Important:** The Elastic IP must be created manually in AWS before running Terraform. See the [Terraform Deployment Guide](../docs/TERRAFORM_DEPLOYMENT.md) for instructions.

**Why is the Elastic IP manual?**
- The Elastic IP address is used in DNS records (e.g., Cloudflare). If Terraform managed the EIP and destroyed/recreated it during `terraform destroy` and `terraform apply` cycles, the IP would change, breaking DNS configuration.
- By keeping the EIP outside Terraform management, you can safely destroy and recreate infrastructure without losing the static IP address.

**Outputs:**
- `instance_id`
- `instance_public_ip` (Elastic IP)
- `security_group_id`
- `elastic_ip` (Elastic IP address)

## Production Environment Configuration

The production environment (`envs/prod`) is configured with:
- Instance sizes: t3.nano (EC2)
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

### SSH into EC2
```bash
# SSH into instance (once it's running, using Elastic IP)
ssh -i ~/.ssh/aws-wedding-gallery-key ubuntu@$(terraform output -raw ec2_public_ip)
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will delete all resources except Elastic IP. Make sure you have backups!

**Note on Elastic IP**: The Elastic IP is **not** managed by Terraform and will **not** be destroyed. It will remain allocated in your AWS account. The EIP association will be removed, but the Elastic IP itself persists. If you want to release it, you must do so manually via the AWS Console or CLI:

```bash
# Find and release the Elastic IP
aws ec2 describe-addresses \
  --filters "Name=tag:Name,Values=wedding-gallery-prod-ec2-eip" \
  --query 'Addresses[0].AllocationId' \
  --output text

# Release it (replace ALLOCATION_ID with the actual ID)
aws ec2 release-address --allocation-id ALLOCATION_ID
```

## Next Steps

After infrastructure is provisioned:

1. Set up CI/CD to push images to ECR
2. Deploy your application to EC2 using docker-compose
3. Configure Cloudflare DNS to point [weddinggallery.site](http://weddinggallery.site/) to your EC2 instance
4. Set up monitoring and alerting

## Production Domain

**Domain:** [weddinggallery.site](http://weddinggallery.site/)

When configuring production environment:
- Set `s3_allowed_origins` to include `https://weddinggallery.site` and `https://www.weddinggallery.site`
- Point Cloudflare DNS A record to the EC2 instance's Elastic IP
- Ensure SSL/TLS is configured via Cloudflare

