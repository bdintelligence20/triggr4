import logging
import os
import json
from flask import Blueprint, request, jsonify
from firebase_admin import firestore
import uuid
from datetime import datetime
import re

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Firestore client
db = firestore.client()

# Create blueprint
member_bp = Blueprint('members', __name__, url_prefix='/members')

# Helper function to validate phone number
def is_valid_phone(phone):
    # Basic validation for international phone numbers
    # Allows for country code with + prefix and digits
    pattern = r'^\+\d{1,3}\d{6,14}$'
    return bool(re.match(pattern, phone))

# Helper function to validate email
def is_valid_email(email):
    # Basic email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# Get all members for the current user's organization
@member_bp.route('', methods=['GET'])
def get_members():
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
        
        # Get all members for the organization
        members_ref = db.collection('members')
        members_query = members_ref.where('organizationId', '==', organization_id).get()
        
        members = []
        for doc in members_query:
            member_data = doc.to_dict()
            member_data['id'] = doc.id
            members.append(member_data)
        
        return jsonify({'members': members}), 200
        
    except Exception as e:
        logger.error(f"Error getting members: {str(e)}")
        return jsonify({'error': f'Failed to get members: {str(e)}'}), 500

# Add a new member to the organization
@member_bp.route('', methods=['POST'])
def add_member():
    try:
        # Get the user ID from the request
        auth_header = request.headers.get('Authorization')
        logger.info(f"Auth header: {auth_header}")
        
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.error("Missing or invalid Authorization header")
            return jsonify({'error': 'Unauthorized'}), 401
        
        token = auth_header.split(' ')[1]
        logger.info(f"Token: {token[:10]}...")  # Log first 10 chars of token for debugging
        
        # Get the user from Firestore
        users_ref = db.collection('users')
        logger.info("Querying users collection for auth_token")
        user_query = users_ref.where('auth_token', '==', token).limit(1).get()
        
        # Check if user_query is empty
        user_query_list = list(user_query)
        logger.info(f"User query results: {len(user_query_list)} documents found")
        
        if not user_query_list:
            logger.error(f"No user found with token: {token[:10]}...")
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user_query_list[0].to_dict()
        logger.info(f"User data: {user_data}")
        
        organization_id = user_data.get('organizationId')
        logger.info(f"Organization ID: {organization_id}")
        
        if not organization_id:
            logger.error(f"User does not have an organizationId: {user_data}")
            return jsonify({'error': 'User does not belong to an organization'}), 400
        
        # Get the member data from the request
        data = request.json
        
        # Validate required fields
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        if not data.get('phone'):
            return jsonify({'error': 'Phone number is required'}), 400
        
        # Validate email format
        if not is_valid_email(data.get('email')):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate phone number format
        if not is_valid_phone(data.get('phone')):
            return jsonify({'error': 'Invalid phone number format. Use international format with + prefix (e.g., +27123456789)'}), 400
        
        # Check if a member with this email already exists
        members_ref = db.collection('members')
        email_query = members_ref.where('email', '==', data.get('email')).limit(1).get()
        
        if email_query:
            return jsonify({'error': 'A member with this email already exists'}), 400
        
        # Check if a member with this phone number already exists
        phone_query = members_ref.where('phone', '==', data.get('phone')).limit(1).get()
        
        if phone_query:
            return jsonify({'error': 'A member with this phone number already exists'}), 400
        
        # Create the member
        member_id = str(uuid.uuid4())
        member_data = {
            'name': data.get('name', ''),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'position': data.get('position', ''),
            'role': data.get('role', 'viewer'),
            'status': 'pending',
            'organizationId': organization_id,
            'whatsappVerified': False,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'createdBy': user_query[0].id
        }
        
        # Add the member to Firestore
        members_ref.document(member_id).set(member_data)
        
        # Return the member data
        member_data['id'] = member_id
        
        return jsonify({'memberId': member_id, 'member': member_data}), 201
        
    except Exception as e:
        logger.error(f"Error adding member: {str(e)}")
        return jsonify({'error': f'Failed to add member: {str(e)}'}), 500

# Update a member
@member_bp.route('/<member_id>', methods=['PUT'])
def update_member(member_id):
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
        
        # Get the member from Firestore
        members_ref = db.collection('members')
        member_doc = members_ref.document(member_id).get()
        
        if not member_doc.exists:
            return jsonify({'error': 'Member not found'}), 404
        
        member_data = member_doc.to_dict()
        
        # Check if the member belongs to the user's organization
        if member_data.get('organizationId') != organization_id:
            return jsonify({'error': 'Unauthorized to update this member'}), 403
        
        # Get the update data from the request
        data = request.json
        
        # Update the member data
        update_data = {}
        
        if 'name' in data:
            update_data['name'] = data['name']
        
        if 'position' in data:
            update_data['position'] = data['position']
        
        if 'role' in data:
            update_data['role'] = data['role']
        
        if 'status' in data:
            update_data['status'] = data['status']
        
        # Add updatedAt timestamp
        update_data['updatedAt'] = firestore.SERVER_TIMESTAMP
        update_data['updatedBy'] = user_query[0].id
        
        # Update the member in Firestore
        members_ref.document(member_id).update(update_data)
        
        return jsonify({'memberId': member_id}), 200
        
    except Exception as e:
        logger.error(f"Error updating member: {str(e)}")
        return jsonify({'error': f'Failed to update member: {str(e)}'}), 500

# Delete a member
@member_bp.route('/<member_id>', methods=['DELETE'])
def delete_member(member_id):
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
        
        # Get the member from Firestore
        members_ref = db.collection('members')
        member_doc = members_ref.document(member_id).get()
        
        if not member_doc.exists:
            return jsonify({'error': 'Member not found'}), 404
        
        member_data = member_doc.to_dict()
        
        # Check if the member belongs to the user's organization
        if member_data.get('organizationId') != organization_id:
            return jsonify({'error': 'Unauthorized to delete this member'}), 403
        
        # Delete the member from Firestore
        members_ref.document(member_id).delete()
        
        return jsonify({'memberId': member_id}), 200
        
    except Exception as e:
        logger.error(f"Error deleting member: {str(e)}")
        return jsonify({'error': f'Failed to delete member: {str(e)}'}), 500

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

import random
import string
from datetime import datetime, timedelta

# Helper function to generate a random verification code
def generate_verification_code(length=6):
    """Generate a random numeric verification code of specified length."""
    return ''.join(random.choices(string.digits, k=length))

# Send WhatsApp verification to a member
@member_bp.route('/send-verification', methods=['POST'])
def send_whatsapp_verification():
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
        
        # Get the member ID from the request
        data = request.json
        member_id = data.get('memberId')
        
        if not member_id:
            return jsonify({'error': 'Member ID is required'}), 400
        
        # Get the member from Firestore
        members_ref = db.collection('members')
        member_doc = members_ref.document(member_id).get()
        
        if not member_doc.exists:
            return jsonify({'error': 'Member not found'}), 404
        
        member_data = member_doc.to_dict()
        
        # Check if the member belongs to the user's organization
        if member_data.get('organizationId') != organization_id:
            return jsonify({'error': 'Unauthorized to verify this member'}), 403
        
        # Get Twilio credentials
        twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        twilio_messaging_service_sid = os.environ.get("TWILIO_MESSAGING_SERVICE_SID")
        
        if not all([twilio_account_sid, twilio_auth_token, twilio_messaging_service_sid]):
            logger.warning("Twilio credentials or Messaging Service SID not found.")
            return jsonify({'error': 'Twilio credentials not fully configured'}), 500
        
        try:
            # Initialize Twilio client
            from twilio.rest import Client
            twilio_client = Client(twilio_account_sid, twilio_auth_token)
            
            # Get or create a Verify service
            verify_service_sid = get_or_create_verify_service(twilio_client)
            
            # Format the phone number (must be E.164 format without the whatsapp: prefix)
            to_number = member_data.get('phone')
            # Remove whatsapp: prefix if present
            if to_number.startswith('whatsapp:'):
                to_number = to_number[9:]
            
            # Get organization name
            org_name = "Knowledge Hub"
            org_doc = db.collection('organizations').document(organization_id).get()
            if org_doc.exists:
                org_data = org_doc.to_dict()
                org_name = org_data.get('name', org_name)
            
            # Send verification via SMS using Verify API
            try:
                logger.info(f"Sending SMS verification to {to_number} using Verify service {verify_service_sid}")
                
                # Create the verification parameters
                verification_params = {
                    'to': to_number,
                    'channel': 'sms'
                }
                
                # Log the verification parameters
                logger.info(f"Verification parameters: {verification_params}")
                
                # Create the verification
                verification = twilio_client.verify.v2.services(verify_service_sid).verifications.create(**verification_params)
                
                # If we get here, the verification was successful
                logger.info(f"SMS verification sent successfully. SID: {verification.sid}")
                
                # Store verification information in Firestore
                members_ref.document(member_id).update({
                    'smsVerificationSent': True,
                    'smsVerificationSentAt': firestore.SERVER_TIMESTAMP,
                    'verificationSid': verification.sid,
                    'updatedAt': firestore.SERVER_TIMESTAMP,
                    'updatedBy': user_query[0].id
                })
                
                return jsonify({
                    'memberId': member_id,
                    'status': 'verification_sent',
                    'verificationSid': verification.sid
                }), 200
                
            except Exception as e:
                logger.error(f"Error sending SMS verification: {str(e)}")
                # Log detailed error information
                if hasattr(e, 'code'):
                    logger.error(f"Twilio error code: {e.code}")
                if hasattr(e, 'msg'):
                    logger.error(f"Twilio error message: {e.msg}")
                if hasattr(e, 'status'):
                    logger.error(f"Twilio error status: {e.status}")
                if hasattr(e, 'details'):
                    logger.error(f"Twilio error details: {e.details}")
                
                return jsonify({'error': f'Failed to send SMS verification: {str(e)}'}), 500
            
        except Exception as e:
            logger.error(f"Error initializing Twilio client: {str(e)}")
            return jsonify({'error': f'Failed to initialize Twilio client: {str(e)}'}), 500
        
    except Exception as e:
        logger.error(f"Error sending verification: {str(e)}")
        return jsonify({'error': f'Failed to send verification: {str(e)}'}), 500

# Verify a member's WhatsApp verification code
@member_bp.route('/verify-code', methods=['POST'])
def verify_whatsapp_code():
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
        
        # Get the verification data from the request
        data = request.json
        member_id = data.get('memberId')
        verification_code = data.get('code')
        
        if not member_id or not verification_code:
            return jsonify({'error': 'Member ID and verification code are required'}), 400
        
        # Get the member from Firestore
        members_ref = db.collection('members')
        member_doc = members_ref.document(member_id).get()
        
        if not member_doc.exists:
            return jsonify({'error': 'Member not found'}), 404
        
        member_data = member_doc.to_dict()
        
        # Check if the member belongs to the user's organization
        if member_data.get('organizationId') != organization_id:
            return jsonify({'error': 'Unauthorized to verify this member'}), 403
        
        # Check if verification was sent
        if not member_data.get('smsVerificationSent'):
            return jsonify({'error': 'No verification was sent to this member'}), 400
        
        # Get the verification SID
        verification_sid = member_data.get('verificationSid')
        
        if not verification_sid:
            return jsonify({'error': 'No verification SID found for this member'}), 400
        
        # Get Twilio credentials
        twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        
        if not all([twilio_account_sid, twilio_auth_token]):
            logger.warning("Twilio credentials not found.")
            return jsonify({'error': 'Twilio credentials not fully configured'}), 500
        
        try:
            # Initialize Twilio client
            from twilio.rest import Client
            twilio_client = Client(twilio_account_sid, twilio_auth_token)
            
            # Get the Verify service SID
            verify_service_sid = get_or_create_verify_service(twilio_client)
            
            # Format the phone number (must be E.164 format without the whatsapp: prefix)
            to_number = member_data.get('phone')
            # Remove whatsapp: prefix if present
            if to_number.startswith('whatsapp:'):
                to_number = to_number[9:]
            
            # Check the verification code with Twilio Verify
            try:
                logger.info(f"Checking verification code for {to_number}")
                
                # Create the verification check
                verification_check = twilio_client.verify.v2.services(verify_service_sid).verification_checks.create(
                    to=to_number,
                    code=verification_code
                )
                
                logger.info(f"Verification check result: {verification_check.status}")
                
                # Check if the verification was successful
                if verification_check.status == "approved":
                    # Mark the member as verified
                    members_ref.document(member_id).update({
                        'whatsappVerified': True,  # Keep this for backward compatibility
                        'smsVerified': True,
                        'status': 'active',
                        'verifiedAt': firestore.SERVER_TIMESTAMP,
                        'updatedAt': firestore.SERVER_TIMESTAMP,
                        'updatedBy': user_query[0].id
                    })
                    
                    return jsonify({
                        'memberId': member_id,
                        'status': 'verified'
                    }), 200
                else:
                    return jsonify({'error': f'Verification failed with status: {verification_check.status}'}), 400
                
            except Exception as e:
                logger.error(f"Error checking verification code: {str(e)}")
                # Log detailed error information
                if hasattr(e, 'code'):
                    logger.error(f"Twilio error code: {e.code}")
                if hasattr(e, 'msg'):
                    logger.error(f"Twilio error message: {e.msg}")
                if hasattr(e, 'status'):
                    logger.error(f"Twilio error status: {e.status}")
                if hasattr(e, 'details'):
                    logger.error(f"Twilio error details: {e.details}")
                
                return jsonify({'error': f'Failed to check verification code: {str(e)}'}), 500
            
        except Exception as e:
            logger.error(f"Error initializing Twilio client: {str(e)}")
            return jsonify({'error': f'Failed to initialize Twilio client: {str(e)}'}), 500
        
    except Exception as e:
        logger.error(f"Error verifying code: {str(e)}")
        return jsonify({'error': f'Failed to verify code: {str(e)}'}), 500

# Original Verify API implementation (commented out)
"""
# Send WhatsApp verification to a member
@member_bp.route('/send-verification', methods=['POST'])
def send_whatsapp_verification():
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
        
        # Get the member ID from the request
        data = request.json
        member_id = data.get('memberId')
        
        if not member_id:
            return jsonify({'error': 'Member ID is required'}), 400
        
        # Get the member from Firestore
        members_ref = db.collection('members')
        member_doc = members_ref.document(member_id).get()
        
        if not member_doc.exists:
            return jsonify({'error': 'Member not found'}), 404
        
        member_data = member_doc.to_dict()
        
        # Check if the member belongs to the user's organization
        if member_data.get('organizationId') != organization_id:
            return jsonify({'error': 'Unauthorized to verify this member'}), 403
        
        # Get Twilio credentials
        twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        twilio_messaging_service_sid = os.environ.get("TWILIO_MESSAGING_SERVICE_SID")
        
        if not all([twilio_account_sid, twilio_auth_token, twilio_messaging_service_sid]):
            logger.warning("Twilio credentials or Messaging Service SID not found.")
            return jsonify({'error': 'Twilio credentials not fully configured'}), 500
        
        try:
            # Initialize Twilio client
            from twilio.rest import Client
            twilio_client = Client(twilio_account_sid, twilio_auth_token)
            
            # Get or create a Verify service
            verify_service_sid = get_or_create_verify_service(twilio_client)
            
            # Format the phone number (must be E.164 format without the whatsapp: prefix)
            to_number = member_data.get('phone')
            # Remove whatsapp: prefix if present
            if to_number.startswith('whatsapp:'):
                to_number = to_number[9:]
            
            # Get organization name
            org_name = "Knowledge Hub"
            org_doc = db.collection('organizations').document(organization_id).get()
            if org_doc.exists:
                org_data = org_doc.to_dict()
                org_name = org_data.get('name', org_name)
            
            # Note: We don't need to check for available channels as this attribute
            # is not directly accessible in the Twilio Python SDK
            
            # Send verification via WhatsApp using Verify API
            try:
                logger.info(f"Sending WhatsApp verification to {to_number} using service {verify_service_sid}")
                
                # Try to get the WhatsApp Business Profile SID
                try:
                    # List all messaging services to find the one with WhatsApp enabled
                    messaging_services = twilio_client.messaging.v1.services.list()
                    whatsapp_service = None
                    
                    for service in messaging_services:
                        # Check if this service has WhatsApp capabilities
                        if service.sid == twilio_messaging_service_sid:
                            whatsapp_service = service
                            logger.info(f"Found WhatsApp messaging service: {service.sid}")
                            break
                    
                    if whatsapp_service:
                        logger.info(f"Using WhatsApp messaging service: {whatsapp_service.sid}")
                    else:
                        logger.warning("No WhatsApp messaging service found")
                except Exception as ms_error:
                    logger.warning(f"Error finding WhatsApp messaging service: {str(ms_error)}")
                
                # Create the verification without specifying locale
                verification_params = {
                    'to': to_number,
                    'channel': 'whatsapp'
                }
                
                # Log the verification parameters
                logger.info(f"Verification parameters: {verification_params}")
                
                # Create the verification
                verification = twilio_client.verify.v2.services(verify_service_sid).verifications.create(**verification_params)
                
                # If we get here, the verification was successful
                logger.info(f"WhatsApp verification sent successfully. SID: {verification.sid}")
                
                # Store verification information in Firestore
                members_ref.document(member_id).update({
                    'whatsappVerificationSent': True,
                    'whatsappVerificationSentAt': firestore.SERVER_TIMESTAMP,
                    'verificationSid': verification.sid,
                    'updatedAt': firestore.SERVER_TIMESTAMP,
                    'updatedBy': user_query[0].id
                })
                
                return jsonify({
                    'memberId': member_id,
                    'status': 'verification_sent',
                    'verificationSid': verification.sid
                }), 200
                
            except Exception as e:
                logger.error(f"Error sending WhatsApp verification: {str(e)}")
                return jsonify({'error': f'Failed to send verification: {str(e)}'}), 500
            
        except Exception as e:
            logger.error(f"Error initializing Twilio client: {str(e)}")
            return jsonify({'error': f'Failed to initialize Twilio client: {str(e)}'}), 500
        
    except Exception as e:
        logger.error(f"Error sending verification: {str(e)}")
        return jsonify({'error': f'Failed to send verification: {str(e)}'}), 500
"""
