"""Unit tests for notifier Lambda function."""
import json
import os
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest
from moto import mock_aws

# Set environment variables before importing the handler
os.environ["QUEUE_URL"] = "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue"

# Import after setting env vars
import sys
from pathlib import Path

# Add the Lambda function to the path
lambda_path = Path(__file__).parent.parent.parent / "lambdas" / "notifier"
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
    context.request_id = "test-request-id-456"
    return context


@mock_aws
def test_handler_success(eventbridge_event: Dict[str, Any], lambda_context: MagicMock) -> None:
    """Test successful notification queuing."""
    # Create SQS queue
    import boto3

    sqs = boto3.client("sqs", region_name="us-east-1")
    queue = sqs.create_queue(QueueName="test-queue")
    queue_url = queue["QueueUrl"]

    # Update environment variable
    os.environ["QUEUE_URL"] = queue_url
    index.QUEUE_URL = queue_url

    # Call the handler
    response = index.handler(eventbridge_event, lambda_context)

    # Assert response
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["message"] == "Notification queued successfully"

    # Verify message was sent to SQS
    messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
    assert "Messages" in messages
    assert len(messages["Messages"]) == 1

    message_body = json.loads(messages["Messages"][0]["Body"])
    assert message_body["recipient"] == "sales@example.com"
    assert "New Order Received: 12345" in message_body["subject"]
    assert message_body["orderData"]["orderId"] == "12345"


@mock_aws
def test_handler_sqs_error(
    eventbridge_event: Dict[str, Any], lambda_context: MagicMock, monkeypatch: Any
) -> None:
    """Test error handling when SQS send fails."""
    import boto3

    sqs_client = boto3.client("sqs", region_name="us-east-1")
    queue = sqs_client.create_queue(QueueName="test-queue")
    queue_url = queue["QueueUrl"]

    os.environ["QUEUE_URL"] = queue_url
    index.QUEUE_URL = queue_url

    # Mock send_message to raise an exception
    def mock_send_message(*args: Any, **kwargs: Any) -> None:
        raise Exception("SQS error")

    monkeypatch.setattr(index.sqs, "send_message", mock_send_message)

    # Should raise the exception
    with pytest.raises(Exception, match="SQS error"):
        index.handler(eventbridge_event, lambda_context)


def test_log_structured() -> None:
    """Test structured logging function."""
    index.log_structured("info", "Test message", key="value")
