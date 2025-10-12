"""CDK Stack for Order Processing with EventBridge."""

from typing import Any

from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    Tags,
)
from aws_cdk import (
    aws_apigateway as apigateway,
)
from aws_cdk import (
    aws_cloudwatch as cloudwatch,
)
from aws_cdk import (
    aws_cloudwatch_actions as cw_actions,
)
from aws_cdk import (
    aws_events as events,
)
from aws_cdk import (
    aws_events_targets as targets,
)
from aws_cdk import (
    aws_lambda as lambda_,
)
from aws_cdk import (
    aws_logs as logs,
)
from aws_cdk import (
    aws_sns as sns,
)
from aws_cdk import (
    aws_sqs as sqs,
)
from constructs import Construct


class OrderProcessingStack(Stack):
    """
    CDK Stack that creates an event-driven order processing system.

    This stack creates:
    - API Gateway with POST /orders endpoint
    - Lambda function to receive orders and publish to EventBridge
    - Custom EventBridge bus for order events
    - Three Lambda functions to consume events (notifier, inventory, and document)
    - SQS queue for email notifications
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        """
        Initialize the Order Processing Stack.

        Args:
            scope: CDK app scope
            construct_id: Unique identifier for this stack
            **kwargs: Additional stack properties
        """
        super().__init__(scope, construct_id, **kwargs)

        # Create custom EventBridge bus
        event_bus = events.EventBus(
            self, "OrderProcessingBus", event_bus_name="order-processing-bus"
        )

        # Create SQS queue for email notifications
        email_queue = sqs.Queue(self, "EmailQueue", queue_name="order-notifications-queue")

        # Create Lambda function: order-receiver
        order_receiver_fn = lambda_.Function(
            self,
            "OrderReceiverFunction",
            function_name="order-receiver",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambdas/order_receiver"),
            environment={
                "EVENT_BUS_NAME": event_bus.event_bus_name,
            },
            timeout=Duration.seconds(30),
        )

        # Grant permission to publish events to the custom bus
        event_bus.grant_put_events_to(order_receiver_fn)

        # Create Lambda function: notifier
        notifier_fn = lambda_.Function(
            self,
            "NotifierFunction",
            function_name="notifier",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambdas/notifier"),
            environment={
                "QUEUE_URL": email_queue.queue_url,
            },
            timeout=Duration.seconds(30),
        )

        # Grant permission to send messages to SQS
        email_queue.grant_send_messages(notifier_fn)

        # Create Lambda function: inventory
        inventory_fn = lambda_.Function(
            self,
            "InventoryFunction",
            function_name="inventory",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambdas/inventory"),
            timeout=Duration.seconds(30),
        )

        # Create Lambda function: document
        document_fn = lambda_.Function(
            self,
            "DocumentFunction",
            function_name="document",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambdas/document"),
            timeout=Duration.seconds(30),
        )

        # Create CloudWatch Log Groups for EventBridge rules
        notifier_rule_log_group = logs.LogGroup(
            self,
            "NotifierRuleLogGroup",
            log_group_name="/aws/events/route-to-notifier",
            retention=logs.RetentionDays.ONE_WEEK,
        )

        inventory_rule_log_group = logs.LogGroup(
            self,
            "InventoryRuleLogGroup",
            log_group_name="/aws/events/route-to-inventory",
            retention=logs.RetentionDays.ONE_WEEK,
        )

        document_rule_log_group = logs.LogGroup(
            self,
            "DocumentRuleLogGroup",
            log_group_name="/aws/events/route-to-document",
            retention=logs.RetentionDays.ONE_WEEK,
        )

        # Create EventBridge rules to route events
        notifier_rule = events.Rule(
            self,
            "NotifierRule",
            event_bus=event_bus,
            event_pattern=events.EventPattern(
                source=["public.api"], detail_type=["order.received.v1"]
            ),
            rule_name="route-to-notifier",
        )
        notifier_rule.add_target(targets.LambdaFunction(notifier_fn))
        notifier_rule.add_target(targets.CloudWatchLogGroup(notifier_rule_log_group))

        inventory_rule = events.Rule(
            self,
            "InventoryRule",
            event_bus=event_bus,
            event_pattern=events.EventPattern(
                source=["public.api"],
                detail_type=["order.received.v1"],
                detail={"purpose": [{"anything-but": ["update"]}]},
            ),
            rule_name="route-to-inventory",
        )
        inventory_rule.add_target(targets.LambdaFunction(inventory_fn))
        inventory_rule.add_target(targets.CloudWatchLogGroup(inventory_rule_log_group))

        document_rule = events.Rule(
            self,
            "DocumentRule",
            event_bus=event_bus,
            event_pattern=events.EventPattern(
                source=["public.api"], detail_type=["order.received.v1"]
            ),
            rule_name="route-to-document",
        )
        document_rule.add_target(targets.LambdaFunction(document_fn))
        document_rule.add_target(targets.CloudWatchLogGroup(document_rule_log_group))

        # Create CloudWatch Log Group for API Gateway access logs
        api_log_group = logs.LogGroup(
            self,
            "ApiGatewayAccessLogs",
            log_group_name="/aws/apigateway/public-api-access",
            retention=logs.RetentionDays.ONE_WEEK,
        )

        # Create API Gateway
        api = apigateway.RestApi(
            self,
            "PublicApi",
            rest_api_name="Public API",
            description="API for receiving order events",
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                access_log_destination=apigateway.LogGroupLogDestination(api_log_group),
                access_log_format=apigateway.AccessLogFormat.json_with_standard_fields(
                    caller=True,
                    http_method=True,
                    ip=True,
                    protocol=True,
                    request_time=True,
                    resource_path=True,
                    response_length=True,
                    status=True,
                    user=True,
                ),
            ),
        )

        # Create /orders resource and POST method
        orders_resource = api.root.add_resource("orders")

        # Create Lambda integration
        integration = apigateway.LambdaIntegration(order_receiver_fn, proxy=True)

        orders_resource.add_method("POST", integration)

        # Create SNS topic for alarm notifications
        alarm_topic = sns.Topic(
            self,
            "AlarmTopic",
            topic_name="order-processing-alarms",
            display_name="Order Processing Alarms",
        )

        # CloudWatch Alarms for Lambda errors
        order_receiver_error_alarm = cloudwatch.Alarm(
            self,
            "OrderReceiverErrorAlarm",
            alarm_name="order-receiver-errors",
            alarm_description="Alert when order-receiver Lambda has errors",
            metric=order_receiver_fn.metric_errors(period=Duration.minutes(5)),
            threshold=1,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        )
        order_receiver_error_alarm.add_alarm_action(cw_actions.SnsAction(alarm_topic))

        notifier_error_alarm = cloudwatch.Alarm(
            self,
            "NotifierErrorAlarm",
            alarm_name="notifier-errors",
            alarm_description="Alert when notifier Lambda has errors",
            metric=notifier_fn.metric_errors(period=Duration.minutes(5)),
            threshold=1,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        )
        notifier_error_alarm.add_alarm_action(cw_actions.SnsAction(alarm_topic))

        inventory_error_alarm = cloudwatch.Alarm(
            self,
            "InventoryErrorAlarm",
            alarm_name="inventory-errors",
            alarm_description="Alert when inventory Lambda has errors",
            metric=inventory_fn.metric_errors(period=Duration.minutes(5)),
            threshold=1,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        )
        inventory_error_alarm.add_alarm_action(cw_actions.SnsAction(alarm_topic))

        document_error_alarm = cloudwatch.Alarm(
            self,
            "DocumentErrorAlarm",
            alarm_name="document-errors",
            alarm_description="Alert when document Lambda has errors",
            metric=document_fn.metric_errors(period=Duration.minutes(5)),
            threshold=1,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        )
        document_error_alarm.add_alarm_action(cw_actions.SnsAction(alarm_topic))

        # CloudWatch Alarm for SQS queue depth
        queue_depth_alarm = cloudwatch.Alarm(
            self,
            "QueueDepthAlarm",
            alarm_name="email-queue-depth",
            alarm_description="Alert when email queue has too many messages",
            metric=email_queue.metric_approximate_number_of_messages_visible(
                period=Duration.minutes(5)
            ),
            threshold=100,
            evaluation_periods=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        )
        queue_depth_alarm.add_alarm_action(cw_actions.SnsAction(alarm_topic))

        # Add cost allocation tags
        Tags.of(self).add("Project", "OrderProcessing")
        Tags.of(self).add("Environment", "Demo")
        Tags.of(self).add("ManagedBy", "CDK")
        Tags.of(self).add("CostCenter", "Engineering")

        # Stack outputs
        CfnOutput(
            self,
            "OrdersApiEndpoint",
            value=api.url,
            description="API Gateway endpoint URL for POST /orders",
            export_name="OrderProcessingApiUrl",
        )

        CfnOutput(
            self,
            "AlarmTopicArn",
            value=alarm_topic.topic_arn,
            description="SNS topic ARN for CloudWatch alarms",
            export_name="OrderProcessingAlarmTopicArn",
        )
