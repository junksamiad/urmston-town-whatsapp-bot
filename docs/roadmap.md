# WhatsApp Chatbot Development and Deployment Roadmap
## Urmston Town Juniors FC Registration System

## Infrastructure and Deployment Approach

### Infrastructure as Code: AWS CDK
- Using Python as the programming language for infrastructure definition
- Leveraging CDK constructs for AWS resources
- Generating CloudFormation templates for actual deployment
- Maintaining infrastructure code alongside application code for version control

### Database Strategy
- **Neon PostgreSQL** for both conversation management and player registration data:
  - Serverless PostgreSQL that scales to zero when not in use
  - Perfect for seasonal usage pattern (heavy for 2 months, minimal rest of year)
  - Free tier likely sufficient for ~200 records
  - Strong consistency for immediate read-after-write operations
  - ACID transactions for data integrity
  - Flexible querying capabilities for all player data fields

### Simplified Approach
- Focus on direct registration initiation through API endpoint
- Accept minimal required data to start the registration process
- No initial Airtable integration or data migration in early phases
- Potential for a simple front-end interface for team managers in later phases

### Deployment Strategy
- Develop locally with CDK
- Test with CDK local testing capabilities
- Deploy to AWS with minimal resource footprint
- Optimize for pay-per-use pricing model

## Overall Architecture

### Core Components
1. **Single Lambda Function with Multiple Routes**:
   - `/trigger` - Processes basic player/parent data and initiates registration conversations
   - `/webhook` - Handles ongoing registration dialogue
2. **OpenAI Integration** - Powers the conversation intelligence
3. **Twilio API Integration** - Manages WhatsApp messaging
4. **Neon PostgreSQL Database** - Stores conversation state and player registration data
5. **Monitoring & Logging** - Basic CloudWatch logs and alerts

### Data Flow
1. **Initial Registration**: API Endpoint → Trigger Route → OpenAI Assistant → Twilio API → Parent
2. **Conversation**: Parent reply → Twilio webhook → Webhook Route → OpenAI Assistant → Twilio API → Parent
3. **Registration Process**: Different OpenAI Assistants handle different stages of registration

## Phased Development Approach

### Phase 1: Basic Lambda Setup (MVP) ✅
- ✅ Create a single AWS Lambda function with route handling using CDK
- ✅ Implement the `/trigger` route that:
  - ✅ Accepts a JSON payload with simplified player/parent information:
    - player_first_name
    - player_last_name
    - team_name
    - age_group
    - manager_full_name
    - current_registration_season
    - parent_first_name
    - parent_last_name
    - parent_tel
  - ✅ Logs the received data (no database integration yet)
  - ✅ Returns a success response
- Deploy this to AWS with HTTP API Gateway (cost-effective option)
- Test with simple HTTP requests using curl or similar tools

### Phase 1a: Infrastructure Hardening ✅
- ✅ Implement API Key Authentication for the `/trigger` endpoint:
  - ✅ Create API key and usage plan
  - ✅ Validate API key in Lambda function
  - ✅ Test with valid and invalid keys
- ✅ Configure Rate Limiting:
  - ✅ Set up usage plan with rate limits (25 requests per second, 50 burst)
  - ✅ Test with multiple concurrent requests
- ✅ Implement Concurrency Handling:
  - ✅ Add structured logging with request IDs
  - ✅ Test with bulk player invitations (25 concurrent requests)
- ✅ Prepare for SQS Queue for the `/webhook` endpoint:
  - ✅ Add code to handle webhook messages directly when SQS is not available
  - ✅ Implement fallback logic for when the SQS queue URL is not set
  - ✅ Test with both single and concurrent webhook requests
- ✅ Enhance Error Handling and Logging:
  - ✅ Add structured JSON logging with request IDs
  - ✅ Implement comprehensive error handling
  - ✅ Add request IDs to all responses for traceability
- ✅ Create Comprehensive Test Scripts:
  - ✅ API key authentication tests
  - ✅ Rate limiting tests
  - ✅ Bulk player invitation tests
  - ✅ Webhook endpoint tests
  - ✅ Webhook concurrency tests

### Phase 2: Twilio Integration
- Enhance the trigger route to:
  - Format data for Twilio WhatsApp templates
  - Send template messages via Twilio API
- Add simple API key validation (environment variable)
- Add error handling and logging for Twilio interactions
- Test end-to-end flow from trigger to WhatsApp message
- Implement the following functions:
  ```python
  def send_whatsapp_template(phone_number, parent_name, player_name, team_name, manager_name, season):
      """Send WhatsApp template message via Twilio API"""
      # Initialize Twilio client
      # Send message with template variables
      # Return message SID
  ```
- Template message: "The manager {manager_name} of the team {team_name} {age_group} has invited you to register {player_name} for the {season} season. Let me know if you are happy to register and we will get that sorted."

### Phase 3: OpenAI Integration
- Implement OpenAI Assistant creation and configuration
- Add thread management for conversations
- Set up function calling for WhatsApp message generation
- Define the `initial_message` function for OpenAI:
  ```json
  {
    "name": "initial_message",
    "description": "Send an initial WhatsApp message to start the registration process",
    "parameters": {
      "type": "object",
      "properties": {
        "parent_name": {
          "type": "string",
          "description": "The parent or guardian's name"
        },
        "player_name": {
          "type": "string",
          "description": "The player's name"
        },
        "team_name": {
          "type": "string",
          "description": "The team name"
        },
        "age_group": {
          "type": "string",
          "description": "The age group"
        },
        "manager_name": {
          "type": "string",
          "description": "The team manager's name"
        },
        "season": {
          "type": "string",
          "description": "The registration season"
        }
      },
      "required": ["parent_name", "player_name", "team_name", "manager_name", "season"]
    }
  }
  ```
- Create the system prompt for the OpenAI Assistant:
  ```
  You are Omega, the Urmston Town Juniors FC Registration Assistant. Your role is to help parents register their children for the upcoming football season.

  For initial contact, you should:
  1. Review the player information provided
  2. Call the initial_message function with the parent's name, player's name, team name, manager's name, and season
  3. This will send a WhatsApp message to start the registration process

  Be friendly, professional, and focused on making the registration process as smooth as possible for parents.
  ```
- Implement run completion monitoring and tool output submission
- Add basic in-memory caching for thread_ids (temporary solution)
- Test conversation flow with sample registration scenarios

### Phase 4: Database Integration
- Set up Neon PostgreSQL with the following simplified schema:
  ```sql
  -- Conversations table for WhatsApp chatbot state
  CREATE TABLE conversations (
      conversation_id SERIAL PRIMARY KEY,
      phone_number VARCHAR(20) NOT NULL,
      thread_id VARCHAR(100) NOT NULL,
      registration_state VARCHAR(50) NOT NULL DEFAULT 'initial_contact',
      last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      last_user_message_timestamp TIMESTAMP, -- Track when user last messaged (for 24-hour window)
      user_messages JSONB DEFAULT '[]'::jsonb, -- Array of user messages
      assistant_messages JSONB DEFAULT '[]'::jsonb, -- Array of assistant messages
      temporary_data JSONB,
      UNIQUE(phone_number)
  );

  -- Players table with simplified fields
  CREATE TABLE players (
      id SERIAL PRIMARY KEY,
      player_first_name VARCHAR(50),
      player_last_name VARCHAR(50),
      team_name VARCHAR(50),
      age_group VARCHAR(20),
      manager_full_name VARCHAR(100),
      registration_season VARCHAR(20),
      
      -- Parent/Guardian information
      parent_first_name VARCHAR(50),
      parent_last_name VARCHAR(50),
      parent_tel VARCHAR(20),
      
      -- Registration status fields
      registration_status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'confirmed', 'declined', 'completed'
      registration_notes TEXT,
      is_returning_player BOOLEAN DEFAULT FALSE,
      
      -- System fields
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      
      -- Foreign key to conversations
      conversation_id INTEGER REFERENCES conversations(conversation_id)
  );

  -- Indexes for performance
  CREATE INDEX idx_conversations_phone ON conversations(phone_number);
  CREATE INDEX idx_players_parent_tel ON players(parent_tel);
  CREATE INDEX idx_players_registration_status ON players(registration_status);
  ```

- Implement database helper functions:
  ```python
  def get_db_connection():
      """Get a connection to the Neon PostgreSQL database"""
      # Return database connection
  
  def check_existing_conversation(conn, phone_number):
      """Check if a conversation exists for this phone number"""
      # Query conversations table
      # Return conversation record if found
  
  def archive_conversation(conn, conversation_id):
      """Archive an existing conversation"""
      # Update conversation state to 'archived'
  
  def create_conversation(conn, phone_number):
      """Create a new conversation record"""
      # Insert new conversation
      # Return conversation_id
  
  def update_conversation_thread(conn, conversation_id, thread_id):
      """Update conversation with thread_id"""
      # Update conversation record
  
  def store_player_data(conn, player_data, conversation_id):
      """Store player data in the database"""
      # Insert player data with conversation_id
      # Set registration_status to 'pending'
  
  def update_player_registration_status(conn, player_id, status, notes=None):
      """Update player registration status"""
      # Update player record with new status and notes
      # Update last_updated timestamp
      
  def add_user_message(conn, conversation_id, message_content, metadata=None):
      """Add a user message to the conversation's user_messages array"""
      # Create message object with timestamp, content, and metadata
      # Append to user_messages JSONB array
      # Update last_user_message_timestamp
      message_obj = {
          "timestamp": datetime.now().isoformat(),
          "content": message_content,
          "metadata": metadata or {}
      }
      query = """
          UPDATE conversations 
          SET user_messages = user_messages || %s::jsonb,
              last_user_message_timestamp = NOW(),
              last_interaction = NOW()
          WHERE conversation_id = %s
      """
      # Execute query with (json.dumps(message_obj), conversation_id)
      
  def add_assistant_message(conn, conversation_id, message_content, metadata=None):
      """Add an assistant message to the conversation's assistant_messages array"""
      # Create message object with timestamp, content, and metadata
      # Append to assistant_messages JSONB array
      message_obj = {
          "timestamp": datetime.now().isoformat(),
          "content": message_content,
          "metadata": metadata or {}
      }
      query = """
          UPDATE conversations 
          SET assistant_messages = assistant_messages || %s::jsonb,
              last_interaction = NOW()
          WHERE conversation_id = %s
      """
      # Execute query with (json.dumps(message_obj), conversation_id)
      
  def get_conversation_history(conn, conversation_id, limit=10):
      """Get the conversation history in chronological order"""
      # Retrieve conversation record
      # Extract and merge user_messages and assistant_messages
      # Sort by timestamp
      # Return the combined history (limited to specified number if needed)
  
  def check_24h_window_status(conn, conversation_id):
      """Check if we're within the 24-hour messaging window"""
      # Get last_user_message_timestamp
      # Calculate time difference from now
      # Return True if within 24 hours, False otherwise
  ```

- Add new OpenAI functions for the registration assistant:
  ```json
  {
    "name": "update_registration_status",
    "description": "Update the registration status of a player",
    "parameters": {
      "type": "object",
      "properties": {
        "player_id": {
          "type": "string",
          "description": "The player's ID"
        },
        "status": {
          "type": "string",
          "enum": ["pending", "confirmed", "declined", "completed"],
          "description": "The new registration status"
        },
        "is_returning_player": {
          "type": "boolean",
          "description": "Whether the player was registered last season"
        },
        "notes": {
          "type": "string",
          "description": "Optional notes about the status change"
        }
      },
      "required": ["player_id", "status"]
    }
  }
  ```

- Enhance the trigger route to use database:
  - Check for existing conversations
  - Create new conversation records
  - Store thread_id and player data
  - Use transactions for data integrity

- Implement state management for the registration process:
  - Define clear state transitions (initial_contact → returning_player_check → info_collection → completed)
  - Configure OpenAI Assistant behavior based on current state

- **Handling Existing Registrations**:
  - Implement detection of existing registration attempts in the trigger route:
    ```python
    def handle_trigger(event):
        # Extract phone number from request
        parent_tel = body.get('parent_tel')
        
        # Check if a conversation already exists for this phone number
        existing_conversation = check_existing_conversation(conn, parent_tel)
        
        if existing_conversation:
            # Handle existing registration scenario with specialized template
            return handle_existing_registration(conn, existing_conversation, body)
        else:
            # Handle new registration scenario with standard template
            return handle_new_registration(conn, body)
    ```
  
  - Create specialized template for existing registrations:
    ```python
    def send_existing_registration_template(phone_number, parent_name, player_name):
        """Send a specialized template for existing registrations"""
        # Initialize Twilio client
        # Send message using a different template acknowledging previous attempt
        # Template: "Hello {parent_name}, we noticed you've already started the registration process for {player_name}. Please let us know if you experienced any issues with the previous registration attempt, and we'll help you resolve them."
    ```
  
  - Enhance webhook handler to process responses with awareness of existing conversations:
    ```python
    def handle_webhook(event):
        # Extract phone number and message from webhook
        # Check if conversation exists for this phone number
        # Add user message to conversation history
        # Process with OpenAI based on current registration state
    ```
  
  - Configure OpenAI Assistant to handle existing registration scenarios:
    ```
    System prompt addition:
    When a parent responds to a message about an existing registration:
    1. Acknowledge that they've previously started the registration process
    2. Ask them if they experienced any issues with the previous attempt
    3. Based on their response:
       - Help resolve specific issues
       - Continue from where they left off based on current state
       - Offer to reset their registration if needed
    ```

### Phase 5: Advanced Features (Future)
- Create a simple web interface for team managers to submit player/parent data
- Implement multiple specialized OpenAI Assistants for different registration stages
- Add payment processing integration
- Implement photo upload functionality
- Add comprehensive logging and basic alerting
- Prepare for website integration (see Phase 6)

### Phase 6: Website Deployment
- Deploy the registration system to a custom domain/website
- Implement components:
  - Admin dashboard for team managers to view registration status
  - Registration form for direct player registration through the website
  - Secure authentication for club officials
  - Integration with the WhatsApp chatbot system
- Technical implementation:
  - Set up domain and hosting (e.g., AWS Amplify, Vercel, or traditional hosting)
  - Create a React/Next.js frontend for the admin interface
  - Implement API endpoints to connect the website with the existing Lambda backend
  - Set up SSL certificates for secure connections
  - Configure DNS settings to point to the deployed application
- Security considerations:
  - Implement proper authentication and authorization
  - Secure API endpoints with appropriate access controls
  - Ensure GDPR compliance for player/parent data
  - Set up regular backups of the database
- Testing and deployment:
  - Develop a staging environment for testing
  - Implement CI/CD pipeline for automated deployments
  - Conduct thorough testing before going live
  - Create a rollback strategy in case of issues

## Technical Implementation Details

### Trigger Route Implementation
```python
def handle_trigger(event):
    """Handle the trigger route for initiating registration"""
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
        
        parent_tel = body.get('parent_tel')
        team_name = body.get('team_name', 'Urmston Town Juniors FC')
        age_group = body.get('age_group', '')
        manager_full_name = body.get('manager_full_name', 'Team Manager')
        current_registration_season = body.get('current_registration_season', '2025-26')
        
        if not parent_tel or not player_first_name or not player_last_name:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Missing required fields'
                })
            }
        
        # Create context object
        context_obj = {
            "player_data": {
                "player_first_name": player_first_name,
                "player_last_name": player_last_name,
                "team_name": team_name,
                "age_group": age_group,
                "manager_full_name": manager_full_name,
                "current_registration_season": current_registration_season,
                "parent_first_name": parent_first_name,
                "parent_last_name": parent_last_name,
                "parent_tel": parent_tel
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # In Phase 2-4, we'll add database, OpenAI, and Twilio integration here
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Registration process initiated',
                'player': player_full_name,
                'parent': parent_full_name,
                'team': f"{team_name} {age_group}",
                'status': 'pending'
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

### OpenAI Assistant Configurations

#### Initial Contact Assistant
- **System Prompt**:
  ```
  You are Omega, the Urmston Town Juniors FC Registration Assistant. Your role is to help parents register their children for the upcoming football season.

  For initial contact, you should:
  1. Review the player information provided
  2. Call the initial_message function with the parent's name, player's name, team name, manager's name, and season
  3. This will send a WhatsApp message to start the registration process

  Be friendly, professional, and focused on making the registration process as smooth as possible for parents.
  ```

#### Registration Assistant
- **System Prompt**:
  ```
  You are Omega, the Urmston Town Juniors FC Registration Assistant. Your role is to help parents register their children for the upcoming football season.

  When a parent responds to your initial message:
  1. First, ask if they were registered last season
  2. If they indicate they want to register their child, guide them through the process
  3. If they indicate they do NOT want to register, politely acknowledge this and update the registration status to "declined"
  4. Update the registration status appropriately at each step

  Use the update_registration_status function to mark records as "confirmed", "declined", or "completed" based on the conversation.

  Be friendly, professional, and focused on making the registration process as smooth as possible for parents.
  ```

## Development Environment Setup
- Python 3.9+ for Lambda functions and CDK code
- Node.js for CDK CLI
- AWS CLI configured with appropriate credentials
- Virtual environment for dependency management
- VS Code or preferred IDE with Python and AWS extensions 
- Neon.tech account for PostgreSQL database
- Twilio account with WhatsApp Business API access
- OpenAI API account with Assistants API access 

## Phase 1a Implementation Notes

### Security Enhancements
- API key authentication implemented for the `/trigger` endpoint
- API key validation in Lambda function with proper error responses
- Rate limiting configured to prevent abuse and ensure system stability

### Performance Optimizations
- Concurrency handling implemented to support bulk player invitations
- Webhook endpoint designed for asynchronous processing with SQS
- Fallback mechanism for direct processing when SQS is not available

### Monitoring and Debugging
- Structured JSON logging with request IDs for traceability
- Comprehensive error handling with detailed error messages
- Request IDs included in all responses for correlation

### Testing Framework
- Comprehensive test scripts created for all key functionality
- Tests for API key authentication, rate limiting, bulk invitations, and webhook handling
- All tests passing successfully, confirming system readiness for Phase 2 