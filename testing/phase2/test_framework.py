import json
import uuid
import os
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from app import handle_trigger, handle_webhook, send_whatsapp_template, send_whatsapp_message

# Load environment variables
load_dotenv()

class TwilioMock:
    """Mock class for Twilio client to avoid sending actual messages during testing"""
    
    def __init__(self, should_succeed=True, error_message=None):
        self.should_succeed = should_succeed
        self.error_message = error_message
        self.messages_sent = []
    
    def create_message_mock(self, **kwargs):
        """Mock the message creation process"""
        if not self.should_succeed:
            raise Exception(self.error_message or "Simulated Twilio error")
        
        # Store the message details for verification
        self.messages_sent.append(kwargs)
        
        # Create a mock message response
        message_mock = MagicMock()
        message_mock.sid = f"MM{uuid.uuid4().hex[:24]}"
        return message_mock
    
    def setup_mock(self):
        """Set up the mock for patching"""
        mock_messages = MagicMock()
        mock_messages.create.side_effect = self.create_message_mock
        
        mock_client = MagicMock()
        mock_client.messages = mock_messages
        
        return mock_client

def run_test(test_name, event, mock_config=None, expected_status=200):
    """Run a test with the given event and mock configuration"""
    print(f"\n=== Running Test: {test_name} ===")
    
    # Default mock configuration
    if mock_config is None:
        mock_config = {"should_succeed": True}
    
    # Create the Twilio mock
    twilio_mock = TwilioMock(
        should_succeed=mock_config.get("should_succeed", True),
        error_message=mock_config.get("error_message")
    )
    
    # Generate a request ID
    request_id = str(uuid.uuid4())
    
    # Run the test with the mock
    with patch('app.twilio_client', twilio_mock.setup_mock()):
        if "webhook" in test_name.lower():
            response = handle_webhook(event, request_id)
        else:
            response = handle_trigger(event, request_id)
    
    # Print the response
    print(f"Response status code: {response['statusCode']}")
    print(f"Response body: {response['body']}")
    
    # Verify the response status code
    if response['statusCode'] != expected_status:
        print(f"❌ Test failed: Expected status code {expected_status}, got {response['statusCode']}")
        return False
    
    # For successful tests, print the message details
    if mock_config.get("should_succeed", True) and "trigger" in test_name.lower():
        if twilio_mock.messages_sent:
            print("\nMessage details that would have been sent:")
            for msg in twilio_mock.messages_sent:
                print(f"  To: {msg.get('to')}")
                print(f"  From: {msg.get('from_')}")
                print(f"  Template SID: {msg.get('content_sid')}")
                if msg.get('content_variables'):
                    print(f"  Variables: {json.dumps(msg.get('content_variables'), indent=2)}")
                else:
                    print("  Variables: None (would use fallback values)")
    
    print(f"✅ Test passed: {test_name}")
    return True

def create_test_event(payload=None, headers=None, path="/trigger"):
    """Create a test event with the given payload and headers"""
    if payload is None:
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
            "parent_tel": "+447835065013",
            "membership_fee_amount": "40",
            "subscription_fee_amount": "26"
        }
    
    if headers is None:
        headers = {
            "x-api-key": os.environ.get("API_KEY", "test-api-key")
        }
    
    return {
        "path": path,
        "headers": headers,
        "body": json.dumps(payload)
    } 