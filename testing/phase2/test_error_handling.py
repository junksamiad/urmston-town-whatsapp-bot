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