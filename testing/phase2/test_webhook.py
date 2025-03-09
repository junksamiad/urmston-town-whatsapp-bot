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