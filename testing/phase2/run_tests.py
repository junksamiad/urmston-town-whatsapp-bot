import test_error_handling
import test_edge_cases
import test_webhook
import test_logging
import test_performance

def run_all_tests():
    """Run all tests"""
    print("=== RUNNING ALL TESTS ===\n")
    
    test_error_handling.test_error_handling()
    test_edge_cases.test_edge_cases()
    test_webhook.test_webhook_responses()
    test_logging.test_logging()
    test_logging.test_security()
    test_performance.test_performance()
    
    print("\n=== ALL TESTS COMPLETED ===")

if __name__ == "__main__":
    run_all_tests() 