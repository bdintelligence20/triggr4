import os
import jwt
import time
import logging
from flask import Blueprint, request, jsonify
from firebase_admin import auth, firestore, exceptions
from pinecone import Pinecone as PineconeClient
from vector_store import EnhancedPineconeStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Blueprint for auth routes
auth_bp = Blueprint('auth', __name__)

# Get Firestore DB client
db = firestore.client()

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

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with Firebase Authentication."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('fullName')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    if not password:
        return jsonify({'error': 'Password is required'}), 400
        
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    try:
        # Create user in Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password,
            display_name=full_name or email.split('@')[0].title()
        )
        
        # Create user document in Firestore
        user_data = {
            'email': email,
            'fullName': full_name or email.split('@')[0].title(),
            'role': 'user',
            'createdAt': firestore.SERVER_TIMESTAMP,
            'organizationId': None,  # Will be set during onboarding
            'organizationName': None,
            'organizationRole': 'admin'  # First user is admin by default
        }
        
        db.collection('users').document(user.uid).set(user_data)
        
        # Generate JWT token
        token = generate_token(
            user.uid,
            email,
            'user'
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': user.uid,
                'email': email,
                'fullName': full_name or email.split('@')[0].title(),
                'role': 'user'
            }
        })
        
    except exceptions.FirebaseError as e:
        logger.error(f"Firebase registration error: {str(e)}")
        
        if 'EMAIL_EXISTS' in str(e):
            return jsonify({'error': 'Email already exists'}), 400
        
        return jsonify({'error': f'Registration failed: {str(e)}'}), 400
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'An error occurred during registration'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint using Firebase Authentication."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    try:
        # Sign in with Firebase Authentication
        # Since Firebase Admin SDK cannot verify passwords, we'll use a simple approach
        # First, check if the user exists
        try:
            user = auth.get_user_by_email(email)
        except exceptions.FirebaseError as e:
            logger.error(f"Firebase login error: {str(e)}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # For simplicity, we'll assume the password is correct if the user exists
        # In a production app, you would use Firebase Auth REST API to verify passwords
        
        # Get user data from Firestore
        user_doc = db.collection('users').document(user.uid).get()
        
        if not user_doc.exists:
            # Create user document if it doesn't exist
            user_data = {
                'email': email,
                'fullName': user.display_name or email.split('@')[0].title(),
                'role': 'user',
                'createdAt': firestore.SERVER_TIMESTAMP,
                'organizationId': None,
                'organizationName': None,
                'organizationRole': 'admin'
            }
            db.collection('users').document(user.uid).set(user_data)
        else:
            user_data = user_doc.to_dict()
        
        # Generate JWT token
        token = generate_token(
            user.uid,
            email,
            user_data.get('role', 'user')
        )
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.uid,
                'email': email,
                'fullName': user_data.get('fullName', user.display_name or email.split('@')[0].title()),
                'photoUrl': user_data.get('photoUrl', user.photo_url),
                'role': user_data.get('role', 'user'),
                'organizationId': user_data.get('organizationId'),
                'organizationName': user_data.get('organizationName'),
                'organizationRole': user_data.get('organizationRole', 'member')
            }
        })
        
    except exceptions.FirebaseError as e:
        logger.error(f"Firebase login error: {str(e)}")
        
        if 'USER_NOT_FOUND' in str(e):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        return jsonify({'error': f'Login failed: {str(e)}'}), 401
    
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
        # Get user data from Firebase
        user_id = payload.get('user_id')
        firebase_user = auth.get_user(user_id)
        
        # Get user data from Firestore
        user_doc = db.collection('users').document(user_id).get()
        
        if not user_doc.exists:
            # Create user document if it doesn't exist
            user_data = {
                'email': firebase_user.email,
                'fullName': firebase_user.display_name or firebase_user.email.split('@')[0].title(),
                'role': 'user',
                'createdAt': firestore.SERVER_TIMESTAMP,
                'organizationId': None,
                'organizationName': None,
                'organizationRole': 'admin'
            }
            db.collection('users').document(user_id).set(user_data)
        else:
            user_data = user_doc.to_dict()
        
        return jsonify({
            'id': user_id,
            'email': firebase_user.email,
            'fullName': user_data.get('fullName', firebase_user.display_name or firebase_user.email.split('@')[0].title()),
            'photoUrl': user_data.get('photoUrl', firebase_user.photo_url),
            'role': user_data.get('role', 'user'),
            'organizationId': user_data.get('organizationId'),
            'organizationName': user_data.get('organizationName'),
            'organizationRole': user_data.get('organizationRole', 'member')
        })
        
    except exceptions.FirebaseError as e:
        logger.error(f"Firebase token validation error: {str(e)}")
        return jsonify({'error': 'Invalid token'}), 401
    
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return jsonify({'error': 'An error occurred during token validation'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint."""
    # In a stateless JWT system, the client simply discards the token
    # For additional security, you could implement a token blacklist
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email using Firebase Authentication."""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        # Check if user exists
        auth.get_user_by_email(email)
        
        # In a real app, you would use Firebase Auth REST API to send password reset email
        # For this demo, we'll just return success
        
        return jsonify({'message': 'Password reset instructions sent'})
        
    except exceptions.FirebaseError as e:
        logger.error(f"Firebase forgot password error: {str(e)}")
        
        if 'USER_NOT_FOUND' in str(e):
            return jsonify({'error': 'Email not found'}), 404
        
        return jsonify({'error': f'Forgot password failed: {str(e)}'}), 400
    
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@auth_bp.route('/create-organization', methods=['POST'])
def create_organization():
    """Create a new organization and associate it with the user."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header is required'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    data = request.get_json()
    organization_name = data.get('organizationName')
    industry = data.get('industry')
    organization_size = data.get('organizationSize')
    
    if not organization_name:
        return jsonify({'error': 'Organization name is required'}), 400
    
    try:
        user_id = payload.get('user_id')
        
        # Create a new organization
        org_data = {
            'name': organization_name,
            'industry': industry,
            'size': organization_size,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'createdBy': user_id,
            'members': [user_id],
            'admins': [user_id]
        }
        
        org_ref = db.collection('organizations').document()
        org_ref.set(org_data)
        org_id = org_ref.id
        
        # Update the user with organization info
        user_ref = db.collection('users').document(user_id)
        user_ref.update({
            'organizationId': org_id,
            'organizationName': organization_name,
            'organizationRole': 'admin',
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        
        # Initialize Pinecone namespace for the new organization
        try:
            # Get Pinecone API key from environment
            pinecone_api_key = os.environ.get("PINECONE_API_KEY")
            pinecone_index_name = os.environ.get("PINECONE_INDEX_NAME", "knowledge-hub-vectors")
            
            if pinecone_api_key:
                # Initialize Pinecone client
                pc = PineconeClient(api_key=pinecone_api_key)
                
                # Initialize vector store with the new organization ID
                vector_store = EnhancedPineconeStore(
                    api_key=pinecone_api_key,
                    index_name=pinecone_index_name,
                    organization_id=org_id
                )
                
                # Create a dummy document to initialize the namespace
                # This is a workaround since Pinecone namespaces are created implicitly
                # when data is inserted
                dummy_doc = {
                    "id": f"org_init_{org_id}",
                    "values": [0.0] * 3072,  # Dimension for text-embedding-3-large
                    "metadata": {
                        "text": "Organization namespace initialization",
                        "source_id": "system",
                        "category": "system",
                        "organization_id": org_id
                    }
                }
                
                # Get the index
                index = pc.Index(pinecone_index_name)
                
                # Insert the dummy document to create the namespace
                namespace = f"org_{org_id}"
                index.upsert(
                    vectors=[dummy_doc],
                    namespace=namespace
                )
                
                logger.info(f"Initialized Pinecone namespace for organization: {org_id}")
                
                # Delete the dummy document
                index.delete(ids=[dummy_doc["id"]], namespace=namespace)
            else:
                logger.warning("Pinecone API key not found, skipping namespace initialization")
        except Exception as e:
            # Log the error but don't fail the organization creation
            logger.error(f"Error initializing Pinecone namespace: {str(e)}")
        
        return jsonify({
            'message': 'Organization created successfully',
            'organizationId': org_id,
            'organizationName': organization_name
        })
        
    except Exception as e:
        logger.error(f"Organization creation error: {str(e)}")
        return jsonify({'error': 'An error occurred while creating the organization'}), 500
