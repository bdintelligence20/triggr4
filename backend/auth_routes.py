import os
import jwt
import time
import logging
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import firestore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firestore DB
db = firestore.client()

# Create a Blueprint for auth routes
auth_bp = Blueprint('auth', __name__)

# JWT Secret Key (should be in environment variables in production)
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key')
JWT_EXPIRATION = 86400  # 24 hours in seconds

def generate_token(user_id, email, role):
    """Generate a JWT token for the user."""
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': int(time.time()) + JWT_EXPIRATION
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    """Verify a JWT token and return the payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    try:
        # Query Firestore for the user
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1)
        user_docs = query.stream()
        
        user_data = None
        for doc in user_docs:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            break
        
        if not user_data:
            # For demo purposes, allow a test user
            if email == 'test@example.com' and password == 'Password123!':
                token = generate_token('test-user-id', email, 'user')
                return jsonify({
                    'token': token,
                    'user': {
                        'id': 'test-user-id',
                        'email': email,
                        'fullName': 'Test User',
                        'role': 'user'
                    }
                })
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password
        if not check_password_hash(user_data.get('password_hash', ''), password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = generate_token(
            user_data['id'],
            user_data['email'],
            user_data.get('role', 'user')
        )
        
        return jsonify({
            'token': token,
            'user': {
                'id': user_data['id'],
                'email': user_data['email'],
                'fullName': user_data.get('fullName', 'User'),
                'photoUrl': user_data.get('photoUrl'),
                'role': user_data.get('role', 'user')
            }
        })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'An error occurred during login'}), 500

@auth_bp.route('/validate-token', methods=['POST'])
def validate_token():
    """Validate a JWT token."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header is required'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    try:
        # Get user data from Firestore
        user_id = payload.get('user_id')
        user_doc = db.collection('users').document(user_id).get()
        
        if not user_doc.exists:
            # For demo purposes, return basic user info from token
            return jsonify({
                'id': payload.get('user_id'),
                'email': payload.get('email'),
                'fullName': 'User',
                'role': payload.get('role', 'user')
            })
        
        user_data = user_doc.to_dict()
        return jsonify({
            'id': user_id,
            'email': user_data.get('email'),
            'fullName': user_data.get('fullName', 'User'),
            'photoUrl': user_data.get('photoUrl'),
            'role': user_data.get('role', 'user')
        })
        
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return jsonify({'error': 'An error occurred during token validation'}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP code."""
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    
    if not email or not otp:
        return jsonify({'error': 'Email and OTP are required'}), 400
    
    try:
        # Query Firestore for the OTP
        otps_ref = db.collection('otps')
        query = otps_ref.where('email', '==', email).where('code', '==', otp).limit(1)
        otp_docs = query.stream()
        
        otp_data = None
        for doc in otp_docs:
            otp_data = doc.to_dict()
            break
        
        # For demo purposes, allow a test OTP
        if not otp_data and (otp != '123456' or email != 'test@example.com'):
            return jsonify({'error': 'Invalid OTP'}), 401
        
        # Get or create user
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1)
        user_docs = query.stream()
        
        user_data = None
        user_id = None
        
        for doc in user_docs:
            user_data = doc.to_dict()
            user_id = doc.id
            break
        
        if not user_data:
            # Create a new user
            new_user = {
                'email': email,
                'fullName': email.split('@')[0].title(),
                'role': 'user',
                'createdAt': firestore.SERVER_TIMESTAMP
            }
            user_ref = users_ref.document()
            user_ref.set(new_user)
            user_id = user_ref.id
            user_data = new_user
        
        # Generate token
        token = generate_token(
            user_id,
            email,
            user_data.get('role', 'user')
        )
        
        return jsonify({
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
                'fullName': user_data.get('fullName', 'User'),
                'photoUrl': user_data.get('photoUrl'),
                'role': user_data.get('role', 'user')
            }
        })
        
    except Exception as e:
        logger.error(f"OTP verification error: {str(e)}")
        return jsonify({'error': 'An error occurred during OTP verification'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint."""
    # In a stateless JWT system, the client simply discards the token
    # For additional security, you could implement a token blacklist
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email."""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        # Check if user exists
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1)
        user_docs = query.stream()
        
        user_exists = False
        for _ in user_docs:
            user_exists = True
            break
        
        # For demo purposes, allow a test email
        if not user_exists and email != 'test@company.com':
            return jsonify({'error': 'Email not found'}), 404
        
        # Generate reset token
        reset_token = generate_token('reset', email, 'reset')
        
        # Store reset token in Firestore
        reset_ref = db.collection('password_resets').document()
        reset_ref.set({
            'email': email,
            'token': reset_token,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'expires': firestore.SERVER_TIMESTAMP + 3600  # 1 hour
        })
        
        # In a real app, send an email with the reset link
        # For demo purposes, just return success
        return jsonify({'message': 'Password reset instructions sent'})
        
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token."""
    data = request.get_json()
    token = data.get('token')
    password = data.get('password')
    
    if not token or not password:
        return jsonify({'error': 'Token and password are required'}), 400
    
    try:
        # Verify token
        payload = verify_token(token)
        if not payload or payload.get('user_id') != 'reset':
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        email = payload.get('email')
        
        # Check if token exists in Firestore
        resets_ref = db.collection('password_resets')
        query = resets_ref.where('email', '==', email).where('token', '==', token).limit(1)
        reset_docs = query.stream()
        
        reset_data = None
        reset_id = None
        
        for doc in reset_docs:
            reset_data = doc.to_dict()
            reset_id = doc.id
            break
        
        # For demo purposes, allow any valid token
        if not reset_data and email != 'test@company.com':
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Update user password
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1)
        user_docs = query.stream()
        
        user_id = None
        for doc in user_docs:
            user_id = doc.id
            break
        
        if user_id:
            # Hash the new password
            password_hash = generate_password_hash(password)
            
            # Update user document
            users_ref.document(user_id).update({
                'password_hash': password_hash,
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
        
        # Delete used reset token
        if reset_id:
            resets_ref.document(reset_id).delete()
        
        return jsonify({'message': 'Password reset successful'})
        
    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        return jsonify({'error': 'An error occurred while resetting your password'}), 500
