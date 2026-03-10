import json
import logging
from typing import Any

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def log_structured(level: str, message: str, **kwargs: Any) -> None:
    """Log structured JSON messages for better CloudWatch querying."""
    log_entry = {"level": level, "message": message, **kwargs}
    logger.log(getattr(logging, level.upper()), json.dumps(log_entry))


def process_order(detail: dict[str, Any], request_id: str) -> None:
    """
    Process a single order for inventory integration.

    Args:
        detail: The order detail from the EventBridge event
        request_id: Lambda request ID for tracing
    """
    order_id = detail.get("orderId", "unknown")
    log_structured(
        "info",
        "Processing order for inventory",
        request_id=request_id,
        order_id=order_id,
        detail=detail,
    )

    # Simulate inventory processing
    log_structured(
        "info",
        "Order processed for inventory integration",
        request_id=request_id,
        order_id=order_id,
    )


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Receives order events from SQS (buffered from EventBridge) and processes them.

    SQS acts as a buffer between EventBridge and this Lambda to prevent
    the inventory service from being overwhelmed by order spikes. Each SQS
    message body contains the full EventBridge event JSON.

    Args:
        event: SQS event containing one or more records
        context: Lambda context object

    Returns:
        Response dictionary with status code and body
    """
    request_id = context.request_id if hasattr(context, "request_id") else "unknown"

    records = event.get("Records", [])
    log_structured(
        "info",
        "Inventory received SQS batch",
        request_id=request_id,
        record_count=len(records),
    )

    processed = 0
    for record in records:
        # Each SQS message body is the full EventBridge event JSON
        eb_event = json.loads(record["body"])
        detail = eb_event.get("detail", {})
        process_order(detail, request_id)
        processed += 1

    log_structured(
        "info",
        "Batch processing complete",
        request_id=request_id,
        processed_count=processed,
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"Processed {processed} orders for inventory"}),
    }
