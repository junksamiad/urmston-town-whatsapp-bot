# Phase 2: Twilio Integration

A step-by-step guide to implementing Twilio integration for our WhatsApp chatbot.

## IMPORTANT: DEPLOYMENT STATUS NOTE

**⚠️ CURRENT STATUS: DEPLOYED BUT NOT TESTED ⚠️**

While the code has been successfully deployed to AWS, the final deployment testing in the AWS environment has **NOT** been carried out yet. A comprehensive testing plan has been created in `docs/phase2/phase2_testing_plan.md`, but the actual execution of these tests against the deployed AWS resources is pending.

Anyone continuing this project should:
1. Review the testing plan in `docs/phase2/phase2_testing_plan.md`
2. Execute the tests against the deployed AWS resources
3. Document the results and any issues encountered
4. Update this document and `docs/phase2/phase2_completion.md` with the testing results

## Directory Structure Note

**Important:** The project is organized with the following directory layout:

```
.
├── diagrams/              # Diagrams for the project
│
├── docs/                  # Documentation
│   ├── phase1/            # Phase 1 documentation
│   │   ├── phase1.md      # Phase 1 implementation guide and completion report
│   │   └── phase1a.md     # Phase 1a implementation guide and completion report
│   ├── phase2/            # Phase 2 documentation
│   │   ├── phase2.md      # Phase 2 implementation guide (this file)
│   │   ├── phase2_completion.md # Phase 2 completion report
│   │   └── phase2_local_testing_schedule.md # Phase 2 testing schedule
│   ├── phase3/            # Phase 3 documentation (future)
│   └── roadmap.md         # Complete project roadmap
│
├── src/                   # Source code
│   ├── lambda/            # Lambda function code
│   │   ├── app.py         # Main Lambda handler
│   │   ├── test_local.py  # Local testing script
│   │   └── requirements.txt # Lambda dependencies
│   │
│   └── cdk/               # AWS CDK infrastructure code
│       ├── app.py         # CDK app entry point
│       └── cdk_stack.py   # CDK stack definition
│
├── testing/               # Test files and scripts
│   ├── payloads/          # Test payloads
│   │   └── test_payload.json  # Sample payload for testing the API
│   ├── phase1/            # Phase 1 test scripts (future)
│   ├── phase2/            # Phase 2 test scripts
│   │   ├── test_framework.py      # Testing framework
│   │   ├── test_error_handling.py # Error handling tests
│   │   ├── test_edge_cases.py     # Edge case tests
│   │   ├── test_webhook.py        # Webhook response tests
│   │   └── run_tests.py           # Main test runner
│   └── phase3/            # Phase 3 test scripts (future)
│
└── .gitignore             # Git ignore file
```

## Implementation Cycle

This project follows a structured implementation cycle to ensure quality and maintainability:

1. **Local Development**: Set up and implement new functionality in the local environment
2. **Local Testing**: Test thoroughly in the local environment until working correctly
3. **Documentation**: Update application docs and diagrams with new functionality and progress
4. **Version Control**: Commit changes to Git with descriptive commit messages
5. **AWS Deployment**: Deploy to AWS and test in production environment
6. **Final Documentation**: Update documentation with production insights and any issues resolved

Each phase of the project follows this cycle to ensure consistent quality and maintainability.

## Deployment Commands

**CDK Deployment:**
```bash
cd src/cdk
cdk deploy
```

**Lambda Function Updates:**
```bash
cd src/lambda
zip -r ../../lambda_function.zip .
aws lambda update-function-code --function-name urmston-town-registration-whatsapp --zip-file fileb://../../lambda_function.zip --region eu-north-1
```

**API Testing:**
```bash
curl -X POST https://j0wucljch3.execute-api.eu-north-1.amazonaws.com/prod/trigger \
-H "Content-Type: application/json" \
-H "x-api-key: YOUR_API_KEY_HERE" \
-d @tests/test_payload.json
```

All commands in this guide assume you're starting from the project root directory.

## Objective
Integrate the Lambda function with Twilio to send and receive WhatsApp messages, enabling a conversational registration process.

## Prerequisites
- Completed Phase 1 (Basic Lambda Setup) and Phase 1a (Infrastructure Hardening)
- Twilio account with WhatsApp Business API access
- AWS Lambda function and API Gateway from Phase 1/1a

## Environment Setup

A `.env` file has already been created in the project root with all the necessary environment variables:

```
API_KEY=YOUR_API_KEY_HERE
TWILIO_ACCOUNT_SID=YOUR_TWILIO_ACCOUNT_SID_HERE
TWILIO_AUTH_TOKEN=YOUR_TWILIO_AUTH_TOKEN_HERE
TWILIO_PHONE_NUMBER=whatsapp:+447700148000
TWILIO_TEMPLATE_SID=HXbd20683c439d5894ded688d2a667a02c
```

The `.env` file is already added to `.gitignore` to prevent committing sensitive information.

### 1. Store Credentials in AWS Secrets Manager for Production

For production use, store the sensitive credentials in AWS Secrets Manager:

```bash
# Store Twilio Account SID
aws secretsmanager create-secret \
    --name urmston/twilio/account-sid \
    --description "Twilio Account SID for Urmston Town Registration WhatsApp bot" \
    --secret-string "YOUR_TWILIO_ACCOUNT_SID_HERE" \
    --region eu-north-1

# Store Twilio Auth Token
aws secretsmanager create-secret \
    --name urmston/twilio/auth-token \
    --description "Twilio Auth Token for Urmston Town Registration WhatsApp bot" \
    --secret-string "YOUR_TWILIO_AUTH_TOKEN_HERE" \
    --region eu-north-1
```

### 2. Update the CDK Stack to Use Secrets Manager

When deploying to production, modify `src/cdk/cdk_stack.py` to use the secrets:

```python
# Add these imports at the top
from aws_cdk import aws_secretsmanager as secretsmanager

# In the Lambda function definition, update the environment section
registration_lambda = _lambda.Function(
    # ... other parameters ...
    environment={
        "TWILIO_ACCOUNT_SID": secretsmanager.Secret.from_secret_name_v2(
            self, "TwilioAccountSid", "urmston/twilio/account-sid"
        ).secret_value.to_string(),
        "TWILIO_AUTH_TOKEN": secretsmanager.Secret.from_secret_name_v2(
            self, "TwilioAuthToken", "urmston/twilio/auth-token"
        ).secret_value.to_string(),
        "TWILIO_PHONE_NUMBER": "whatsapp:+447700148000",
        "TWILIO_TEMPLATE_SID": "HXbd20683c439d5894ded688d2a667a02c"
    }
)
```

## Testing Configuration

**Important:** For all testing purposes, we'll use the following configuration:

- **Test Phone Number**: `+447835065013` (This should be used in all test payloads)
- **Template SID**: `HXbd20683c439d5894ded688d2a667a02c`
- **WhatsApp Template Variables**:
  - `1`: Parent's first name (e.g., "Lee")
  - `2`: Player's first name (e.g., "Seb")
  - `3`: Team name (e.g., "Panthers")
  - `4`: Age group (e.g., "u11s")
  - `5`: Current registration season (e.g., "2025-26")
  - `6`: Membership fee amount (e.g., "40")
  - `7`: Subscription fee amount (e.g., "26")
  - `8`: Team manager's full name (e.g., "Neil Dring")
  - `9`: Team manager's phone number (e.g., "07835 065 013")

The template message is:
```
Hi {{1}} 👋, 

Omega here, the Umrston Town Registration Assistant. 

You've been invited to register {{2}} to join Urmston Town {{3}} {{4}} for the upcoming {{5}} season. 

The registration process takes around 5-10 minutes—just let me know when you're ready to begin. 

To complete registration, you'll be required to make an immediate one-off membership (signing-on) payment for the season of £{{6}}, and also setup a direct debit payment of £{{7}} per month using our online payment system. 

If you have any questions before registering, please feel free to reach out to team manager {{8}} on {{9}}.  Let me know when you're ready to get started!
```

Update the test_payload.json file to include all required template variables:

```json
{
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
}
```

## Implementation Steps

### 1. Update Lambda Function for Twilio Integration (Local Development)
- [ ] Update the Lambda function to include Twilio SDK:
  ```bash
  cd src/lambda
  pip install twilio -t .
  ```
- [ ] Update the requirements.txt file:
  ```
  # src/lambda/requirements.txt
  requests==2.28.2
  twilio==7.16.0
  python-dotenv==1.0.0
  ```
- [ ] Modify the Lambda handler to integrate with Twilio:
  ```python
  # Add to src/lambda/app.py
  import os
  from twilio.rest import Client
  from dotenv import load_dotenv
  
  # Load environment variables from .env file
  load_dotenv()
  
  # Twilio credentials from environment variables
  TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
  TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
  TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
  TWILIO_TEMPLATE_SID = os.environ.get('TWILIO_TEMPLATE_SID')
  
  # Initialize Twilio client
  twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
  ```

### 2. Implement WhatsApp Message Sending (Local Development)
- [ ] Add a function to send WhatsApp messages using templates:
  ```python
  def send_whatsapp_template(to_number, template_variables, request_id):
      """Send a WhatsApp template message using Twilio"""
      logger_context = {'request_id': request_id}
      
      try:
          # If template_variables is None, Twilio will use fallback values
          message = twilio_client.messages.create(
              content_sid=TWILIO_TEMPLATE_SID,
              from_=TWILIO_PHONE_NUMBER,
              to=f"whatsapp:{to_number}",
              content_variables=template_variables
          )
          logger.info(f"Template message sent to {to_number}: {message.sid}", extra=logger_context)
          return message.sid
      except Exception as e:
          logger.error(f"Error sending WhatsApp template message: {str(e)}", extra=logger_context)
          raise
  ```

- [ ] Add a function to send a regular WhatsApp message (for responses):
  ```python
  def send_whatsapp_message(to_number, message, request_id):
      """Send a regular WhatsApp message using Twilio"""
      logger_context = {'request_id': request_id}
      
      try:
          message = twilio_client.messages.create(
              body=message,
              from_=TWILIO_PHONE_NUMBER,
              to=f"whatsapp:{to_number}"
          )
          logger.info(f"Message sent to {to_number}: {message.sid}", extra=logger_context)
          return message.sid
      except Exception as e:
          logger.error(f"Error sending WhatsApp message: {str(e)}", extra=logger_context)
          raise
  ```

### 3. Update the Trigger Handler (Local Development)
- [ ] Modify the handle_trigger function to send a WhatsApp template message while preserving API key validation and request ID tracking:
  ```python
  def handle_trigger(event, request_id):
      """Handle the trigger route for initiating registration"""
      logger_context = {'request_id': request_id}
      
      try:
          # Parse the incoming JSON payload
          body = json.loads(event.get('body', '{}'))
          
          # Extract key information
          player_first_name = body.get('player_first_name', '')
          player_last_name = body.get('player_last_name', '')
          player_full_name = f"{player_first_name} {player_last_name}".strip() or 'Unknown Player'
          
          parent_first_name = body.get('parent_first_name', '')
          parent_last_name = body.get('parent_last_name', '')
          parent_full_name = f"{parent_first_name} {parent_last_name}".strip() or 'Unknown Parent'
          
          parent_tel = body.get('parent_tel', 'Unknown Phone')
          team_name = body.get('team_name', 'Unknown Team')
          age_group = body.get('age_group', 'Unknown Age Group')
          team_manager_1_full_name = body.get('team_manager_1_full_name', 'Team Manager')
          team_manager_1_tel = body.get('team_manager_1_tel', 'Not provided')
          current_registration_season = body.get('current_registration_season', '2025-26')
          membership_fee_amount = body.get('membership_fee_amount', '40')
          subscription_fee_amount = body.get('subscription_fee_amount', '26')
          
          # Log the received data
          logger.info(f"Received registration data: {json.dumps(body)}", extra=logger_context)
          logger.info(f"Processing registration for {player_full_name}, parent: {parent_full_name}, phone: {parent_tel}, team: {team_name} {age_group}", extra=logger_context)
          
          # Prepare template variables
          template_variables = {
              "1": parent_first_name,            # Sample: Lee
              "2": player_first_name,            # Sample: Seb
              "3": team_name,                    # Sample: Panthers
              "4": age_group,                    # Sample: u11s
              "5": current_registration_season,  # Sample: 2025-26
              "6": membership_fee_amount,        # Sample: 40
              "7": subscription_fee_amount,      # Sample: 26
              "8": team_manager_1_full_name,     # Sample: Neil Dring
              "9": team_manager_1_tel            # Sample: 07835 065 013
          }
          
          # Create context object
          context_obj = {
              "player_data": {
                  "player_first_name": player_first_name,
                  "player_last_name": player_last_name,
                  "team_name": team_name,
                  "age_group": age_group,
                  "team_manager_1_full_name": team_manager_1_full_name,
                  "team_manager_1_tel": team_manager_1_tel,
                  "current_registration_season": current_registration_season,
                  "parent_first_name": parent_first_name,
                  "parent_last_name": parent_last_name,
                  "parent_tel": parent_tel,
                  "membership_fee_amount": membership_fee_amount,
                  "subscription_fee_amount": subscription_fee_amount
              },
              "timestamp": datetime.now().isoformat(),
              "request_id": request_id
          }
          
          # Send WhatsApp template message to parent
          try:
              # Option 1: Send with template variables
              message_sid = send_whatsapp_template(parent_tel, template_variables, request_id)
              
              # Option 2: Send without template variables (using fallback values)
              # message_sid = send_whatsapp_template(parent_tel, None, request_id)
              
              return {
                  'statusCode': 200,
                  'body': json.dumps({
                      'message': 'Registration data received successfully',
                      'player': player_full_name,
                      'parent': parent_full_name,
                      'team': f"{team_name} {age_group}",
                      'status': 'message_sent',
                      'message_sid': message_sid,
                      'request_id': request_id
                  })
              }
          except Exception as e:
              logger.error(f"Error in handle_trigger: {str(e)}", extra=logger_context)
              return {
                  'statusCode': 500,
                  'body': json.dumps({
                      'message': 'Error processing registration request',
                      'error': str(e),
                      'request_id': request_id
                  })
              }
          
      except Exception as e:
          logger.error(f"Error in handle_trigger: {str(e)}", extra=logger_context)
          return {
              'statusCode': 500,
              'body': json.dumps({
                  'message': 'Error processing registration request',
                  'error': str(e),
                  'request_id': request_id
              })
          }
  ```

### 4. Preserve Webhook Handler Structure (Local Development)
- [ ] Keep the existing webhook handler structure from Phase 1a, but add a simple response for Phase 2:
  ```python
  def handle_webhook(event, request_id):
      """Handle the webhook route for incoming WhatsApp messages"""
      logger_context = {'request_id': request_id}
      
      try:
          # Parse the incoming webhook data from Twilio
          body = json.loads(event.get('body', '{}'))
          
          # Log the received message
          logger.info(f"Received webhook data: {json.dumps(body)}", extra=logger_context)
          
          # Extract message SID for idempotency check (preserved from Phase 1a)
          message_sid = body.get('MessageSid', '')
          logger.info(f"Processing message with SID: {message_sid}", extra=logger_context)
          
          # For Phase 2, we'll just acknowledge receipt
          return {
              'statusCode': 200,
              'body': json.dumps({
                  'message': 'Webhook received successfully',
                  'request_id': request_id
              })
          }
      except Exception as e:
          logger.error(f"Error in handle_webhook: {str(e)}", extra=logger_context)
          return {
              'statusCode': 500,
              'body': json.dumps({
                  'message': 'Error processing webhook',
                  'error': str(e),
                  'request_id': request_id
              })
          }
  ```

### 5. Local Testing

**⚠️ IMPORTANT: WhatsApp Testing Caution ⚠️**

Meta (Facebook) has strict anti-spam policies for WhatsApp Business API. To ensure responsible testing and avoid potential account restrictions:

- **Operator Authorization Required**: All test messages must be explicitly authorized by the operator (you) before sending
- **One Message at a Time**: Send a single test message and wait for operator confirmation before sending another
- **Manual Verification**: After sending a test message, wait for the operator to physically verify receipt on their phone
- **No Automated Testing**: Do not run automated scripts that send multiple messages without explicit operator approval
- **Concurrency Testing**: Any concurrency or load testing must be reviewed and approved by the operator before execution

**Local Testing Steps:**

1. Set up a local test environment with the environment variables in a `.env` file:
   ```
   # .env file
   TWILIO_ACCOUNT_SID=YOUR_TWILIO_ACCOUNT_SID_HERE
   TWILIO_AUTH_TOKEN=YOUR_TWILIO_AUTH_TOKEN_HERE
   TWILIO_PHONE_NUMBER=whatsapp:+447700148000
   TWILIO_TEMPLATE_SID=HXbd20683c439d5894ded688d2a667a02c
   ```

2. Create a simple test script to simulate the Lambda function locally:
   ```python
   # test_local.py
   import json
   import uuid
   import os
   from dotenv import load_dotenv
   from app import handle_trigger
   
   # Load environment variables from .env file
   load_dotenv()
   
   # Print environment variables for debugging (with partial masking for security)
   print(f"TWILIO_ACCOUNT_SID: {os.environ.get('TWILIO_ACCOUNT_SID')[:10]}...")
   print(f"TWILIO_AUTH_TOKEN: {os.environ.get('TWILIO_AUTH_TOKEN')[:5]}...")
   print(f"TWILIO_PHONE_NUMBER: {os.environ.get('TWILIO_PHONE_NUMBER')}")
   print(f"TWILIO_TEMPLATE_SID: {os.environ.get('TWILIO_TEMPLATE_SID')}")
   
   # Simulate an API Gateway event
   event = {
       'body': json.dumps({
           "player_first_name": "Stefan",
           "player_last_name": "Hayton",
           "team_name": "Wolves",
           "age_group": "u7s",
           "team_manager_1_full_name": "Alex Johnson",
           "team_manager_1_tel": "+447700900001",
           "current_registration_season": "2025-26",
           "parent_first_name": "Lee",
           "parent_last_name": "Hayton",
           "parent_tel": "+447835065013",
           "membership_fee_amount": "40",
           "subscription_fee_amount": "26"
       })
   }
   
   # Generate a request ID
   request_id = str(uuid.uuid4())
   
   # Call the handler
   response = handle_trigger(event, request_id)
   print(json.dumps(response, indent=2))
   ```

3. Run the test script and verify the WhatsApp message is sent (with operator approval):
   ```bash
   python test_local.py
   ```

4. Wait for the message to arrive on your phone and verify the content.

### 6. Update Documentation and Diagrams

After successful local testing, update the project documentation and diagrams:

- [ ] Update the sequence diagram in `diagrams/registration_flow.md` to include the Twilio integration
- [ ] Document any issues encountered during development and their solutions
- [ ] Update the Phase 2 completion report with implementation details

### 7. Commit Changes to Git

Once the local implementation is working and documented:

```bash
# Stage all changes
git add .

# Commit with a descriptive message
git commit -m "Phase 2: Implement Twilio WhatsApp template messaging"

# Push to remote repository (phase2 branch)
git push origin phase2
```

**Note**: For this project, we're using the `phase2` branch for development, not the `main` branch as originally specified. This allows us to keep the development work isolated until it's ready to be merged into the main branch.

### 8. Update CDK Stack with Environment Variables (AWS Deployment)
- [x] Update the CDK stack to use environment variables and AWS Secrets Manager for production:
  ```python
  # Update src/cdk/cdk_stack.py
  
  # Import the required modules
  from aws_cdk import (
      # ... other imports ...
      aws_secretsmanager as secretsmanager,
      aws_ssm as ssm,
  )
  
  # In the CdkStack class __init__ method:
  
  # Get configuration from SSM Parameter Store for non-sensitive values
  twilio_phone_number = ssm.StringParameter.from_string_parameter_name(
      self, "TwilioPhoneNumber",
      string_parameter_name="/urmston/twilio/phone-number"
  ).string_value
  
  twilio_template_sid = ssm.StringParameter.from_string_parameter_name(
      self, "TwilioTemplateSid",
      string_parameter_name="/urmston/twilio/template-sid"
  ).string_value
  
  # For the Lambda function definition, use Secrets Manager for sensitive credentials
  # and SSM Parameter Store for non-sensitive configuration
  registration_lambda = _lambda.Function(
      self, "RegistrationHandler",
      runtime=_lambda.Runtime.PYTHON_3_9,
      code=_lambda.Code.from_asset("../lambda"),
      handler="app.lambda_handler",
      memory_size=256,
      timeout=Duration.seconds(30),
      log_retention=logs.RetentionDays.ONE_WEEK,
      environment={
          "TWILIO_ACCOUNT_SID": secretsmanager.Secret.from_secret_name_v2(
              self, "TwilioAccountSid", "urmston/twilio/account-sid"
          ).secret_value.to_string(),
          "TWILIO_AUTH_TOKEN": secretsmanager.Secret.from_secret_name_v2(
              self, "TwilioAuthToken", "urmston/twilio/auth-token"
          ).secret_value.to_string(),
          "TWILIO_PHONE_NUMBER": twilio_phone_number,
          "TWILIO_TEMPLATE_SID": twilio_template_sid
      }
  )
  ```

- [x] Create a script to set up the SSM parameters:
  ```bash
  # Create src/cdk/setup_parameters.sh
  #!/bin/bash
  # Script to set up SSM parameters for Twilio configuration
  
  # Set the AWS region
  REGION="eu-north-1"
  
  # Set the parameter values (these should be replaced with actual values)
  TWILIO_PHONE_NUMBER="whatsapp:+447700148000"
  TWILIO_TEMPLATE_SID="HX7d785aa7b15519a858cfc7f0d485ff2c"
  
  # Create or update the parameters
  echo "Creating/updating SSM parameters..."
  
  # Twilio Phone Number
  aws ssm put-parameter \
      --name "/urmston/twilio/phone-number" \
      --value "$TWILIO_PHONE_NUMBER" \
      --type "String" \
      --description "Twilio WhatsApp phone number for Urmston Town Registration bot" \
      --overwrite \
      --region $REGION
  
  # Twilio Template SID
  aws ssm put-parameter \
      --name "/urmston/twilio/template-sid" \
      --value "$TWILIO_TEMPLATE_SID" \
      --type "String" \
      --description "Twilio WhatsApp template SID for Urmston Town Registration bot" \
      --overwrite \
      --region $REGION
  ```

- [x] Make the script executable and run it:
  ```bash
  chmod +x src/cdk/setup_parameters.sh
  ./src/cdk/setup_parameters.sh
  ```

**Note**: Using SSM Parameter Store for non-sensitive configuration values (like the Twilio phone number and template SID) makes the application more modular and reusable. Different businesses can use different WhatsApp numbers and templates without code changes, simply by updating the parameters in SSM.

### 9. Deploy to AWS
- [ ] Deploy the updated Lambda function to AWS:
  ```bash
  # Package the Lambda function
  cd src/lambda
  zip -r ../../lambda_function.zip .
  
  # Update the Lambda function code
  aws lambda update-function-code \
    --function-name urmston-town-registration-whatsapp \
    --zip-file fileb://../../lambda_function.zip \
    --region eu-north-1
  ```

- [ ] Deploy the updated CDK stack:
  ```bash
  cd src/cdk
  cdk deploy
  ```

### 10. Production Testing

Test the deployed function in the production environment with the same caution as local testing:

1. Test the trigger endpoint with the API key (ONE AT A TIME, with operator approval):
   ```bash
   curl -X POST https://j0wucljch3.execute-api.eu-north-1.amazonaws.com/prod/trigger \
   -H "Content-Type: application/json" \
   -H "x-api-key: YOUR_API_KEY_HERE" \
   -d @tests/test_payload.json
   ```

2. After sending the request, wait for the WhatsApp message to arrive on your phone
   - Confirm the message was received with the correct template variables
   - Check that the formatting is correct
   - Verify all dynamic content is properly displayed

3. Check CloudWatch logs to confirm the message was sent successfully:
   ```bash
   aws logs get-log-events \
   --log-group-name /aws/lambda/urmston-town-registration-whatsapp \
   --log-stream-name $(aws logs describe-log-streams --log-group-name /aws/lambda/urmston-town-registration-whatsapp --order-by LastEventTime --descending --limit 1 --query 'logStreams[0].logStreamName' --output text) \
   --limit 10
   ```

### 11. Final Documentation Update

After successful production deployment and testing:

- [ ] Update the Phase 2 completion report with production deployment details
- [ ] Document any production-specific issues and their solutions
- [ ] Update the project roadmap with progress (green tick emoji's and relevant comments or notes) and next steps

## Verification Checklist
- [x] Twilio SDK installed and configured in Lambda function
- [x] Environment variables set up for Twilio credentials
- [x] WhatsApp template message sending implemented
- [x] API key authentication preserved from Phase 1a
- [x] Request ID tracking preserved from Phase 1a
- [x] Structured logging with request IDs implemented
- [x] Error handling implemented for Twilio API calls
- [x] CDK stack updated with environment variables
- [x] WhatsApp messages successfully sent to test phone number (verified with caution)
- [x] Testing conducted with appropriate pauses between messages
- [x] Documentation and diagrams updated with new functionality
- [x] Changes committed to Git repository
- [x] Successfully deployed to AWS production environment

## Testing Completion

We have successfully completed all phases of the testing schedule:

### Phase 1: Mock-Based Testing ✅
- **Error Handling Tests**: Successfully tested handling of invalid phone numbers, missing required fields, service disruptions, and malformed payloads. Fixed an issue with API key validation.
- **Edge Case Tests**: Verified handling of minimum required fields, very long field values, special characters, international phone numbers, and empty optional fields.
- **Webhook Response Tests**: Confirmed proper processing of basic webhook messages, webhooks with media, and handling of malformed payloads.
- **Logging Tests**: Verified request and error logging functionality, including request ID tracking.
- **Security Tests**: Tested API key validation for both valid and invalid keys, and fixed issues with the validation process.
- **Performance Tests**: Demonstrated quick response times for all operations, with an average response time under 0.5 seconds.

### Phase 2: Limited Real Message Testing ✅
- **Basic Real Message Test**: Successfully sent a WhatsApp message using template variables to phone number +447835065013.
- **Fallback Values Test**: Successfully sent a WhatsApp message using fallback values to phone number +447835065013.
- Both messages were received promptly and contained the expected content.

### Phase 3: Concurrency Testing ✅
- **Test Configuration**: Used 4 different phone numbers: +447835065013, +447789690081, +447759213004, and +447929333733.
- **Test Results**:
  - All messages were delivered successfully with status code 200
  - Performance metrics:
    - Average response time: 0.4043 seconds
    - Maximum response time: 0.4058 seconds
    - Minimum response time: 0.4031 seconds
  - All messages were received by the recipients, confirming the system's ability to handle multiple simultaneous requests.

## Next Steps
After completing Phase 2, we'll move on to Phase 3 where we'll implement advanced features such as:
1. Storing registration data in a database (DynamoDB)
2. Implementing a conversational flow with multiple steps
3. Adding authentication and authorization
4. Setting up monitoring and alerting
5. Implementing error handling and validation 

## Deployment Status

The Phase 2 implementation has been deployed to AWS, but **final testing in the AWS environment has not been completed**. Here's a summary of the deployment:

### Deployment Resources

1. **API Gateway Endpoint**: `https://2q6z7thwxa.execute-api.eu-north-1.amazonaws.com/prod/`
   - Trigger endpoint: `https://2q6z7thwxa.execute-api.eu-north-1.amazonaws.com/prod/trigger`
   - Webhook endpoint: `https://2q6z7thwxa.execute-api.eu-north-1.amazonaws.com/prod/webhook`

2. **API Key**: `3XBis5FzF78FyVlPqqdzDupXZJ5c0lU59n9gTY2d`
   - Name: `UrmstonTownRegistrationKey`
   - Use this key in the `x-api-key` header for all requests to the trigger endpoint

3. **Usage Plan**: `TriggerEndpointPlan`
   - Rate limit: 25 requests per second
   - Burst limit: 50 requests

4. **Environment Variables**:
   - SSM Parameters:
     - `/urmston/twilio/phone-number`: `whatsapp:+447700148000`
     - `/urmston/twilio/template-sid`: `HX7d785aa7b15519a858cfc7f0d485ff2c`
   - AWS Secrets Manager:
     - `urmston/twilio/account-sid`: Twilio Account SID
     - `urmston/twilio/auth-token`: Twilio Auth Token

### Testing the Deployment

A comprehensive testing plan has been created in `docs/phase2/phase2_testing_plan.md` but has not yet been executed. The plan includes:

1. Basic functionality tests for the trigger endpoint
2. Authentication and security tests for API key validation
3. Error handling tests for missing fields and invalid phone numbers
4. Performance and concurrency tests

**⚠️ IMPORTANT: These tests need to be executed before considering Phase 2 complete.**

You can test the deployment with this command:

```bash
curl -X POST https://2q6z7thwxa.execute-api.eu-north-1.amazonaws.com/prod/trigger \
-H "Content-Type: application/json" \
-H "x-api-key: 3XBis5FzF78FyVlPqqdzDupXZJ5c0lU59n9gTY2d" \
-d @testing/payloads/test_payload.json
```

### Deployment Challenges Resolved

1. **CDK Bootstrap Issues**: Fixed by deleting the existing bootstrap stack and creating a fresh one
2. **AWS Secrets Manager Access**: Resolved by creating a SecretsManagerAccess policy in IAM
3. **API Gateway Resource Conflicts**: Resolved by deleting existing resources and recreating them
4. **Lambda Concurrency Limits**: Fixed by removing the reserved concurrency setting

For a detailed deployment report, see `docs/phase2/phase2_completion.md`. 