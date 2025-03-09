import json
import uuid
import os
import sys
import time
from unittest.mock import MagicMock
from dotenv import load_dotenv

# Add the src/lambda directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/lambda')))

from app import lambda_handler

# Load environment variables
load_dotenv()

def run_real_test(test_name, payload, phone_number):
    """Run a test that actually sends a WhatsApp message"""
    print(f"\n=== Running Real Message Test: {test_name} ===")
    print(f"Sending to: {phone_number}")
    
    # Create the event with API Gateway v2 format
    event = {
        "requestContext": {
            "http": {
                "path": "/trigger"
            }
        },
        "headers": {
            "x-api-key": os.environ.get("API_KEY", "test-api-key")
        },
        "body": json.dumps(payload)
    }
    
    # Generate a request ID and create a mock context
    request_id = str(uuid.uuid4())
    mock_context = MagicMock()
    mock_context.aws_request_id = request_id
    
    # Get confirmation from the user
    confirmation = input("Are you sure you want to send a real WhatsApp message? (yes/no): ")
    if confirmation.lower() != "yes":
        print("Test aborted by user.")
        return
    
    # Run the test using lambda_handler
    response = lambda_handler(event, mock_context)
    
    # Print the response
    print(f"Response status code: {response['statusCode']}")
    print(f"Response body: {response['body']}")
    
    # Wait for user confirmation that the message was received
    received = input("Did you receive the WhatsApp message? (yes/no): ")
    if received.lower() == "yes":
        print(f"✅ Test passed: {test_name}")
    else:
        print(f"❌ Test failed: Message not received for {test_name}")

def test_real_messages():
    """Run tests with real message sending (limited)"""
    print("\n=== REAL MESSAGE TESTS (LIMITED) ===")
    print("WARNING: These tests will send actual WhatsApp messages.")
    print("Only run these tests when necessary and with proper authorization.")
    
    # Test 1: Basic message with template variables
    payload = {
        "player_first_name": "Test",
        "player_last_name": "User",
        "team_name": "Test Team",
        "age_group": "u10s",
        "team_manager_1_full_name": "Test Manager",
        "team_manager_1_tel": "+447700900001",
        "current_registration_season": "2025-26",
        "parent_first_name": "Test",
        "parent_last_name": "Parent",
        "parent_tel": "+447835065013",  # Use your test number
        "membership_fee_amount": "40",
        "subscription_fee_amount": "26"
    }
    run_real_test("Basic Message with Template Variables", payload, payload["parent_tel"])
    
    # Wait between tests to avoid rate limiting
    time.sleep(5)
    
    # Test 2: Message with fallback values
    # For this test, we'll modify the app.py temporarily to use fallback values
    print("\nFor the next test, please modify app.py to use fallback values:")
    print("1. Comment out the line with template_variables in handle_trigger")
    print("2. Uncomment the line with send_whatsapp_template(parent_tel, None, request_id)")
    
    confirmation = input("Have you made these changes? (yes/no): ")
    if confirmation.lower() == "yes":
        run_real_test("Message with Fallback Values", payload, payload["parent_tel"])
    else:
        print("Test skipped.")

if __name__ == "__main__":
    test_real_messages() 