import json
import logging
import os
from typing import Any, Dict

import boto3

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client("sqs")
QUEUE_URL = os.environ["QUEUE_URL"]


def log_structured(level: str, message: str, **kwargs: Any) -> None:
    """Log structured JSON messages for better CloudWatch querying."""
    log_entry = {"level": level, "message": message, **kwargs}
    logger.log(getattr(logging, level.upper()), json.dumps(log_entry))


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Receives order event from EventBridge and queues it for email notification.
    This simulates notifying the Sales team via email by placing the event in an SQS queue.

    Args:
        event: EventBridge event containing the order detail
        context: Lambda context object

    Returns:
        Response dictionary with status code and body
    """
    request_id = context.request_id if hasattr(context, "request_id") else "unknown"

    # Log the event received from EventBridge
    log_structured("info", "Notifier received event", request_id=request_id, event=event)

    # Extract the detail from the EventBridge event
    detail = event.get("detail", {})
    order_id = detail.get("orderId", "unknown")
    log_structured(
        "info",
        "Processing order for notification",
        request_id=request_id,
        order_id=order_id,
        detail=detail,
    )

    # Send message to SQS queue for email processing
    try:
        email_message = {
            "recipient": "sales@example.com",
            "subject": f"New Order Received: {order_id}",
            "orderData": detail,
        }
        response = sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(email_message))
        message_id = response["MessageId"]
        log_structured(
            "info",
            "Message sent to SQS queue",
            request_id=request_id,
            order_id=order_id,
            message_id=message_id,
        )
    except Exception as e:
        log_structured(
            "error",
            "Error sending message to SQS",
            request_id=request_id,
            order_id=order_id,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise

    log_structured(
        "info",
        "Notification queued successfully",
        request_id=request_id,
        order_id=order_id,
    )
    return {"statusCode": 200, "body": json.dumps({"message": "Notification queued successfully"})}
