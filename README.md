# Introduction

This code sample was used in an AWS User Group Presentation
titled "Building Event-Driven Architecture with AWS EventBridge".

# Architecture

This demo showcases an event-driven architecture using AWS EventBridge:

1. **API Gateway** (`POST /orders`) receives order webhooks
2. **Lambda (order-receiver)** logs the payload and publishes an event to EventBridge
3. **EventBridge Custom Bus** (`order-processing-bus`) receives events with:
   - Source: `public.api`
   - Detail Type: `order.received.v1`
4. **EventBridge Rules** route events to two Lambda functions:
   - **Lambda (notifier)** - Simulates notifying the Sales team by sending a message to an SQS queue
   - **Lambda (marketplace)** - Processes orders for marketplace integration
5. **SQS Queue** (`order-notifications-queue`) receives notification messages

All infrastructure is defined using AWS CDK in Python.

# Usage

If you want to try this yourself, here's how.

## Quick Start

```bash
pip install -r requirements.txt
cdk bootstrap  # if first time using CDK in this account/region
cdk deploy
```

## Prerequisites

In the Cloud:

- An AWS account that you own

On your computer:

- Python 3.13 installed
- Node.js and npm installed (for AWS CDK CLI)
- AWS CLI configured with credentials
- AWS CDK CLI installed (`npm install -g aws-cdk`)

## Deployment

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Bootstrap CDK (if this is your first time using CDK in this account/region):**
   ```bash
   cdk bootstrap
   ```

3. **Deploy the stack:**
   ```bash
   cdk deploy
   ```

4. **Save the API Gateway URL from the output.** You'll need it for testing.

## Demo

1. **Send a test order to the API:**
   ```bash
   curl -X POST https://YOUR_API_URL/prod/orders \
     -H "Content-Type: application/json" \
     -d '{
       "orderId": "12345",
       "customer": "John Doe",
       "items": ["Widget A", "Widget B"],
       "total": 99.99
     }'
   ```

2. **Log into AWS Management Console**

3. **Observe how the event travels through the system:**
   - **CloudWatch Logs** → Check logs for the `order-receiver` Lambda to see the incoming payload
   - **EventBridge** → View the `order-processing-bus` to see events published with source `public.api` and detail-type `order.received.v1`
   - **CloudWatch Logs** → Check logs for the `notifier` Lambda to see it processing the event
   - **CloudWatch Logs** → Check logs for the `marketplace` Lambda to see it processing the event
   - **SQS** → Check the `order-notifications-queue` to see messages queued for email notifications

We assume that you know your way around AWS CloudWatch and observability tools.

## GitHub Actions Deployment

This repository includes automated CI/CD workflows via GitHub Actions.

### CI Workflow

The CI workflow runs automatically on all pushes and pull requests:
- Linting (ruff, black)
- Type checking (mypy)
- Security scans (bandit, safety)
- Unit tests with coverage
- CDK diff on pull requests (if AWS credentials are configured)

### Deployment Workflow

The deployment workflow can deploy the stack to AWS automatically:
- **Automatic**: Triggers on pushes to `main` branch
- **Manual**: Can be triggered via the "Actions" tab in GitHub

#### Setting Up GitHub Secrets

To enable automated deployments, you need to configure AWS credentials as GitHub secrets:

1. **Go to your GitHub repository** → Settings → Secrets and variables → Actions

2. **Add the following secrets:**

   - `AWS_ACCESS_KEY_ID`
     - Your AWS access key ID
     - Create via AWS Console → IAM → Users → Security credentials

   - `AWS_SECRET_ACCESS_KEY`
     - Your AWS secret access key
     - Generated when you create the access key

   - `AWS_REGION` (optional, defaults to `us-east-1`)
     - The AWS region to deploy to (e.g., `us-east-1`, `us-west-2`)

3. **IAM Permissions Required:**

   The AWS credentials need permissions to:
   - Deploy CloudFormation stacks
   - Create/manage Lambda functions
   - Create/manage API Gateway
   - Create/manage EventBridge resources
   - Create/manage SQS queues
   - Create/manage SNS topics
   - Create/manage CloudWatch alarms
   - Create/manage IAM roles (for Lambda execution)

   For simplicity in a demo environment, you can use `AdministratorAccess` policy. For production, create a custom policy with only the required permissions.

4. **Bootstrap CDK (one-time setup):**

   Before the first deployment, bootstrap CDK in your AWS account:
   ```bash
   cdk bootstrap aws://ACCOUNT-ID/REGION
   ```

   Or let the GitHub Actions workflow do it automatically (it runs `cdk bootstrap` as part of deployment).

#### Manual Deployment via GitHub Actions

1. Go to the "Actions" tab in your GitHub repository
2. Select "Deploy to AWS" workflow
3. Click "Run workflow" → select branch `main` → Click "Run workflow" button

The workflow will output the API Gateway URL in the deployment summary.

#### Disable Automated Deployments

If you don't want automatic deployments on every push to `main`, edit `.github/workflows/deploy.yml` and remove the `push:` trigger:

```yaml
on:
  # push:              # Comment this out
  #   branches: [main] # to disable auto-deploy
  workflow_dispatch:   # Keep this for manual triggers
```

# Support

## Documentation

## Resources

If you have questions, get stuck or need help, consider reaching out to your local AWS User Group. Part of their mission is to help you learn from others who are actually using AWS.

# Notice

If you use this code in demos, presentations, or talks,
please credit Christopher Wolfe and link to this repository.
