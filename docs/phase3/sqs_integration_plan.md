# SQS Queue Integration Plan

## Overview

This document outlines the plan for integrating Amazon SQS (Simple Queue Service) into our WhatsApp chatbot application. While the SQS queue was initially planned for Phase 1a, it has been deferred to Phase 3 to be implemented alongside the OpenAI integration.

## Why SQS Queue?

The SQS queue will provide several important benefits for our webhook processing:

1. **Message Buffering**: Provides a buffer for high-traffic periods on the webhook endpoint
2. **Message Reliability**: Ensures no messages are lost during concurrent processing
3. **Asynchronous Processing**: Allows immediate response to Twilio while processing messages asynchronously
4. **Concurrency Handling**: Prevents timeouts when multiple users respond at the same time
5. **Scalability**: Enables the system to handle spikes in traffic, especially during registration season

## Current Implementation Status

The codebase already contains several components related to SQS integration:

1. **CDK Stack Definition**: The AWS CDK stack includes:
   - SQS queue creation
   - Lambda permissions to send messages to the queue
   - SQS event source for Lambda
   - Environment variable for the queue URL

2. **Lambda Function Code**: The Lambda function includes:
   - `queue_webhook_message` function to send messages to SQS
   - Fallback logic to process webhooks directly if SQS is not available
   - `process_sqs_messages` function to handle messages from the queue

## Implementation Plan for Phase 3

1. **Enable SQS Queue in Deployment**:
   - Ensure the SQS queue is properly deployed with the CDK stack
   - Verify the Lambda function has the correct permissions

2. **Update Lambda Handler**:
   - Modify the Lambda handler to use the SQS queue for webhook processing
   - Ensure the `WEBHOOK_QUEUE_URL` environment variable is properly set

3. **Enhance Message Processing**:
   - Update the `process_sqs_messages` function to integrate with OpenAI
   - Add database operations for conversation state tracking

4. **Testing**:
   - Test with simulated high-traffic scenarios
   - Verify message processing reliability
   - Measure response times with and without the queue

5. **Monitoring**:
   - Set up CloudWatch alarms for queue depth
   - Monitor for any failed message processing
   - Track queue processing latency

## Integration with OpenAI

The SQS queue will work alongside the OpenAI integration by:

1. Receiving webhook messages and immediately acknowledging them to Twilio
2. Queuing the messages for asynchronous processing
3. Processing each message with OpenAI to generate appropriate responses
4. Storing conversation state in the database
5. Sending responses back to users via Twilio

This approach ensures that even during high-traffic periods, the system can maintain responsiveness and process all messages reliably. 