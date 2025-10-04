import json
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client('sqs')
QUEUE_URL = os.environ['QUEUE_URL']


def handler(event, context):
    """
    Receives order event from EventBridge and queues it for email notification.
    This simulates notifying the Sales team via email by placing the event in an SQS queue.
    """
    # Log the event received from EventBridge
    logger.info(f"Notifier received event: {json.dumps(event)}")

    # Extract the detail from the EventBridge event
    detail = event.get('detail', {})
    logger.info(f"Order detail for notification: {json.dumps(detail)}")

    # Send message to SQS queue for email processing
    try:
        response = sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps({
                'recipient': 'sales@example.com',
                'subject': f"New Order Received: {detail.get('orderId', 'unknown')}",
                'orderData': detail
            })
        )
        logger.info(f"Message sent to SQS queue: {response['MessageId']}")
    except Exception as e:
        logger.error(f"Error sending message to SQS: {str(e)}")
        raise

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Notification queued successfully'})
    }
