# Urmston Town WhatsApp Bot - Future Registration Flow Diagram

```mermaid
sequenceDiagram
    participant TM as Team Manager
    participant API as API Gateway
    participant Lambda as Lambda Function
    participant SQS as SQS Queue
    participant OpenAI as OpenAI API
    participant DB as Database
    participant Twilio as Twilio API
    participant Parent as Parent/Guardian
    
    Note over TM, Parent: Phase 1: Invitation (Implemented)
    TM->>API: POST /trigger with player details
    API->>Lambda: Forward request with API key validation
    Lambda->>Twilio: Send template message
    Twilio->>Parent: Deliver WhatsApp invitation
    
    Note over Parent, DB: Phase 3: Full Registration Flow (Planned)
    Parent->>Twilio: Reply to WhatsApp message
    Twilio->>API: Webhook with message content
    API->>Lambda: Forward webhook
    Lambda->>SQS: Queue message for async processing
    Lambda-->>Twilio: Immediate acknowledgment
    SQS->>Lambda: Deliver message for processing
    Lambda->>DB: Store conversation state
    Lambda->>OpenAI: Process message with AI
    OpenAI->>Lambda: Generate response
    Lambda->>DB: Update registration data
    Lambda->>Twilio: Send response message
    Twilio->>Parent: Deliver response
    
    Note over Parent, DB: Conversation continues until registration complete
    Parent->>Twilio: Send additional information
    Twilio->>API: Webhook with message
    API->>Lambda: Forward webhook
    Lambda->>SQS: Queue message for async processing
    Lambda-->>Twilio: Immediate acknowledgment
    SQS->>Lambda: Deliver message for processing
    Lambda->>DB: Update conversation state
    Lambda->>OpenAI: Process with context
    OpenAI->>Lambda: Generate contextual response
    Lambda->>DB: Update registration data
    Lambda->>Twilio: Send response message
    Twilio->>Parent: Deliver response
```

## Future Registration Process

This diagram illustrates the planned full registration flow that will be implemented in Phase 3, including:

1. **SQS Queue Integration** for reliable message handling:
   - Buffers incoming webhook messages during high traffic
   - Enables asynchronous processing
   - Ensures no messages are lost
   - Provides immediate response to Twilio

2. **OpenAI Integration** for intelligent conversation handling:
   - Processes messages with context awareness
   - Generates appropriate responses
   - Guides users through the registration process

3. **Database Storage** for:
   - Conversation state tracking
   - Registration data persistence
   - Player information management

The system will maintain context throughout the conversation, allowing for a natural registration experience where parents can provide information incrementally and receive appropriate guidance at each step.

For more details on the SQS integration plan, see `docs/phase3/sqs_integration_plan.md`.
