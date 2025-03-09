import json
import uuid
import os
from dotenv import load_dotenv
from app import handle_trigger

# Load environment variables from .env file
load_dotenv()

# Print environment variables for debugging
print("Environment variables:")
print(f"TWILIO_ACCOUNT_SID: {os.environ.get('TWILIO_ACCOUNT_SID')}")
print(f"TWILIO_AUTH_TOKEN: {os.environ.get('TWILIO_AUTH_TOKEN')[:4]}...") # Only log first 4 chars for security
print(f"TWILIO_PHONE_NUMBER: {os.environ.get('TWILIO_PHONE_NUMBER')}")
print(f"TWILIO_TEMPLATE_SID: {os.environ.get('TWILIO_TEMPLATE_SID')}")

# Simulate an API Gateway event
event = {
    'body': json.dumps({
        "player_first_name": "Stefan",
        "player_last_name": "Hayton",
        "team_name": "Wolves",
        "age_group": "u7s",
        "team_manager_1_full_name": "Lee Hayton",
        "team_manager_1_tel": "07835 065 013",
        "current_registration_season": "2025-26",
        "parent_first_name": "Lee",
        "parent_last_name": "Hayton",
        "parent_tel": "+447835065013",
        "membership_fee_amount": "40",
        "subscription_fee_amount": "22.50"
    })
}

# Generate a request ID
request_id = str(uuid.uuid4())

# Call the handler
response = handle_trigger(event, request_id)
print(json.dumps(response, indent=2)) 