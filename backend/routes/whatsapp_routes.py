import os
import uuid
import logging
import re
import json
from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from rag_system import RAGSystem
from utils import split_message_semantically
from datetime import datetime, timedelta
from wati_client import get_wati_client

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
whatsapp_bp = Blueprint('whatsapp', __name__)

# Get database instance
db = firestore.client()

# Message deduplication cache
# Store message IDs with timestamps to prevent processing duplicates
# Format: {message_id: timestamp}
processed_messages = {}
# How long to keep messages in the deduplication cache (in hours)
MESSAGE_CACHE_HOURS = 24

# Get environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "knowledge-hub-vectors")
WATI_API_URL = os.environ.get("WATI_API_URL")
WATI_API_TOKEN = os.environ.get("WATI_API_TOKEN")
WATI_WHATSAPP_NUMBER = os.environ.get("WATI_WHATSAPP_NUMBER")

# Initialize WATI client
try:
    wati_client = get_wati_client()
    logger.info("WATI client initialized")
except Exception as e:
    logger.error(f"WATI initialization error: {str(e)}")
    wati_client = None

def send_whatsapp_message(to_number, message_body):
    """
    Sends a WhatsApp message using the WATI client.
    If the message exceeds 1500 characters, it is split semantically into multiple parts.
    """
    max_length = 1500
    
    # Format the phone number for WATI (remove + prefix if present)
    if to_number.startswith('whatsapp:'):
        to_number = to_number[9:]
    if to_number.startswith('+'):
        to_number = to_number[1:]
    
    # Ensure message body is not empty
    if not message_body or message_body.strip() == "":
        message_body = "No message content available."
        logger.warning(f"Empty message body provided to send_whatsapp_message, using placeholder")
    
    # Ensure message body is a string
    if not isinstance(message_body, str):
        message_body = str(message_body)
        logger.warning(f"Non-string message body provided, converted to string")
    
    logger.info(f"Sending WhatsApp message to {to_number}, length: {len(message_body)}")
    
    try:
        # Split the message semantically if it exceeds the max_length
        if len(message_body) > max_length:
            logger.info(f"Message exceeds max length ({len(message_body)} > {max_length}), splitting into chunks")
            chunks = split_message_semantically(message_body, max_length=max_length)
            logger.info(f"Split message into {len(chunks)} chunks")
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Sending chunk {i+1}/{len(chunks)}, length: {len(chunk)}")
                # Add chunk indicator for multiple messages
                if len(chunks) > 1:
                    chunk = f"[Part {i+1}/{len(chunks)}] {chunk}"
                response = wati_client.send_session_message(to_number, chunk)
                logger.info(f"Chunk {i+1} sent, response: {response}")
        else:
            response = wati_client.send_session_message(to_number, message_body)
            logger.info(f"Message sent, response: {response}")
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        
        # Try a direct approach as fallback
        try:
            logger.info("Trying fallback method for sending message")
            # Create a very simple message as fallback
            simple_message = "Message from Knowledge Hub. Please check the web interface for complete information."
            wati_client.send_session_message(to_number, simple_message)
            logger.info("Fallback message sent successfully")
            return jsonify({'status': 'partial_success', 'message': 'Sent fallback message'}), 200
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {str(fallback_error)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

def send_whatsapp_template_message(to_number, template_name, parameters):
    """
    Sends a templated WhatsApp message using WATI's template API.
    
    Parameters:
      - to_number: Recipient's phone number.
      - template_name: The name of the approved WhatsApp template.
      - parameters: A list of dicts with name and value for template parameters.
    """
    # Format the phone number for WATI (remove + prefix if present)
    if to_number.startswith('whatsapp:'):
        to_number = to_number[9:]
    if to_number.startswith('+'):
        to_number = to_number[1:]
    
    # Validate parameters
    validated_parameters = []
    for param in parameters:
        if 'name' in param and 'value' in param:
            # Ensure value is not empty
            if not param['value'] or str(param['value']).strip() == "":
                logger.warning(f"Empty parameter value for {param['name']}, using placeholder")
                param['value'] = "No content available"
            validated_parameters.append(param)
        else:
            logger.warning(f"Skipping invalid parameter: {param}")
    
    logger.info(f"Sending template message '{template_name}' to {to_number}")
    logger.info(f"Template parameters: {validated_parameters}")
    
    try:
        response = wati_client.send_template_message(to_number, template_name, validated_parameters)
        logger.info(f"Template message response: {response}")
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        error_message = str(e)
        logger.error(f"Template error: {error_message}")
        
        # Fall back to direct message if template fails
        try:
            # Extract the main content from parameters if possible
            content = None
            for param in validated_parameters:
                if param.get('name') == '1' or param.get('name') == '2':
                    content = param.get('value')
                    if content:
                        break
            
            if not content:
                content = f"Message from {template_name} template: Sorry, we couldn't send the template message properly."
            
            logger.info(f"Falling back to plain text message: {content[:50]}...")
            return send_whatsapp_message(to_number, content)
        except Exception as fallback_error:
            logger.error(f"Error sending fallback message: {str(fallback_error)}")
            
            # Last resort - try a very simple message
            try:
                simple_message = "Message from Knowledge Hub. Please check the web interface for complete information."
                send_whatsapp_message(to_number, simple_message)
                return jsonify({'status': 'partial_success', 'message': 'Sent simple fallback message'}), 200
            except:
                return jsonify({'status': 'error', 'message': str(e)}), 500

def get_member_by_phone(phone_number):
    """Get member data by phone number."""
    # Clean the phone number (remove whatsapp: prefix if present)
    if phone_number.startswith('whatsapp:'):
        phone_number = phone_number[9:]
    
    # Add + prefix if not present (for database lookup)
    if not phone_number.startswith('+'):
        phone_number = f"+{phone_number}"
    
    # Query for member with this phone number
    members_ref = db.collection('members').where('phone', '==', phone_number).limit(1)
    members = list(members_ref.stream())
    
    if not members:
        return None
    
    member_doc = members[0]
    member_data = member_doc.to_dict()
    member_data['id'] = member_doc.id
    
    return member_data

def sanitize_ai_response(text):
    """Aggressively sanitize AI responses for WhatsApp messages."""
    if not text:
        return "Sorry, I couldn't generate a response. Please try again."
        
    # Remove markdown headers (# Header)
    text = re.sub(r'^#+ +(.+)$', r'\1', text, flags=re.MULTILINE)
    
    # Remove markdown bold/italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    
    # Remove markdown links
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    # Remove markdown code blocks and their content (can cause formatting issues)
    text = re.sub(r'```[\s\S]+?```', '', text)
    
    # Remove markdown inline code
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    # Remove HTML tags that might be in the response
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove special characters that might trigger WhatsApp filters
    # Keep only alphanumeric, basic punctuation, and common symbols
    text = re.sub(r'[^\w\s.,;:!?()\-+\'\"\/]', '', text)
    
    # Limit length to ensure it fits in WhatsApp message
    # WhatsApp has a limit of 4096 characters, but we'll use a lower limit
    # to ensure reliable delivery and better user experience on mobile
    max_length = 1500  # Increased from 1000 but still well below WhatsApp limit
    if len(text) > max_length:
        # Find a good breaking point (end of sentence)
        break_point = text[:max_length].rfind('.')
        if break_point == -1 or break_point < max_length - 200:
            # If no good breaking point, just cut at max_length
            text = text[:max_length-3] + "..."
        else:
            # Cut at the end of a sentence
            text = text[:break_point+1] + " [Message truncated due to length]"
    
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    # Ensure there are no leading/trailing whitespaces
    text = text.strip()
    
    # Final check to ensure we're not returning empty content
    if not text:
        return "I couldn't generate a response. Please try asking your question differently or contact your administrator."
        
    return text

def handle_verification_code(from_number, message):
    """Handle verification code messages."""
    # Extract verification code (must be exactly 6 digits)
    code_match = re.search(r'\b([0-9]{6})\b', message)
    if not code_match:
        logger.info(f"No verification code found in message: '{message}'")
        return None
    
    # Additional check to ensure the message is primarily a verification code
    # If the message is much longer than the code, it's likely a regular query
    verification_code = code_match.group(1)
    message_without_code = message.replace(verification_code, "").strip()
    
    # If there's a lot of other text, this is probably not a verification attempt
    if len(message_without_code) > 20:  # If there's more than 20 chars of other text
        logger.info(f"Message contains a 6-digit code but appears to be a regular query: '{message}'")
        return None
    
    logger.info(f"Verification code extracted: {verification_code}")
    
    # Clean the phone number (remove whatsapp: prefix if present)
    phone_number = from_number
    if phone_number.startswith('whatsapp:'):
        phone_number = phone_number[9:]
    
    # Format phone number with + prefix for database lookup
    if not phone_number.startswith('+'):
        phone_number = f"+{phone_number}"
    
    # Query for member with this phone number
    members_ref = db.collection('members').where('phone', '==', phone_number).limit(1)
    members = list(members_ref.stream())
    
    # Format phone number for WATI (remove + prefix)
    wati_phone = phone_number
    if wati_phone.startswith('+'):
        wati_phone = wati_phone[1:]
    
    if not members:
        send_whatsapp_message(wati_phone, "Your number is not registered in our system. Please contact your organization administrator.")
        return True
    
    member_doc = members[0]
    member_data = member_doc.to_dict()
    
    # Check if already verified
    if member_data.get('whatsappVerified'):
        logger.info(f"Phone number {phone_number} is already verified")
        send_whatsapp_message(wati_phone, "Your WhatsApp number is already verified. You can start querying the knowledge base.")
        return True
    
    # Check if verification was sent
    if not (member_data.get('verificationSent') or member_data.get('verificationSentAt')):
        logger.warning(f"No verification was sent to {phone_number} but received code: {verification_code}")
        send_whatsapp_message(wati_phone, "No verification was requested for this number. Please contact your organization administrator.")
        return True
    
    # Check if verification code matches and is not expired
    stored_code = member_data.get('verificationCode')
    expiry_str = member_data.get('verificationExpiry')
    
    # Log member data for debugging
    logger.info(f"Member data for verification: {json.dumps({k: v for k, v in member_data.items() if k in ['verificationCode', 'verificationExpiry', 'verificationSent', 'verificationSentAt', 'whatsappVerified']})}")
    
    if not stored_code or not expiry_str:
        logger.warning(f"No verification code or expiry found for {phone_number}")
        send_whatsapp_message(wati_phone, "Verification information not found. Please contact your organization administrator.")
        return True
    
    # Check if code is expired
    try:
        expiry = datetime.fromisoformat(expiry_str)
        if datetime.now() > expiry:
            logger.warning(f"Verification code expired for {phone_number}")
            send_whatsapp_message(wati_phone, "Verification code has expired. Please contact your organization administrator for a new code.")
            return True
    except:
        logger.warning(f"Invalid expiry format for {phone_number}: {expiry_str}")
    
    # Check if code matches
    if verification_code != stored_code:
        logger.warning(f"Invalid verification code for {phone_number}. Expected {stored_code}, got {verification_code}")
        send_whatsapp_message(wati_phone, "Invalid verification code. Please try again or contact your organization administrator.")
        return True
    
    # Code matches and is not expired, mark as verified
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
    
    # Update member as verified
    db.collection('members').document(member_id).update({
        'whatsappVerified': True,
        'status': 'active',
        'verifiedAt': firestore.SERVER_TIMESTAMP
    })
    
    logger.info(f"WhatsApp verification successful for member {member_id}")
    
    # Send welcome message using template
    try:
        send_whatsapp_template_message(wati_phone, "welcome_message", [
            {"name": "1", "value": org_name}
        ])
    except Exception as e:
        logger.error(f"Error sending welcome template: {str(e)}")
        # Fall back to session message
        send_whatsapp_message(wati_phone, f"Your WhatsApp number has been verified successfully! You can now query the knowledge base for {org_name}. Try asking a question!")
    
    return True

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
                
                # Format phone number for WATI (remove + prefix)
                wati_phone = phone_number
                if wati_phone.startswith('+'):
                    wati_phone = wati_phone[1:]
                
                # Send the message
                try:
                    # Format the message with personalization if needed
                    personalized_message = data.get('message').replace('{name}', member_data.get('name', 'Member'))
                    
                    # Send message using WATI
                    wati_client.send_session_message(wati_phone, personalized_message)
                    
                    # Record the successful delivery
                    results.append({
                        'memberId': member_id,
                        'status': 'sent',
                        'phone': phone_number,
                        'method': 'session'
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

# Clean up old entries from the message deduplication cache
def clean_message_cache():
    """Remove old entries from the message deduplication cache."""
    current_time = datetime.now()
    expired_keys = []
    
    for message_id, timestamp in processed_messages.items():
        # Check if the entry is older than MESSAGE_CACHE_HOURS
        if current_time - timestamp > timedelta(hours=MESSAGE_CACHE_HOURS):
            expired_keys.append(message_id)
    
    # Remove expired keys
    for key in expired_keys:
        processed_messages.pop(key, None)
    
    if expired_keys:
        logger.info(f"Cleaned {len(expired_keys)} expired entries from message cache")

# WATI webhook handler
@whatsapp_bp.route('/wati-webhook', methods=['POST'])
def wati_webhook():
    """Handle incoming WhatsApp messages from WATI."""
    try:
        # Clean up old entries from the message cache
        clean_message_cache()
        
        # Get the webhook data
        data = request.json
        logger.info(f"Received WATI webhook: {data}")
        
        # Extract message data - WATI webhook format
        if not data:
            logger.warning("No data in webhook")
            return jsonify({'status': 'success'}), 200
        
        # Get message ID for deduplication
        message_id = data.get('id')
        if not message_id:
            logger.warning("No message ID in webhook data")
            # Continue processing as we can't deduplicate without an ID
        else:
            # Check if we've already processed this message
            if message_id in processed_messages:
                logger.info(f"Skipping already processed message: {message_id}")
                return jsonify({'status': 'success'}), 200
            
            # Mark this message as processed
            processed_messages[message_id] = datetime.now()
            
        # Handle different webhook event types
        event_type = data.get('eventType', '')
        
        # For template message events, we don't need to process them
        if event_type == 'templateMessageSent':
            logger.info(f"Received template message event, no action needed")
            return jsonify({'status': 'success'}), 200
            
        # For message status updates, we don't need to process them
        if event_type == 'messageStatusUpdate' or event_type == 'messageStatus':
            logger.info(f"Received message status update, no action needed")
            return jsonify({'status': 'success'}), 200
            
        # For incoming messages
        if event_type == 'message':
            # Extract the text directly - in WATI format 'text' is a string, not an object
            message_body = data.get('text', '').strip()
            from_number = data.get('waId', '')
        else:
            # For other event types or direct text field
            if 'text' in data:
                if isinstance(data['text'], str):
                    message_body = data['text'].strip()
                else:
                    # Try to convert to string if possible
                    try:
                        message_body = str(data['text']).strip()
                        logger.warning(f"Converted non-string text to string: {message_body}")
                    except:
                        logger.warning("Could not convert text field to string")
                        return jsonify({'status': 'success'}), 200
            else:
                logger.warning("No text in webhook data")
                return jsonify({'status': 'success'}), 200
                
            from_number = data.get('waId', '')
        
        if not message_body or not from_number:
            logger.warning("Missing message body or sender number")
            return jsonify({'status': 'success'}), 200
        
        logger.info(f"Processing message from {from_number}: {message_body}")
        
        # Check if this is a verification code
        verification_response = handle_verification_code(from_number, message_body)
        if verification_response:
            return jsonify({'status': 'success'}), 200
        
        # Get the member by phone number
        member = get_member_by_phone(from_number)
        
        if not member:
            logger.warning(f"No member found for phone number: {from_number}")
            # Format phone number for WATI (remove + prefix)
            wati_phone = from_number
            if wati_phone.startswith('+'):
                wati_phone = wati_phone[1:]
            
            # Send response using WATI
            send_whatsapp_message(wati_phone, "Your number is not registered in our system. Please contact your organization administrator.")
            return jsonify({'status': 'success'}), 200
        
        # Check if the member is verified
        if not member.get('whatsappVerified'):
            logger.warning(f"Member {member['id']} with phone {from_number} is not verified")
            # Format phone number for WATI (remove + prefix)
            wati_phone = from_number
            if wati_phone.startswith('+'):
                wati_phone = wati_phone[1:]
            
            # Send response using WATI
            send_whatsapp_message(wati_phone, "Your WhatsApp number is not verified. Please contact your organization administrator.")
            return jsonify({'status': 'success'}), 200
        
        # Get the organization ID
        organization_id = member.get('organizationId')
        
        if not organization_id:
            logger.warning(f"Member {member['id']} does not belong to an organization")
            # Format phone number for WATI (remove + prefix)
            wati_phone = from_number
            if wati_phone.startswith('+'):
                wati_phone = wati_phone[1:]
            
            send_whatsapp_message(wati_phone, "You are not associated with any organization. Please contact your administrator.")
            return jsonify({'status': 'success'}), 200
        
        # Get organization name for logging
        org_name = "Unknown Organization"
        try:
            org_doc = db.collection('organizations').document(organization_id).get()
            if org_doc.exists:
                org_data = org_doc.to_dict()
                org_name = org_data.get('name', 'Unknown Organization')
        except Exception as e:
            logger.error(f"Error fetching organization data: {str(e)}")
        
        logger.info(f"Processing WhatsApp query for organization: {org_name} (ID: {organization_id})")
        
        # Initialize RAG system with organization ID
        rag = RAGSystem(
            openai_api_key=OPENAI_API_KEY,
            anthropic_api_key=ANTHROPIC_API_KEY,
            pinecone_api_key=PINECONE_API_KEY,
            index_name=PINECONE_INDEX_NAME,
            organization_id=organization_id
        )
        
        # Format phone number for WATI (remove + prefix)
        wati_phone = from_number
        if wati_phone.startswith('+'):
            wati_phone = wati_phone[1:]
        
        # Send an intermediate message to indicate processing
        try:
            send_whatsapp_message(wati_phone, "Searching through our knowledge base...")
            
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
            
            # Query the knowledge base
            import threading
            import queue

            # Create a queue to hold the response
            response_queue = queue.Queue()
            
            # Get conversation history for this member
            conversation_history = ""
            try:
                # Get the last 5 queries for this member
                history_query = db.collection('queries') \
                    .where('memberId', '==', member['id']) \
                    .where('status', '==', 'completed') \
                    .order_by('createdAt', direction=firestore.Query.DESCENDING) \
                    .limit(5)
                
                history_docs = list(history_query.stream())
                
                # Format the history in the expected format for the RAG system
                if history_docs:
                    history_items = []
                    for doc in reversed(history_docs):  # Oldest first
                        doc_data = doc.to_dict()
                        if 'query' in doc_data and 'response' in doc_data:
                            history_items.append(f"User: {doc_data['query']}")
                            history_items.append(f"AI: {doc_data['response']}")
                    
                    conversation_history = "\n".join(history_items)
                    logger.info(f"Retrieved conversation history with {len(history_docs)} previous exchanges")
            except Exception as history_error:
                logger.warning(f"Error retrieving conversation history: {str(history_error)}")
                # Continue without history if there's an error
            
            # Define a function to run the query in a separate thread
            def run_query():
                try:
                    result = rag.query(
                        user_query=message_body,  # Use the correct parameter name
                        user_id=member['id'],
                        history=conversation_history
                        # Don't pass organization_id again - it's already set during initialization
                    )
                    response_queue.put(("success", result))
                except Exception as e:
                    response_queue.put(("error", str(e)))
            
            # Start the query in a separate thread
            query_thread = threading.Thread(target=run_query)
            query_thread.daemon = True
            query_thread.start()
            
            # Wait for the query to complete with a timeout
            try:
                status, response = response_queue.get(timeout=60)  # 60 second timeout
                if status == "error":
                    raise Exception(response)
            except queue.Empty:
                # Timeout occurred
                logger.error(f"RAG query timed out after 60 seconds for query: {message_body}")
                db.collection('queries').document(query_id).update({
                    'status': 'failed',
                    'error': 'Query timed out after 60 seconds',
                    'completedAt': firestore.SERVER_TIMESTAMP
                })
                send_whatsapp_message(wati_phone, "Sorry, your query is taking too long to process. Please try a simpler question or contact your administrator.")
                return jsonify({'status': 'success'}), 200
            
            # Sanitize the response for WhatsApp
            sanitized_response = sanitize_ai_response(response.get('answer', ''))
            
            # Update the query with the response
            db.collection('queries').document(query_id).update({
                'response': response.get('answer', ''),
                'sources': response.get('sources', []),
                'status': 'completed',
                'completedAt': firestore.SERVER_TIMESTAMP
            })
            
            # Try to send as session message first (within 24-hour window)
            try:
                send_whatsapp_message(wati_phone, sanitized_response)
            except Exception as session_error:
                logger.warning(f"Error sending session message: {str(session_error)}")
                # Fall back to template message if session message fails
                try:
                    send_whatsapp_template_message(
                        wati_phone,
                        "knowledge_response",
                        [
                            {"name": "1", "value": org_name},
                            {"name": "2", "value": sanitized_response}
                        ]
                    )
                except Exception as template_error:
                    logger.error(f"Error sending template message: {str(template_error)}")
                    # If all else fails, try one more time with session message
                    send_whatsapp_message(
                        wati_phone, 
                        "Sorry, we couldn't process your query. Please try again later."
                    )
            
            return jsonify({'status': 'success'}), 200
            
        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}")
            
            # Update the query with the error
            db.collection('queries').document(query_id).update({
                'status': 'failed',
                'error': str(e),
                'completedAt': firestore.SERVER_TIMESTAMP
            })
            
            # Send error message
            send_whatsapp_message(
                wati_phone, 
                "Sorry, we couldn't process your query. Please try again later or contact your administrator."
            )
            
            return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        logger.error(f"Error handling WATI webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Legacy Twilio webhook handler (kept for backward compatibility)
@whatsapp_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming WhatsApp messages from Twilio (legacy)."""
    try:
        # Get the message data
        form_data = request.form.to_dict()
        
        # Log the incoming message
        logger.info(f"Received Twilio webhook (legacy): {form_data}")
        
        # Get the message body and sender
        message_body = form_data.get('Body', '').strip()
        from_number = form_data.get('From', '')
        message_sid = form_data.get('MessageSid')  # Twilio's message ID
        
        if not message_body or not from_number:
            logger.warning("Missing message body or sender number")
            return jsonify({'status': 'success'}), 200
        
        # Check for message deduplication if we have a message ID
        if message_sid:
            # Clean up old entries from the message cache
            clean_message_cache()
            
            # Check if we've already processed this message
            if message_sid in processed_messages:
                logger.info(f"Skipping already processed Twilio message: {message_sid}")
                return jsonify({'status': 'success'}), 200
            
            # Mark this message as processed
            processed_messages[message_sid] = datetime.now()
        
        # Redirect to WATI webhook handler
        logger.info(f"Redirecting legacy Twilio webhook to WATI handler")
        
        # Create a WATI-like webhook payload
        wati_data = {
            'text': message_body,
            'waId': from_number,
            'eventType': 'message',
            'id': message_sid  # Include the message ID for deduplication in the WATI handler
        }
        
        # Call the WATI webhook handler with the transformed data
        request._cached_json = (wati_data, request._cached_json[1] if hasattr(request, '_cached_json') else {})
        return wati_webhook()
        
    except Exception as e:
        logger.error(f"Error handling legacy webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
