#!/usr/bin/env python3
"""AWS CDK app entry point for the Order Processing stack."""
import aws_cdk as cdk

from infrastructure.order_processing_stack import OrderProcessingStack

app = cdk.App()
OrderProcessingStack(app, "OrderProcessingStack")

app.synth()
