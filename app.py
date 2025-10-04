#!/usr/bin/env python3
import aws_cdk as cdk
from order_processing_stack import OrderProcessingStack

app = cdk.App()
OrderProcessingStack(app, "OrderProcessingStack")

app.synth()
