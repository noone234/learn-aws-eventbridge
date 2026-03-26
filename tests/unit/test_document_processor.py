"""Unit tests for document-processor Lambda function."""

import importlib.util
import json
import os
import sys
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import boto3
import pytest
from moto import mock_aws

# Set environment variables before importing the handler
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["EVENT_BUS_NAME"] = "order-processing-bus"

# Load the Lambda function module dynamically
lambda_path = (
    Path(__file__).parent.parent.parent / "lambdas" / "document_processor" / "index.py"
)
spec = importlib.util.spec_from_file_location("document_processor_index", lambda_path)
index = importlib.util.module_from_spec(spec)
sys.modules["document_processor_index"] = index
spec.loader.exec_module(index)

BUCKET_NAME = "order-documents-123456789012"
EVENT_BUS_NAME = "order-processing-bus"


@pytest.fixture(autouse=True)
def _reset_clients(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset lazy clients and ensure correct env var for every test."""
    monkeypatch.setenv("EVENT_BUS_NAME", EVENT_BUS_NAME)
    index._s3_client = None
    index._events_client = None


@pytest.fixture
def aws_mocks() -> Generator[None]:
    """Provide moto mock context and reset Lambda clients inside it."""
    with mock_aws():
        # Reset again inside the mock so clients bind to moto
        index._s3_client = None
        index._events_client = None
        yield


def _make_s3_eventbridge_event(
    bucket: str = BUCKET_NAME, key: str = "inbound/ORD-100/invoice.edi", size: int = 2048
) -> dict[str, Any]:
    """Create an EventBridge event matching the S3 Object Created schema."""
    return {
        "version": "0",
        "id": "test-event-id",
        "detail-type": "Object Created",
        "source": "aws.s3",
        "time": "2025-06-01T10:30:00Z",
        "region": "us-east-1",
        "account": "123456789012",
        "detail": {
            "version": "0",
            "bucket": {"name": bucket},
            "object": {
                "key": key,
                "size": size,
                "etag": "abc123",
                "sequencer": "00123456789",
            },
            "request-id": "s3-req-id",
            "requester": "123456789012",
            "source-ip-address": "10.0.0.1",
            "reason": "PutObject",
        },
    }


def _setup_s3(key: str, body: bytes, content_type: str = "application/octet-stream") -> None:
    """Create a mock S3 bucket and put an object."""
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=BUCKET_NAME)
    s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=body, ContentType=content_type)


def _setup_eventbridge() -> None:
    """Create the mock EventBridge custom bus."""
    eb = boto3.client("events", region_name="us-east-1")
    eb.create_event_bus(Name=EVENT_BUS_NAME)


@pytest.fixture
def lambda_context() -> MagicMock:
    """Create a mock Lambda context."""
    context = MagicMock()
    context.request_id = "test-request-id-doc"
    return context


def test_handler_edi_document(aws_mocks: None, lambda_context: MagicMock) -> None:
    """Test processing an EDI document upload."""
    _setup_s3("inbound/ORD-100/invoice.edi", b"ISA*00*...", "application/edi-x12")
    _setup_eventbridge()

    event = _make_s3_eventbridge_event()
    response = index.handler(event, lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["orderId"] == "ORD-100"
    assert body["documentType"] == "EDI"


def test_handler_bol_document(aws_mocks: None, lambda_context: MagicMock) -> None:
    """Test processing a Bill of Lading upload."""
    _setup_s3("inbound/ORD-200/shipping.bol", b"BOL content")
    _setup_eventbridge()

    event = _make_s3_eventbridge_event(key="inbound/ORD-200/shipping.bol", size=512)
    response = index.handler(event, lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["orderId"] == "ORD-200"
    assert body["documentType"] == "BOL"


def test_handler_unknown_extension(aws_mocks: None, lambda_context: MagicMock) -> None:
    """Test processing a document with an unsupported extension."""
    _setup_s3("inbound/ORD-300/readme.txt", b"text")
    _setup_eventbridge()

    event = _make_s3_eventbridge_event(key="inbound/ORD-300/readme.txt")
    response = index.handler(event, lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["documentType"] == "UNKNOWN"


def test_handler_flat_key_no_order_id(aws_mocks: None, lambda_context: MagicMock) -> None:
    """Test processing a document with a flat key (no order ID in path)."""
    _setup_s3("invoice.edi", b"ISA*00*...")
    _setup_eventbridge()

    event = _make_s3_eventbridge_event(key="invoice.edi")
    response = index.handler(event, lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["orderId"] == "unknown"


def test_handler_publishes_downstream_event(aws_mocks: None, lambda_context: MagicMock) -> None:
    """Test that handler publishes order.document-uploaded.v1 event."""
    _setup_s3("inbound/ORD-400/delivery.pod", b"POD data", "application/pdf")

    # Spy on put_events via mock (don't need real EventBridge for this)
    mock_eb_client = MagicMock()
    with patch.object(index, "get_events_client", return_value=mock_eb_client):
        event = _make_s3_eventbridge_event(key="inbound/ORD-400/delivery.pod", size=1024)
        index.handler(event, lambda_context)

    mock_eb_client.put_events.assert_called_once()
    call_args = mock_eb_client.put_events.call_args
    entries = call_args[1].get("Entries") or call_args[0][0].get("Entries")
    published = entries[0]
    assert published["Source"] == "document.processor"
    assert published["DetailType"] == "order.document-uploaded.v1"
    detail = json.loads(published["Detail"])
    assert detail["orderId"] == "ORD-400"
    assert detail["documentType"] == "POD"
    assert detail["bucket"] == BUCKET_NAME
    assert detail["key"] == "inbound/ORD-400/delivery.pod"


def test_handler_s3_head_failure(lambda_context: MagicMock) -> None:
    """Test graceful handling when S3 head_object fails."""
    mock_s3 = MagicMock()
    mock_s3.head_object.side_effect = Exception("Access Denied")
    mock_eb = MagicMock()

    with patch.object(index, "get_s3_client", return_value=mock_s3), patch.object(
        index, "get_events_client", return_value=mock_eb
    ):
        event = _make_s3_eventbridge_event(key="inbound/ORD-500/data.csv")
        response = index.handler(event, lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["orderId"] == "ORD-500"
    assert body["documentType"] == "CSV"
    mock_eb.put_events.assert_called_once()


def test_log_structured() -> None:
    """Test structured logging function."""
    index.log_structured("info", "Test message", key="value")
