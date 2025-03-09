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