# Test API

Generate example API requests for testing the order processing system.

## Get API Endpoint

```bash
aws cloudformation describe-stacks \
  --stack-name OrderProcessingStack \
  --query 'Stacks[0].Outputs[?OutputKey==`OrdersApiEndpoint`].OutputValue' \
  --output text
```

Or check the CloudFormation outputs in AWS Console.

## Example Requests

### Basic Order (All Rules Match)
```bash
curl -X POST https://{api-id}.execute-api.{region}.amazonaws.com/prod/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "order-123",
    "customerId": "customer-456",
    "items": ["item-1", "item-2"],
    "purpose": "new-order"
  }'
```

**Expected**: 202 Accepted, all 3 consumer Lambdas invoked

### Update Order (Inventory Skips)
```bash
curl -X POST https://{api-id}.execute-api.{region}.amazonaws.com/prod/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "order-789",
    "purpose": "update",
    "updateType": "address-change"
  }'
```

**Expected**: 202 Accepted, only notifier and document Lambdas invoked (inventory skips because purpose="update")

### Minimal Payload
```bash
curl -X POST https://{api-id}.execute-api.{region}.amazonaws.com/prod/orders \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello EventBridge"
  }'
```

**Expected**: 202 Accepted (any JSON is valid)

### Missing Body (Error)
```bash
curl -X POST https://{api-id}.execute-api.{region}.amazonaws.com/prod/orders \
  -H "Content-Type: application/json"
```

**Expected**: 400 Bad Request, "Request body is required"

### Invalid JSON (Error)
```bash
curl -X POST https://{api-id}.execute-api.{region}.amazonaws.com/prod/orders \
  -H "Content-Type: application/json" \
  -d 'not valid json'
```

**Expected**: 400 Bad Request, "Invalid JSON in request body"

## Check CloudWatch Logs

### API Gateway Logs
```bash
aws logs tail /aws/apigateway/public-api-access --follow
```

### EventBridge Rule Logs
```bash
# Notifier rule
aws logs tail /aws/events/route-to-notifier --follow

# Inventory rule
aws logs tail /aws/events/route-to-inventory --follow

# Document rule
aws logs tail /aws/events/route-to-document --follow
```

### Lambda Logs
```bash
aws logs tail /aws/lambda/order-receiver --follow
aws logs tail /aws/lambda/notifier --follow
aws logs tail /aws/lambda/inventory --follow
aws logs tail /aws/lambda/document --follow
```

## Check SQS Queue
```bash
aws sqs receive-message \
  --queue-url $(aws sqs get-queue-url --queue-name order-notifications-queue --query 'QueueUrl' --output text) \
  --max-number-of-messages 10
```

## Demo Flow

1. Send a request with purpose="new-order"
2. Show CloudWatch Logs for all 3 EventBridge rules (all match)
3. Send a request with purpose="update"
4. Show CloudWatch Logs - inventory rule doesn't log this event (filtered)
5. Check SQS queue for notification messages
