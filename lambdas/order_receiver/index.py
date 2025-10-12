import json
import logging
import os
from typing import Any

import boto3

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Lazy initialization for boto3 client (created on first use)
_eventbridge_client = None
EVENT_BUS_NAME = os.environ["EVENT_BUS_NAME"]


def get_eventbridge_client():
    """Get or create EventBridge client (lazy initialization for better testability)."""
    global _eventbridge_client
    if _eventbridge_client is None:
        _eventbridge_client = boto3.client("events")
    return _eventbridge_client


def log_structured(level: str, message: str, **kwargs: Any) -> None:
    """Log structured JSON messages for better CloudWatch querying."""
    log_entry = {"level": level, "message": message, **kwargs}
    logger.log(getattr(logging, level.upper()), json.dumps(log_entry))


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Receives order from API Gateway, logs it, and publishes to EventBridge.

    Accepts any valid JSON payload and passes it through to EventBridge.
    Returns 400 if request body is missing or contains invalid JSON.

    Args:
        event: API Gateway event containing the order payload
        context: Lambda context object

    Returns:
        API Gateway response with status code and body
    """
    request_id = context.request_id if hasattr(context, "request_id") else "unknown"

    # Log the incoming payload
    log_structured("info", "Received order", request_id=request_id, event=event)

    # Extract the body from API Gateway event
    body = event.get("body")

    # Return 400 if no request body provided
    if not body:
        log_structured("error", "Missing request body", request_id=request_id)
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Request body is required"}),
        }

    # Parse JSON body
    if isinstance(body, str):
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as e:
            log_structured(
                "error", "Invalid JSON in request body", request_id=request_id, error=str(e)
            )
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Invalid JSON in request body"}),
            }
    else:
        payload = body

    log_structured(
        "info", "Processing order", request_id=request_id, order_data=payload
    )

    # Publish event to EventBridge
    try:
        eventbridge = get_eventbridge_client()
        response = eventbridge.put_events(
            Entries=[
                {
                    "Source": "public.api",
                    "DetailType": "order.received.v1",
                    "Detail": json.dumps(payload),
                    "EventBusName": EVENT_BUS_NAME,
                }
            ]
        )
        log_structured(
            "info",
            "Published event to EventBridge",
            request_id=request_id,
            eventbridge_response=response,
        )
    except Exception as e:
        log_structured(
            "error",
            "Error publishing to EventBridge",
            request_id=request_id,
            error=str(e),
            error_type=type(e).__name__,
        )
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Error processing order"}),
        }

    # Return success response immediately (async pattern)
    log_structured(
        "info", "Order accepted for processing", request_id=request_id
    )
    return {
        "statusCode": 202,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Order received and processing"}),
    }
