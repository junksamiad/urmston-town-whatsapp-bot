# Phase 1: Basic Lambda Setup (MVP)
A step-by-step guide to implementing the minimal viable product for our WhatsApp chatbot.

## Objective
Create a simple AWS Lambda function that can receive basic player/parent data and log it, setting the foundation for our registration chatbot.

## Prerequisites
- AWS account with appropriate permissions
- Node.js installed (for AWS CDK)
- Python 3.9+ installed
- AWS CLI configured with credentials

## Implementation Steps

### 1. Set Up Development Environment
- [x] Install AWS CDK globally:
  ```bash
  npm install -g aws-cdk
  ```
- [x] Create a new directory for the project:
  ```bash
  mkdir urmston-town-registration-whatsapp
  cd urmston-town-registration-whatsapp
  ```
- [x] Initialize a new CDK project:
  ```bash
  cdk init app --language python
  ```
- [x] Activate the virtual environment:
  ```bash
  # On Windows
  .venv\Scripts\activate
  
  # On macOS/Linux
  source .venv/bin/activate
  ```
- [x] Install required dependencies:
  ```bash
  pip install -r requirements.txt
  pip install aws-cdk-lib
  ```

### 2. Create Lambda Function Code
- [x] Create a `lambda` directory in the project root:
  ```bash
  mkdir lambda
  ```
- [x] Create the main Lambda handler file:
  ```bash
  touch lambda/app.py
  ```
- [x] Implement the basic Lambda handler with route handling:
  ```python
  # lambda/app.py
  import json
  import logging
  
  # Configure logging
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)
  
  def lambda_handler(event, context):
      """
      Lambda function that handles both trigger and webhook routes
      for the football registration WhatsApp bot.
      """
      try:
          # Log the entire event for debugging
          logger.info(f"Received event: {json.dumps(event)}")
          
          # Determine which route was called
          # Check for API Gateway v2 format first
          if 'requestContext' in event and 'http' in event['requestContext']:
              path = event['requestContext']['http']['path']
          elif 'rawPath' in event:
              path = event['rawPath']
          else:
              # Fall back to the original path extraction
              path = event.get('path', '')
              
          logger.info(f"Path: {path}")
          
          if '/trigger' in path:
              return handle_trigger(event)
          elif '/webhook' in path:
              return handle_webhook(event)
          else:
              logger.error(f"Route not found for path: {path}")
              return {
                  'statusCode': 404,
                  'body': json.dumps({'message': 'Route not found'})
              }
              
      except Exception as e:
          logger.error(f"Error processing request: {str(e)}")
          return {
              'statusCode': 500,
              'body': json.dumps({
                  'message': 'Error processing request',
                  'error': str(e)
              })
          }
  
  def handle_trigger(event):
      """Handle the trigger route for initiating registration"""
      # Parse the incoming JSON payload
      body = json.loads(event.get('body', '{}'))
      
      # Log the received data
      logger.info(f"Received registration data: {json.dumps(body)}")
      
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
      
      logger.info(f"Processing registration for {player_full_name}, parent: {parent_full_name}, phone: {parent_tel}, team: {team_name} {age_group}")
      
      # In future phases, we'll add OpenAI and Twilio integration here
      
      return {
          'statusCode': 200,
          'body': json.dumps({
              'message': 'Registration data received successfully',
              'player': player_full_name,
              'parent': parent_full_name,
              'team': f"{team_name} {age_group}",
              'status': 'pending'
          })
      }
  
  def handle_webhook(event):
      """Handle the webhook route for incoming WhatsApp messages"""
      # Parse the incoming webhook data from Twilio
      body = json.loads(event.get('body', '{}'))
      
      # Log the received message
      logger.info(f"Received webhook data: {json.dumps(body)}")
      
      # In Phase 1, we'll just acknowledge receipt
      return {
          'statusCode': 200,
          'body': json.dumps({
              'message': 'Webhook received successfully'
          })
      }
  ```
- [x] Create a requirements file for Lambda:
  ```bash
  touch lambda/requirements.txt
  ```
- [x] Add required dependencies:
  ```
  # lambda/requirements.txt
  requests==2.28.2
  ```

### 3. Define CDK Stack
- [x] Update the CDK stack file to define the Lambda function and API Gateway:
  ```python
  # cdk/cdk_stack.py
  from aws_cdk import (
      Stack,
      Duration,
      aws_lambda as _lambda,
      aws_apigateway as apigw,
      aws_logs as logs,
  )
  from constructs import Construct
  
  class CdkStack(Stack):
      def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
          super().__init__(scope, construct_id, **kwargs)
          
          # Create Lambda function
          registration_lambda = _lambda.Function(
              self, "RegistrationHandler",
              runtime=_lambda.Runtime.PYTHON_3_9,
              code=_lambda.Code.from_asset("../lambda"),
              handler="app.lambda_handler",
              memory_size=256,
              timeout=Duration.seconds(30),
              log_retention=logs.RetentionDays.ONE_WEEK
          )
          
          # Create HTTP API (more cost-effective than REST API)
          api = apigw.HttpApi(
              self, "RegistrationApi",
              default_integration=apigw.HttpLambdaIntegration(
                  "LambdaIntegration", registration_lambda
              )
          )
          
          # Add routes
          api.add_routes(
              path="/trigger",
              methods=[apigw.HttpMethod.POST],
              integration=apigw.HttpLambdaIntegration(
                  "TriggerIntegration", registration_lambda
              )
          )
          
          api.add_routes(
              path="/webhook",
              methods=[apigw.HttpMethod.POST],
              integration=apigw.HttpLambdaIntegration(
                  "WebhookIntegration", registration_lambda
              )
          )
  ```

### 4. Deploy the Stack
- [x] Bootstrap CDK (if not already done):
  ```bash
  cdk bootstrap
  ```
- [x] Synthesize the CloudFormation template:
  ```bash
  cdk synth
  ```
- [x] Deploy the stack:
  ```bash
  cdk deploy
  ```
- [x] Note the API endpoint URL from the deployment output

### 5. Test the Endpoint
- [x] Create a test payload file:
  ```bash
  touch test_payload.json
  ```
- [x] Add sample player data:
  ```json
  {
    "player_first_name": "John",
    "player_last_name": "Smith",
    "team_name": "Urmston Town Juniors FC",
    "age_group": "U12",
    "manager_full_name": "Alex Johnson",
    "current_registration_season": "2025-26",
    "parent_first_name": "Jane",
    "parent_last_name": "Smith",
    "parent_tel": "+447700900000"
  }
  ```
- [x] Test the trigger endpoint using curl:
  ```bash
  curl -X POST https://j0wucljch3.execute-api.eu-north-1.amazonaws.com/prod/trigger \
  -H "Content-Type: application/json" \
  -d @test_payload.json
  ```
- [x] Verify the response is successful
- [x] Check CloudWatch logs to confirm the payload was logged correctly

## Verification Checklist
- [x] Lambda function deployed successfully
- [x] API Gateway endpoints created
- [x] Trigger endpoint accepts and logs JSON payload
- [x] Webhook endpoint responds to requests
- [x] CloudWatch logs show correct information

## Next Steps
After completing Phase 1, we'll move on to Phase 2 where we'll integrate Twilio to send WhatsApp template messages. 

## Phase 1 Completion Report

### Issues Resolved

1. **API Gateway Route Handling**: Fixed the Lambda function to correctly handle the API Gateway v2 format for path extraction.
2. **Path Extraction**: Updated the Lambda function to extract the path from the correct location in the event object.
3. **Deployment**: Created a new deployment and updated the prod stage to use it.

### Current Status

- Both /trigger and /webhook endpoints are working correctly.
- The Lambda function is correctly processing and logging the registration data.
- The API Gateway is correctly routing requests to the Lambda function.

### API Details

- **API Gateway Endpoint**: https://j0wucljch3.execute-api.eu-north-1.amazonaws.com/prod
- **Trigger Endpoint**: https://j0wucljch3.execute-api.eu-north-1.amazonaws.com/prod/trigger
- **Webhook Endpoint**: https://j0wucljch3.execute-api.eu-north-1.amazonaws.com/prod/webhook

### Next Steps for Phase 2

1. Proceed to Phase 2: Twilio Integration
2. Set up CloudWatch alarms for monitoring
3. Implement error handling and validation
4. Add authentication and authorization

### Technical Notes for Future Reference

The key issue we encountered was that the Lambda function was not correctly extracting the path from the API Gateway v2 event format. In API Gateway v2, the path is located in `event['requestContext']['http']['path']` or `event['rawPath']`, not in `event.get('path', '')` as originally implemented.

The updated Lambda function now checks for the path in multiple locations, with priority given to the API Gateway v2 format:
```python
if 'requestContext' in event and 'http' in event['requestContext']:
    path = event['requestContext']['http']['path']
elif 'rawPath' in event:
    path = event['rawPath']
else:
    path = event.get('path', '')
```

This ensures that the Lambda function can handle both API Gateway v1 and v2 formats, making it more robust for future changes. 