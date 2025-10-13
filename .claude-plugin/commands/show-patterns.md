# Show Patterns

Coding patterns and best practices used in this project.

## 1. Lazy Initialization for Boto3 Clients

**Why**: Enables moto mocking in tests. Boto3 clients created at module import time cannot be mocked.

**Pattern**:
```python
_eventbridge_client = None

def get_eventbridge_client():
    """Get or create EventBridge client (lazy initialization for better testability)."""
    global _eventbridge_client
    if _eventbridge_client is None:
        _eventbridge_client = boto3.client("events")
    return _eventbridge_client

# In handler
eventbridge = get_eventbridge_client()
eventbridge.put_events(...)
```

**In Tests**:
```python
@mock_aws
def test_handler_success():
    # Reset the global boto3 client cache
    index._eventbridge_client = None

    # Now moto can intercept boto3.client() call
    response = index.handler(event, context)
```

**Trade-off**: Slightly slower Lambda cold starts vs. testability. Testability prioritized for demo.

## 2. Structured Logging

**Why**: Better CloudWatch Insights queries, easier troubleshooting.

**Pattern**:
```python
def log_structured(level: str, message: str, **kwargs: Any) -> None:
    """Log structured JSON messages for better CloudWatch querying."""
    log_entry = {"level": level, "message": message, **kwargs}
    logger.log(getattr(logging, level.upper()), json.dumps(log_entry))

# Usage
log_structured("info", "Processing order", request_id=request_id, order_data=payload)
log_structured("error", "Error publishing to EventBridge",
               request_id=request_id, error=str(e), error_type=type(e).__name__)
```

**CloudWatch Insights Query Example**:
```
fields @timestamp, message, request_id, error_type
| filter level = "error"
| sort @timestamp desc
```

## 3. EventBridge Event Patterns

**Pattern**: Filter events at the rule level, not in Lambda code.

**Example: Anything-But Pattern**:
```python
inventory_rule = events.Rule(
    self,
    "InventoryRule",
    event_bus=event_bus,
    event_pattern=events.EventPattern(
        source=["public.api"],
        detail_type=["order.received.v1"],
        detail={"purpose": [{"anything-but": ["update"]}]},
    ),
)
```

**Benefit**: Filtered events never reach Lambda (no invocation cost).

## 4. API Gateway Lambda Proxy Integration

**Pattern**: Lambda receives full API Gateway event, returns formatted response.

**Request Handling**:
```python
def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    # Extract body from API Gateway event
    body = event.get("body")

    # Parse JSON if string
    if isinstance(body, str):
        payload = json.loads(body)
    else:
        payload = body
```

**Response Format**:
```python
return {
    "statusCode": 202,
    "headers": {"Content-Type": "application/json"},
    "body": json.dumps({"message": "Order received and processing"}),
}
```

## 5. Asynchronous Processing Pattern

**Pattern**: API Gateway returns immediately (202 Accepted), processing happens asynchronously.

**Benefits**:
- API responds quickly (low latency)
- Failures don't block API response
- Can scale consumers independently

**Flow**:
1. API Gateway receives request
2. order-receiver publishes to EventBridge
3. Returns 202 Accepted immediately
4. EventBridge routes to consumers asynchronously

## 6. CDK Resource Naming

**Pattern**: Use explicit names for resources that you reference outside CDK.

**Explicit Names**:
```python
event_bus = events.EventBus(
    self, "OrderProcessingBus",
    event_bus_name="order-processing-bus"  # Explicit name
)

email_queue = sqs.Queue(
    self, "EmailQueue",
    queue_name="order-notifications-queue"  # Explicit name
)
```

**Generated Names** (when OK):
```python
api = apigateway.RestApi(
    self, "PublicApi",
    rest_api_name="Public API"  # Display name, ID is generated
)
```

## 7. CloudWatch Logs for EventBridge Rules

**Pattern**: Add CloudWatch Logs as rule target for demo visibility.

```python
rule_log_group = logs.LogGroup(
    self,
    "NotifierRuleLogGroup",
    log_group_name="/aws/events/route-to-notifier",
    retention=logs.RetentionDays.ONE_WEEK,
)

rule.add_target(targets.LambdaFunction(notifier_fn))
rule.add_target(targets.CloudWatchLogGroup(rule_log_group))
```

**Benefit**: See which events matched which rules without checking Lambda logs.

## 8. Python Type Hints

**Pattern**: Use modern Python type hints (3.9+).

**Modern**:
```python
def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(body)
```

**Deprecated** (Don't use):
```python
from typing import Dict
def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
```

## 9. CDK Stack Tagging

**Pattern**: Tag all resources for cost allocation and management.

```python
Tags.of(self).add("Project", "OrderProcessing")
Tags.of(self).add("Environment", "Demo")
Tags.of(self).add("ManagedBy", "CDK")
Tags.of(self).add("CostCenter", "Engineering")
```

## 10. Error Handling in Lambdas

**Pattern**: Catch exceptions, log details, return appropriate status codes.

```python
try:
    eventbridge = get_eventbridge_client()
    response = eventbridge.put_events(...)
    log_structured("info", "Published event to EventBridge",
                   request_id=request_id, eventbridge_response=response)
except Exception as e:
    log_structured("error", "Error publishing to EventBridge",
                   request_id=request_id, error=str(e), error_type=type(e).__name__)
    return {
        "statusCode": 500,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Error processing order"}),
    }
```

**Key Points**:
- Log error details (error message, type, request ID)
- Return user-friendly error message (don't expose internals)
- Return appropriate HTTP status code
