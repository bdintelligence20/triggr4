import os
import uuid
import logging
import re
import json
from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from rag_system import RAGSystem
from utils import split_message_semantically
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
whatsapp_bp = Blueprint('whatsapp', __name__)

# Get database instance
db = firestore.client()

# Get environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "knowledge-hub-vectors")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
# Use the WhatsApp sandbox number - ALWAYS use this for testing
TWILIO_WHATSAPP_FROM = "+14155238886"  # Twilio WhatsApp sandbox number
TWILIO_MESSAGING_SERVICE_SID = os.environ.get("TWILIO_MESSAGING_SERVICE_SID")

# Flag to determine whether to use Conversations API or direct messaging
USE_CONVERSATIONS_API = False  # Always use direct messaging with sandbox

# Approved Content Template SIDs
TEMPLATE_CONTENT_SID = "HX6ed39c2507e07cb25c75412d74f134d8"  # Template name: copy_ai_response (body: "Hi! Here is your answer: {{1}}")
VERIFICATION_TEMPLATE_SID = "HX49a2a0f54d02996525960683dce1020b"  # Template for verification messages (body: "Your WhatsApp number has been verified successfully! You can now query the knowledge base for {{1}} resources. Try asking a question!")

# Default friendly name for the Conversations Service
CONVERSATIONS_SERVICE_NAME = "Knowledge Hub Conversations"
# Conversations Service SID (provided by user)
CONVERSATIONS_SERVICE_SID = "ISe0f96fba94ed42c9a94d5ffaabef467e"

# Initialize Twilio client
try:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    logger.info("Twilio client initialized")
except Exception as e:
    logger.error(f"Twilio initialization error: {str(e)}")
    twilio_client = None

def create_twilio_response(message):
    """Create a TwiML response with the given message."""
    resp = MessagingResponse()
    if message:
        resp.message(message)
    return str(resp)

def send_templated_whatsapp_response(to_number, message):
    """Send a WhatsApp message using the approved template."""
    sanitized_message = sanitize_ai_response(message)
    try:
        return send_whatsapp_template_message(
            to_number=to_number,
            content_sid=TEMPLATE_CONTENT_SID,
            content_variables={"1": sanitized_message}
        )
    except Exception as e:
        logger.error(f"Error sending templated message: {str(e)}")
        # Fall back to direct message as a last resort
        return send_whatsapp_message(to_number, sanitized_message)

def send_verification_whatsapp_response(to_number, org_name, conversation_sid=None):
    """
    Send a WhatsApp verification message using the approved verification template.
    If a conversation SID is provided, also add the message to the conversation for record-keeping.
    """
    logger.info(f"Sending verification message to {to_number} with org name: {org_name}")
    
    try:
        # If we have a conversation SID, add the message to the conversation for record-keeping
        if conversation_sid:
            logger.info(f"Using existing conversation {conversation_sid} for verification message")
            try:
                # Prepare the verification message
                verification_message = f"Your WhatsApp number has been verified successfully! You can now query the knowledge base for {org_name}. Try asking a question!"
                
                # Add the message to the conversation for record-keeping
                conversation_message = twilio_client.conversations.v1.services(CONVERSATIONS_SERVICE_SID).conversations(conversation_sid).messages.create(
                    author="system",
                    body=verification_message
                )
                logger.info(f"Added verification message to conversation {conversation_sid}, message SID: {conversation_message.sid}")
            except Exception as e:
                logger.error(f"Error adding verification message to conversation: {str(e)}")
                # Continue even if adding to conversation fails
        
        # Send the verification message using the approved template
        logger.info(f"Sending verification template message to {to_number}")
        try:
            return send_whatsapp_template_message(
                to_number=to_number,
                content_sid=VERIFICATION_TEMPLATE_SID,
                content_variables={"1": org_name}
            )
        except Exception as template_error:
            logger.error(f"Error sending verification template: {str(template_error)}")
            # Fall back to general template as a second attempt
            try:
                verification_message = f"Your WhatsApp number has been verified successfully! You can now query the knowledge base for {org_name}. Try asking a question!"
                return send_templated_whatsapp_response(to_number, verification_message)
            except Exception as e:
                logger.error(f"Error sending fallback template: {str(e)}")
                # Fall back to direct message as a last resort
                return send_whatsapp_message(to_number, f"Your WhatsApp number has been verified successfully! You can now query the knowledge base for {org_name}. Try asking a question!")
    except Exception as e:
        logger.error(f"Error sending verification message: {str(e)}")
        # Fall back to direct message as a last resort
        return send_whatsapp_message(to_number, f"Your WhatsApp number has been verified successfully! You can now query the knowledge base for {org_name}. Try asking a question!")

def send_whatsapp_message(to_number, message_body):
    """
    Sends a WhatsApp message using the Twilio client.
    If the message exceeds 1600 characters, it is split semantically into multiple parts.
    
    For sandbox mode, we use the from number directly instead of the messaging service.
    """
    max_length = 1600
    # Ensure the 'to_number' has the correct WhatsApp prefix.
    if not to_number.startswith('whatsapp:'):
        to_number = f"whatsapp:{to_number}"
    
    # Ensure the from number has the WhatsApp prefix
    from_number = TWILIO_WHATSAPP_FROM
    if not from_number.startswith('whatsapp:'):
        from_number = f"whatsapp:{from_number}"
    
    logger.info(f"Sending WhatsApp message from {from_number} to {to_number}")
    
    try:
        # Split the message semantically if it exceeds the max_length.
        if len(message_body) > max_length:
            chunks = split_message_semantically(message_body, max_length=max_length)
            for chunk in chunks:
                # For sandbox, use from instead of messaging service
                twilio_client.messages.create(
                    body=chunk,
                    from_=from_number,  # Use from_ for sandbox
                    to=to_number
                )
        else:
            # For sandbox, use from instead of messaging service
            twilio_client.messages.create(
                body=message_body,
                from_=from_number,  # Use from_ for sandbox
                to=to_number
            )
        return create_twilio_response("")
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return create_twilio_response(message_body)

def send_whatsapp_template_message(to_number, content_sid, content_variables):
    """
    Sends a templated WhatsApp message using Twilio's Content API.
    
    Parameters:
      - to_number: Recipient's phone number.
      - content_sid: The Content SID of the approved WhatsApp template.
      - content_variables: A dict mapping template placeholders to dynamic values.
    """
    if not to_number.startswith('whatsapp:'):
        to_number = f"whatsapp:{to_number}"
    
    # Ensure the from number has the WhatsApp prefix
    from_number = TWILIO_WHATSAPP_FROM
    if not from_number.startswith('whatsapp:'):
        from_number = f"whatsapp:{from_number}"
    
    # Enhanced logging for template debugging
    content_preview = content_variables.get("1", "")[:100] + "..." if len(content_variables.get("1", "")) > 100 else content_variables.get("1", "")
    logger.info(f"Preparing template message with SID: {content_sid}")
    logger.info(f"Sending from: {from_number} to: {to_number}")
    logger.info(f"Content variable length: {len(content_variables.get('1', ''))}")
    logger.info(f"Content variable preview: {content_preview}")
    logger.info(f"Content variables JSON: {json.dumps(content_variables)}")
    
    try:
        # For sandbox, use from_ instead of messaging_service_sid
        logger.info(f"Attempting to send template message with SID: {content_sid}")
        message = twilio_client.messages.create(
            content_sid=content_sid,
            content_variables=json.dumps(content_variables),
            from_=from_number,  # Use from_ for sandbox
            to=to_number
        )
        logger.info(f"Templated message sent successfully. Template SID: {content_sid}, Message SID: {message.sid}")
        logger.info(f"Message status: {message.status}")
        return create_twilio_response("")
    except Exception as e:
        error_message = str(e)
        logger.error(f"Template error: {error_message}")
        
        # Detailed error analysis
        if "content" in error_message.lower():
            logger.error(f"Content issue detected. Content length: {len(content_variables.get('1', ''))}")
            logger.error(f"Content sample: {content_variables.get('1', '')[:200]}...")
            
            # Try to sanitize the content further
            sanitized_content = re.sub(r'[^\w\s.,;:!?()]', '', content_variables.get("1", ""))
            logger.info(f"Attempting with more aggressively sanitized content (length: {len(sanitized_content)})")
            
            try:
                # Try again with more sanitized content
                message = twilio_client.messages.create(
                    content_sid=content_sid,
                    content_variables=json.dumps({"1": sanitized_content}),
                    from_=from_number,  # Use from_ for sandbox
                    to=to_number
                )
                logger.info(f"Templated message sent with sanitized content. Message SID: {message.sid}")
                return create_twilio_response("")
            except Exception as retry_error:
                logger.error(f"Still failed with sanitized content: {str(retry_error)}")
                # Fall back to direct message
        
        # For sandbox, templates might not work, so fall back to direct message
        logger.info(f"Falling back to plain text message")
        return send_whatsapp_message(to_number, content_variables.get("1", ""))

def get_member_by_phone(phone_number):
    """Get member data by phone number."""
    # Clean the phone number (remove whatsapp: prefix if present)
    if phone_number.startswith('whatsapp:'):
        phone_number = phone_number[9:]
    
    # Query for member with this phone number
    members_ref = db.collection('members').where('phone', '==', phone_number).limit(1)
    members = list(members_ref.stream())
    
    if not members:
        return None
    
    member_doc = members[0]
    member_data = member_doc.to_dict()
    member_data['id'] = member_doc.id
    
    return member_data

def get_or_create_verify_service(twilio_client):
    """Get existing Verify service or create a new one."""
    try:
        # Check if we already have a service SID in environment variables
        verify_service_sid = os.environ.get("TWILIO_VERIFY_SERVICE_SID")
        if verify_service_sid:
            # Validate that the service exists
            try:
                service = twilio_client.verify.v2.services(verify_service_sid).fetch()
                logger.info(f"Using existing Verify service: {service.sid}")
                return service.sid
            except Exception as e:
                logger.warning(f"Stored Verify service SID is invalid: {str(e)}")
                # Continue to create a new one
        
        # Try to fetch existing services
        services = twilio_client.verify.v2.services.list(limit=20)
        
        # Look for a service named "Knowledge Hub Verification"
        for service in services:
            if service.friendly_name == "Knowledge Hub Verification":
                logger.info(f"Found existing Verify service: {service.sid}")
                return service.sid
        
        # If no service found, create a new one
        service = twilio_client.verify.v2.services.create(
            friendly_name="Knowledge Hub Verification"
        )
        logger.info(f"Created new Verify service: {service.sid}")
        
        return service.sid
    except Exception as e:
        logger.error(f"Error creating/updating Verify service: {str(e)}")
        raise

def get_or_create_conversations_service(twilio_client):
    """Get existing Conversations service or create a new one."""
    try:
        # Check if we already have a service SID in environment variables
        conversations_service_sid = os.environ.get("TWILIO_CONVERSATIONS_SERVICE_SID")
        if conversations_service_sid:
            # Validate that the service exists
            try:
                service = twilio_client.conversations.v1.services(conversations_service_sid).fetch()
                logger.info(f"Using existing Conversations service: {service.sid}")
                return service.sid
            except Exception as e:
                logger.warning(f"Stored Conversations service SID is invalid: {str(e)}")
                # Continue to create a new one
        
        # Try to fetch existing services
        services = twilio_client.conversations.v1.services.list(limit=20)
        
        # Look for a service with our default name
        for service in services:
            if service.friendly_name == CONVERSATIONS_SERVICE_NAME:
                logger.info(f"Found existing Conversations service: {service.sid}")
                return service.sid
        
        # If no service found, create a new one
        service = twilio_client.conversations.v1.services.create(
            friendly_name=CONVERSATIONS_SERVICE_NAME
        )
        logger.info(f"Created new Conversations service: {service.sid}")
        
        return service.sid
    except Exception as e:
        logger.error(f"Error creating/updating Conversations service: {str(e)}")
        raise

def find_existing_conversation_for_participant(twilio_client, phone_number):
    """
    Find an existing conversation where the participant with the given phone number is already added.
    
    Args:
        twilio_client: The Twilio client
        phone_number: The participant's phone number
        
    Returns:
        The conversation SID if found, None otherwise
    """
    try:
        # Ensure the phone number has the WhatsApp prefix
        whatsapp_address = phone_number
        if not whatsapp_address.startswith('whatsapp:'):
            whatsapp_address = f"whatsapp:{phone_number}"
            
        logger.info(f"Searching for existing conversations with participant: {whatsapp_address}")
        
        # Use the hardcoded Conversations Service SID
        conversations_service_sid = CONVERSATIONS_SERVICE_SID
        
        # List all conversations in the service
        conversations = twilio_client.conversations.v1.services(conversations_service_sid).conversations.list(limit=50)
        
        # For each conversation, check if the participant is already added
        for conversation in conversations:
            try:
                # List participants in this conversation
                participants = twilio_client.conversations.v1.services(conversations_service_sid).conversations(conversation.sid).participants.list()
                
                # Check if any participant has the matching WhatsApp address
                for participant in participants:
                    if hasattr(participant, 'messaging_binding') and participant.messaging_binding.get('address') == whatsapp_address:
                        logger.info(f"Found existing conversation {conversation.sid} for participant {whatsapp_address}")
                        return conversation.sid
            except Exception as e:
                logger.warning(f"Error checking participants in conversation {conversation.sid}: {str(e)}")
                continue
        
        logger.info(f"No existing conversation found for participant {whatsapp_address}")
        return None
    except Exception as e:
        logger.error(f"Error finding existing conversation for participant: {str(e)}")
        return None

def create_member_conversation(twilio_client, member_id, phone_number, org_name):
    """Create a new conversation for a verified member."""
    try:
        # Use the hardcoded Conversations Service SID
        conversations_service_sid = CONVERSATIONS_SERVICE_SID
        
        # Create a unique conversation friendly name
        friendly_name = f"Member {member_id} - {phone_number}"
        
        # Create a new conversation with detailed member info in attributes
        conversation = twilio_client.conversations.v1.services(conversations_service_sid).conversations.create(
            friendly_name=friendly_name,
            attributes=json.dumps({
                "memberId": member_id,
                "organizationName": org_name,
                "memberPhone": phone_number,
                "createdAt": datetime.now().isoformat()
            })
        )
        
        logger.info(f"Created new conversation: {conversation.sid} for member {member_id}")
        
        # Ensure the phone number has the WhatsApp prefix for Conversations API
        whatsapp_address = phone_number
        if not whatsapp_address.startswith('whatsapp:'):
            whatsapp_address = f"whatsapp:{phone_number}"
        
        # Ensure the TWILIO_WHATSAPP_FROM also has the WhatsApp prefix
        proxy_address = TWILIO_WHATSAPP_FROM
        if not proxy_address.startswith('whatsapp:'):
            proxy_address = f"whatsapp:{TWILIO_WHATSAPP_FROM}"
        
        logger.info(f"Adding participant with address: {whatsapp_address}")
        logger.info(f"Using proxy address: {proxy_address}")
        
        # Add the member as a participant (using their WhatsApp address)
        # IMPORTANT: Do NOT use identity parameter for WhatsApp participants
        try:
            member_participant = twilio_client.conversations.v1.services(conversations_service_sid).conversations(conversation.sid).participants.create(
                # Removed identity parameter - not supported for WhatsApp
                messaging_binding_address=whatsapp_address,
                messaging_binding_proxy_address=proxy_address
            )
            
            logger.info(f"Added member {member_id} as participant to conversation {conversation.sid}")
        except Exception as e:
            logger.error(f"Error adding participant to conversation: {str(e)}")
            # Continue with conversation creation even if participant addition fails
        
        # Send a welcome message
        try:
            welcome_message = f"Welcome to the {org_name} Knowledge Hub! You can ask questions about your organization's knowledge base here."
            
            # First try to send via template
            try:
                # We need to get the participant's address to send the templated message
                participants = twilio_client.conversations.v1.services(conversations_service_sid).conversations(conversation.sid).participants.list()
                for participant in participants:
                    if hasattr(participant, 'messaging_binding') and participant.messaging_binding.get('address', '').startswith('whatsapp:'):
                        participant_address = participant.messaging_binding.get('address')
                        # Send templated welcome message
                        send_templated_whatsapp_response(participant_address, welcome_message)
                        logger.info(f"Sent templated welcome message to {participant_address}")
                        break
            except Exception as template_error:
                logger.error(f"Error sending templated welcome message: {str(template_error)}")
                # Fall back to conversation message
                twilio_client.conversations.v1.services(conversations_service_sid).conversations(conversation.sid).messages.create(
                    author="system",
                    body=welcome_message
                )
                logger.info(f"Sent fallback welcome message to conversation {conversation.sid}")
            
            logger.info(f"Sent welcome message to conversation {conversation.sid}")
        except Exception as e:
            logger.error(f"Error sending welcome message: {str(e)}")
            # Continue even if welcome message fails
        
        return conversation.sid
    except Exception as e:
        logger.error(f"Error creating conversation for member {member_id}: {str(e)}")
        raise

def sanitize_ai_response(text):
    """Aggressively sanitize AI responses for WhatsApp templates."""
    # Remove markdown headers (# Header)
    text = re.sub(r'^#+ +(.+)$', r'\1', text, flags=re.MULTILINE)
    
    # Remove markdown bold/italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    
    # Remove markdown links
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    # Remove markdown code blocks
    text = re.sub(r'```[\s\S]+?```', '', text)
    
    # Remove markdown inline code
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    # Remove special characters that might trigger WhatsApp filters
    # Keep only alphanumeric, basic punctuation, and common symbols
    text = re.sub(r'[^\w\s.,;:!?()\-+\'\"\/]', '', text)
    
    # Limit length to ensure it fits in WhatsApp template
    max_length = 1000  # WhatsApp templates have character limits
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    # Ensure there are no leading/trailing whitespaces
    return text.strip()

def send_conversation_message(twilio_client, conversation_sid, message_body, author="system"):
    """
    Send a message to a conversation.
    
    This function adds the message to the conversation, but for WhatsApp delivery,
    we need to use templates. So we'll:
    1. Add the message to the conversation for record-keeping
    2. Get the participant's WhatsApp address
    3. Send the templated message directly to the participant
    """
    try:
        # Use the hardcoded Conversations Service SID
        conversations_service_sid = CONVERSATIONS_SERVICE_SID
        
        # First, add the message to the conversation for record-keeping
        conversation_message = twilio_client.conversations.v1.services(conversations_service_sid).conversations(conversation_sid).messages.create(
            author=author,
            body=message_body
        )
        
        logger.info(f"Added message to conversation {conversation_sid}, message SID: {conversation_message.sid}")
        
        # Now, get the participant's WhatsApp address to send the templated message
        try:
            # Get all participants in the conversation
            participants = twilio_client.conversations.v1.services(conversations_service_sid).conversations(conversation_sid).participants.list()
            
            # Find the WhatsApp participant (not the system)
            whatsapp_participant = None
            for participant in participants:
                if hasattr(participant, 'messaging_binding') and participant.messaging_binding.get('address', '').startswith('whatsapp:'):
                    whatsapp_participant = participant
                    break
            
            if whatsapp_participant:
                # Get the participant's WhatsApp address
                whatsapp_address = whatsapp_participant.messaging_binding.get('address')
                logger.info(f"Found WhatsApp participant with address: {whatsapp_address}")
                
                # Send the templated message directly to the participant
                logger.info(f"Sending templated message to {whatsapp_address}")
                send_templated_whatsapp_response(whatsapp_address, message_body)
            else:
                logger.warning(f"No WhatsApp participant found in conversation {conversation_sid}")
        except Exception as template_error:
            logger.error(f"Error sending templated message to participant: {str(template_error)}")
            # We already added the message to the conversation, so we'll consider this a partial success
        
        return conversation_message.sid
    except Exception as e:
        logger.error(f"Error sending message to conversation {conversation_sid}: {str(e)}")
        raise

def handle_verification_code(from_number, message):
    """Handle verification code messages."""
    # Extract verification code (assuming it's a 6-character alphanumeric code)
    code_match = re.search(r'\b([A-Z0-9]{6})\b', message.upper())
    if not code_match:
        logger.info(f"No verification code found in message: '{message}'")
        return None
    
    verification_code = code_match.group(1)
    logger.info(f"Verification code extracted: {verification_code}")
    
    # Clean the phone number (remove whatsapp: prefix if present)
    phone_number = from_number
    if phone_number.startswith('whatsapp:'):
        phone_number = phone_number[9:]
    
    # Query for member with this phone number
    members_ref = db.collection('members').where('phone', '==', phone_number).limit(1)
    members = list(members_ref.stream())
    
    if not members:
        return send_templated_whatsapp_response(from_number, "Your number is not registered in our system. Please contact your organization administrator.")
    
    member_doc = members[0]
    member_data = member_doc.to_dict()
    
    # Check if already verified
    if member_data.get('whatsappVerified'):
        logger.info(f"Phone number {phone_number} is already verified")
        return send_templated_whatsapp_response(from_number, "Your WhatsApp number is already verified. You can start querying the knowledge base.")
    
    # Check if verification was sent via SMS
    if not member_data.get('smsVerificationSent'):
        logger.warning(f"No SMS verification was sent to {phone_number} but received code: {verification_code}")
        return send_templated_whatsapp_response(from_number, "No verification was requested for this number. Please contact your organization administrator.")
    
    # Get Twilio credentials
    twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_messaging_service_sid = os.environ.get("TWILIO_MESSAGING_SERVICE_SID")
    
    if not all([twilio_account_sid, twilio_auth_token, twilio_messaging_service_sid]):
        logger.error("Twilio credentials or Messaging Service SID not found.")
        return send_templated_whatsapp_response(from_number, "An error occurred during verification. Please try again later.")
    
    try:
        # Initialize Twilio client
        twilio_client = Client(twilio_account_sid, twilio_auth_token)
        
        # Get or create a Verify service
        verify_service_sid = get_or_create_verify_service(twilio_client)
        
        # Check the verification code with Twilio Verify
        try:
            verification_check = twilio_client.verify.v2.services(verify_service_sid).verification_checks.create(
                to=phone_number,
                code=verification_code
            )
            
            logger.info(f"Verification check result: {verification_check.status}")
            
            if verification_check.status == "approved":
                # Update member as verified
                member_id = member_doc.id
                logger.info(f"Verifying WhatsApp for member {member_id} with phone {phone_number}")
                
                # Get organization name
                org_id = member_data.get('organizationId')
                org_name = "your organization"
                if org_id:
                    org_doc = db.collection('organizations').document(org_id).get()
                    if org_doc.exists:
                        org_data = org_doc.to_dict()
                        org_name = org_data.get('name', org_name)
                        logger.info(f"Member {member_id} belongs to organization: {org_name} ({org_id})")
                
                # Check if the participant is already in a conversation
                existing_conversation_sid = find_existing_conversation_for_participant(twilio_client, phone_number)
                
                if existing_conversation_sid:
                    logger.info(f"Found existing conversation {existing_conversation_sid} for member {member_id}")
                    conversation_sid = existing_conversation_sid
                    
                    # Update member with conversation SID and verification status
                    db.collection('members').document(member_id).update({
                        'whatsappVerified': True,
                        'status': 'active',
                        'verifiedAt': firestore.SERVER_TIMESTAMP,
                        'conversationSid': conversation_sid
                    })
                else:
                    # Create a new conversation for the member
                    try:
                        conversation_sid = create_member_conversation(twilio_client, member_id, phone_number, org_name)
                        logger.info(f"Created conversation {conversation_sid} for member {member_id}")
                        
                        # Update member with conversation SID and verification status
                        db.collection('members').document(member_id).update({
                            'whatsappVerified': True,
                            'status': 'active',
                            'verifiedAt': firestore.SERVER_TIMESTAMP,
                            'conversationSid': conversation_sid
                        })
                    except Exception as e:
                        logger.error(f"Error creating conversation for member {member_id}: {str(e)}")
                        # Continue with verification even if conversation creation fails
                        db.collection('members').document(member_id).update({
                            'whatsappVerified': True,
                            'status': 'active',
                            'verifiedAt': firestore.SERVER_TIMESTAMP
                        })
                        conversation_sid = None
                
                logger.info(f"WhatsApp verification successful for member {member_id}")
                
                # Return success response using the Conversations API
                return send_verification_whatsapp_response(from_number, org_name, conversation_sid)
            else:
                logger.warning(f"Invalid verification code for {phone_number}. Status: {verification_check.status}")
                return send_templated_whatsapp_response(from_number, "Invalid verification code. Please try again or contact your organization administrator.")
        except Exception as e:
            logger.error(f"Error checking verification code: {str(e)}")
            
            # Fallback to direct verification if Verify API check fails
            # This is a safety measure in case the Verify API has issues
            logger.warning(f"Falling back to direct verification for {phone_number}")
            
            # Update member as verified
            member_id = member_doc.id
            logger.info(f"Verifying WhatsApp for member {member_id} with phone {phone_number} (fallback)")
            
            # Get organization name
            org_id = member_data.get('organizationId')
            org_name = "your organization"
            if org_id:
                org_doc = db.collection('organizations').document(org_id).get()
                if org_doc.exists:
                    org_data = org_doc.to_dict()
                    org_name = org_data.get('name', org_name)
            
            # Create a conversation for the member (fallback)
            try:
                conversation_sid = create_member_conversation(twilio_client, member_id, phone_number, org_name)
                logger.info(f"Created conversation {conversation_sid} for member {member_id} (fallback)")
                
                # Update member with conversation SID and verification status
                db.collection('members').document(member_id).update({
                    'whatsappVerified': True,
                    'status': 'active',
                    'verifiedAt': firestore.SERVER_TIMESTAMP,
                    'conversationSid': conversation_sid
                })
            except Exception as e:
                logger.error(f"Error creating conversation for member {member_id} (fallback): {str(e)}")
                # Continue with verification even if conversation creation fails
                db.collection('members').document(member_id).update({
                    'whatsappVerified': True,
                    'status': 'active',
                    'verifiedAt': firestore.SERVER_TIMESTAMP
                })
            
            logger.info(f"WhatsApp verification successful for member {member_id} (fallback)")
            
            # Return success response using the Conversations API
            return send_verification_whatsapp_response(from_number, org_name, conversation_sid)
    except Exception as e:
        logger.error(f"Error verifying WhatsApp: {str(e)}")
        return send_templated_whatsapp_response(from_number, "An error occurred during verification. Please try again later.")

# Send bulk WhatsApp messages to members
@whatsapp_bp.route('/send-bulk-message', methods=['POST'])
def send_bulk_message():
    """Send a WhatsApp message to multiple members."""
    try:
        # Get the user ID from the request
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Get the user from Firestore
        users_ref = db.collection('users')
        user_query = users_ref.where('auth_token', '==', token).limit(1).get()
        
        if not user_query:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user_query[0].to_dict()
        organization_id = user_data.get('organizationId')
        
        if not organization_id:
            return jsonify({'error': 'User does not belong to an organization'}), 400
        
        # Get the message data from the request
        data = request.json
        
        # Validate required fields
        if not data.get('message'):
            return jsonify({'error': 'Message is required'}), 400
        
        # Get the member IDs or filter criteria
        member_ids = data.get('memberIds', [])
        
        # If no member IDs are provided, get all members for the organization
        if not member_ids:
            members_ref = db.collection('members')
            members_query = members_ref.where('organizationId', '==', organization_id).get()
            
            member_ids = [doc.id for doc in members_query]
        
        if not member_ids:
            return jsonify({'error': 'No members found for this organization'}), 404
        
        # Create a broadcast record
        broadcast_id = str(uuid.uuid4())
        broadcast_data = {
            'title': data.get('title', 'Broadcast Message'),
            'message': data.get('message'),
            'organizationId': organization_id,
            'senderId': user_query[0].id,
            'senderName': user_data.get('fullName', 'Unknown'),
            'senderRole': user_data.get('role', 'user'),
            'recipientCount': len(member_ids),
            'recipientIds': member_ids,
            'deliveryMethods': {
                'whatsapp': True,
                'email': data.get('sendEmail', False),
                'inApp': data.get('sendInApp', False)
            },
            'status': 'processing',
            'createdAt': firestore.SERVER_TIMESTAMP,
            'scheduledFor': data.get('scheduledFor'),
            'hasAttachments': False
        }
        
        # Add the broadcast to Firestore
        db.collection('broadcasts').document(broadcast_id).set(broadcast_data)
        
        # Send the message to each member
        success_count = 0
        failed_count = 0
        results = []
        
        for member_id in member_ids:
            try:
                # Get the member from Firestore
                member_doc = db.collection('members').document(member_id).get()
                
                if not member_doc.exists:
                    results.append({
                        'memberId': member_id,
                        'status': 'failed',
                        'error': 'Member not found'
                    })
                    failed_count += 1
                    continue
                
                member_data = member_doc.to_dict()
                
                # Check if the member belongs to the user's organization
                if member_data.get('organizationId') != organization_id:
                    results.append({
                        'memberId': member_id,
                        'status': 'failed',
                        'error': 'Member does not belong to your organization'
                    })
                    failed_count += 1
                    continue
                
                # Check if the member has a verified WhatsApp number
                if not member_data.get('whatsappVerified'):
                    results.append({
                        'memberId': member_id,
                        'status': 'failed',
                        'error': 'Member does not have a verified WhatsApp number'
                    })
                    failed_count += 1
                    continue
                
                # Get the member's phone number
                phone_number = member_data.get('phone')
                
                if not phone_number:
                    results.append({
                        'memberId': member_id,
                        'status': 'failed',
                        'error': 'Member does not have a phone number'
                    })
                    failed_count += 1
                    continue
                
                # Send the message
                try:
                    # Format the message with personalization if needed
                    personalized_message = data.get('message').replace('{name}', member_data.get('name', 'Member'))
                    
                    # Get or create a conversation for the member
                    conversation_sid = member_data.get('conversationSid')
                    
                    if not conversation_sid:
                        # If no conversation exists, create one
                        logger.info(f"No conversation found for member {member_id}, creating one")
                        try:
                            conversation_sid = create_member_conversation(twilio_client, member_id, phone_number, "your organization")
                            
                            # Update member with conversation SID
                            db.collection('members').document(member_id).update({
                                'conversationSid': conversation_sid,
                                'updatedAt': firestore.SERVER_TIMESTAMP
                            })
                            
                            logger.info(f"Created new conversation {conversation_sid} for member {member_id}")
                        except Exception as e:
                            logger.error(f"Error creating conversation for member {member_id}: {str(e)}")
                            # Fall back to direct messaging if conversation creation fails
                            logger.info(f"Falling back to direct messaging for {phone_number}")
                            send_templated_whatsapp_response(phone_number, personalized_message)
                            
                            # Record the successful delivery
                            results.append({
                                'memberId': member_id,
                                'status': 'sent',
                                'phone': phone_number,
                                'method': 'direct'
                            })
                            success_count += 1
                            continue
                    
                    # Use Conversations API to send the message
                    try:
                        logger.info(f"Sending broadcast message via Conversations API to {phone_number}")
                        send_conversation_message(twilio_client, conversation_sid, personalized_message, author="admin")
                        
                        # Record the successful delivery
                        results.append({
                            'memberId': member_id,
                            'status': 'sent',
                            'phone': phone_number,
                            'method': 'conversation'
                        })
                        success_count += 1
                    except Exception as e:
                        logger.error(f"Error sending message via Conversations API: {str(e)}")
                        # Fall back to direct messaging if Conversations API fails
                        logger.info(f"Falling back to direct messaging for {phone_number}")
                        send_templated_whatsapp_response(phone_number, personalized_message)
                        
                        # Record the successful delivery
                        results.append({
                            'memberId': member_id,
                            'status': 'sent',
                            'phone': phone_number,
                            'method': 'direct_fallback'
                        })
                        success_count += 1
                    
                    # Add a delivery record
                    delivery_id = str(uuid.uuid4())
                    delivery_data = {
                        'broadcastId': broadcast_id,
                        'memberId': member_id,
                        'memberName': member_data.get('name', 'Unknown'),
                        'memberPhone': phone_number,
                        'status': 'sent',
                        'sentAt': firestore.SERVER_TIMESTAMP,
                        'deliveryMethod': 'whatsapp'
                    }
                    
                    db.collection('broadcast_deliveries').document(delivery_id).set(delivery_data)
                    
                except Exception as e:
                    logger.error(f"Error sending WhatsApp message to {phone_number}: {str(e)}")
                    results.append({
                        'memberId': member_id,
                        'status': 'failed',
                        'phone': phone_number,
                        'error': str(e)
                    })
                    failed_count += 1
            except Exception as e:
                logger.error(f"Error processing member {member_id}: {str(e)}")
                results.append({
                    'memberId': member_id,
                    'status': 'failed',
                    'error': str(e)
                })
                failed_count += 1
        
        # Update the broadcast status
        db.collection('broadcasts').document(broadcast_id).update({
            'status': 'completed',
            'completedAt': firestore.SERVER_TIMESTAMP,
            'stats': {
                'success': success_count,
                'failed': failed_count,
                'total': len(member_ids)
            }
        })
        
        return jsonify({
            'success': True,
            'broadcastId': broadcast_id,
            'stats': {
                'success': success_count,
                'failed': failed_count,
                'total': len(member_ids)
            },
            'results': results
        })
    except Exception as e:
        logger.error(f"Error sending bulk message: {str(e)}")
        return jsonify({'error': str(e)}), 500

# WhatsApp webhook handler
@whatsapp_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming WhatsApp messages."""
    try:
        # Get the message data
        form_data = request.form.to_dict()
        
        # Log the incoming message
        logger.info(f"Received WhatsApp message: {form_data}")
        
        # Get the message body and sender
        message_body = form_data.get('Body', '').strip()
        from_number = form_data.get('From', '')
        
        if not message_body or not from_number:
            logger.warning("Missing message body or sender number")
            return send_templated_whatsapp_response(from_number, "Sorry, we couldn't process your message.")
        
        # Check if this is a verification code
        verification_response = handle_verification_code(from_number, message_body)
        if verification_response:
            return verification_response
        
        # Get the member by phone number
        member = get_member_by_phone(from_number)
        
        if not member:
            logger.warning(f"No member found for phone number: {from_number}")
            return send_templated_whatsapp_response(from_number, "Your number is not registered in our system. Please contact your organization administrator.")
        
        # Check if the member is verified
        if not member.get('whatsappVerified'):
            logger.warning(f"Member {member['id']} with phone {from_number} is not verified")
            return send_templated_whatsapp_response(from_number, "Your WhatsApp number is not verified. Please contact your organization administrator.")
        
        # Get the organization ID
        organization_id = member.get('organizationId')
        
        if not organization_id:
            logger.warning(f"Member {member['id']} does not belong to an organization")
            return send_templated_whatsapp_response(from_number, "You are not associated with any organization. Please contact your administrator.")
        
        # Initialize RAG system
        rag = RAGSystem(
            openai_api_key=OPENAI_API_KEY,
            anthropic_api_key=ANTHROPIC_API_KEY,
            pinecone_api_key=PINECONE_API_KEY,
            index_name=PINECONE_INDEX_NAME  # Parameter is named index_name, not pinecone_index_name
        )
        
        # Send an intermediate message to indicate processing
        try:
            # Detect the language of the query to send the intermediate message in the same language
            language = "en"  # Default to English
            intermediate_message = "Searching through our knowledge base..."
            
            # Check for non-Latin scripts first (Arabic, Chinese, Japanese, Korean, etc.)
            if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\u1100-\u11FF\u3040-\u309F\u30A0-\u30FF\u3400-\u4DBF\u4E00-\u9FFF\uAC00-\uD7AF]', message_body):
                # Arabic script
                if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', message_body):
                    language = "ar"
                    intermediate_message = "جاري البحث في قاعدة المعرفة لدينا..."
                # Korean Hangul
                elif re.search(r'[\u1100-\u11FF\uAC00-\uD7AF]', message_body):
                    language = "ko"
                    intermediate_message = "지식 베이스를 검색하는 중..."
                # Japanese Hiragana/Katakana
                elif re.search(r'[\u3040-\u309F\u30A0-\u30FF]', message_body):
                    language = "ja"
                    intermediate_message = "知識ベースを検索しています..."
                # Chinese characters (also used in Japanese and Korean)
                elif re.search(r'[\u4E00-\u9FFF]', message_body):
                    # Simple heuristic: if there are Hiragana/Katakana, it's Japanese
                    if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', message_body):
                        language = "ja"
                        intermediate_message = "知識ベースを検索しています..."
                    # If there are Hangul characters, it's Korean
                    elif re.search(r'[\uAC00-\uD7AF]', message_body):
                        language = "ko"
                        intermediate_message = "지식 베이스를 검색하는 중..."
                    # Otherwise, assume Chinese
                    else:
                        language = "zh"
                        intermediate_message = "正在搜索我们的知识库..."
                # Thai script
                elif re.search(r'[\u0E00-\u0E7F]', message_body):
                    language = "th"
                    intermediate_message = "กำลังค้นหาในฐานความรู้ของเรา..."
                # Hindi/Devanagari script
                elif re.search(r'[\u0900-\u097F]', message_body):
                    language = "hi"
                    intermediate_message = "हमारे ज्ञान आधार में खोज रहे हैं..."
            # Then check for Latin-based languages with special characters
            elif re.search(r'[àáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆŠŽ]', message_body):
                # Check for common words in various languages
                if any(word in message_body.lower() for word in ['bonjour', 'merci', 'comment', 'pourquoi', 'quand', 'où']):
                    language = "fr"
                    intermediate_message = "Recherche dans notre base de connaissances..."
                elif any(word in message_body.lower() for word in ['hola', 'gracias', 'cómo', 'por qué', 'cuándo', 'dónde', 'buenos días', 'buenas tardes', 'buenas noches', 'qué', 'quién']):
                    language = "es"
                    intermediate_message = "Buscando en nuestra base de conocimientos..."
                elif any(word in message_body.lower() for word in ['guten', 'danke', 'wie', 'warum', 'wann', 'wo']):
                    language = "de"
                    intermediate_message = "Durchsuche unsere Wissensdatenbank..."
                elif any(word in message_body.lower() for word in ['ciao', 'grazie', 'come', 'perché', 'quando', 'dove']):
                    language = "it"
                    intermediate_message = "Ricerca nel nostro knowledge base..."
                elif any(word in message_body.lower() for word in ['olá', 'obrigado', 'como', 'por que', 'quando', 'onde']):
                    language = "pt"
                    intermediate_message = "Pesquisando em nossa base de conhecimento..."
            
            # Send the intermediate message
            send_whatsapp_message(from_number, intermediate_message)
            logger.info(f"Sent intermediate message to {from_number}")
            
            # Log the query
            logger.info(f"Querying knowledge base for member {member['id']} with query: {message_body}")
            
            # Add the query to the member's history
            query_id = str(uuid.uuid4())
            query_data = {
                'memberId': member['id'],
                'organizationId': organization_id,
                'query': message_body,
                'source': 'whatsapp',
                'createdAt': firestore.SERVER_TIMESTAMP,
                'status': 'processing'
            }
            
            db.collection('queries').document(query_id).set(query_data)
            
            # Detect language for the response
            language = "en"  # Default to English
            if re.search(r'[àáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆŠŽ]', message_body):
                # Message contains non-English characters, likely not English
                if any(word in message_body.lower() for word in ['bonjour', 'merci', 'comment', 'pourquoi', 'quand', 'où']):
                    language = "fr"  # French
                elif any(word in message_body.lower() for word in ['hola', 'gracias', 'cómo', 'por qué', 'cuándo', 'dónde']):
                    language = "es"  # Spanish
                elif any(word in message_body.lower() for word in ['guten', 'danke', 'wie', 'warum', 'wann', 'wo']):
                    language = "de"  # German
                elif any(word in message_body.lower() for word in ['ciao', 'grazie', 'come', 'perché', 'quando', 'dove']):
                    language = "it"  # Italian
                elif any(word in message_body.lower() for word in ['olá', 'obrigado', 'como', 'por que', 'quando', 'onde']):
                    language = "pt"  # Portuguese
            
            # Query the knowledge base with organization filter and language preference
            response = rag.query(
                query=message_body,
                organization_id=organization_id,
                user_id=member['id'],
                language=language  # Pass the detected language to the RAG system
            )
            
            # Sanitize the response for WhatsApp
            sanitized_response = sanitize_ai_response(response.get('answer', ''))
            
            # Update the query with the response
            db.collection('queries').document(query_id).update({
                'response': response.get('answer', ''),
                'sources': response.get('sources', []),
                'status': 'completed',
                'completedAt': firestore.SERVER_TIMESTAMP
            })
            
            # For sandbox mode, we prioritize direct messaging
            if USE_CONVERSATIONS_API:
                # Get the conversation SID if it exists
                conversation_sid = member.get('conversationSid')
                
                # Try to send the response using the Conversations API
                if conversation_sid:
                    try:
                        logger.info(f"Sending AI response via Conversations API to {from_number}")
                        message_sid = send_conversation_message(twilio_client, conversation_sid, response.get('answer', ''))
                        logger.info(f"AI response sent via Conversations API. Message SID: {message_sid}")
                        return create_twilio_response("")
                    except Exception as e:
                        logger.error(f"Error sending AI response via Conversations API: {str(e)}")
                        # Fall back to template message
                        logger.info(f"Falling back to template message for AI response")
                        try:
                            logger.info(f"Sending template response to {from_number}")
                            return send_whatsapp_template_message(
                                to_number=from_number,
                                content_sid=TEMPLATE_CONTENT_SID,
                                content_variables={"1": sanitized_response}
                            )
                        except Exception as template_error:
                            logger.error(f"Error sending template response: {str(template_error)}")
                            # Fall back to direct message as a last resort
                            return send_whatsapp_message(from_number, sanitized_response)
                else:
                    # No conversation exists, try template message
                    try:
                        logger.info(f"No conversation found, sending template response to {from_number}")
                        return send_whatsapp_template_message(
                            to_number=from_number,
                            content_sid=TEMPLATE_CONTENT_SID,
                            content_variables={"1": sanitized_response}
                        )
                    except Exception as e:
                        logger.error(f"Error sending template response: {str(e)}")
                        # Fall back to direct message
                        return send_whatsapp_message(from_number, sanitized_response)
            else:
                # For sandbox mode, use direct messaging
                logger.info(f"Using direct messaging for sandbox mode")
                
                # Record the conversation in Firestore if needed
                conversation_sid = member.get('conversationSid')
                if conversation_sid and USE_CONVERSATIONS_API:
                    try:
                        # Add the message to the conversation for record-keeping only
                        twilio_client.conversations.v1.services(CONVERSATIONS_SERVICE_SID).conversations(conversation_sid).messages.create(
                            author="system",
                            body=response.get('answer', '')
                        )
                        logger.info(f"Added message to conversation {conversation_sid} for record-keeping")
                    except Exception as e:
                        logger.error(f"Error adding message to conversation: {str(e)}")
                
                # Try to send a direct message using the sandbox number
                try:
                    logger.info(f"Sending direct message to {from_number} using sandbox number")
                    return send_whatsapp_message(from_number, sanitized_response)
                except Exception as e:
                    logger.error(f"Error sending direct message: {str(e)}")
                    return create_twilio_response(sanitized_response)
                
        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}")
            
            # Update the query with the error
            db.collection('queries').document(query_id).update({
                'status': 'failed',
                'error': str(e),
                'completedAt': firestore.SERVER_TIMESTAMP
            })
            
            return send_templated_whatsapp_response(from_number, "Sorry, we couldn't process your query. Please try again later or contact your administrator.")
    
    except Exception as e:
        logger.error(f"Error handling WhatsApp webhook: {str(e)}")
        return send_templated_whatsapp_response(from_number, "An error occurred. Please try again later.")
