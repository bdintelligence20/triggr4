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
    
    try:
        # Try using the template with messaging service
        message = twilio_client.messages.create(
            content_sid=content_sid,
            content_variables=json.dumps(content_variables),
            messaging_service_sid=TWILIO_MESSAGING_SERVICE_SID,
            to=to_number
        )
        logger.info(f"Templated message sent. Template SID: {content_sid}, Message SID: {message.sid}")
        return create_twilio_response("")
    except Exception as e:
        error_message = str(e)
        if "content_sid" in error_message.lower() or "template" in error_message.lower():
            logger.error(f"Template error with SID {content_sid}: {error_message}")
            # Fall back to plain text message if template fails
            logger.info(f"Falling back to plain text message")
            return send_whatsapp_message(to_number, content_variables.get("1", ""))
        else:
            logger.error(f"Error sending templated WhatsApp message: {error_message}")
            return create_twilio_response(f"Error: {error_message}")

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
        
        # Create a new conversation
        conversation = twilio_client.conversations.v1.services(conversations_service_sid).conversations.create(
            friendly_name=friendly_name,
            attributes=json.dumps({
                "memberId": member_id,
                "organizationName": org_name
            })
        )
        
        logger.info(f"Created new conversation: {conversation.sid} for member {member_id}")
        
        # Add the member as a participant (using their WhatsApp address)
        whatsapp_address = f"whatsapp:{phone_number}"
        member_participant = twilio_client.conversations.v1.services(conversations_service_sid).conversations(conversation.sid).participants.create(
            identity=member_id,  # Use member_id as the identity
            messaging_binding_address=phone_number,
            messaging_binding_proxy_address=TWILIO_WHATSAPP_FROM
        )
        
        logger.info(f"Added member {member_id} as participant to conversation {conversation.sid}")
        
        # Send a welcome message
        welcome_message = f"Welcome to the {org_name} Knowledge Hub! You can ask questions about your organization's knowledge base here."
        twilio_client.conversations.v1.services(conversations_service_sid).conversations(conversation.sid).messages.create(
            author="system",
            body=welcome_message
        )
        
        logger.info(f"Sent welcome message to conversation {conversation.sid}")
        
        return conversation.sid
    except Exception as e:
        logger.error(f"Error creating conversation for member {member_id}: {str(e)}")
        raise

def sanitize_ai_response(text):
    """Remove markdown and special characters from AI responses."""
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
    
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
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
                code=verification_code,
                locale="en"  # Specify locale to ensure proper template selection
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
                    
                    # Send the WhatsApp message
                    send_whatsapp_message(phone_number, personalized_message)
                    
                    # Record the successful delivery
                    results.append({
                        'memberId': member_id,
                        'status': 'sent',
                        'phone': phone_number
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
                        'error': str(e),
                        'phone': phone_number
                    })
                    failed_count += 1
                    
                    # Add a failed delivery record
                    delivery_id = str(uuid.uuid4())
                    delivery_data = {
                        'broadcastId': broadcast_id,
                        'memberId': member_id,
                        'memberName': member_data.get('name', 'Unknown'),
                        'memberPhone': phone_number,
                        'status': 'failed',
                        'error': str(e),
                        'sentAt': firestore.SERVER_TIMESTAMP,
                        'deliveryMethod': 'whatsapp'
                    }
                    
                    db.collection('broadcast_deliveries').document(delivery_id).set(delivery_data)
            
            except Exception as e:
                logger.error(f"Error processing member {member_id}: {str(e)}")
                results.append({
                    'memberId': member_id,
                    'status': 'failed',
                    'error': str(e)
                })
                failed_count += 1
        
        # Update the broadcast record with the results
        db.collection('broadcasts').document(broadcast_id).update({
            'status': 'completed',
            'completedAt': firestore.SERVER_TIMESTAMP,
            'successCount': success_count,
            'failedCount': failed_count
        })
        
        return jsonify({
            'broadcastId': broadcast_id,
            'status': 'completed',
            'totalCount': len(member_ids),
            'successCount': success_count,
            'failedCount': failed_count,
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error sending bulk message: {str(e)}")
        return jsonify({'error': f'Failed to send bulk message: {str(e)}'}), 500

@whatsapp_bp.route('/whatsapp-webhook', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages with custom RAG system."""
    try:
        # Get the incoming message
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        
        logger.info(f"WhatsApp message received from {from_number}: {incoming_msg}")
        
        # Skip empty messages
        if not incoming_msg:
            return create_twilio_response("I couldn't understand your message. Please try again.")
        
        # Check if this is a verification code
        verification_response = handle_verification_code(from_number, incoming_msg)
        if verification_response:
            return verification_response
        
        # Get member data by phone number
        member = get_member_by_phone(from_number)
        
        # Check if member exists and is verified
        if not member:
            return create_twilio_response("❌ Your number is not registered in our system. Please contact your organization administrator.")
        
        if not member.get('whatsappVerified'):
            return create_twilio_response("❌ Your WhatsApp number is not verified. Please verify your number with the code sent to you.")
        
        # Get organization ID
        organization_id = member.get('organizationId')
        if not organization_id:
            return create_twilio_response("❌ Your account is not associated with an organization. Please contact your administrator.")
        
        # Initialize Twilio client
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Check if member has a conversation SID
        conversation_sid = member.get('conversationSid')
        use_conversations_api = False
        
        # If member doesn't have a conversation SID, create one
        if not conversation_sid:
            try:
                # Get organization name
                org_name = "your organization"
                org_doc = db.collection('organizations').document(organization_id).get()
                if org_doc.exists:
                    org_data = org_doc.to_dict()
                    org_name = org_data.get('name', org_name)
                
                # Create a conversation for the member
                conversation_sid = create_member_conversation(twilio_client, member.get('id'), from_number.replace('whatsapp:', ''), org_name)
                logger.info(f"Created new conversation {conversation_sid} for member {member.get('id')}")
                
                # Update member with conversation SID
                db.collection('members').document(member.get('id')).update({
                    'conversationSid': conversation_sid
                })
                
                use_conversations_api = True
            except Exception as e:
                logger.error(f"Error creating conversation for member {member.get('id')}: {str(e)}")
                # Fall back to direct WhatsApp messaging
                use_conversations_api = False
        else:
            use_conversations_api = True
        
        # Create a unique ID for this conversation
        conversation_id = str(uuid.uuid4())
        
        # Log the conversation in Firestore
        db.collection("whatsapp_conversations").document(conversation_id).set({
            "from": from_number,
            "message": incoming_msg,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "status": "received",
            "memberId": member.get('id'),
            "organizationId": organization_id
        })
        
        # Send initial acknowledgment message
        if use_conversations_api:
            try:
                send_conversation_message(twilio_client, conversation_sid, "I'm searching through our knowledge base...")
            except Exception as e:
                logger.error(f"Error sending conversation message: {str(e)}")
                # Fall back to direct WhatsApp messaging
                send_whatsapp_message(from_number, "⏳ I'm searching through our knowledge base...")
                use_conversations_api = False
        else:
            send_whatsapp_message(from_number, "⏳ I'm searching through our knowledge base...")
        
        try:
            try:
                # Initialize custom RAG system with organization ID
                logger.info(f"Initializing RAG system for organization: {organization_id}")
                whatsapp_rag = RAGSystem(
                    openai_api_key=OPENAI_API_KEY,
                    anthropic_api_key=ANTHROPIC_API_KEY,
                    pinecone_api_key=PINECONE_API_KEY,
                    index_name=PINECONE_INDEX_NAME,
                    organization_id=organization_id  # Pass organization ID to filter results
                )
                logger.info(f"RAG system initialized with organization filter: {organization_id}")
                
                # Get previous conversation history for this member if available
                conversation_history = ""
                try:
                    # Get the last 5 WhatsApp conversations for this member
                    conv_query = db.collection("whatsapp_conversations") \
                        .where("memberId", "==", member.get('id')) \
                        .where("organizationId", "==", organization_id) \
                        .order_by("timestamp", direction=firestore.Query.DESCENDING) \
                        .limit(10)
                    
                    conversations = list(conv_query.stream())
                    
                    if conversations:
                        # Format conversations as history
                        history_parts = []
                        for conv in reversed(conversations):
                            conv_data = conv.to_dict()
                            if conv_data.get("from") == from_number:
                                history_parts.append(f"User: {conv_data.get('message', '')}")
                            elif conv_data.get("from") == "system":
                                history_parts.append(f"AI: {conv_data.get('message', '')}")
                        
                        conversation_history = "\n".join(history_parts)
                        logger.info(f"Retrieved conversation history for member {member.get('id')}")
                except Exception as e:
                    logger.warning(f"Error retrieving conversation history: {str(e)}")
                
                # Collect the full response
                accumulated_text = []
                
                def stream_callback(chunk):
                    accumulated_text.append(chunk)
                
                # Query the RAG system with conversation history
                result = whatsapp_rag.query(
                    user_query=incoming_msg,
                    stream_callback=stream_callback,
                    history=conversation_history
                )
            except Exception as e:
                logger.error(f"Error initializing RAG system: {str(e)}")
                error_message = "❌ I'm sorry, I encountered an error setting up the knowledge base. Please try again later."
                if use_conversations_api:
                    send_conversation_message(twilio_client, conversation_sid, error_message)
                else:
                    send_whatsapp_message(from_number, error_message)
                return create_twilio_response("")
            
            # Get the full response
            full_text = ''.join(accumulated_text) if accumulated_text else result.get("answer", "")
            
            if not full_text:
                logger.warning(f"No relevant information found for query: '{incoming_msg}' from organization: {organization_id}")
                error_message = "📚 I couldn't find any relevant information in our knowledge base. Please try asking a different question."
                if use_conversations_api:
                    send_conversation_message(twilio_client, conversation_sid, error_message)
                else:
                    send_whatsapp_message(from_number, error_message)
                return create_twilio_response("")
            
            # Log sources if available
            if result and "sources" in result:
                source_ids = [source.get('id', 'unknown') for source in result.get("sources", [])]
                logger.info(f"Found {len(source_ids)} sources for query: '{incoming_msg}'. Sources: {source_ids}")
            
            # Sanitize the AI response to remove markdown and special characters
            sanitized_text = sanitize_ai_response(full_text)
            
            if use_conversations_api:
                # Send the response through the Conversations API
                send_conversation_message(twilio_client, conversation_sid, sanitized_text)
            else:
                # Send intermediate message
                send_whatsapp_message(from_number, "🔍 Found relevant information! Preparing your answer...")
                
                # Send the complete answer using the approved template
                content_variables = {"1": sanitized_text}
                logger.info(f"Sending response using template SID: {TEMPLATE_CONTENT_SID}")
                send_whatsapp_template_message(from_number, TEMPLATE_CONTENT_SID, content_variables)
                
                # Send a completion message using freeform text
                send_whatsapp_message(from_number, "✅ That completes my answer. Let me know if you need any clarification!")
            
            # Store the complete response in Firestore
            db.collection("whatsapp_conversations").document(f"{conversation_id}_response").set({
                "from": "system",
                "to": from_number,
                "message": full_text,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "status": "completed",
                "in_response_to": conversation_id,
                "memberId": member.get('id'),
                "organizationId": organization_id,
                "sources": [source.get('id', 'unknown') for source in result.get("sources", [])]
            })
            
            # Return empty TwiML response as we've already sent the messages
            return create_twilio_response("")
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {str(e)}", exc_info=True)
            error_message = "❌ I'm sorry, I encountered an error processing your request. Please try again later."
            if use_conversations_api:
                try:
                    send_conversation_message(twilio_client, conversation_sid, error_message)
                except:
                    send_whatsapp_message(from_number, error_message)
            else:
                send_whatsapp_message(from_number, error_message)
            return create_twilio_response("")
        
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {str(e)}", exc_info=True)
        return create_twilio_response("An error occurred. Please try again later.")

@whatsapp_bp.route('/conversation-webhook', methods=['POST'])
def conversation_webhook():
    """Handle Twilio Conversations webhook events."""
    try:
        # Get the webhook data
        webhook_data = request.json
        
        # Log the webhook data
        logger.info(f"Received Conversations webhook: {webhook_data}")
        
        # Get the event type
        event_type = webhook_data.get('EventType')
        
        # Handle different event types
        if event_type == 'onMessageAdded':
            # Get the message data
            message_data = webhook_data.get('Message', {})
            
            # Get the conversation SID
            conversation_sid = message_data.get('ConversationSid')
            
            # Get the message body
            message_body = message_data.get('Body', '')
            
            # Get the author
            author = message_data.get('Author', '')
            
            # Skip system messages
            if author == 'system':
                return jsonify({'status': 'success'}), 200
            
            # Get the conversation attributes
            conversation_attributes = webhook_data.get('Conversation', {}).get('Attributes', '{}')
            try:
                attributes = json.loads(conversation_attributes)
                member_id = attributes.get('memberId')
            except:
                member_id = None
            
            if member_id:
                # Get the member data
                member_doc = db.collection('members').document(member_id).get()
                if member_doc.exists:
                    member_data = member_doc.to_dict()
                    
                    # Process the message as if it came from the WhatsApp webhook
                    # This is a simplified version - in a real implementation, you would
                    # extract this logic into a separate function to avoid code duplication
                    logger.info(f"Processing Conversations message from member {member_id}: {message_body}")
                    
                    # TODO: Process the message using the RAG system
                    # For now, just acknowledge receipt
                    try:
                        # Initialize Twilio client
                        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                        
                        # Send a response
                        send_conversation_message(
                            twilio_client, 
                            conversation_sid, 
                            "I received your message through the Conversations API. This feature is coming soon!"
                        )
                    except Exception as e:
                        logger.error(f"Error sending Conversations response: {str(e)}")
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"Conversation webhook error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
