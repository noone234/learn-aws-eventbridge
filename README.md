# Building Event-Driven Architecture with AWS EventBridge

Welcome! This is a hands-on demo that shows you how to build event-driven applications using AWS EventBridge.

**What you'll learn:**
- How to publish events from an API to EventBridge
- How to route events to multiple consumers using EventBridge rules
- How to build decoupled, scalable microservices
- Production-ready practices: structured logging, testing, CI/CD, and monitoring

**What's included:**
- A working order processing system with API Gateway, Lambda, EventBridge, and SQS
- Complete infrastructure-as-code using AWS CDK (Python)
- Unit tests, linting, type checking, and security scans
- GitHub Actions for automated deployment
- CloudWatch alarms and structured logging for observability

This demo was originally created for an AWS User Group presentation. Whether you're new to EventBridge or looking for best practices, you can deploy this to your AWS account in minutes and start experimenting!

# Architecture

This demo showcases an event-driven architecture using AWS EventBridge:

1. **API Gateway** (`POST /orders`) receives order webhooks
2. **Lambda (order-receiver)** logs the payload and publishes an event to EventBridge
3. **EventBridge Custom Bus** (`order-processing-bus`) receives events with:
   - Source: `public.api`
   - Detail Type: `order.received.v1`
4. **EventBridge Rules** route events to three Lambda functions:
   - **Lambda (notifier)** - Simulates notifying the Sales team by sending a message to an SQS queue
   - **Lambda (inventory)** - Processes orders for inventory integration
   - **Lambda (document)** - Processes orders for document generation
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
   - **CloudWatch Logs** → Check logs for the `inventory` Lambda to see it processing the event
   - **CloudWatch Logs** → Check logs for the `document` Lambda to see it processing the event
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

#### Setting Up AWS Authentication

You have two options for authenticating GitHub Actions with AWS:

##### Option 1: OIDC with IAM Role (Recommended - More Secure)

This method uses temporary credentials and doesn't require storing AWS access keys in GitHub.

1. **Deploy the OIDC Stack (one-time setup):**

   ```bash
   # Install dependencies
   pip install -r requirements.txt

   # Option A: Using Makefile (easier)
   make setup-github GITHUB_ORG=myusername GITHUB_REPO=learn-aws-eventbridge

   # Option B: Using CDK directly
   cdk deploy -a "python setup_github_oidc.py myusername learn-aws-eventbridge"
   ```

2. **Copy the Role ARN from the output**

   The deployment will output a Role ARN like:
   ```
   arn:aws:iam::123456789012:role/GitHubActionsDeploymentRole
   ```

3. **Add GitHub Secret:**

   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `AWS_ROLE_ARN`
   - Value: The Role ARN from step 2
   - (Optional) Add `AWS_REGION` if not using `us-east-1`

4. **Done!** GitHub Actions will now use OIDC to assume the role.

##### Option 2: Access Keys (Simple but Less Secure)

If you prefer simplicity over security for a demo:

1. **Create IAM User:**
   - AWS Console → IAM → Users → Create user
   - Attach `AdministratorAccess` policy (demo only!)
   - Create access key → "Application running outside AWS"

2. **Add GitHub Secrets:**

   Go to GitHub repository → Settings → Secrets and variables → Actions

   Add these secrets:
   - `AWS_ACCESS_KEY_ID`: Your access key ID
   - `AWS_SECRET_ACCESS_KEY`: Your secret access key
   - `AWS_REGION` (optional, defaults to `us-east-1`)

3. **Bootstrap CDK (one-time):**
   ```bash
   cdk bootstrap
   ```

**Note:** The workflow automatically detects which method you're using based on whether `AWS_ROLE_ARN` secret exists.

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

# Documentation

## Project Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Detailed architecture diagrams, event schemas, and design patterns
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines and best practices

## AWS Documentation

- **[Amazon EventBridge User Guide](https://docs.aws.amazon.com/eventbridge/latest/userguide/)** - Official AWS EventBridge documentation
- **[AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)** - CDK API documentation for Python
- **[AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/)** - Lambda best practices and documentation
- **[AWS CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html)** - Query structured logs

### Event-Driven Architecture Patterns

- **[Publish-Subscribe Pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-integrating-microservices/pub-sub.html)** - AWS Prescriptive Guidance for pub/sub messaging
- **[Choreography Pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-integrating-microservices/choreography.html)** - Event-driven choreography for microservices
- **[Orchestration Pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-integrating-microservices/orchestration.html)** - Centralized orchestration with Step Functions

## Learning Resources

- Find your local [AWS User Group](https://aws.amazon.com/developer/community/usergroups/) to connect with others using AWS
- [AWS EventBridge Workshop](https://catalog.workshops.aws/eventbridge) - Hands-on EventBridge exercises
- [Serverless Land](https://serverlessland.com/patterns?services=eventbridge) - EventBridge patterns and examples

# About This Project

This repository was created for an AWS User Group presentation on event-driven architecture. It's intended as a **learning resource and demo**, not production software.

## Support

This is educational demonstration code shared with the community. While we hope you find it useful:

- **No warranty or support is provided** - Use at your own risk
- **No bug fixes or enhancements planned** - This code demonstrates concepts from a specific presentation
- **Not actively maintained** - Feel free to fork and adapt for your own learning

## Getting Help

If you're learning AWS and EventBridge:
- Review the [AWS Documentation](#aws-documentation) above
- Check out the [Learning Resources](#learning-resources) section
- Reach out to your local AWS User Group for community support
- Explore AWS's official [re:Post](https://repost.aws/) community forums

This demo is meant to inspire your own experiments and learning!

# Notice

If you use this code in demos, presentations, or talks,
please credit Christopher Wolfe and link to this repository.
