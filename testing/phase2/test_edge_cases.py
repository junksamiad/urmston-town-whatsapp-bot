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