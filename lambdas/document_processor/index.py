import json
import logging
import os
from typing import Any

import boto3

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Lazy-initialized clients for testability
_s3_client = None
_events_client = None

SUPPORTED_EXTENSIONS = {".edi", ".bol", ".pod", ".csv", ".json", ".xml"}


def get_s3_client():  # type: ignore[no-untyped-def]
    """Lazy-initialize S3 client."""
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client("s3")
    return _s3_client


def get_events_client():  # type: ignore[no-untyped-def]
    """Lazy-initialize EventBridge client."""
    global _events_client
    if _events_client is None:
        _events_client = boto3.client("events")
    return _events_client


def log_structured(level: str, message: str, **kwargs: Any) -> None:
    """Log structured JSON messages for better CloudWatch querying."""
    log_entry = {"level": level, "message": message, **kwargs}
    logger.log(getattr(logging, level.upper()), json.dumps(log_entry))


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Process S3 document upload events received via EventBridge.

    S3 sends ObjectCreated events to the default EventBridge bus when
    documents (EDI, BOL, POD, etc.) are uploaded. This Lambda reads
    the document metadata from S3 and publishes a downstream
    "order.document-uploaded.v1" event to the custom bus.

    Args:
        event: EventBridge event with S3 object details in "detail"
        context: Lambda context object

    Returns:
        Response dictionary with status code and body
    """
    request_id = context.request_id if hasattr(context, "request_id") else "unknown"
    event_bus_name = os.environ.get("EVENT_BUS_NAME", "order-processing-bus")

    log_structured("info", "Document processor received event", request_id=request_id, event=event)

    detail = event.get("detail", {})
    bucket_name = detail.get("bucket", {}).get("name", "unknown")
    object_key = detail.get("object", {}).get("key", "unknown")
    object_size = detail.get("object", {}).get("size", 0)

    log_structured(
        "info",
        "Processing uploaded document",
        request_id=request_id,
        bucket=bucket_name,
        key=object_key,
        size=object_size,
    )

    # Determine document type from file extension
    extension = ""
    if "." in object_key:
        extension = "." + object_key.rsplit(".", 1)[-1].lower()
    doc_type = extension.lstrip(".").upper() if extension in SUPPORTED_EXTENSIONS else "UNKNOWN"

    # Extract order ID from key convention: <prefix>/<orderId>/<filename>
    key_parts = object_key.split("/")
    order_id = key_parts[1] if len(key_parts) >= 3 else "unknown"

    # Read object metadata from S3 (HEAD, not full GET — saves cost/time)
    s3 = get_s3_client()
    try:
        head = s3.head_object(Bucket=bucket_name, Key=object_key)
        content_type = head.get("ContentType", "application/octet-stream")
        metadata = head.get("Metadata", {})
    except Exception:
        log_structured(
            "warning",
            "Failed to read object metadata, continuing with defaults",
            request_id=request_id,
            bucket=bucket_name,
            key=object_key,
        )
        content_type = "application/octet-stream"
        metadata = {}

    log_structured(
        "info",
        "Document metadata retrieved",
        request_id=request_id,
        doc_type=doc_type,
        content_type=content_type,
        order_id=order_id,
        user_metadata=metadata,
    )

    # Publish downstream event to custom bus
    downstream_detail = {
        "orderId": order_id,
        "documentType": doc_type,
        "bucket": bucket_name,
        "key": object_key,
        "size": object_size,
        "contentType": content_type,
    }

    eb = get_events_client()
    try:
        eb.put_events(
            Entries=[
                {
                    "Source": "document.processor",
                    "DetailType": "order.document-uploaded.v1",
                    "Detail": json.dumps(downstream_detail),
                    "EventBusName": event_bus_name,
                }
            ]
        )
        log_structured(
            "info",
            "Published document-uploaded event",
            request_id=request_id,
            order_id=order_id,
            doc_type=doc_type,
        )
    except Exception:
        log_structured(
            "error",
            "Failed to publish document-uploaded event",
            request_id=request_id,
            order_id=order_id,
        )
        raise

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Document processed",
                "orderId": order_id,
                "documentType": doc_type,
            }
        ),
    }
