#!/usr/bin/env python
"""
Independent script to test Twilio API for sending WhatsApp template messages.
This script doesn't rely on any existing codebase and has hardcoded credentials and variables.
"""

import json
import logging
import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
TWILIO_TEMPLATE_SID = os.environ.get('TWILIO_TEMPLATE_SID')

# Log the environment variables
logger.info(f"TWILIO_ACCOUNT_SID: {TWILIO_ACCOUNT_SID}")
logger.info(f"TWILIO_AUTH_TOKEN: {TWILIO_AUTH_TOKEN[:4]}...") # Only log first 4 chars for security
logger.info(f"TWILIO_PHONE_NUMBER: {TWILIO_PHONE_NUMBER}")
logger.info(f"TWILIO_TEMPLATE_SID: {TWILIO_TEMPLATE_SID}")

# Hardcoded recipient phone number
TO_PHONE_NUMBER = '+447835065013'

# Hardcoded template variables
# TEMPLATE_VARIABLES = {
#     "parent_first_name": "Jane",
#     "player_first_name": "John",
#     "team_name": "Panthers",
#     "age_group": "u11s",
#     "current_season": "2025-26",
#     "membership_fee_amount": "40",
#     "subscription_fee_amount": "26",
#     "team_manager_1_full_name": "Alex Johnson",
#     "team_manager_1_tel": "+447700900001"
# }

def send_whatsapp_template():
    """Send a WhatsApp template message using Twilio API"""
    logger.info("Initializing Twilio client...")
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Convert template variables to JSON string
        # content_variables_json = json.dumps(TEMPLATE_VARIABLES)
        # logger.info(f"Template variables: {content_variables_json}")
        
        logger.info(f"Sending template message to {TO_PHONE_NUMBER}...")
        logger.info(f"Using template SID: {TWILIO_TEMPLATE_SID}")
        logger.info(f"From phone number: {TWILIO_PHONE_NUMBER}")
        
        # Send the message
        message = client.messages.create(
            content_sid=TWILIO_TEMPLATE_SID,
            from_=TWILIO_PHONE_NUMBER,
            to=f"whatsapp:{TO_PHONE_NUMBER}"
            # content_variables=content_variables_json
        )
        
        logger.info(f"Message sent successfully! SID: {message.sid}")
        logger.info(f"Message status: {message.status}")
        return message.sid
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp template message: {str(e)}")
        raise

def main():
    """Main function to run the test"""
    logger.info("Starting Twilio API test...")
    try:
        message_sid = send_whatsapp_template()
        logger.info(f"Test completed successfully. Message SID: {message_sid}")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    main() 