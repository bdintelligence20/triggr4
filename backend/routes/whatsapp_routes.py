import os
import uuid
import logging
import re
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
    
    # Format the sender number.
    from_number = TWILIO_WHATSAPP_FROM
    if not from_number.startswith('whatsapp:'):
        from_number = f"whatsapp:{from_number}"
    
    try:
        # Split the message semantically if it exceeds the max_length.
        if len(message_body) > max_length:
            chunks = split_message_semantically(message_body, max_length=max_length)
            for chunk in chunks:
                twilio_client.messages.create(
                    body=chunk,
                    from_=from_number,
                    to=to_number
                )
        else:
            twilio_client.messages.create(
                body=message_body,
                from_=from_number,
                to=to_number
            )
        return create_twilio_response("")
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return create_twilio_response(message_body)

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

def handle_verification_code(from_number, message):
    """Handle verification code messages."""
    # Extract verification code (assuming it's a 6-character alphanumeric code)
    code_match = re.search(r'\b([A-Z0-9]{6})\b', message.upper())
    if not code_match:
        return None
    
    verification_code = code_match.group(1)
    
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
        return create_twilio_response("✅ Your WhatsApp number is already verified. You can start querying the knowledge base.")
    
    # Check verification code
    if member_data.get('verificationCode') != verification_code:
        return create_twilio_response("❌ Invalid verification code. Please try again or contact your organization administrator.")
    
    try:
        # Update member as verified
        db.collection('members').document(member_doc.id).update({
            'whatsappVerified': True,
            'status': 'active',
            'verifiedAt': firestore.SERVER_TIMESTAMP
        })
        
        # Get organization name
        org_id = member_data.get('organizationId')
        org_name = "your organization"
        if org_id:
            org_doc = db.collection('organizations').document(org_id).get()
            if org_doc.exists:
                org_data = org_doc.to_dict()
                org_name = org_data.get('name', org_name)
        
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
        send_whatsapp_message(from_number, "⏳ I'm searching through our knowledge base...")
        
        try:
            try:
                # Initialize custom RAG system with organization ID
                whatsapp_rag = RAGSystem(
                    openai_api_key=OPENAI_API_KEY,
                    anthropic_api_key=ANTHROPIC_API_KEY,
                    pinecone_api_key=PINECONE_API_KEY,
                    index_name=PINECONE_INDEX_NAME,
                    organization_id=organization_id  # Pass organization ID to filter results
                )
                
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
                return send_whatsapp_message(
                    from_number, 
                    "❌ I'm sorry, I encountered an error setting up the knowledge base. Please try again later."
                )
            
            # Get the full response
            full_text = ''.join(accumulated_text) if accumulated_text else result.get("answer", "")
            
            if not full_text:
                return send_whatsapp_message(
                    from_number, 
                    "📚 I couldn't find any relevant information in our knowledge base. Please try asking a different question."
                )
            
            # Send intermediate message
            send_whatsapp_message(from_number, "🔍 Found relevant information! Preparing your answer...")
            
            # Send the complete answer
            send_whatsapp_message(from_number, f"📋 {full_text}")
            
            # Send a completion message
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
            return send_whatsapp_message(
                from_number, 
                "❌ I'm sorry, I encountered an error processing your request. Please try again later."
            )
        
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {str(e)}", exc_info=True)
        return create_twilio_response("An error occurred. Please try again later.")
