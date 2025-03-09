#!/bin/bash

# Package the Lambda function
cd src/lambda
zip -r ../../lambda_function.zip .

# Update the Lambda function code
aws lambda update-function-code \
  --function-name urmston-town-registration-whatsapp \
  --zip-file fileb://../../lambda_function.zip \
  --region eu-north-1

# Return to the project root
cd ../.. 