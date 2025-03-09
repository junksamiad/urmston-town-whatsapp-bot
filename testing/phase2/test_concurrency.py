import json
import uuid
import os
import sys
import time
import concurrent.futures
from unittest.mock import MagicMock
from dotenv import load_dotenv

# Add the src/lambda directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/lambda')))

from app import lambda_handler

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
    
    start_time = time.time()
    response = lambda_handler(event, mock_context)
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
    
    # Use the provided phone numbers
    phone_numbers = [
        "+447835065013",  # Format the numbers with country code
        "+447789690081",
        "+447759213004",
        "+447929333733"
    ]
    
    # Display the phone numbers
    print(f"\nUsing {len(phone_numbers)} phone numbers:")
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