import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """
    Receives order event from EventBridge and logs it.
    This function processes orders for marketplace integration.
    """
    # Log the event received from EventBridge
    logger.info(f"Marketplace received event: {json.dumps(event)}")

    # Extract the detail from the EventBridge event
    detail = event.get('detail', {})
    logger.info(f"Processing order for marketplace: {json.dumps(detail)}")

    # Simulate marketplace processing
    order_id = detail.get('orderId', 'unknown')
    logger.info(f"Order {order_id} processed for marketplace integration")

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Order processed for marketplace'})
    }
