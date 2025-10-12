# Architecture

## Event Flow Diagram

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ POST /orders
       │ (JSON payload)
       │
       ▼
┌──────────────────────┐
│   API Gateway        │
│   (POST /orders)     │
└──────────┬───────────┘
           │
           │ Invokes
           │
           ▼
┌─────────────────────────────────┐
│  Lambda: order-receiver         │
│  ├─ Logs payload (JSON)         │
│  └─ Publishes event             │
└──────────┬──────────────────────┘
           │
           │ PutEvents
           │
           ▼
┌────────────────────────────────────┐
│  EventBridge Custom Bus            │
│  (order-processing-bus)            │
│                                    │
│  Event:                            │
│  ├─ Source: public.api             │
│  └─ DetailType: order.received.v1  │
└──────┬─────────────────────┬───────────────────────┬───────┘
       │                     │                       │
       │                     │                       │
       │ Rule 1              │ Rule 2                │ Rule 3
       │ (route-to-notifier) │ (route-to-inventory)  │ (route-to-document)
       │                     │                       │
       ▼                     ▼                       ▼
┌─────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ Lambda:         │   │ Lambda:          │   │ Lambda:          │
│ notifier        │   │ inventory        │   │ document         │
│ ├─ Logs event   │   │ └─ Logs event    │   │ └─ Logs event    │
│ └─ Sends to SQS │   └──────────────────┘   └──────────────────┘
└────────┬────────┘
         │
         │ SendMessage
         │
         ▼
┌──────────────────────┐
│  SQS Queue           │
│  (email queue)       │
│                      │
│  Message:            │
│  ├─ recipient        │
│  ├─ subject          │
│  └─ orderData        │
└──────────────────────┘
```

## Components

### 1. API Gateway
- **Endpoint**: `POST /orders`
- **Stage**: prod
- **Purpose**: Receives order webhooks from external clients
- **Response**: 202 Accepted (async pattern)

### 2. Lambda: order-receiver
- **Runtime**: Python 3.13
- **Trigger**: API Gateway
- **Actions**:
  1. Validates and parses incoming JSON
  2. Logs order details (structured JSON logging)
  3. Publishes event to EventBridge custom bus
- **Environment Variables**:
  - `EVENT_BUS_NAME`: order-processing-bus

### 3. EventBridge Custom Bus
- **Name**: order-processing-bus
- **Event Pattern**:
  - Source: `public.api`
  - DetailType: `order.received.v1`
- **Purpose**: Central event router for order events

### 4. EventBridge Rules
Three rules route events to consumer Lambda functions:

#### Rule 1: route-to-notifier
- **Target**: notifier Lambda
- **Pattern**: Matches all `order.received.v1` events

#### Rule 2: route-to-inventory
- **Target**: inventory Lambda
- **Pattern**: Matches all `order.received.v1` events

#### Rule 3: route-to-document
- **Target**: document Lambda
- **Pattern**: Matches all `order.received.v1` events

### 5. Lambda: notifier
- **Runtime**: Python 3.13
- **Trigger**: EventBridge (order.received.v1 events)
- **Actions**:
  1. Logs event details (structured JSON logging)
  2. Creates email notification message
  3. Sends message to SQS queue
- **Environment Variables**:
  - `QUEUE_URL`: URL of the email queue

### 6. Lambda: inventory
- **Runtime**: Python 3.13
- **Trigger**: EventBridge (order.received.v1 events)
- **Actions**:
  1. Logs event details (structured JSON logging)
  2. Simulates inventory integration processing

### 7. Lambda: document
- **Runtime**: Python 3.13
- **Trigger**: EventBridge (order.received.v1 events)
- **Actions**:
  1. Logs event details (structured JSON logging)
  2. Simulates document generation processing

### 8. SQS Queue
- **Name**: order-notifications-queue
- **Type**: Standard
- **Purpose**: Holds email notification messages for the Sales team
- **Consumer**: (Not implemented in this demo - would be an email service)

## Observability

### CloudWatch Alarms
All alarms publish to SNS topic: `order-processing-alarms`

1. **Lambda Error Alarms** (4)
   - Monitors errors for each Lambda function (order-receiver, notifier, inventory, document)
   - Threshold: ≥1 error in 5 minutes
   - Action: Send SNS notification

2. **SQS Queue Depth Alarm**
   - Monitors queue depth for email queue
   - Threshold: ≥100 messages (evaluated over 2 periods of 5 minutes)
   - Action: Send SNS notification

### Structured Logging
All Lambda functions use structured JSON logging for better CloudWatch Insights querying:

```json
{
  "level": "info",
  "message": "Processing order",
  "request_id": "abc-123",
  "order_id": "12345",
  "order_data": {...}
}
```

### Cost Allocation Tags
All resources are tagged with:
- `Project`: OrderProcessing
- `Environment`: Demo
- `ManagedBy`: CDK
- `CostCenter`: Engineering

## Event Schema

### Input: API Gateway Request Body
```json
{
  "orderId": "12345",
  "customer": "John Doe",
  "items": ["Widget A", "Widget B"],
  "total": 99.99
}
```

### EventBridge Event
```json
{
  "version": "0",
  "id": "event-id",
  "detail-type": "order.received.v1",
  "source": "public.api",
  "time": "2025-01-01T12:00:00Z",
  "region": "us-east-1",
  "detail": {
    "orderId": "12345",
    "customer": "John Doe",
    "items": ["Widget A", "Widget B"],
    "total": 99.99
  }
}
```

### SQS Message Body
```json
{
  "recipient": "sales@example.com",
  "subject": "New Order Received: 12345",
  "orderData": {
    "orderId": "12345",
    "customer": "John Doe",
    "items": ["Widget A", "Widget B"],
    "total": 99.99
  }
}
```

## Design Patterns

### 1. Async Processing (Fire and Forget)
The API Gateway returns immediately (202 Accepted) without waiting for downstream processing. This provides:
- Fast response times
- Resilience to downstream failures
- Ability to scale consumers independently

### 2. Event-Driven Architecture
EventBridge acts as a central event bus, enabling:
- Loose coupling between services
- Easy addition of new consumers
- Event filtering and routing

### 3. Fan-out Pattern
One event triggers multiple independent consumers (notifier, inventory, and document), allowing:
- Parallel processing
- Independent scaling
- Different failure modes

### 4. Dead Letter Queues (Recommended)
For production, consider adding DLQs to:
- Lambda functions (for failed invocations)
- SQS queue (for failed message processing)

## Security Considerations

### IAM Permissions
- Lambda functions have minimal IAM permissions (least privilege)
- EventBridge grants specific `events:PutEvents` permission
- SQS grants specific `sqs:SendMessage` permission

### API Gateway
- Currently public (no authentication)
- For production, consider adding:
  - API keys
  - AWS IAM authorization
  - Lambda authorizer
  - WAF rules

### Encryption
- All data encrypted in transit (HTTPS)
- Consider enabling encryption at rest for:
  - SQS queue
  - CloudWatch Logs
