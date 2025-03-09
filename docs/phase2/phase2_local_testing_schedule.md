# Phase 2: Local Testing Schedule

This document outlines the comprehensive testing schedule for Phase 2 of the WhatsApp chatbot project. The tests are designed to verify the robustness of our Twilio integration while minimizing actual WhatsApp message sending to avoid potential spam blocks.

## Testing Approach

Our testing approach follows these principles:

1. **Mock-Based Testing**: The majority of our tests use mocks to avoid sending actual WhatsApp messages while still verifying our code logic.
2. **Limited Real Message Testing**: We limit real message testing to just a few messages, with explicit user confirmation required before sending.
3. **Comprehensive Coverage**: We test error handling, edge cases, webhook responses, logging, security, and performance.
4. **Documentation**: Each test includes detailed output to help diagnose any issues that arise.

## Test Execution Schedule

### Phase 1: Mock-Based Testing
1. Set up the test framework
2. Run error handling tests
3. Run edge case tests
4. Run webhook response tests
5. Run logging and security tests
6. Run performance tests (mock-based)

### Phase 2: Limited Real Message Testing
1. Run the basic real message test (1 message)
2. Run the fallback values test (1 message)
3. Fix any issues identified in mock or real testing

### Phase 3 (Optional): Concurrency Testing
1. Gather multiple test phone numbers
2. Run the concurrency test with explicit approval
3. Document the results and any issues

**Note**: These phases don't need to be executed on separate days. They can be run whenever convenient, but should be executed in order, with each phase building on the successful completion of the previous one.

## Test Framework

First, let's create a mock-based testing framework that will allow us to test most functionality without actually sending WhatsApp messages:

```python
# test_framework.py
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
```

## Error Handling Tests

These tests verify that our system properly handles various error scenarios:

```python
# test_error_handling.py
from test_framework import run_test, create_test_event

def test_error_handling():
    """Test various error handling scenarios"""
    print("\n=== ERROR HANDLING TESTS ===")
    
    # Test 1: Invalid phone number
    event = create_test_event({
        "player_first_name": "Test",
        "player_last_name": "User",
        "team_name": "Test Team",
        "age_group": "u10s",
        "team_manager_1_full_name": "Test Manager",
        "team_manager_1_tel": "+447700900001",
        "current_registration_season": "2025-26",
        "parent_first_name": "Test",
        "parent_last_name": "Parent",
        "parent_tel": "invalid-phone",  # Invalid phone number
        "membership_fee_amount": "40",
        "subscription_fee_amount": "26"
    })
    mock_config = {
        "should_succeed": False,
        "error_message": "Invalid 'To' phone number: invalid-phone"
    }
    run_test("Invalid Phone Number", event, mock_config, expected_status=500)
    
    # Test 2: Missing required fields
    event = create_test_event({
        "player_first_name": "Test",
        # Missing player_last_name
        "team_name": "Test Team",
        # Missing other required fields
    })
    run_test("Missing Required Fields", event)
    
    # Test 3: Twilio service disruption
    event = create_test_event()
    mock_config = {
        "should_succeed": False,
        "error_message": "Twilio service unavailable"
    }
    run_test("Twilio Service Disruption", event, mock_config, expected_status=500)
    
    # Test 4: Invalid API key
    event = create_test_event()
    event["headers"]["x-api-key"] = "invalid-api-key"
    run_test("Invalid API Key", event, expected_status=403)
    
    # Test 5: Malformed JSON payload
    event = create_test_event()
    event["body"] = "{ invalid json"
    run_test("Malformed JSON Payload", event, expected_status=500)

if __name__ == "__main__":
    test_error_handling()
```

## Edge Case Tests

These tests verify that our system handles various edge cases correctly:

```python
# test_edge_cases.py
from test_framework import run_test, create_test_event

def test_edge_cases():
    """Test various edge cases"""
    print("\n=== EDGE CASE TESTS ===")
    
    # Test 1: Minimum required fields only
    event = create_test_event({
        "player_first_name": "Test",
        "player_last_name": "User",
        "parent_tel": "+447835065013"
    })
    run_test("Minimum Required Fields", event)
    
    # Test 2: Very long field values
    long_name = "A" * 100  # 100 character name
    event = create_test_event({
        "player_first_name": long_name,
        "player_last_name": long_name,
        "team_name": long_name,
        "age_group": long_name,
        "team_manager_1_full_name": long_name,
        "team_manager_1_tel": "+447700900001",
        "current_registration_season": long_name,
        "parent_first_name": long_name,
        "parent_last_name": long_name,
        "parent_tel": "+447835065013",
        "membership_fee_amount": "40",
        "subscription_fee_amount": "26"
    })
    run_test("Very Long Field Values", event)
    
    # Test 3: Special characters in fields
    special_chars = "!@#$%^&*()_+{}[]|\"':;<>,.?/~`"
    event = create_test_event({
        "player_first_name": f"Test{special_chars}",
        "player_last_name": f"User{special_chars}",
        "team_name": f"Team{special_chars}",
        "age_group": "u10s",
        "team_manager_1_full_name": f"Manager{special_chars}",
        "team_manager_1_tel": "+447700900001",
        "current_registration_season": "2025-26",
        "parent_first_name": f"Parent{special_chars}",
        "parent_last_name": f"Test{special_chars}",
        "parent_tel": "+447835065013",
        "membership_fee_amount": "40",
        "subscription_fee_amount": "26"
    })
    run_test("Special Characters in Fields", event)
    
    # Test 4: International phone numbers
    event = create_test_event({
        "player_first_name": "Test",
        "player_last_name": "User",
        "team_name": "Test Team",
        "age_group": "u10s",
        "team_manager_1_full_name": "Test Manager",
        "team_manager_1_tel": "+12025550142",  # US number
        "current_registration_season": "2025-26",
        "parent_first_name": "Test",
        "parent_last_name": "Parent",
        "parent_tel": "+33123456789",  # French number
        "membership_fee_amount": "40",
        "subscription_fee_amount": "26"
    })
    run_test("International Phone Numbers", event)
    
    # Test 5: Empty strings for optional fields
    event = create_test_event({
        "player_first_name": "Test",
        "player_last_name": "User",
        "team_name": "",
        "age_group": "",
        "team_manager_1_full_name": "",
        "team_manager_1_tel": "",
        "current_registration_season": "",
        "parent_first_name": "Test",
        "parent_last_name": "Parent",
        "parent_tel": "+447835065013",
        "membership_fee_amount": "",
        "subscription_fee_amount": ""
    })
    run_test("Empty Strings for Optional Fields", event)

if __name__ == "__main__":
    test_edge_cases()
```

## Webhook Response Tests

These tests verify that our webhook handler correctly processes incoming WhatsApp messages:

```python
# test_webhook.py
import json
from test_framework import run_test, create_test_event

def test_webhook_responses():
    """Test webhook response handling"""
    print("\n=== WEBHOOK RESPONSE TESTS ===")
    
    # Test 1: Basic webhook message
    webhook_event = {
        "path": "/webhook",
        "body": json.dumps({
            "MessageSid": "SM123456789",
            "From": "whatsapp:+447835065013",
            "To": "whatsapp:+447700148000",
            "Body": "Hello, I'm ready to register"
        })
    }
    run_test("Basic Webhook Message", webhook_event)
    
    # Test 2: Webhook with media
    webhook_event = {
        "path": "/webhook",
        "body": json.dumps({
            "MessageSid": "SM123456789",
            "From": "whatsapp:+447835065013",
            "To": "whatsapp:+447700148000",
            "Body": "Here's my photo",
            "NumMedia": "1",
            "MediaUrl0": "https://example.com/image.jpg",
            "MediaContentType0": "image/jpeg"
        })
    }
    run_test("Webhook with Media", webhook_event)
    
    # Test 3: Webhook with empty body
    webhook_event = {
        "path": "/webhook",
        "body": json.dumps({
            "MessageSid": "SM123456789",
            "From": "whatsapp:+447835065013",
            "To": "whatsapp:+447700148000",
            "Body": ""
        })
    }
    run_test("Webhook with Empty Body", webhook_event)
    
    # Test 4: Malformed webhook payload
    webhook_event = {
        "path": "/webhook",
        "body": "{ invalid json"
    }
    run_test("Malformed Webhook Payload", webhook_event, expected_status=500)
    
    # Test 5: Missing MessageSid
    webhook_event = {
        "path": "/webhook",
        "body": json.dumps({
            "From": "whatsapp:+447835065013",
            "To": "whatsapp:+447700148000",
            "Body": "Hello"
        })
    }
    run_test("Missing MessageSid", webhook_event)

if __name__ == "__main__":
    test_webhook_responses()
```

## Logging and Security Tests

These tests verify that our system properly logs events and handles security concerns:

```python
# test_logging.py
import logging
from io import StringIO
import json
from test_framework import run_test, create_test_event

def test_logging():
    """Test logging functionality"""
    print("\n=== LOGGING TESTS ===")
    
    # Capture logs
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    logger = logging.getLogger()
    logger.addHandler(handler)
    
    # Test 1: Successful request logging
    event = create_test_event()
    run_test("Successful Request Logging", event)
    
    # Test 2: Error logging
    event = create_test_event()
    mock_config = {
        "should_succeed": False,
        "error_message": "Simulated error for logging test"
    }
    run_test("Error Logging", event, mock_config, expected_status=500)
    
    # Check captured logs
    logs = log_capture.getvalue()
    print("\nCaptured Logs:")
    print(logs)
    
    # Verify log content
    if "request_id" in logs and "Received registration data" in logs:
        print("✅ Request ID and payload logging verified")
    else:
        print("❌ Missing expected log entries")
    
    if "Error" in logs and "Simulated error" in logs:
        print("✅ Error logging verified")
    else:
        print("❌ Missing expected error logs")
    
    # Remove the handler to avoid duplicate logs
    logger.removeHandler(handler)

def test_security():
    """Test security features"""
    print("\n=== SECURITY TESTS ===")
    
    # Test 1: Missing API key
    event = create_test_event()
    event["headers"] = {}  # Remove all headers
    run_test("Missing API Key", event, expected_status=403)
    
    # Test 2: Invalid API key
    event = create_test_event()
    event["headers"]["x-api-key"] = "invalid-key"
    run_test("Invalid API Key", event, expected_status=403)
    
    # Test 3: Valid API key
    event = create_test_event()
    event["headers"]["x-api-key"] = os.environ.get("API_KEY", "test-api-key")
    run_test("Valid API Key", event)
    
    # Test 4: Case-insensitive API key header
    event = create_test_event()
    del event["headers"]["x-api-key"]
    event["headers"]["X-Api-Key"] = os.environ.get("API_KEY", "test-api-key")
    run_test("Case-insensitive API Key Header", event)
    
    # Test 5: Sensitive data handling
    # This test checks if sensitive data like auth tokens are properly masked in logs
    print("\nChecking sensitive data handling in logs...")
    print("Note: This is a manual verification step. Ensure that:")
    print("1. Auth tokens are not logged in full")
    print("2. Phone numbers are properly formatted")
    print("3. No sensitive data appears in error messages")

if __name__ == "__main__":
    test_logging()
    test_security()
```

## Performance Tests

These tests verify that our system performs efficiently:

```python
# test_performance.py
import time
from test_framework import run_test, create_test_event
import concurrent.futures

def test_performance():
    """Test performance aspects"""
    print("\n=== PERFORMANCE TESTS ===")
    
    # Test 1: Response time
    event = create_test_event()
    
    print("Testing response time...")
    start_time = time.time()
    run_test("Response Time", event)
    end_time = time.time()
    
    response_time = end_time - start_time
    print(f"Response time: {response_time:.4f} seconds")
    
    # Test 2: Sequential requests (mock-based)
    print("\nTesting sequential requests (mock-based)...")
    
    start_time = time.time()
    for i in range(5):
        event = create_test_event({
            "player_first_name": f"Player{i}",
            "player_last_name": "Test",
            "team_name": "Test Team",
            "age_group": "u10s",
            "team_manager_1_full_name": "Test Manager",
            "team_manager_1_tel": "+447700900001",
            "current_registration_season": "2025-26",
            "parent_first_name": f"Parent{i}",
            "parent_last_name": "Test",
            "parent_tel": "+447835065013",
            "membership_fee_amount": "40",
            "subscription_fee_amount": "26"
        })
        run_test(f"Sequential Request {i+1}", event)
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / 5
    
    print(f"Total time for 5 sequential requests: {total_time:.4f} seconds")
    print(f"Average time per request: {avg_time:.4f} seconds")

if __name__ == "__main__":
    test_performance()
```

## Real Message Testing

These tests send actual WhatsApp messages, but with explicit user confirmation required:

```python
# test_real_messages.py
import json
import uuid
import os
import time
from dotenv import load_dotenv
from app import handle_trigger

# Load environment variables
load_dotenv()

def run_real_test(test_name, payload, phone_number):
    """Run a test that actually sends a WhatsApp message"""
    print(f"\n=== Running Real Message Test: {test_name} ===")
    print(f"Sending to: {phone_number}")
    
    # Create the event
    event = {
        "body": json.dumps(payload)
    }
    
    # Generate a request ID
    request_id = str(uuid.uuid4())
    
    # Get confirmation from the user
    confirmation = input("Are you sure you want to send a real WhatsApp message? (yes/no): ")
    if confirmation.lower() != "yes":
        print("Test aborted by user.")
        return
    
    # Run the test
    response = handle_trigger(event, request_id)
    
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
```

## Concurrency Test (Optional)

This test should only be run if you have multiple phone numbers available and explicit approval:

```python
# test_concurrency.py
import json
import uuid
import os
import time
import concurrent.futures
from dotenv import load_dotenv
from app import handle_trigger

# Load environment variables
load_dotenv()

def send_message(phone_number, index):
    """Send a message to the specified phone number"""
    payload = {
        "player_first_name": f"Player{index}",
        "player_last_name": "Test",
        "team_name": "Test Team",
        "age_group": "u10s",
        "team_manager_1_full_name": "Test Manager",
        "team_manager_1_tel": "+447700900001",
        "current_registration_season": "2025-26",
        "parent_first_name": f"Parent{index}",
        "parent_last_name": "Test",
        "parent_tel": phone_number,
        "membership_fee_amount": "40",
        "subscription_fee_amount": "26"
    }
    
    event = {
        "body": json.dumps(payload)
    }
    
    request_id = str(uuid.uuid4())
    
    start_time = time.time()
    response = handle_trigger(event, request_id)
    end_time = time.time()
    
    return {
        "phone_number": phone_number,
        "index": index,
        "status_code": response["statusCode"],
        "response_body": response["body"],
        "time_taken": end_time - start_time
    }

def test_concurrency():
    """Test concurrent message sending (requires multiple phone numbers)"""
    print("\n=== CONCURRENCY TEST (REQUIRES MULTIPLE PHONE NUMBERS) ===")
    print("WARNING: This test will send actual WhatsApp messages to multiple numbers.")
    print("Only run this test with explicit approval and multiple test phone numbers.")
    
    # Get phone numbers from user
    print("\nEnter phone numbers (one per line, blank line to finish):")
    phone_numbers = []
    while True:
        number = input("> ")
        if not number:
            break
        phone_numbers.append(number)
    
    if len(phone_numbers) < 2:
        print("At least 2 phone numbers are required for this test.")
        return
    
    # Get confirmation
    print(f"\nYou entered {len(phone_numbers)} phone numbers:")
    for i, number in enumerate(phone_numbers):
        print(f"{i+1}. {number}")
    
    confirmation = input("\nAre you sure you want to send WhatsApp messages to these numbers? (yes/no): ")
    if confirmation.lower() != "yes":
        print("Test aborted by user.")
        return
    
    # Run concurrent tests
    print("\nRunning concurrent tests...")
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(phone_numbers)) as executor:
        future_to_index = {
            executor.submit(send_message, phone_number, i): i 
            for i, phone_number in enumerate(phone_numbers)
        }
        
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Message {index+1} sent to {result['phone_number']}: Status {result['status_code']}")
            except Exception as e:
                print(f"Message {index+1} failed: {str(e)}")
    
    # Print results
    print("\nTest Results:")
    for result in sorted(results, key=lambda x: x["index"]):
        print(f"Message {result['index']+1} to {result['phone_number']}:")
        print(f"  Status Code: {result['status_code']}")
        print(f"  Time Taken: {result['time_taken']:.4f} seconds")
    
    # Calculate statistics
    if results:
        times = [r["time_taken"] for r in results]
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        print("\nStatistics:")
        print(f"  Average Time: {avg_time:.4f} seconds")
        print(f"  Maximum Time: {max_time:.4f} seconds")
        print(f"  Minimum Time: {min_time:.4f} seconds")
    
    # Get confirmation of receipt
    print("\nPlease check all phones for message receipt.")
    received = input("Were all messages received? (yes/no): ")
    if received.lower() == "yes":
        print("✅ Concurrency test passed!")
    else:
        print("❌ Concurrency test failed: Not all messages were received.")

if __name__ == "__main__":
    test_concurrency()
```

## Main Test Runner

This script runs all the mock-based tests:

```python
# run_tests.py
import test_error_handling
import test_edge_cases
import test_webhook
import test_logging
import test_security
import test_performance

def run_all_tests():
    """Run all tests"""
    print("=== RUNNING ALL TESTS ===\n")
    
    test_error_handling.test_error_handling()
    test_edge_cases.test_edge_cases()
    test_webhook.test_webhook_responses()
    test_logging.test_logging()
    test_security.test_security()
    test_performance.test_performance()
    
    print("\n=== ALL TESTS COMPLETED ===")

if __name__ == "__main__":
    run_all_tests()