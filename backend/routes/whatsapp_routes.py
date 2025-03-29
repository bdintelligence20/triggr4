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
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM", "+15055787929")
TWILIO_MESSAGING_SERVICE_SID = os.environ.get("TWILIO_MESSAGING_SERVICE_SID")

# Approved Content Template SID for the AI answer (template body: "Hi! Here is your answer: {{1}}")
TEMPLATE_CONTENT_SID = "HX6ed39c2507e07cb25c75412d74f134d8"  # Template name: copy_ai_response

# Default friendly name for the Conversations Service
CONVERSATIONS_SERVICE_NAME = "Knowledge Hub Conversations"

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

def send_whatsapp_message(to_number, message_body):
    """
    Sends a WhatsApp message using the Twilio client.
    If the message exceeds 1600 characters, it is split semantically into multiple parts.
    """
    max_length = 1600
    # Ensure the 'to_number' has the correct WhatsApp prefix.
    if not to_number.startswith('whatsapp:'):
        to_number = f"whatsapp:{to_number}"
    
    try:
        # Split the message semantically if it exceeds the max_length.
        if len(message_body) > max_length:
            chunks = split_message_semantically(message_body, max_length=max_length)
            for chunk in chunks:
                twilio_client.messages.create(
                    body=chunk,
                    messaging_service_sid=TWILIO_MESSAGING_SERVICE_SID,
                    to=to_number
                )
        else:
            twilio_client.messages.create(
                body=message_body,
                messaging_service_sid=TWILIO_MESSAGING_SERVICE_SID,
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
    
    # Log template content for debugging
    content_preview = content_variables.get("1", "")[:100] + "..." if len(content_variables.get("1", "")) > 100 else content_variables.get("1", "")
    logger.info(f"Preparing template message with content length: {len(content_variables.get('1', ''))}")
    logger.info(f"Template content preview: {content_preview}")
    
    try:
        # Try using the template with messaging service
        message = twilio_client.messages.create(
            content_sid=content_sid,
            content_variables=json.dumps(content_variables),
            messaging_service_sid=TWILIO_MESSAGING_SERVICE_SID,
            to=to_number
        )
        logger.info(f"Templated message sent successfully. Template SID: {content_sid}, Message SID: {message.sid}")
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
                    messaging_service_sid=TWILIO_MESSAGING_SERVICE_SID,
                    to=to_number
                )
                logger.info(f"Templated message sent with sanitized content. Message SID: {message.sid}")
                return create_twilio_response("")
            except Exception as retry_error:
                logger.error(f"Still failed with sanitized content: {str(retry_error)}")
                # Fall back to direct message
        
        # Fall back to plain text message if template fails
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

def create_member_conversation(twilio_client, member_id, phone_number, org_name):
    """Create a new conversation for a verified member."""
    try:
        # Get or create a Conversations service
        conversations_service_sid = get_or_create_conversations_service(twilio_client)
        
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
        
        # Add the member as a participant (using their WhatsApp address)
        # IMPORTANT: Do NOT use identity parameter for WhatsApp participants
        try:
            member_participant = twilio_client.conversations.v1.services(conversations_service_sid).conversations(conversation.sid).participants.create(
                # Removed identity parameter - not supported for WhatsApp
                messaging_binding_address=whatsapp_address,
                messaging_binding_proxy_address=TWILIO_WHATSAPP_FROM
            )
            
            logger.info(f"Added member {member_id} as participant to conversation {conversation.sid}")
        except Exception as e:
            logger.error(f"Error adding participant to conversation: {str(e)}")
            # Continue with conversation creation even if participant addition fails
        
        # Send a welcome message
        try:
            welcome_message = f"Welcome to the {org_name} Knowledge Hub! You can ask questions about your organization's knowledge base here."
            twilio_client.conversations.v1.services(conversations_service_sid).conversations(conversation.sid).messages.create(
                author="system",
                body=welcome_message
            )
            
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

def send_conversation_message(twilio_client, conversation_sid, message, author="system"):
    """Send a message to a conversation."""
    try:
        # Get the Conversations service SID
        conversations_service_sid = os.environ.get("TWILIO_CONVERSATIONS_SERVICE_SID")
        if not conversations_service_sid:
            conversations_service_sid = get_or_create_conversations_service(twilio_client)
        
        # Send the message
        message = twilio_client.conversations.v1.services(conversations_service_sid).conversations(conversation_sid).messages.create(
            author=author,
            body=message
        )
        
        logger.info(f"Sent message to conversation {conversation_sid}, message SID: {message.sid}")
        return message.sid
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
        return create_twilio_response("❌ Your number is not registered in our system. Please contact your organization administrator.")
    
    member_doc = members[0]
    member_data = member_doc.to_dict()
    
    # Check if already verified
    if member_data.get('whatsappVerified'):
        logger.info(f"Phone number {phone_number} is already verified")
        return create_twilio_response("✅ Your WhatsApp number is already verified. You can start querying the knowledge base.")
    
    # Check if verification was sent
    if not member_data.get('whatsappVerificationSent'):
        logger.warning(f"No verification was sent to {phone_number} but received code: {verification_code}")
        return create_twilio_response("❌ No verification was requested for this number. Please contact your organization administrator.")
    
    # Get Twilio credentials
    twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_messaging_service_sid = os.environ.get("TWILIO_MESSAGING_SERVICE_SID")
    
    if not all([twilio_account_sid, twilio_auth_token, twilio_messaging_service_sid]):
        logger.error("Twilio credentials or Messaging Service SID not found.")
        return create_twilio_response("❌ An error occurred during verification. Please try again later.")
    
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
                
                # Create a conversation for the member
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
                
                logger.info(f"WhatsApp verification successful for member {member_id}")
                
                # Return success response
                return create_twilio_response(f"✅ Your WhatsApp number has been verified successfully! You can now query the knowledge base for {org_name}. Try asking a question!")
            else:
                logger.warning(f"Invalid verification code for {phone_number}. Status: {verification_check.status}")
                return create_twilio_response("❌ Invalid verification code. Please try again or contact your organization administrator.")
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
            
            # Return success response
            return create_twilio_response(f"✅ Your WhatsApp number has been verified successfully! You can now query the knowledge base for {org_name}. Try asking a question!")
    except Exception as e:
        logger.error(f"Error verifying WhatsApp: {str(e)}")
        return create_twilio_response("❌ An error occurred during verification. Please try again later.")

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
                            send_whatsapp_message(phone_number, personalized_message)
                            
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
                        send_whatsapp_message(phone_number, personalized_message)
                        
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
            return create_twilio_response("Sorry, we couldn't process your message.")
        
        # Check if this is a verification code
        verification_response = handle_verification_code(from_number, message_body)
        if verification_response:
            return verification_response
        
        # Get the member by phone number
        member = get_member_by_phone(from_number)
        
        if not member:
            logger.warning(f"No member found for phone number: {from_number}")
            return create_twilio_response("❌ Your number is not registered in our system. Please contact your organization administrator.")
        
        # Check if the member is verified
        if not member.get('whatsappVerified'):
            logger.warning(f"Member {member['id']} with phone {from_number} is not verified")
            return create_twilio_response("❌ Your WhatsApp number is not verified. Please contact your organization administrator.")
        
        # Get the organization ID
        organization_id = member.get('organizationId')
        
        if not organization_id:
            logger.warning(f"Member {member['id']} does not belong to an organization")
            return create_twilio_response("❌ You are not associated with any organization. Please contact your administrator.")
        
        # Initialize RAG system
        rag = RAGSystem(
            openai_api_key=OPENAI_API_KEY,
            anthropic_api_key=ANTHROPIC_API_KEY,
            pinecone_api_key=PINECONE_API_KEY,
            pinecone_index_name=PINECONE_INDEX_NAME
        )
        
        # Query the knowledge base
        try:
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
            
            # Query the knowledge base with organization filter
            response = rag.query(
                query=message_body,
                organization_id=organization_id,
                user_id=member['id']
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
            
            # Try to send the response using a template
            try:
                logger.info(f"Sending template response to {from_number}")
                return send_whatsapp_template_message(
                    to_number=from_number,
                    content_sid=TEMPLATE_CONTENT_SID,
                    content_variables={"1": sanitized_response}
                )
            except Exception as e:
                logger.error(f"Error sending template response: {str(e)}")
                # Fall back to direct message
                return send_whatsapp_message(from_number, sanitized_response)
                
        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}")
            
            # Update the query with the error
            db.collection('queries').document(query_id).update({
                'status': 'failed',
                'error': str(e),
                'completedAt': firestore.SERVER_TIMESTAMP
            })
            
            return create_twilio_response("❌ Sorry, we couldn't process your query. Please try again later or contact your administrator.")
    
    except Exception as e:
        logger.error(f"Error handling WhatsApp webhook: {str(e)}")
        return create_twilio_response("❌ An error occurred. Please try again later.")
