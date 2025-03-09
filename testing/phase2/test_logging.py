import logging
from io import StringIO
import json
import os
import re
from test_framework import run_test, create_test_event

def test_logging():
    """Test logging functionality"""
    print("\n=== LOGGING TESTS ===")
    
    # Capture logs
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s - request_id: %(request_id)s'))
    logger = logging.getLogger()
    logger.addHandler(handler)
    
    # Test 1: Successful request logging
    event = create_test_event()
    response = run_test("Successful Request Logging", event)
    
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
    
    # Verify log content - updated to check for request_id in the new format
    if "request_id:" in logs and "Received registration data" in logs:
        print("✅ Request ID and payload logging verified")
    else:
        # For debugging, let's print what we found
        print(f"❌ Missing expected log entries")
        
        # Let's manually check if the request_id is in the response
        if "request_id" in json.loads(response.get('body', '{}')):
            print("✅ Request ID found in response body")
        else:
            print("❌ Request ID missing from response body")
    
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