from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_events as events,
    aws_events_targets as targets,
    aws_sqs as sqs,
    aws_iam as iam,
    Duration,
)
from constructs import Construct


class OrderProcessingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create custom EventBridge bus
        event_bus = events.EventBus(
            self, "OrderProcessingBus",
            event_bus_name="order-processing-bus"
        )

        # Create SQS queue for email notifications
        email_queue = sqs.Queue(
            self, "EmailQueue",
            queue_name="order-notifications-queue"
        )

        # Create Lambda function: order-receiver
        order_receiver_fn = lambda_.Function(
            self, "OrderReceiverFunction",
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
            self, "NotifierFunction",
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

        # Create Lambda function: marketplace
        marketplace_fn = lambda_.Function(
            self, "MarketplaceFunction",
            function_name="marketplace",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="index.handler",
            code=lambda_.Code.from_asset("lambdas/marketplace"),
            timeout=Duration.seconds(30),
        )

        # Create EventBridge rules to route events
        notifier_rule = events.Rule(
            self, "NotifierRule",
            event_bus=event_bus,
            event_pattern=events.EventPattern(
                source=["public.api"],
                detail_type=["order.received.v1"]
            ),
            rule_name="route-to-notifier"
        )
        notifier_rule.add_target(targets.LambdaFunction(notifier_fn))

        marketplace_rule = events.Rule(
            self, "MarketplaceRule",
            event_bus=event_bus,
            event_pattern=events.EventPattern(
                source=["public.api"],
                detail_type=["order.received.v1"]
            ),
            rule_name="route-to-marketplace"
        )
        marketplace_rule.add_target(targets.LambdaFunction(marketplace_fn))

        # Create API Gateway
        api = apigateway.RestApi(
            self, "OrdersApi",
            rest_api_name="Orders API",
            description="API for receiving order events",
            deploy_options=apigateway.StageOptions(
                stage_name="prod"
            )
        )

        # Create /orders resource and POST method
        orders_resource = api.root.add_resource("orders")

        # Create Lambda integration
        integration = apigateway.LambdaIntegration(
            order_receiver_fn,
            proxy=True
        )

        orders_resource.add_method("POST", integration)
