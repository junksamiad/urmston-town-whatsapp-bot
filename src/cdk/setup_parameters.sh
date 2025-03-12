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

echo "SSM parameters created/updated successfully!"
echo "Phone Number: $TWILIO_PHONE_NUMBER"
echo "Template SID: $TWILIO_TEMPLATE_SID" 