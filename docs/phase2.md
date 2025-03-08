# Phase 2: Twilio Integration

A step-by-step guide to implementing Twilio integration for our WhatsApp chatbot.

## Directory Structure Note

**Important:** The project has been restructured into a more organized directory layout:

```
.
├── docs/                  # Documentation
│   ├── phase1.md          # Phase 1 implementation guide and completion report
│   ├── phase2.md          # Phase 2 implementation guide (this file)
│   ├── roadmap.md         # Complete project roadmap
│   └── aws_credentials.txt # AWS credentials and setup information
│
├── src/                   # Source code
│   ├── lambda/            # Lambda function code
│   │   ├── app.py         # Main Lambda handler
│   │   └── requirements.txt # Lambda dependencies
│   │
│   └── cdk/               # AWS CDK infrastructure code
│       ├── app.py         # CDK app entry point
│       └── cdk_stack.py   # CDK stack definition
│
├── tests/                 # Test files
│   └── test_payload.json  # Sample payload for testing the API
│
└── README.md              # Project overview
```

This restructuring affects deployment commands as follows:

**CDK Deployment:**
```bash
# Before restructuring
cd cdk
cdk deploy

# After restructuring
cd src/cdk
cdk deploy
```

**Lambda Function Updates:**
```bash
# Before restructuring
cd lambda
zip -r ../lambda_function.zip .
aws lambda update-function-code --function-name urmston-town-registration-whatsapp --zip-file fileb://lambda_function.zip --region eu-north-1

# After restructuring
cd src/lambda
zip -r ../../lambda_function.zip .
aws lambda update-function-code --function-name urmston-town-registration-whatsapp --zip-file fileb://../../lambda_function.zip --region eu-north-1
```

**API Testing:**
```bash
# Before restructuring
curl -X POST https://j0wucljch3.execute-api.eu-north-1.amazonaws.com/prod/trigger \
-H "Content-Type: application/json" \
-d @test_payload.json

# After restructuring
curl -X POST https://j0wucljch3.execute-api.eu-north-1.amazonaws.com/prod/trigger \
-H "Content-Type: application/json" \
-d @tests/test_payload.json
```

All commands in this guide assume you're starting from the project root directory.

## Objective
Integrate the Lambda function with Twilio to send and receive WhatsApp messages, enabling a conversational registration process.

## Prerequisites
- Completed Phase 1 (Basic Lambda Setup)
- Twilio account with WhatsApp Business API access
- AWS Lambda function and API Gateway from Phase 1

## Testing Configuration

**Important:** For all testing purposes, we'll use the following configuration:

- **Test Phone Number**: `+447835065013` (This should be used in all test payloads)
- **Template SID**: `HX7d785aa7b15519a858cfc7f0d485ff2c`
- **WhatsApp Template Variables**:
  - `parent_first_name`: Parent's first name
  - `player_first_name`: Player's first name
  - `team_name`: Team name
  - `age_group`: Age group (e.g., "u11s")
  - `current_season`: Current season (e.g., "2025-26")
  - `membership_fee_amount`: One-off membership fee (e.g., "40")
  - `subscription_fee_amount`: Monthly subscription fee (e.g., "26")

The template message is:
```
Hi {{parent_first_name}} 👋, 

Omega here, the Umrston Town Registration Assistant. 

You've been invited to register {{player_first_name}} to join Urmston Town {{team_name}} {{age_group}} for the upcoming {{current_season}} season. 

The registration process takes around 5-10 minutes—just let me know when you're ready to begin. 

To complete registration, you'll be required to make an immediate one-off membership (signing-on) payment for the season of £{{membership_fee_amount}}, and also setup a direct debit payment of £{{subscription_fee_amount}} per month using our online payment system. 

If you have any questions before registering, please feel free to reach out to team manager <team_manager_1_full_name> on <team_manager_1_tel>.  Let me know when you're ready to get started!
```

Update the test_payload.json file to include all required template variables:

```json
{
  "player_first_name": "John",
  "player_last_name": "Smith",
  "team_name": "Panthers",
  "age_group": "u11s",
  "manager_full_name": "Alex Johnson",
  "current_registration_season": "2025-26",
  "parent_first_name": "Jane",
  "parent_last_name": "Smith",
  "parent_tel": "+447835065013",
  "membership_fee_amount": "40",
  "subscription_fee_amount": "26"
}
```

## Implementation Steps

### 1. Set Up Twilio Account
- [x] Create a Twilio account (already done)
- [x] Set up WhatsApp messaging with Twilio
- [x] Note down the Account SID and Auth Token
- [x] Configure the WhatsApp template with SID: `HX7d785aa7b15519a858cfc7f0d485ff2c`

### 2. Update Lambda Function for Twilio Integration
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
  ```
- [ ] Modify the Lambda handler to integrate with Twilio:
  ```python
  # Add to src/lambda/app.py
  from twilio.rest import Client
  
  # Twilio credentials
  TWILIO_ACCOUNT_SID = 'YOUR_TWILIO_ACCOUNT_SID'
  TWILIO_AUTH_TOKEN = 'YOUR_TWILIO_AUTH_TOKEN'
  TWILIO_PHONE_NUMBER = 'whatsapp:+447700148000'
  TWILIO_TEMPLATE_SID = 'HX7d785aa7b15519a858cfc7f0d485ff2c'
  
  # Initialize Twilio client
  twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
  ```

### 3. Implement WhatsApp Message Sending
- [ ] Add a function to send WhatsApp messages using templates:
  ```python
  def send_whatsapp_template(to_number, template_variables):
      """Send a WhatsApp template message using Twilio"""
      try:
          message = twilio_client.messages.create(
              content_sid=TWILIO_TEMPLATE_SID,
              from_=TWILIO_PHONE_NUMBER,
              to=f"whatsapp:{to_number}",
              content_variables=template_variables
          )
          logger.info(f"Template message sent to {to_number}: {message.sid}")
          return message.sid
      except Exception as e:
          logger.error(f"Error sending WhatsApp template message: {str(e)}")
          raise
  ```

- [ ] Add a function to send a regular WhatsApp message (for responses):
  ```python
  def send_whatsapp_message(to_number, message):
      """Send a regular WhatsApp message using Twilio"""
      try:
          message = twilio_client.messages.create(
              body=message,
              from_=TWILIO_PHONE_NUMBER,
              to=f"whatsapp:{to_number}"
          )
          logger.info(f"Message sent to {to_number}: {message.sid}")
          return message.sid
      except Exception as e:
          logger.error(f"Error sending WhatsApp message: {str(e)}")
          raise
  ```

### 4. Update the Trigger Handler
- [ ] Modify the handle_trigger function to send a WhatsApp template message:
  ```python
  def handle_trigger(event):
      """Handle the trigger route for initiating registration"""
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
      manager_full_name = body.get('manager_full_name', 'Team Manager')
      current_registration_season = body.get('current_registration_season', '2025-26')
      membership_fee_amount = body.get('membership_fee_amount', '40')
      subscription_fee_amount = body.get('subscription_fee_amount', '26')
      
      # Log the received data
      logger.info(f"Received registration data: {json.dumps(body)}")
      logger.info(f"Processing registration for {player_full_name}, parent: {parent_full_name}, phone: {parent_tel}, team: {team_name} {age_group}")
      
      # Prepare template variables
      template_variables = {
          "parent_first_name": parent_first_name,
          "player_first_name": player_first_name,
          "team_name": team_name,
          "age_group": age_group,
          "current_season": current_registration_season,
          "membership_fee_amount": membership_fee_amount,
          "subscription_fee_amount": subscription_fee_amount
      }
      
      # Send WhatsApp template message to parent
      try:
          message_sid = send_whatsapp_template(parent_tel, template_variables)
          
          return {
              'statusCode': 200,
              'body': json.dumps({
                  'message': 'Registration data received successfully',
                  'player': player_full_name,
                  'parent': parent_full_name,
                  'team': f"{team_name} {age_group}",
                  'status': 'message_sent',
                  'message_sid': message_sid
              })
          }
      except Exception as e:
          logger.error(f"Error in handle_trigger: {str(e)}")
          return {
              'statusCode': 500,
              'body': json.dumps({
                  'message': 'Error processing registration request',
                  'error': str(e)
              })
          }
  ```

### 5. Implement Webhook Handler for Incoming Messages
- [ ] Update the handle_webhook function to process incoming WhatsApp messages:
  ```python
  def handle_webhook(event):
      """Handle the webhook route for incoming WhatsApp messages"""
      # Parse the incoming webhook data from Twilio
      body = json.loads(event.get('body', '{}'))
      
      # Log the received message
      logger.info(f"Received webhook data: {json.dumps(body)}")
      
      # Extract message details
      message_sid = body.get('MessageSid', '')
      from_number = body.get('From', '').replace('whatsapp:', '')
      to_number = body.get('To', '').replace('whatsapp:', '')
      message_body = body.get('Body', '')
      
      logger.info(f"Received message from {from_number}: {message_body}")
      
      # In Phase 2, we'll just acknowledge and respond with a simple message
      response_message = "Thank you for your message. We'll get back to you shortly."
      
      try:
          send_whatsapp_message(from_number, response_message)
          
          return {
              'statusCode': 200,
              'body': json.dumps({
                  'message': 'Webhook processed successfully',
                  'from': from_number,
                  'message_received': message_body
              })
          }
      except Exception as e:
          logger.error(f"Error in handle_webhook: {str(e)}")
          return {
              'statusCode': 500,
              'body': json.dumps({
                  'message': 'Error processing webhook',
                  'error': str(e)
              })
          }
  ```

### 6. Update AWS Lambda Environment Variables
- [ ] Add Twilio credentials as environment variables in the Lambda function:
  ```python
  # Update src/cdk/cdk_stack.py
  registration_lambda = _lambda.Function(
      self, "RegistrationHandler",
      runtime=_lambda.Runtime.PYTHON_3_9,
      code=_lambda.Code.from_asset("../lambda"),  # Note the updated path
      handler="app.lambda_handler",
      memory_size=256,
      timeout=Duration.seconds(30),
      log_retention=logs.RetentionDays.ONE_WEEK,
      environment={
          "TWILIO_ACCOUNT_SID": "YOUR_TWILIO_ACCOUNT_SID",
          "TWILIO_AUTH_TOKEN": "YOUR_TWILIO_AUTH_TOKEN",
          "TWILIO_PHONE_NUMBER": "whatsapp:+447700148000",
          "TWILIO_TEMPLATE_SID": "HX7d785aa7b15519a858cfc7f0d485ff2c"
      }
  )
  ```

### 7. Update Lambda Function to Use Environment Variables
- [ ] Modify the Lambda function to use environment variables:
  ```python
  # Update in src/lambda/app.py
  import os
  
  # Twilio credentials from environment variables
  TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
  TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
  TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
  TWILIO_TEMPLATE_SID = os.environ.get('TWILIO_TEMPLATE_SID')
  ```

### 8. Configure Twilio Webhook URL
- [ ] In the Twilio console, configure the webhook URL to point to the API Gateway webhook endpoint:
  ```
  https://j0wucljch3.execute-api.eu-north-1.amazonaws.com/prod/webhook
  ```

### 9. Deploy and Test
- [ ] Deploy the updated Lambda function:
  ```bash
  cd src/lambda
  zip -r ../../lambda_function.zip .
  aws lambda update-function-code --function-name urmston-town-registration-whatsapp --zip-file fileb://../../lambda_function.zip --region eu-north-1
  ```
- [ ] Update the test_payload.json file with the test phone number and fee amounts:
  ```bash
  cat > tests/test_payload.json << 'EOF'
  {
    "player_first_name": "John",
    "player_last_name": "Smith",
    "team_name": "Panthers",
    "age_group": "u11s",
    "manager_full_name": "Alex Johnson",
    "current_registration_season": "2025-26",
    "parent_first_name": "Jane",
    "parent_last_name": "Smith",
    "parent_tel": "+447835065013",
    "membership_fee_amount": "40",
    "subscription_fee_amount": "26"
  }
  EOF
  ```
- [ ] Test the trigger endpoint:
  ```bash
  curl -X POST https://j0wucljch3.execute-api.eu-north-1.amazonaws.com/prod/trigger \
  -H "Content-Type: application/json" \
  -d @tests/test_payload.json
  ```
- [ ] Verify that a WhatsApp message is sent to the test phone number
- [ ] Test the webhook by sending a WhatsApp message to the Twilio number
- [ ] Verify that the Lambda function receives the message and responds

## Verification Checklist
- [ ] Twilio account configured with WhatsApp template
- [ ] Lambda function updated with Twilio integration
- [ ] Environment variables configured for Twilio credentials
- [ ] Trigger endpoint sends WhatsApp template messages
- [ ] Webhook endpoint receives and processes incoming messages
- [ ] Error handling implemented for Twilio API calls

## Next Steps
After completing Phase 2, we'll move on to Phase 3 where we'll implement advanced features such as:
1. Storing registration data in a database (DynamoDB)
2. Implementing a conversational flow with multiple steps
3. Adding authentication and authorization
4. Setting up monitoring and alerting
5. Implementing error handling and validation 