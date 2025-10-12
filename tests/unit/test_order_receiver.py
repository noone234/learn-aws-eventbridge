"""Unit tests for order_receiver Lambda function."""

import json
import os
from typing import Any
from unittest.mock import MagicMock

import pytest
from moto import mock_aws

# Set environment variables before importing the handler
os.environ["EVENT_BUS_NAME"] = "test-event-bus"

# Import after setting env vars
import importlib.util
import sys
from pathlib import Path

# Load the Lambda function module dynamically
lambda_path = Path(__file__).parent.parent.parent / "lambdas" / "order_receiver" / "index.py"
spec = importlib.util.spec_from_file_location("order_receiver_index", lambda_path)
index = importlib.util.module_from_spec(spec)
sys.modules["order_receiver_index"] = index
spec.loader.exec_module(index)


@pytest.fixture
def api_gateway_event() -> dict[str, Any]:
    """Create a sample API Gateway event."""
    return {
        "body": json.dumps(
            {"orderId": "12345", "customer": "John Doe", "items": ["Widget A"], "total": 99.99}
        ),
        "headers": {"Content-Type": "application/json"},
        "httpMethod": "POST",
        "path": "/orders",
    }


@pytest.fixture
def lambda_context() -> MagicMock:
    """Create a mock Lambda context."""
    context = MagicMock()
    context.request_id = "test-request-id-123"
    return context


@mock_aws
def test_handler_success(api_gateway_event: dict[str, Any], lambda_context: MagicMock) -> None:
    """Test successful order processing."""
    # Mock EventBridge
    import boto3

    events = boto3.client("events", region_name="us-east-1")
    events.create_event_bus(Name="test-event-bus")

    # Call the handler
    response = index.handler(api_gateway_event, lambda_context)

    # Assert response
    assert response["statusCode"] == 202
    assert "Content-Type" in response["headers"]

    body = json.loads(response["body"])
    assert body["message"] == "Order received and processing"
    assert body["orderId"] == "12345"


@mock_aws
def test_handler_invalid_json(lambda_context: MagicMock) -> None:
    """Test handling of invalid JSON in request body."""
    import boto3

    events = boto3.client("events", region_name="us-east-1")
    events.create_event_bus(Name="test-event-bus")

    event = {"body": "invalid json{{{", "headers": {}, "httpMethod": "POST", "path": "/orders"}

    response = index.handler(event, lambda_context)

    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["message"] == "Invalid JSON in request body"


@mock_aws
def test_handler_eventbridge_error(
    api_gateway_event: dict[str, Any], lambda_context: MagicMock, monkeypatch: Any
) -> None:
    """Test error handling when EventBridge publish fails."""
    import boto3

    events = boto3.client("events", region_name="us-east-1")
    events.create_event_bus(Name="test-event-bus")

    # Mock put_events to raise an exception
    def mock_put_events(*args: Any, **kwargs: Any) -> None:
        raise Exception("EventBridge error")

    monkeypatch.setattr(index.eventbridge, "put_events", mock_put_events)

    response = index.handler(api_gateway_event, lambda_context)

    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert body["message"] == "Error processing order"


def test_log_structured() -> None:
    """Test structured logging function."""
    # Just verify it doesn't raise exceptions
    index.log_structured("info", "Test message", key="value", number=123)
