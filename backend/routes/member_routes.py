import os
import logging
from flask import Blueprint, request, jsonify
from firebase_admin import firestore, auth
from twilio.rest import Client
import uuid
import jwt

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
member_bp = Blueprint('member', __name__)

# Get database instance
db = firestore.client()

# Get environment variables
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM", "+14155238886")
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key')

# Initialize Twilio client
try:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    logger.info("Twilio client initialized for member management")
except Exception as e:
    logger.error(f"Twilio initialization error: {str(e)}")
    twilio_client = None

def verify_token(token):
    """Verify a JWT token and return the payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user(request):
    """Get the current user from the request's Authorization header."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        return None
    
    return payload

@member_bp.route('/members', methods=['GET'])
def get_members():
    """Get all members for the current user's organization."""
    current_user = get_current_user(request)
    
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get user data from Firestore to get organization ID
    user_doc = db.collection('users').document(current_user['user_id']).get()
    
    if not user_doc.exists:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = user_doc.to_dict()
    organization_id = user_data.get('organizationId')
    
    if not organization_id:
        return jsonify({'error': 'User is not associated with an organization'}), 400
    
    # Query members collection for the organization
    members_ref = db.collection('members').where('organizationId', '==', organization_id)
    members = []
    
    try:
        for doc in members_ref.stream():
            member_data = doc.to_dict()
            member_data['id'] = doc.id
            members.append(member_data)
        
        return jsonify({'members': members})
    except Exception as e:
        logger.error(f"Error fetching members: {str(e)}")
        return jsonify({'error': 'Failed to fetch members'}), 500

@member_bp.route('/members', methods=['POST'])
def add_member():
    """Add a new member to the organization."""
    current_user = get_current_user(request)
    
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get user data from Firestore to get organization ID
    user_doc = db.collection('users').document(current_user['user_id']).get()
    
    if not user_doc.exists:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = user_doc.to_dict()
    organization_id = user_data.get('organizationId')
    
    if not organization_id:
        return jsonify({'error': 'User is not associated with an organization'}), 400
    
    # Get organization data to check if user is admin
    org_doc = db.collection('organizations').document(organization_id).get()
    
    if not org_doc.exists:
        return jsonify({'error': 'Organization not found'}), 404
    
    org_data = org_doc.to_dict()
    
    # Check if user is admin of the organization
    if current_user['user_id'] not in org_data.get('admins', []):
        return jsonify({'error': 'Only organization admins can add members'}), 403
    
    # Get member data from request
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    position = data.get('position')
    role = data.get('role', 'viewer')
    
    # Validate required fields
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    if not phone:
        return jsonify({'error': 'Phone number is required'}), 400
    
    # Check if member with this email already exists
    existing_email_query = db.collection('members').where('email', '==', email).limit(1)
    if len(list(existing_email_query.stream())) > 0:
        return jsonify({'error': 'A member with this email already exists'}), 400
    
    # Check if member with this phone already exists
    existing_phone_query = db.collection('members').where('phone', '==', phone).limit(1)
    if len(list(existing_phone_query.stream())) > 0:
        return jsonify({'error': 'A member with this phone number already exists'}), 400
    
    # Create member document
    member_data = {
        'name': name or email.split('@')[0],
        'email': email,
        'phone': phone,
        'position': position or 'Member',
        'role': role,
        'status': 'pending',
        'organizationId': organization_id,
        'whatsappVerified': False,
        'createdAt': firestore.SERVER_TIMESTAMP,
        'createdBy': current_user['user_id']
    }
    
    try:
        # Add member to Firestore
        member_ref = db.collection('members').document()
        member_ref.set(member_data)
        
        # Send WhatsApp verification message
        if twilio_client:
            try:
                # Generate verification code
                verification_code = str(uuid.uuid4())[:6].upper()
                
                # Store verification code in Firestore
                member_ref.update({
                    'verificationCode': verification_code,
                    'verificationExpiry': firestore.SERVER_TIMESTAMP
                })
                
                # Format the phone number for WhatsApp
                to_number = phone
                if not to_number.startswith('whatsapp:'):
                    to_number = f"whatsapp:{to_number}"
                
                # Format the sender number
                from_number = TWILIO_WHATSAPP_FROM
                if not from_number.startswith('whatsapp:'):
                    from_number = f"whatsapp:{from_number}"
                
                # Send verification message
                message = twilio_client.messages.create(
                    body=f"Welcome to Knowledge Hub! Your verification code is: {verification_code}. Reply with this code to verify your WhatsApp number.",
                    from_=from_number,
                    to=to_number
                )
                
                logger.info(f"WhatsApp verification message sent to {phone}: {message.sid}")
            except Exception as e:
                logger.error(f"Error sending WhatsApp verification: {str(e)}")
                # Continue even if WhatsApp verification fails
        
        # Return success response with member ID
        return jsonify({
            'message': 'Member added successfully',
            'memberId': member_ref.id,
            'member': {
                'id': member_ref.id,
                **member_data
            }
        })
    except Exception as e:
        logger.error(f"Error adding member: {str(e)}")
        return jsonify({'error': 'Failed to add member'}), 500

@member_bp.route('/members/<member_id>', methods=['PUT'])
def update_member(member_id):
    """Update a member's details."""
    current_user = get_current_user(request)
    
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get user data from Firestore to get organization ID
    user_doc = db.collection('users').document(current_user['user_id']).get()
    
    if not user_doc.exists:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = user_doc.to_dict()
    organization_id = user_data.get('organizationId')
    
    if not organization_id:
        return jsonify({'error': 'User is not associated with an organization'}), 400
    
    # Get member document
    member_doc = db.collection('members').document(member_id).get()
    
    if not member_doc.exists:
        return jsonify({'error': 'Member not found'}), 404
    
    member_data = member_doc.to_dict()
    
    # Check if member belongs to the user's organization
    if member_data.get('organizationId') != organization_id:
        return jsonify({'error': 'Member does not belong to your organization'}), 403
    
    # Get organization data to check if user is admin
    org_doc = db.collection('organizations').document(organization_id).get()
    
    if not org_doc.exists:
        return jsonify({'error': 'Organization not found'}), 404
    
    org_data = org_doc.to_dict()
    
    # Check if user is admin of the organization
    if current_user['user_id'] not in org_data.get('admins', []):
        return jsonify({'error': 'Only organization admins can update members'}), 403
    
    # Get update data from request
    data = request.get_json()
    
    # Fields that can be updated
    updatable_fields = ['name', 'position', 'role', 'status']
    update_data = {}
    
    for field in updatable_fields:
        if field in data:
            update_data[field] = data[field]
    
    # Add updatedAt timestamp
    update_data['updatedAt'] = firestore.SERVER_TIMESTAMP
    update_data['updatedBy'] = current_user['user_id']
    
    try:
        # Update member in Firestore
        db.collection('members').document(member_id).update(update_data)
        
        # Return success response
        return jsonify({
            'message': 'Member updated successfully',
            'memberId': member_id
        })
    except Exception as e:
        logger.error(f"Error updating member: {str(e)}")
        return jsonify({'error': 'Failed to update member'}), 500

@member_bp.route('/members/<member_id>', methods=['DELETE'])
def delete_member(member_id):
    """Delete a member."""
    current_user = get_current_user(request)
    
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get user data from Firestore to get organization ID
    user_doc = db.collection('users').document(current_user['user_id']).get()
    
    if not user_doc.exists:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = user_doc.to_dict()
    organization_id = user_data.get('organizationId')
    
    if not organization_id:
        return jsonify({'error': 'User is not associated with an organization'}), 400
    
    # Get member document
    member_doc = db.collection('members').document(member_id).get()
    
    if not member_doc.exists:
        return jsonify({'error': 'Member not found'}), 404
    
    member_data = member_doc.to_dict()
    
    # Check if member belongs to the user's organization
    if member_data.get('organizationId') != organization_id:
        return jsonify({'error': 'Member does not belong to your organization'}), 403
    
    # Get organization data to check if user is admin
    org_doc = db.collection('organizations').document(organization_id).get()
    
    if not org_doc.exists:
        return jsonify({'error': 'Organization not found'}), 404
    
    org_data = org_doc.to_dict()
    
    # Check if user is admin of the organization
    if current_user['user_id'] not in org_data.get('admins', []):
        return jsonify({'error': 'Only organization admins can delete members'}), 403
    
    try:
        # Delete member from Firestore
        db.collection('members').document(member_id).delete()
        
        # Return success response
        return jsonify({
            'message': 'Member deleted successfully',
            'memberId': member_id
        })
    except Exception as e:
        logger.error(f"Error deleting member: {str(e)}")
        return jsonify({'error': 'Failed to delete member'}), 500

@member_bp.route('/members/verify-whatsapp', methods=['POST'])
def verify_whatsapp():
    """Verify a member's WhatsApp number."""
    data = request.get_json()
    phone = data.get('phone')
    code = data.get('code')
    
    if not phone or not code:
        return jsonify({'error': 'Phone number and verification code are required'}), 400
    
    # Query for member with this phone number
    members_ref = db.collection('members').where('phone', '==', phone).limit(1)
    members = list(members_ref.stream())
    
    if not members:
        return jsonify({'error': 'No member found with this phone number'}), 404
    
    member_doc = members[0]
    member_data = member_doc.to_dict()
    
    # Check verification code
    if member_data.get('verificationCode') != code:
        return jsonify({'error': 'Invalid verification code'}), 400
    
    try:
        # Update member as verified
        db.collection('members').document(member_doc.id).update({
            'whatsappVerified': True,
            'status': 'active',
            'verifiedAt': firestore.SERVER_TIMESTAMP
        })
        
        # Return success response
        return jsonify({
            'message': 'WhatsApp number verified successfully',
            'memberId': member_doc.id
        })
    except Exception as e:
        logger.error(f"Error verifying WhatsApp: {str(e)}")
        return jsonify({'error': 'Failed to verify WhatsApp number'}), 500

@member_bp.route('/members/send-verification', methods=['POST'])
def send_verification():
    """Send a verification message to a member's WhatsApp number."""
    current_user = get_current_user(request)
    
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    member_id = data.get('memberId')
    
    if not member_id:
        return jsonify({'error': 'Member ID is required'}), 400
    
    # Get member document
    member_doc = db.collection('members').document(member_id).get()
    
    if not member_doc.exists:
        return jsonify({'error': 'Member not found'}), 404
    
    member_data = member_doc.to_dict()
    phone = member_data.get('phone')
    
    if not phone:
        return jsonify({'error': 'Member does not have a phone number'}), 400
    
    # Get user data from Firestore to get organization ID
    user_doc = db.collection('users').document(current_user['user_id']).get()
    
    if not user_doc.exists:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = user_doc.to_dict()
    organization_id = user_data.get('organizationId')
    
    # Check if member belongs to the user's organization
    if member_data.get('organizationId') != organization_id:
        return jsonify({'error': 'Member does not belong to your organization'}), 403
    
    if not twilio_client:
        return jsonify({'error': 'Twilio client not initialized'}), 500
    
    try:
        # Generate verification code
        verification_code = str(uuid.uuid4())[:6].upper()
        
        # Store verification code in Firestore
        db.collection('members').document(member_id).update({
            'verificationCode': verification_code,
            'verificationExpiry': firestore.SERVER_TIMESTAMP
        })
        
        # Format the phone number for WhatsApp
        to_number = phone
        if not to_number.startswith('whatsapp:'):
            to_number = f"whatsapp:{to_number}"
        
        # Format the sender number
        from_number = TWILIO_WHATSAPP_FROM
        if not from_number.startswith('whatsapp:'):
            from_number = f"whatsapp:{from_number}"
        
        # Send verification message
        message = twilio_client.messages.create(
            body=f"Welcome to Knowledge Hub! Your verification code is: {verification_code}. Reply with this code to verify your WhatsApp number.",
            from_=from_number,
            to=to_number
        )
        
        logger.info(f"WhatsApp verification message sent to {phone}: {message.sid}")
        
        # Return success response
        return jsonify({
            'message': 'Verification message sent successfully',
            'memberId': member_id
        })
    except Exception as e:
        logger.error(f"Error sending verification message: {str(e)}")
        return jsonify({'error': f'Failed to send verification message: {str(e)}'}), 500
