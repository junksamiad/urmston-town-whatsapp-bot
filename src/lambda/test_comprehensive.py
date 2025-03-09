import json
import uuid
import os
import sys
from app import handle_trigger

def setup_environment():
    """Set up environment variables for testing"""
    os.environ['TWILIO_ACCOUNT_SID'] = 'YOUR_TWILIO_ACCOUNT_SID_HERE'
    os.environ['TWILIO_AUTH_TOKEN'] = 'YOUR_TWILIO_AUTH_TOKEN_HERE'
    os.environ['TWILIO_PHONE_NUMBER'] = 'whatsapp:+447700148000'
    os.environ['TWILIO_TEMPLATE_SID'] = 'HX7d785aa7b15519a858cfc7f0d485ff2c'
    print("Environment variables set up successfully.")

def create_test_event(valid=True):
    """Create a test event for the Lambda function"""
    if valid:
        return {
            'body': json.dumps({
                "player_first_name": "John",
                "player_last_name": "Smith",
                "team_name": "Panthers",
                "age_group": "u11s",
                "manager_full_name": "Alex Johnson",
                "manager_tel": "+447700900001",
                "current_registration_season": "2025-26",
                "parent_first_name": "Jane",
                "parent_last_name": "Smith",
                "parent_tel": "+447835065013",
                "membership_fee_amount": "40",
                "subscription_fee_amount": "26"
            })
        }
    else:
        # Missing required fields
        return {
            'body': json.dumps({
                "player_first_name": "John",
                "player_last_name": "Smith",
                "team_name": "Panthers",
                "age_group": "u11s",
                "manager_full_name": "Alex Johnson",
                "manager_tel": "+447700900001",
                "current_registration_season": "2025-26",
                "parent_first_name": "Jane",
                "parent_last_name": "Smith",
                # Missing parent_tel
                "membership_fee_amount": "40",
                "subscription_fee_amount": "26"
            })
        }

def run_test(test_name, event):
    """Run a test with the given event"""
    print(f"\n=== Running Test: {test_name} ===")
    request_id = str(uuid.uuid4())
    print(f"Request ID: {request_id}")
    
    try:
        response = handle_trigger(event, request_id)
        print(f"Status Code: {response['statusCode']}")
        body = json.loads(response['body'])
        print(f"Response Body: {json.dumps(body, indent=2)}")
        
        if response['statusCode'] == 200:
            print(f"✅ Test Passed: {test_name}")
            return True
        else:
            print(f"❌ Test Failed: {test_name}")
            return False
    except Exception as e:
        print(f"❌ Test Failed with Exception: {str(e)}")
        return False

def main():
    """Main function to run all tests"""
    setup_environment()
    
    # Test 1: Valid request
    valid_event = create_test_event(valid=True)
    test1_result = run_test("Valid Request", valid_event)
    
    # Test 2: Invalid request (missing parent_tel)
    invalid_event = create_test_event(valid=False)
    test2_result = run_test("Invalid Request (Missing parent_tel)", invalid_event)
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Test 1 (Valid Request): {'✅ Passed' if test1_result else '❌ Failed'}")
    print(f"Test 2 (Invalid Request): {'✅ Passed' if not test2_result else '❌ Failed'}")
    
    if test1_result and not test2_result:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 