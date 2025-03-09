# Urmston Town WhatsApp Bot - Registration Flow Diagram

```mermaid
sequenceDiagram
    participant TM as Team Manager
    participant API as API Gateway
    participant Lambda as Lambda Function
    participant Twilio as Twilio API
    participant Parent as Parent/Guardian
    participant SQS as SQS Queue
    
    Note over TM, Parent: Phase 1: Invitation
    TM->>API: POST /trigger with player details
    API->>Lambda: Forward request
    Lambda->>Twilio: Send template message
    Twilio->>Parent: Deliver WhatsApp invitation
    
    Note over Parent, SQS: Phase 2: Response Handling
    Parent->>Twilio: Reply to WhatsApp message
    Twilio->>API: Webhook with message content
    API->>Lambda: Forward webhook
    Lambda->>SQS: Queue message for processing
    SQS->>Lambda: Process message (async)
    Lambda->>Twilio: Send response message
    Twilio->>Parent: Deliver response
```

## Registration Process Description

### Phase 1: Invitation
- Team Manager initiates the registration process by sending player details to the `/trigger` endpoint
- System sends a WhatsApp template message to the parent/guardian with registration information

### Phase 2: Response Handling
- Parent/Guardian responds to the WhatsApp message
- Twilio sends a webhook to our API with the message content
- System queues the message for processing
- System processes the message and sends a response
- Parent/Guardian receives the response message

### Technical Implementation
- Twilio WhatsApp Business API for messaging
- AWS Lambda for serverless processing
- AWS SQS for message queuing
- AWS API Gateway for HTTP endpoints
- AWS Secrets Manager for secure credential storage
