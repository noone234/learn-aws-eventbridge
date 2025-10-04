"""Unit tests for marketplace Lambda function."""
import json
import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

# Add the Lambda function to the path
lambda_path = Path(__file__).parent.parent.parent / "lambdas" / "marketplace"
sys.path.insert(0, str(lambda_path))

import index  # noqa: E402


@pytest.fixture
def eventbridge_event() -> Dict[str, Any]:
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


def test_handler_success(eventbridge_event: Dict[str, Any], lambda_context: MagicMock) -> None:
    """Test successful marketplace processing."""
    response = index.handler(eventbridge_event, lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["message"] == "Order processed for marketplace"


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
