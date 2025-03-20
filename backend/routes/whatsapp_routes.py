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
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM", "+14155238886")

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
            # Initialize custom RAG system with organization ID
            whatsapp_rag = RAGSystem(
                openai_api_key=OPENAI_API_KEY,
                anthropic_api_key=ANTHROPIC_API_KEY,
                pinecone_api_key=PINECONE_API_KEY,
                index_name=PINECONE_INDEX_NAME,
                organization_id=organization_id  # Pass organization ID to filter results
            )
            
            # Collect the full response
            accumulated_text = []
            
            def stream_callback(chunk):
                accumulated_text.append(chunk)
            
            # Query the RAG system
            result = whatsapp_rag.query(
                user_query=incoming_msg,
                stream_callback=stream_callback
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
