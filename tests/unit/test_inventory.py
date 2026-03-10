"""Unit tests for inventory Lambda function."""

import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

# Set environment variables before importing the handler
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# Load the Lambda function module dynamically
lambda_path = Path(__file__).parent.parent.parent / "lambdas" / "inventory" / "index.py"
spec = importlib.util.spec_from_file_location("inventory_index", lambda_path)
index = importlib.util.module_from_spec(spec)
sys.modules["inventory_index"] = index
spec.loader.exec_module(index)


def _make_eventbridge_event(detail: dict[str, Any]) -> dict[str, Any]:
    """Create a sample EventBridge event."""
    return {
        "version": "0",
        "id": "test-event-id",
        "detail-type": "order.received.v1",
        "source": "public.api",
        "time": "2025-01-01T12:00:00Z",
        "region": "us-east-1",
        "detail": detail,
    }


def _wrap_in_sqs_event(*eb_events: dict[str, Any]) -> dict[str, Any]:
    """Wrap EventBridge events in an SQS event structure."""
    return {
        "Records": [
            {
                "messageId": f"msg-{i}",
                "receiptHandle": f"handle-{i}",
                "body": json.dumps(eb_event),
                "attributes": {},
                "messageAttributes": {},
                "md5OfBody": "test",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:inventory-processing-queue",
                "awsRegion": "us-east-1",
            }
            for i, eb_event in enumerate(eb_events)
        ]
    }


@pytest.fixture
def sqs_event() -> dict[str, Any]:
    """Create a sample SQS event wrapping a single EventBridge event."""
    eb_event = _make_eventbridge_event(
        {
            "orderId": "12345",
            "customer": "John Doe",
            "items": ["Widget A"],
            "total": 99.99,
        }
    )
    return _wrap_in_sqs_event(eb_event)


@pytest.fixture
def lambda_context() -> MagicMock:
    """Create a mock Lambda context."""
    context = MagicMock()
    context.request_id = "test-request-id-789"
    return context


def test_handler_single_record(sqs_event: dict[str, Any], lambda_context: MagicMock) -> None:
    """Test successful processing of a single SQS record."""
    response = index.handler(sqs_event, lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["message"] == "Processed 1 orders for inventory"


def test_handler_batch_records(lambda_context: MagicMock) -> None:
    """Test successful processing of a batch of SQS records."""
    eb_events = [
        _make_eventbridge_event({"orderId": f"order-{i}", "customer": f"Customer {i}"})
        for i in range(3)
    ]
    sqs_event = _wrap_in_sqs_event(*eb_events)

    response = index.handler(sqs_event, lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["message"] == "Processed 3 orders for inventory"


def test_handler_missing_order_id(lambda_context: MagicMock) -> None:
    """Test handling of events without order ID."""
    eb_event = _make_eventbridge_event({"customer": "John Doe"})
    sqs_event = _wrap_in_sqs_event(eb_event)

    response = index.handler(sqs_event, lambda_context)

    # Should still succeed, just log "unknown" for order_id
    assert response["statusCode"] == 200


def test_handler_empty_batch(lambda_context: MagicMock) -> None:
    """Test handling of an empty SQS batch."""
    sqs_event: dict[str, Any] = {"Records": []}

    response = index.handler(sqs_event, lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["message"] == "Processed 0 orders for inventory"


def test_process_order() -> None:
    """Test the process_order helper directly."""
    detail = {"orderId": "test-123", "customer": "Jane", "items": ["X"], "total": 50.0}
    # Should not raise
    index.process_order(detail, "req-1")


def test_log_structured() -> None:
    """Test structured logging function."""
    index.log_structured("info", "Test message", key="value")
