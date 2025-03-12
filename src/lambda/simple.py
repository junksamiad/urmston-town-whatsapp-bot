# lambda/simple.py
import json
import logging
import os
import uuid

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Lambda handler function
def lambda_handler(event, context):
    """Main Lambda handler function"""
    # Generate a unique request ID for tracking
    request_id = str(uuid.uuid4())
    
    # Log the incoming event
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Get environment variables
    env_vars = {
        'TWILIO_ACCOUNT_SID': os.environ.get('TWILIO_ACCOUNT_SID', 'Not set'),
        'TWILIO_AUTH_TOKEN': os.environ.get('TWILIO_AUTH_TOKEN', 'Not set'),
        'TWILIO_PHONE_NUMBER': os.environ.get('TWILIO_PHONE_NUMBER', 'Not set'),
        'TWILIO_TEMPLATE_SID': os.environ.get('TWILIO_TEMPLATE_SID', 'Not set')
    }
    
    # Return environment variables
    return {
        'statusCode': 200,
        'body': json.dumps({
            'environment_variables': env_vars,
            'request_id': request_id,
            'event': event
        })
    } 