"""Unit tests for inventory Lambda function."""

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

# Load the Lambda function module dynamically
lambda_path = Path(__file__).parent.parent.parent / "lambdas" / "inventory" / "index.py"
spec = importlib.util.spec_from_file_location("inventory_index", lambda_path)
index = importlib.util.module_from_spec(spec)
sys.modules["inventory_index"] = index
spec.loader.exec_module(index)


@pytest.fixture
def eventbridge_event() -> dict[str, Any]:
    """Create a sample EventBridge event."""
    return {
        "version": "0",
        "id": "test-event-id",
        "detail-type": "order.received.v1",
        "source": "public.api",
        "time": "2025-01-01T12:00:00Z",
        "region": "us-east-1",
        "detail": {
            "orderId": "12345",
            "customer": "John Doe",
            "items": ["Widget A"],
            "total": 99.99,
        },
    }


@pytest.fixture
def lambda_context() -> MagicMock:
    """Create a mock Lambda context."""
    context = MagicMock()
    context.request_id = "test-request-id-789"
    return context


def test_handler_success(eventbridge_event: dict[str, Any], lambda_context: MagicMock) -> None:
    """Test successful inventory processing."""
    response = index.handler(eventbridge_event, lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["message"] == "Order processed for inventory"


def test_handler_missing_order_id(lambda_context: MagicMock) -> None:
    """Test handling of events without order ID."""
    event = {
        "version": "0",
        "id": "test-event-id",
        "detail-type": "order.received.v1",
        "source": "public.api",
        "time": "2025-01-01T12:00:00Z",
        "region": "us-east-1",
        "detail": {"customer": "John Doe"},  # No orderId
    }

    response = index.handler(event, lambda_context)

    # Should still succeed, just log "unknown"
    assert response["statusCode"] == 200


def test_log_structured() -> None:
    """Test structured logging function."""
    index.log_structured("info", "Test message", key="value")
