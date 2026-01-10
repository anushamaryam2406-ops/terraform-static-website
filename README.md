# Cloud Computing Portfolio — AWS Terraform Project

A fully cloud-native portfolio website showcasing cloud computing skills. Demonstrates **Infrastructure as Code (IaC)** with Terraform, serverless architecture, and AWS best practices.

## 📋 Project Overview

This project deploys a simple cloud-focused portfolio website on AWS with the following architecture:

- **Frontend**: Static HTML/CSS portfolio highlighting cloud computing interests
- **Hosting**: S3 bucket + CloudFront CDN for global distribution
- **Backend**: Serverless visitor counter using Lambda + API Gateway + DynamoDB
- **Infrastructure**: All provisioned and managed with Terraform

## 🏗️ Architecture

```
┌─────────────┐
│  Portfolio  │ (index.html, style.css)
│  Website    │
└──────┬──────┘
       │
       ├──→ [S3 Bucket] (Static files)
       │      │
       │      └──→ [CloudFront CDN] (Global distribution with OAC)
       │
       └──→ [API Gateway] (/visit endpoint)
              │
              └──→ [Lambda Function] (lambda_function.py)
                     │
                     └──→ [DynamoDB] (visitor-count table)
```

## 📁 Project Files

- **`index.html`** — Portfolio page with cloud computing focus, visitor counter integration
- **`style.css`** — Minimal, responsive CSS for clean design
- **`lambda_function.py`** — AWS Lambda handler: increments visitor count in DynamoDB
- **`main.tf`** — S3 bucket, CloudFront distribution, Origin Access Control
- **`api_gateway.tf`** — REST API endpoint for visitor counter
- **`lambda.tf`** — Lambda function, IAM role, DynamoDB permissions
- **`dynamodb.tf`** — DynamoDB table for storing visitor count
- **`.gitignore`** — Ignores Terraform state files and crash logs
- **`lambda.zip`** — Packaged Python function (generated during deployment)

## 🚀 Features

✅ **Cloud-Focused Portfolio** — Emphasizes AWS, Terraform, and serverless skills  
✅ **Infrastructure as Code** — 100% Terraform-managed infrastructure  
✅ **Serverless Visitor Counter** — Real-time tracking using Lambda + DynamoDB  
✅ **Global CDN** — CloudFront for low-latency worldwide delivery  
✅ **Modern Security** — Origin Access Control (OAC), bucket policies, no public access  
✅ **Responsive Design** — Mobile-friendly CSS with minimal dependencies  
✅ **Remote State** — Terraform state stored securely in S3

## 📋 Prerequisites

- AWS account with appropriate permissions
- Terraform v1.0+ installed
- AWS CLI configured (`aws configure`)
- Python 3.11+ (for packaging Lambda)
- Existing S3 bucket for remote Terraform state (name: `tfstate-anusha-eu-north-1-2026`)

## ⚙️ Setup Instructions

### 1. Clone/Navigate to Project
```bash
cd c:/Users/Admin/Desktop/tf_new/static_web
```

### 2. Package Lambda Function
```bash
pip install boto3
zip lambda.zip lambda_function.py
```

### 3. Initialize Terraform
```bash
terraform init
```
This connects to your remote S3 state bucket.

### 4. Plan Deployment
```bash
terraform plan
```
Review the resources Terraform will create.

### 5. Apply Configuration
```bash
terraform apply
```
Confirms and provisions:
- S3 bucket (random suffix)
- CloudFront distribution
- API Gateway + Lambda
- DynamoDB table

### 6. Deploy Website
```bash
terraform apply
```
Your files (`index.html`, `style.css`) are uploaded to S3 automatically.

## 🔗 Outputs

After `terraform apply`, you'll see:

```
api_url = "https://{id}.execute-api.eu-north-1.amazonaws.com/prod/visit"
cloudfront_url = "{random-hash}.cloudfront.net"
```

- **CloudFront URL** — Your public portfolio website
- **API URL** — Visitor counter endpoint (called by `index.html`)

## 🌐 Accessing Your Portfolio

1. Wait ~5 minutes for CloudFront to cache
2. Visit: `https://{cloudfront-url}`
3. The visitor counter displays total visits (stored in DynamoDB)

## 📝 Customization

- **Replace Portfolio Image** — Update the `src` in `index.html` hero section (currently placeholder)
- **Update Email/Contact** — Modify contact section in `index.html`
- **Change Styling** — Edit `style.css` for colors, fonts, layout
- **Add Projects** — Expand `.projects` section with real project links

## 🧹 Cleanup

To remove all AWS resources:
```bash
terraform destroy
```
Confirm when prompted. This removes:
- S3 bucket
- CloudFront distribution
- Lambda function
- API Gateway
- DynamoDB table
- IAM roles and policies

## 📚 Key Learnings

This project demonstrates:
- ✅ S3 static hosting with private buckets
- ✅ CloudFront CDN with Origin Access Control (modern OAC vs. deprecated OAI)
- ✅ Serverless backend: Lambda + API Gateway + DynamoDB
- ✅ Infrastructure as Code with Terraform
- ✅ CORS headers for cross-origin API calls
- ✅ Environment variables (DynamoDB table name)
- ✅ Decimal handling in Python/DynamoDB
- ✅ Remote state management in S3

## 📦 Technologies Used

| Component | Technology |
|-----------|-----------|
| Frontend | HTML5, CSS3 |
| Hosting | AWS S3 + CloudFront |
| Backend | AWS Lambda (Python 3.11) |
| API | AWS API Gateway |
| Database | AWS DynamoDB |
| IaC | Terraform ~6.0 |
| Region | eu-north-1 (Stockholm) |

## 🐛 Troubleshooting

**Visitor counter shows "Error":**
- Check Lambda execution logs: `aws logs tail /aws/lambda/testLambdaBasic --follow`
- Verify DynamoDB table exists
- Confirm Lambda has DynamoDB permissions

**CloudFront shows 403 Forbidden:**
- Wait 5 minutes for CloudFront to cache after deployment
- Verify S3 bucket policy includes CloudFront OAC

**Terraform state lock:**
- Force unlock if needed: `terraform force-unlock {lock-id}`


**Project created:** January 2026  
**Author:** Anusha  
**Cloud Focus:** AWS, Terraform, Serverless Architecture
