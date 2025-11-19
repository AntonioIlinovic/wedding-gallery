# Terraform Deployment Steps

Step-by-step guide to provision AWS infrastructure for the wedding gallery application.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **IAM user** dedicated to Terraform (with access keys)
3. **AWS CLI** installed and configured
4. **Terraform** >= 1.0 installed
5. **SSH Key Pair** in AWS (or you'll create one)

## Step 1: Create IAM Access and Configure AWS CLI

Create a dedicated IAM group and user for Terraform, attach the required permissions, and configure your local AWS CLI profile.

### 1.1 Create the IAM group `wedding-gallery-full-access-group`

1. In the AWS Console: IAM → User groups → **Create group**.
2. Name the group `wedding-gallery-full-access-group`.
3. Attach the following AWS-managed policies (tighten later if needed):
   - `AmazonVPCFullAccess`
   - `AmazonEC2FullAccess`
   - `AmazonRDSFullAccess`
   - `AmazonS3FullAccess`
   - `AmazonEC2ContainerRegistryFullAccess`
   - `SecretsManagerFullAccess`
   - `IAMFullAccess` *(required: Terraform creates IAM roles/policies for EC2)*
   - `CloudWatchLogsFullAccess` *(optional, for RDS log exports)*

CLI alternative (requires admin credentials):
```bash
aws iam create-group --group-name wedding-gallery-full-access-group
for policy in \
arn:aws:iam::aws:policy/AmazonVPCFullAccess \
arn:aws:iam::aws:policy/AmazonEC2FullAccess \
arn:aws:iam::aws:policy/AmazonRDSFullAccess \
arn:aws:iam::aws:policy/AmazonS3FullAccess \
arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess \
arn:aws:iam::aws:policy/SecretsManagerFullAccess \
arn:aws:iam::aws:policy/IAMFullAccess \
arn:aws:iam::aws:policy/CloudWatchLogsFullAccess; do
aws iam attach-group-policy \
--group-name wedding-gallery-full-access-group \
--policy-arn "$policy"
done
```
(Remove the CloudWatch policy from the loop if you do not need RDS log exports.)

### 1.2 Create the IAM user `terraform-user-wedding-gallery`

1. IAM → Users → **Create user**.
2. Enter the user name `terraform-user-wedding-gallery`.
3. Check **Access key - Programmatic access**.
4. On the permissions page, add the user to `wedding-gallery-full-access-group`.
5. Finish creation and download/save the access key CSV (contains `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`).

CLI alternative:
```bash
aws iam create-user --user-name terraform-user-wedding-gallery
aws iam add-user-to-group \
--user-name terraform-user-wedding-gallery \
--group-name wedding-gallery-full-access-group
aws iam create-access-key \
--user-name terraform-user-wedding-gallery > ~/terraform-user-access-key.json
```
Keep the JSON/CSV secure; you will copy the values into local config files next.

### 1.3 Configure AWS CLI on your local machine

1. Ensure the AWS CLI is installed (`aws --version`).
2. Create the AWS config directory if it does not exist:
   ```bash
mkdir -p ~/.aws
   ```
3. Copy the example credentials file and edit the placeholders:
   ```bash
cp infra/terraform/.aws-credentials.example ~/.aws/credentials
chmod 600 ~/.aws/credentials
# Edit the placeholders with the keys from terraform-user-wedding-gallery
${EDITOR:-nano} ~/.aws/credentials
   ```
   Replace `YOUR_TERRAFORM_USER_ACCESS_KEY_ID` and `YOUR_TERRAFORM_USER_SECRET_ACCESS_KEY` with the values from the IAM console/CSV.
4. Create (or update) the AWS config file for the `wedding-gallery` profile:
   ```bash
cat > ~/.aws/config <<'EOF'
[profile wedding-gallery]
region = eu-central-1
output = json
EOF
   ```
   Adjust the region if you plan to deploy to somewhere other than `eu-central-1`.
5. Test the profile:
   ```bash
AWS_PROFILE=wedding-gallery aws sts get-caller-identity
   ```

Terraform will also use this profile (see provider config in `main.tf`). Set `AWS_PROFILE=wedding-gallery` before running `terraform` commands, or export `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` manually if you prefer environment variables.

## Step 2: Create or Get SSH Key Pair

You need an SSH key pair to access the EC2 instance.

### Option A: Use Existing Key Pair

If you already have a key pair in AWS:
1. Note the key pair name
2. You'll use it in Step 3

### Option B: Create New Key Pair

1. **Generate SSH key locally** (if you don't have one):
   ```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/aws-wedding-gallery-key
   ```

2. **Import to AWS**:
   ```bash
aws ec2 import-key-pair \
--key-name aws-wedding-gallery-prod \
--public-key-material fileb://~/.ssh/aws-wedding-gallery-key.pub \
--region eu-central-1
   ```

   Note the key pair name (e.g., `aws-wedding-gallery-prod`)

## Step 3: Configure Terraform Variables

1. **Navigate to production environment**:
   ```bash
cd infra/terraform/envs/prod
   ```

2. **Copy the example variables file**:
   ```bash
cp terraform.tfvars.example terraform.tfvars
   ```

3. **Edit `terraform.tfvars`** with your values:
   ```bash
# Required: Set your key pair name
key_pair_name = "aws-wedding-gallery-prod"  # or your existing key pair name

# Required: Restrict SSH access to your IP
ssh_allowed_cidrs = ["YOUR.IP.ADDRESS/32"]  # Replace with your public IP

   **To find your public IP**:
   ```bash
curl ifconfig.me
   ```

## Step 4: Initialize Terraform

```bash
cd infra/terraform/envs/prod
terraform init
```

This downloads the required providers (AWS, random).

## Step 5: Review the Plan

Before applying, review what Terraform will create:

```bash
terraform plan
```

This will show you:
- Resources to be created (VPC, subnets, EC2, RDS, S3, ECR)
- Estimated costs (if enabled)
- Any errors or warnings

**Review carefully** - this will create billable AWS resources!

## Step 6: Apply the Configuration

If the plan looks good, apply it:

```bash
terraform apply
```

Terraform will ask for confirmation. Type `yes` to proceed.

**This will take 10-15 minutes** because:
- RDS instance creation takes time
- NAT Gateways need to be created
- EC2 instance needs to boot

## Step 7: Save the Outputs

After successful deployment, save the important outputs:

```bash
terraform output > terraform-outputs.txt
```

Or view specific outputs:

```bash
# S3 bucket name
terraform output s3_bucket_id

# EC2 public IP
terraform output ec2_public_ip

# RDS endpoint
terraform output rds_endpoint

# ECR repository URLs
terraform output ecr_backend_repository_url
terraform output ecr_frontend_repository_url

# Database password secret ARN
terraform output db_password_secret_arn
```

## Step 8: Get Database Password

The database password is stored in AWS Secrets Manager:

```bash
# Get the secret ARN from outputs
SECRET_ARN=$(terraform output -raw db_password_secret_arn)

# Retrieve the password
aws secretsmanager get-secret-value \
--secret-id $SECRET_ARN \
--query SecretString --output text
```

## Step 9: Verify Resources

### Check EC2 Instance

```bash
# Get instance ID
INSTANCE_ID=$(terraform output -raw ec2_instance_id)

# Check instance status
aws ec2 describe-instances --instance-ids $INSTANCE_ID

# SSH into instance (once it's running)
ssh -i ~/.ssh/aws-wedding-gallery-key ubuntu@$(terraform output -raw ec2_public_ip)
```

### Check S3 Bucket

```bash
BUCKET=$(terraform output -raw s3_bucket_id)
aws s3 ls s3://$BUCKET
```

### Check RDS Instance

```bash
# Get RDS endpoint
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
echo $RDS_ENDPOINT
```

### Check ECR Repositories

```bash
# List repositories
aws ecr describe-repositories --query 'repositories[*].repositoryUri'
```


### Cleaning Up: Destroying Resources

If you want to remove all resources that were created, you can use Terraform to destroy them:

```bash
terraform destroy
```

This command will prompt you for confirmation before deleting all infrastructure resources defined in your Terraform configuration. **Only run this if you are sure you want to remove everything!**


## Next Steps


- **Deploy application** to EC2 instance. We will use Github Actions workflow to deploy it to running server

- **Configure Cloudflare DNS** to point `weddinggallery.site` to EC2 public IP
