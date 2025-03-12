# lambda/app.py
import json
import logging
import os
import uuid
import boto3
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
sqs_client = boto3.client('sqs')
WEBHOOK_QUEUE_URL = os.environ.get('WEBHOOK_QUEUE_URL')

# API key for /trigger endpoint
VALID_API_KEY = os.environ.get('API_KEY', 'YOUR_API_KEY_HERE')

# Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
TWILIO_TEMPLATE_SID = os.environ.get('TWILIO_TEMPLATE_SID', 'HXbae39f90eb98c2550ec550a2b5f4d2a1')

# Initialize Twilio client if credentials are available
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def lambda_handler(event, context):
    """
    Lambda function that handles both trigger and webhook routes
    for the football registration WhatsApp bot.
    """
    # Generate request ID for tracking
    request_id = str(uuid.uuid4())
    
    # Add request ID to logger context
    logger_context = {'request_id': request_id}
    
    try:
        # Log the entire event for debugging
        logger.info(f"Received event: {json.dumps(event)}", extra=logger_context)
        
        # Check if this is an SQS event (batch processing)
        if 'Records' in event and event.get('Records', []) and 'eventSource' in event['Records'][0] and event['Records'][0]['eventSource'] == 'aws:sqs':
            return process_sqs_messages(event, context, request_id)
        
        # Determine which route was called
        # Check for API Gateway v2 format first
        if 'requestContext' in event and 'http' in event['requestContext']:
            path = event['requestContext']['http']['path']
        elif 'rawPath' in event:
            path = event['rawPath']
        else:
            # Fall back to the original path extraction
            path = event.get('path', '')
            
        logger.info(f"Path: {path}", extra=logger_context)
        
        if '/trigger' in path:
            # Validate API key for /trigger endpoint
            api_key = None
            
            # Extract API key from headers
            if 'headers' in event:
                headers = event['headers']
                api_key = headers.get('x-api-key') or headers.get('X-Api-Key')
            
            # Check if API key is valid
            if api_key != VALID_API_KEY:
                logger.warning(f"Invalid or missing API key: {api_key}", extra=logger_context)
                return {
                    'statusCode': 403,
                    'body': json.dumps({
                        'message': 'Forbidden: Invalid or missing API key',
                        'request_id': request_id
                    })
                }
            
            # Process trigger requests synchronously (direct Lambda invocation)
            return handle_trigger(event, request_id)
        elif '/webhook' in path:
            # For webhook, process directly if SQS queue URL is not available
            if not WEBHOOK_QUEUE_URL:
                logger.warning("SQS queue URL not available, processing webhook directly", extra=logger_context)
                return handle_webhook(event, request_id)
            else:
                # Send to SQS and return immediate response
                return queue_webhook_message(event, request_id)
        else:
            logger.error(f"Route not found for path: {path}", extra=logger_context)
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': 'Route not found',
                    'request_id': request_id
                })
            }
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", extra=logger_context)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing request',
                'error': str(e),
                'request_id': request_id
            })
        }

def handle_trigger(event, request_id):
    """Handle the trigger route for initiating registration"""
    logger_context = {'request_id': request_id}
    
    try:
        # Parse the incoming JSON payload
        body = json.loads(event.get('body', '{}'))
        
        # Extract key information
        player_first_name = body.get('player_first_name', '')
        player_last_name = body.get('player_last_name', '')
        player_full_name = f"{player_first_name} {player_last_name}".strip() or 'Unknown Player'
        
        parent_first_name = body.get('parent_first_name', '')
        parent_last_name = body.get('parent_last_name', '')
        parent_full_name = f"{parent_first_name} {parent_last_name}".strip() or 'Unknown Parent'
        
        parent_tel = body.get('parent_tel', 'Unknown Phone')
        team_name = body.get('team_name', 'Unknown Team')
        age_group = body.get('age_group', 'Unknown Age Group')
        team_manager_1_full_name = body.get('team_manager_1_full_name', 'Team Manager')
        team_manager_1_tel = body.get('team_manager_1_tel', 'Not provided')
        current_registration_season = body.get('current_registration_season', '2025-26')
        membership_fee_amount = body.get('membership_fee_amount', '40')
        subscription_fee_amount = body.get('subscription_fee_amount', '26')
        
        # Log the received data
        logger.info(f"Received registration data: {json.dumps(body)}", extra=logger_context)
        logger.info(f"Processing registration for {player_full_name}, parent: {parent_full_name}, phone: {parent_tel}, team: {team_name} {age_group}", extra=logger_context)
        
        # Create context object
        context_obj = {
            "player_data": {
                "player_first_name": player_first_name,
                "player_last_name": player_last_name,
                "team_name": team_name,
                "age_group": age_group,
                "team_manager_1_full_name": team_manager_1_full_name,
                "team_manager_1_tel": team_manager_1_tel,
                "current_registration_season": current_registration_season,
                "parent_first_name": parent_first_name,
                "parent_last_name": parent_last_name,
                "parent_tel": parent_tel,
                "membership_fee_amount": membership_fee_amount,
                "subscription_fee_amount": subscription_fee_amount
            },
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id
        }
        
        # Template variables using numbered format for Twilio templates
        template_variables = {
            "1": parent_first_name,            # Sample: Lee
            "2": player_first_name,            # Sample: Seb
            "3": team_name,                    # Sample: Panthers
            "4": age_group,                    # Sample: u11s
            "5": current_registration_season,  # Sample: 2025-26
            "6": membership_fee_amount,        # Sample: 40
            "7": subscription_fee_amount,      # Sample: 26
            "8": team_manager_1_full_name,     # Sample: Neil Dring
            "9": team_manager_1_tel            # Sample: 07835 065 013
        }
        
        # Send WhatsApp template message to parent with template variables
        try:
            # Use the template_variables dictionary
            message_sid = send_whatsapp_template(parent_tel, template_variables, request_id)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Registration data received successfully',
                    'player': player_full_name,
                    'parent': parent_full_name,
                    'team': f"{team_name} {age_group}",
                    'status': 'message_sent',
                    'message_sid': message_sid,
                    'request_id': request_id
                })
            }
        except Exception as e:
            logger.error(f"Error in handle_trigger: {str(e)}", extra=logger_context)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Error processing registration request',
                    'error': str(e),
                    'request_id': request_id
                })
            }
        
    except Exception as e:
        logger.error(f"Error in handle_trigger: {str(e)}", extra=logger_context)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing registration request',
                'error': str(e),
                'request_id': request_id
            })
        }

def queue_webhook_message(event, request_id):
    """Queue webhook message in SQS for processing"""
    logger_context = {'request_id': request_id}
    
    try:
        # Check if SQS queue URL is available
        if not WEBHOOK_QUEUE_URL:
            logger.warning("SQS queue URL not available, processing webhook directly", extra=logger_context)
            return handle_webhook(event, request_id)
        
        # Send the event to SQS
        message_body = {
            'event': event,
            'request_id': request_id,
            'timestamp': datetime.now().isoformat()
        }
        
        response = sqs_client.send_message(
            QueueUrl=WEBHOOK_QUEUE_URL,
            MessageBody=json.dumps(message_body),
            MessageAttributes={
                'Source': {
                    'DataType': 'String',
                    'StringValue': 'webhook'
                },
                'RequestId': {
                    'DataType': 'String',
                    'StringValue': request_id
                }
            }
        )
        
        logger.info(f"Message sent to SQS: {response['MessageId']}", extra=logger_context)
        
        # Return immediate success response to Twilio
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Webhook received and queued for processing',
                'request_id': request_id
            })
        }
    except Exception as e:
        logger.error(f"Error queuing webhook message: {str(e)}", extra=logger_context)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing webhook',
                'error': str(e),
                'request_id': request_id
            })
        }

def process_sqs_messages(event, context, request_id):
    """Process messages from SQS queue"""
    logger_context = {'request_id': request_id}
    logger.info(f"Processing {len(event['Records'])} SQS messages", extra=logger_context)
    
    processed_count = 0
    error_count = 0
    
    for record in event['Records']:
        try:
            # Parse the SQS message body
            message_body = json.loads(record['body'])
            message_request_id = message_body.get('request_id', 'unknown')
            message_logger_context = {'request_id': message_request_id}
            
            logger.info(f"Processing SQS message with request ID: {message_request_id}", extra=message_logger_context)
            
            # Extract the original event from the message body
            original_event = message_body.get('event', {})
            
            # Process as webhook
            handle_webhook(original_event, message_request_id)
            
            processed_count += 1
            
        except Exception as e:
            error_count += 1
            logger.error(f"Error processing SQS message: {str(e)}", extra=logger_context)
    
    logger.info(f"Completed processing SQS messages. Processed: {processed_count}, Errors: {error_count}", extra=logger_context)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Processed {processed_count} messages with {error_count} errors',
            'request_id': request_id
        })
    }

def handle_webhook(event, request_id):
    """Handle the webhook route for incoming WhatsApp messages"""
    logger_context = {'request_id': request_id}
    
    try:
        # Parse the incoming webhook data from Twilio
        body = json.loads(event.get('body', '{}'))
        
        # Extract message SID for idempotency check
        message_sid = body.get('MessageSid', '')
        
        # Check if we've already processed this message (implement with database in Phase 4)
        # For now, we'll log and continue
        logger.info(f"Processing message with SID: {message_sid}", extra=logger_context)
        
        # Log the received message
        logger.info(f"Received webhook data: {json.dumps(body)}", extra=logger_context)
        
        # For Phase 2, we'll just acknowledge receipt
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Webhook received successfully',
                'request_id': request_id
            })
        }
    except Exception as e:
        logger.error(f"Error in handle_webhook: {str(e)}", extra=logger_context)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing webhook',
                'error': str(e),
                'request_id': request_id
            })
        }

def send_whatsapp_template(to_number, template_variables, request_id):
    """Send a WhatsApp template message using Twilio"""
    logger_context = {'request_id': request_id}
    
    try:
        if not twilio_client:
            logger.warning("Twilio client not initialized. Check environment variables.", extra=logger_context)
            return "twilio_client_not_initialized"
        
        # Log the template SID being used
        logger.info(f"Using template SID: {TWILIO_TEMPLATE_SID}", extra=logger_context)
        
        # If template_variables is None, don't include content_variables parameter
        if template_variables is None:
            logger.info(f"Sending template message without variables to {to_number}...", extra=logger_context)
            
            message = twilio_client.messages.create(
                content_sid=TWILIO_TEMPLATE_SID,
                from_=TWILIO_PHONE_NUMBER,
                to=f"whatsapp:{to_number}"
            )
        else:
            # Convert template_variables to a JSON string
            content_variables_json = json.dumps(template_variables)
            logger.info(f"Sending template message with variables: {content_variables_json}", extra=logger_context)
                
            message = twilio_client.messages.create(
                content_sid=TWILIO_TEMPLATE_SID,
                from_=TWILIO_PHONE_NUMBER,
                to=f"whatsapp:{to_number}",
                content_variables=content_variables_json
            )
        
        logger.info(f"Template message sent to {to_number}: {message.sid}", extra=logger_context)
        return message.sid
    except Exception as e:
        logger.error(f"Error sending WhatsApp template message: {str(e)}", extra=logger_context)
        raise

def send_whatsapp_message(to_number, message, request_id):
    """Send a regular WhatsApp message using Twilio"""
    logger_context = {'request_id': request_id}
    
    try:
        if not twilio_client:
            logger.warning("Twilio client not initialized. Check environment variables.", extra=logger_context)
            return "twilio_client_not_initialized"
            
        message = twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=f"whatsapp:{to_number}"
        )
        logger.info(f"Message sent to {to_number}: {message.sid}", extra=logger_context)
        return message.sid
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}", extra=logger_context)
        raise 