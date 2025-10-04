import json
import logging
from typing import Any, Dict

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def log_structured(level: str, message: str, **kwargs: Any) -> None:
    """Log structured JSON messages for better CloudWatch querying."""
    log_entry = {"level": level, "message": message, **kwargs}
    logger.log(getattr(logging, level.upper()), json.dumps(log_entry))


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Receives order event from EventBridge and logs it.
    This function processes orders for marketplace integration.

    Args:
        event: EventBridge event containing the order detail
        context: Lambda context object

    Returns:
        Response dictionary with status code and body
    """
    request_id = context.request_id if hasattr(context, "request_id") else "unknown"

    # Log the event received from EventBridge
    log_structured("info", "Marketplace received event", request_id=request_id, event=event)

    # Extract the detail from the EventBridge event
    detail = event.get("detail", {})
    order_id = detail.get("orderId", "unknown")
    log_structured(
        "info",
        "Processing order for marketplace",
        request_id=request_id,
        order_id=order_id,
        detail=detail,
    )

    # Simulate marketplace processing
    log_structured(
        "info",
        "Order processed for marketplace integration",
        request_id=request_id,
        order_id=order_id,
    )

    return {"statusCode": 200, "body": json.dumps({"message": "Order processed for marketplace"})}
