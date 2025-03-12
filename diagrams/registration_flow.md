# Urmston Town WhatsApp Bot - Registration Flow Diagram

```mermaid
sequenceDiagram
    participant TM as Team Manager
    participant API as API Gateway
    participant Lambda as Lambda Function
    participant Twilio as Twilio API
    participant Parent as Parent/Guardian
    
    Note over TM, Parent: Phase 1: Invitation (Implemented)
    TM->>API: POST /trigger with player details
    API->>Lambda: Forward request with API key validation
    Lambda->>Twilio: Send template message
    Twilio->>Parent: Deliver WhatsApp invitation
    
    Note over Parent, Lambda: Phase 2: Basic Response Handling (Partially Implemented)
    Parent->>Twilio: Reply to WhatsApp message
    Twilio->>API: Webhook with message content
    API->>Lambda: Forward webhook
    Lambda-->>Twilio: Acknowledge receipt (no processing yet)
    
    Note over Parent, Lambda: Phase 3: Conversational Flow (Future)
    Lambda->>Lambda: Process message with OpenAI
    Lambda->>Twilio: Send response message
    Twilio->>Parent: Deliver response
```

## Registration Process Description

### Phase 1: Invitation (Implemented)
- Team Manager initiates the registration process by sending player details to the `/trigger` endpoint
- API Gateway validates the API key
- System sends a WhatsApp template message to the parent/guardian with registration information

### Phase 2: Basic Response Handling (Partially Implemented)
- Parent/Guardian responds to the WhatsApp message
- Twilio sends a webhook to our API with the message content
- System acknowledges receipt of the webhook but does not process the message yet

### Phase 3: Conversational Flow (Future)
- System will process incoming messages using OpenAI
- System will send appropriate responses based on the conversation context
- Parent/Guardian will receive personalized responses

### Technical Implementation
- Twilio WhatsApp Business API for messaging
- AWS Lambda for serverless processing
- AWS API Gateway for HTTP endpoints with API key authentication
- AWS Secrets Manager for secure credential storage
- SSM Parameter Store for configuration
- OpenAI integration (planned for Phase 3)
- SQS Queue for webhook message buffering (planned for Phase 3)
  - Will provide message reliability during high traffic
  - Enables asynchronous processing of incoming messages
  - See `docs/phase3/sqs_integration_plan.md` for details
