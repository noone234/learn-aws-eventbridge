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

# Support

## Documentation

## Resources

If you have questions, get stuck or need help, consider reaching out to your local AWS User Group. Part of their mission is to help you learn from others who are actually using AWS.

# Notice

If you use this code in demos, presentations, or talks,
please credit Christopher Wolfe and link to this repository.
