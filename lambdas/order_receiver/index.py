import json
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

eventbridge = boto3.client('events')
EVENT_BUS_NAME = os.environ['EVENT_BUS_NAME']


def handler(event, context):
    """
    Receives order from API Gateway, logs it, and publishes to EventBridge.
    """
    # Log the incoming payload
    logger.info(f"Received order: {json.dumps(event)}")

    # Extract the body from API Gateway event
    body = event.get('body', '{}')
    if isinstance(body, str):
        order_data = json.loads(body)
    else:
        order_data = body

    logger.info(f"Order data: {json.dumps(order_data)}")

    # Publish event to EventBridge
    try:
        response = eventbridge.put_events(
            Entries=[
                {
                    'Source': 'public.api',
                    'DetailType': 'order.received.v1',
                    'Detail': json.dumps(order_data),
                    'EventBusName': EVENT_BUS_NAME
                }
            ]
        )
        logger.info(f"Published event to EventBridge: {json.dumps(response)}")
    except Exception as e:
        logger.error(f"Error publishing to EventBridge: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error processing order'})
        }

    # Return success response immediately (async pattern)
    return {
        'statusCode': 202,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': 'Order received and processing',
            'orderId': order_data.get('orderId', 'unknown')
        })
    }
