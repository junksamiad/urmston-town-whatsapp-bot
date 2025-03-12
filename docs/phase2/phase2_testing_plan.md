# Phase 2 AWS Deployment Testing Plan

## Overview

This testing plan aims to verify that our Phase 2 deployment with Twilio integration is working correctly in the AWS environment. The tests will focus on the trigger endpoint's ability to send WhatsApp messages via Twilio.

## Prerequisites

- AWS deployment completed successfully
- Twilio credentials configured in AWS Secrets Manager
- Test phone numbers available for receiving WhatsApp messages
- API key for accessing the trigger endpoint

## Test Environment Details

- **API Gateway Endpoint**: `https://2q6z7thwxa.execute-api.eu-north-1.amazonaws.com/prod/`
- **API Key**: `3XBis5FzF78FyVlPqqdzDupXZJ5c0lU59n9gTY2d`
- **Test Phone Number**: `+447835065013` (primary test number)
- **Additional Test Numbers**: `+447789690081`, `+447759213004`, `+447929333733`

## Test Categories

### 1. Basic Functionality Tests

#### 1.1 Trigger Endpoint - Basic Message Sending

**Objective**: Verify that the trigger endpoint can successfully send a WhatsApp template message.

**Test Steps**:
1. Send a POST request to the trigger endpoint with valid player/parent data
2. Verify the API response is successful (200 status code)
3. Check that the WhatsApp message is received on the test phone number
4. Verify the message content matches the expected template with correct variables

**Test Command**:
```bash
curl -X POST https://2q6z7thwxa.execute-api.eu-north-1.amazonaws.com/prod/trigger \
-H "Content-Type: application/json" \
-H "x-api-key: 3XBis5FzF78FyVlPqqdzDupXZJ5c0lU59n9gTY2d" \
-d '{
  "player_first_name": "John",
  "player_last_name": "Smith",
  "team_name": "Panthers",
  "age_group": "u11s",
  "team_manager_1_full_name": "Alex Johnson",
  "team_manager_1_tel": "+447700900001",
  "current_registration_season": "2025-26",
  "parent_first_name": "Jane",
  "parent_last_name": "Smith",
  "parent_tel": "+447835065013",
  "membership_fee_amount": "40",
  "subscription_fee_amount": "26"
}'
```

### 2. Authentication and Security Tests

#### 2.1 API Key Validation

**Objective**: Verify that the trigger endpoint requires a valid API key.

**Test Steps**:
1. Send a request to the trigger endpoint without an API key
2. Verify the request is rejected with a 403 status code
3. Send a request with an invalid API key
4. Verify the request is rejected with a 403 status code
5. Send a request with the valid API key
6. Verify the request is accepted with a 200 status code

**Test Commands**:
```bash
# Test without API key
curl -X POST https://2q6z7thwxa.execute-api.eu-north-1.amazonaws.com/prod/trigger \
-H "Content-Type: application/json" \
-d @testing/payloads/test_payload.json

# Test with invalid API key
curl -X POST https://2q6z7thwxa.execute-api.eu-north-1.amazonaws.com/prod/trigger \
-H "Content-Type: application/json" \
-H "x-api-key: invalid_key_value" \
-d @testing/payloads/test_payload.json

# Test with valid API key
curl -X POST https://2q6z7thwxa.execute-api.eu-north-1.amazonaws.com/prod/trigger \
-H "Content-Type: application/json" \
-H "x-api-key: 3XBis5FzF78FyVlPqqdzDupXZJ5c0lU59n9gTY2d" \
-d @testing/payloads/test_payload.json
```

### 3. Error Handling Tests

#### 3.1 Missing Required Fields

**Objective**: Verify that the trigger endpoint properly handles missing required fields.

**Test Steps**:
1. Send a request to the trigger endpoint with missing required fields
2. Verify the API returns an appropriate error response (400 status code)
3. Check CloudWatch logs to confirm the error was properly logged

**Test Command**:
```bash
curl -X POST https://2q6z7thwxa.execute-api.eu-north-1.amazonaws.com/prod/trigger \
-H "Content-Type: application/json" \
-H "x-api-key: 3XBis5FzF78FyVlPqqdzDupXZJ5c0lU59n9gTY2d" \
-d '{
  "player_first_name": "John",
  "team_name": "Panthers"
}'
```

#### 3.2 Invalid Phone Number

**Objective**: Verify that the trigger endpoint properly handles invalid phone numbers.

**Test Steps**:
1. Send a request with an invalid phone number format
2. Verify the API returns an appropriate error response
3. Check CloudWatch logs to confirm the error was properly logged

**Test Command**:
```bash
curl -X POST https://2q6z7thwxa.execute-api.eu-north-1.amazonaws.com/prod/trigger \
-H "Content-Type: application/json" \
-H "x-api-key: 3XBis5FzF78FyVlPqqdzDupXZJ5c0lU59n9gTY2d" \
-d '{
  "player_first_name": "John",
  "player_last_name": "Smith",
  "team_name": "Panthers",
  "age_group": "u11s",
  "team_manager_1_full_name": "Alex Johnson",
  "team_manager_1_tel": "+447700900001",
  "current_registration_season": "2025-26",
  "parent_first_name": "Jane",
  "parent_last_name": "Smith",
  "parent_tel": "invalid_number",
  "membership_fee_amount": "40",
  "subscription_fee_amount": "26"
}'
```

### 4. Performance and Concurrency Tests

#### 4.1 Sequential Requests

**Objective**: Verify that the system can handle multiple sequential requests.

**Test Steps**:
1. Send 5 sequential requests to the trigger endpoint with different player data
2. Verify all requests receive successful responses
3. Confirm all WhatsApp messages are delivered
4. Check CloudWatch logs for any errors or performance issues

**Test Script**:
```bash
#!/bin/bash

API_KEY="3XBis5FzF78FyVlPqqdzDupXZJ5c0lU59n9gTY2d"
API_ENDPOINT="https://2q6z7thwxa.execute-api.eu-north-1.amazonaws.com/prod/trigger"

echo "Sending 5 sequential requests..."

for i in {1..5}
do
  echo "Request $i"
  curl -s -X POST $API_ENDPOINT \
    -H "Content-Type: application/json" \
    -H "x-api-key: $API_KEY" \
    -d '{
      "player_first_name": "Player'$i'",
      "player_last_name": "Smith",
      "team_name": "Panthers",
      "age_group": "u11s",
      "team_manager_1_full_name": "Alex Johnson",
      "team_manager_1_tel": "+447700900001",
      "current_registration_season": "2025-26",
      "parent_first_name": "Jane",
      "parent_last_name": "Smith",
      "parent_tel": "+447835065013",
      "membership_fee_amount": "40",
      "subscription_fee_amount": "26"
    }'
  echo ""
  sleep 5  # Wait 5 seconds between requests to avoid overwhelming Twilio
done
```

#### 4.2 Limited Concurrent Requests

**Objective**: Verify that the system can handle a limited number of concurrent requests.

**Test Steps**:
1. Send 3 concurrent requests to the trigger endpoint with different phone numbers
2. Verify all requests receive successful responses
3. Confirm all WhatsApp messages are delivered to the respective phone numbers
4. Check CloudWatch logs for any errors or performance issues

**Test Script**:
```bash
#!/bin/bash

API_KEY="3XBis5FzF78FyVlPqqdzDupXZJ5c0lU59n9gTY2d"
API_ENDPOINT="https://2q6z7thwxa.execute-api.eu-north-1.amazonaws.com/prod/trigger"

echo "Sending 3 concurrent requests to different phone numbers..."

# Phone numbers array
PHONE_NUMBERS=("+447835065013" "+447789690081" "+447759213004")

for i in {0..2}
do
  curl -s -X POST $API_ENDPOINT \
    -H "Content-Type: application/json" \
    -H "x-api-key: $API_KEY" \
    -d '{
      "player_first_name": "Player'$i'",
      "player_last_name": "Smith",
      "team_name": "Panthers",
      "age_group": "u11s",
      "team_manager_1_full_name": "Alex Johnson",
      "team_manager_1_tel": "+447700900001",
      "current_registration_season": "2025-26",
      "parent_first_name": "Parent'$i'",
      "parent_last_name": "Smith",
      "parent_tel": "'${PHONE_NUMBERS[$i]}'",
      "membership_fee_amount": "40",
      "subscription_fee_amount": "26"
    }' &
done

wait
echo "All concurrent requests sent."
```

## Test Results Documentation

For each test, document the following:

1. **Test ID and Name**: e.g., "1.1 Trigger Endpoint - Basic Message Sending"
2. **Date and Time**: When the test was performed
3. **Test Result**: Pass/Fail
4. **Response Status Code**: HTTP status code received
5. **Response Time**: Time taken for the request to complete
6. **Response Body**: JSON response received
7. **Observations**: Any notable behavior or issues
8. **Screenshots**: If applicable, screenshots of WhatsApp messages received
9. **CloudWatch Logs**: Relevant log entries

## Test Execution Plan

1. Execute basic functionality tests first to verify core functionality
2. Proceed with authentication and security tests
3. Execute error handling tests
4. Perform performance and concurrency tests
5. Document all results and issues found
6. Address any issues before proceeding to Phase 3

## Considerations for Twilio Testing

- **Rate Limiting**: Be mindful of Twilio's rate limits for WhatsApp messaging
- **24-Hour Window**: WhatsApp has a 24-hour window for business-initiated conversations
- **Template Approval**: Ensure all templates used are approved by WhatsApp
- **Test Phone Numbers**: Use only phone numbers that have opted in to receive test messages
- **Cost**: Be aware of the costs associated with sending WhatsApp messages through Twilio 