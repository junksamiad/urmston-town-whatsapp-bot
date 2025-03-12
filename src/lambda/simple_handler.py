# lambda/simple_handler.py
import json
import logging
import os
import uuid
import boto3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
ssm_client = boto3.client('ssm')

# Function to get parameter from SSM if it starts with a slash
def get_parameter_value(param_name, default_value=None):
    param_value = os.environ.get(param_name, default_value)
    
    # If the parameter value starts with a slash, it's an SSM parameter path
    if param_value and param_value.startswith('/'):
        try:
            response = ssm_client.get_parameter(Name=param_value)
            return response['Parameter']['Value']
        except Exception as e:
            logger.error(f"Error retrieving parameter {param_name} from SSM: {str(e)}")
            return default_value
    
    return param_value

# Lambda handler function
def simple_handler(event, context):
    """Simple Lambda handler function for testing"""
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
    
    # Get SSM values if environment variables are SSM paths
    ssm_values = {
        'TWILIO_ACCOUNT_SID': get_parameter_value('TWILIO_ACCOUNT_SID', 'Not retrieved'),
        'TWILIO_AUTH_TOKEN': get_parameter_value('TWILIO_AUTH_TOKEN', 'Not retrieved'),
        'TWILIO_PHONE_NUMBER': get_parameter_value('TWILIO_PHONE_NUMBER', 'Not retrieved'),
        'TWILIO_TEMPLATE_SID': get_parameter_value('TWILIO_TEMPLATE_SID', 'Not retrieved')
    }
    
    # Return environment variables and SSM values
    return {
        'statusCode': 200,
        'body': json.dumps({
            'environment_variables': env_vars,
            'ssm_values': ssm_values,
            'request_id': request_id,
            'event': event
        })
    } 