"""Unit tests for CDK stack."""
import aws_cdk as cdk
from aws_cdk import assertions

from order_processing_stack import OrderProcessingStack


def test_lambda_functions_created() -> None:
    """Test that all Lambda functions are created."""
    app = cdk.App()
    stack = OrderProcessingStack(app, "TestStack")
    template = assertions.Template.from_stack(stack)

    # Check that 3 Lambda functions are created
    template.resource_count_is("AWS::Lambda::Function", 3)

    # Check specific Lambda functions
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {"FunctionName": "order-receiver", "Runtime": "python3.13"},
    )
    template.has_resource_properties(
        "AWS::Lambda::Function", {"FunctionName": "notifier", "Runtime": "python3.13"}
    )
    template.has_resource_properties(
        "AWS::Lambda::Function", {"FunctionName": "marketplace", "Runtime": "python3.13"}
    )


def test_eventbridge_bus_created() -> None:
    """Test that EventBridge custom bus is created."""
    app = cdk.App()
    stack = OrderProcessingStack(app, "TestStack")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties(
        "AWS::Events::EventBus", {"Name": "order-processing-bus"}
    )


def test_eventbridge_rules_created() -> None:
    """Test that EventBridge rules are created."""
    app = cdk.App()
    stack = OrderProcessingStack(app, "TestStack")
    template = assertions.Template.from_stack(stack)

    # Check that 2 EventBridge rules are created
    template.resource_count_is("AWS::Events::Rule", 2)

    # Check rule patterns
    template.has_resource_properties(
        "AWS::Events::Rule",
        {
            "EventPattern": {
                "source": ["public.api"],
                "detail-type": ["order.received.v1"],
            }
        },
    )


def test_api_gateway_created() -> None:
    """Test that API Gateway is created."""
    app = cdk.App()
    stack = OrderProcessingStack(app, "TestStack")
    template = assertions.Template.from_stack(stack)

    # Check that API Gateway REST API is created
    template.has_resource_properties(
        "AWS::ApiGateway::RestApi",
        {"Name": "Orders API", "Description": "API for receiving order events"},
    )

    # Check that deployment stage is "prod"
    template.has_resource_properties(
        "AWS::ApiGateway::Stage",
        {"StageName": "prod"},
    )


def test_sqs_queue_created() -> None:
    """Test that SQS queue is created."""
    app = cdk.App()
    stack = OrderProcessingStack(app, "TestStack")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties(
        "AWS::SQS::Queue", {"QueueName": "order-notifications-queue"}
    )


def test_lambda_permissions() -> None:
    """Test that Lambda functions have correct IAM permissions."""
    app = cdk.App()
    stack = OrderProcessingStack(app, "TestStack")
    template = assertions.Template.from_stack(stack)

    # Check that IAM roles are created for Lambda functions
    template.resource_count_is("AWS::IAM::Role", 3)

    # Check that EventBridge and SQS permissions are granted
    # This is done via IAM policies attached to the Lambda roles
    template.resource_count_is("AWS::IAM::Policy", 3)
