# Explain Architecture

Overview of the event-driven order processing system architecture.

## High-Level Architecture

This is an **event-driven architecture** demo using AWS EventBridge as the central event bus.

```
API Gateway → order-receiver Lambda → EventBridge Bus → EventBridge Rules → Consumer Lambdas
                                                                          ↓
                                                                    CloudWatch Logs
```

## Components

### 1. API Gateway
- **Endpoint**: POST /orders (stage: prod)
- **Purpose**: Public entry point for order submissions
- **Logs**: CloudWatch Log Group `/aws/apigateway/public-api-access`
- **Authentication**: None (demo purposes only)

### 2. order-receiver Lambda
- **Purpose**: Receives API requests, publishes events to EventBridge
- **Input**: Any valid JSON payload
- **Output**: 202 Accepted (async pattern)
- **EventBridge Event**:
  - Source: `public.api`
  - DetailType: `order.received.v1`
  - Detail: Raw JSON payload from request body

### 3. EventBridge Custom Bus
- **Name**: `order-processing-bus`
- **Purpose**: Central event routing hub
- **Pattern**: Decouples producers from consumers

### 4. EventBridge Rules
Three rules route events to different consumers:

- **route-to-notifier**: All `order.received.v1` events → notifier Lambda
- **route-to-inventory**: `order.received.v1` events WHERE purpose != "update" → inventory Lambda
- **route-to-document**: All `order.received.v1` events → document Lambda

Each rule also logs to CloudWatch for demo visibility.

### 5. Consumer Lambdas
- **notifier**: Queues email notifications to SQS
- **inventory**: Updates inventory (skips "update" purpose events)
- **document**: Generates order documents

### 6. SQS Queue
- **Name**: `order-notifications-queue`
- **Purpose**: Asynchronous email notification queue

### 7. Monitoring
- CloudWatch Alarms for Lambda errors (all 4 functions)
- CloudWatch Alarm for SQS queue depth
- SNS topic for alarm notifications

## Key Design Decisions

### Event-Driven Pattern
- **Benefit**: Loose coupling between components
- **Trade-off**: Eventual consistency, harder to trace requests

### Lazy Initialization for Boto3 Clients
- **Pattern**: Create clients on first use, not at module import
- **Benefit**: Enables moto mocking in tests
- **Trade-off**: Slightly slower Lambda cold starts
- **Decision**: Testability prioritized for demo purposes

### EventBridge Filtering
- Uses EventBridge rule patterns (not Lambda filtering)
- **Benefit**: Events never reach Lambda if filtered
- **Example**: `anything-but` pattern to skip inventory updates

### CloudWatch Logs Everywhere
- API Gateway logs, EventBridge rule logs, Lambda logs
- **Purpose**: Demo visibility for presentations
- **Retention**: 1 week for all log groups

### No Request Body Schema
- order-receiver accepts any JSON payload
- **Benefit**: Flexibility for demo scenarios
- **Trade-off**: No validation at API layer
- **Decision**: Simplicity for demo purposes

## Infrastructure as Code
- CDK (Python) in `infrastructure/` directory
- Two stacks:
  1. `OrderProcessingStack`: Main application
  2. `GitHubOIDCStack`: GitHub Actions authentication

## Cost Optimization
- All resources tagged with Project, Environment, CostCenter
- 1-week log retention (not 30 days or indefinite)
- No NAT Gateway or expensive services
