import os
import logging
import nltk
from flask import Flask, request
from flask_cors import CORS
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import base64
import json
import utils

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Download NLTK data
nltk.download('punkt', quiet=True)

# -------------------------------
# Load External Service Credentials from Environment Variables
# -------------------------------

# API Keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "knowledge-hub-vectors"

# Firebase credentials
firebase_cred_b64 = os.environ.get("FIREBASE_CRED_B64")
gcs_cred_b64 = os.environ.get("GCS_CRED_B64")
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "knowledge-hub-files")

# Twilio Credentials (Legacy)
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM", "+15055787929") 

# WATI Credentials
WATI_API_URL = os.environ.get("WATI_API_URL")
WATI_API_TOKEN = os.environ.get("WATI_API_TOKEN")
WATI_WHATSAPP_NUMBER = os.environ.get("WATI_WHATSAPP_NUMBER", "15557107684")

# Validate required environment variables
if not (OPENAI_API_KEY and ANTHROPIC_API_KEY and PINECONE_API_KEY and 
        firebase_cred_b64 and gcs_cred_b64):
    logger.critical("Missing required environment variables")
    missing = []
    if not OPENAI_API_KEY: missing.append("OPENAI_API_KEY")
    if not ANTHROPIC_API_KEY: missing.append("ANTHROPIC_API_KEY") 
    if not PINECONE_API_KEY: missing.append("PINECONE_API_KEY")
    if not firebase_cred_b64: missing.append("FIREBASE_CRED_B64")
    if not gcs_cred_b64: missing.append("GCS_CRED_B64")
    logger.critical(f"Missing: {', '.join(missing)}")
    raise EnvironmentError("Missing required environment variables")

# Decode Base64 credentials
try:
    firebase_cred_json_str = base64.b64decode(firebase_cred_b64).decode("utf-8")
    gcs_cred_json_str = base64.b64decode(gcs_cred_b64).decode("utf-8")
    firebase_cred_info = json.loads(firebase_cred_json_str)
    gcs_cred_info = json.loads(gcs_cred_json_str)
except Exception as e:
    logger.critical(f"Failed to decode credentials: {str(e)}")
    raise

# -------------------------------
# Initialize External Services
# -------------------------------

# Firebase Admin
import firebase_admin
from firebase_admin import credentials
try:
    firebase_admin.initialize_app(credentials.Certificate(firebase_cred_info))
    logger.info("Firebase initialized successfully")
except Exception as e:
    logger.critical(f"Firebase initialization failed: {str(e)}")
    raise

# Google Cloud Storage
from google.cloud import storage
gcs_client = storage.Client.from_service_account_info(gcs_cred_info)
bucket = gcs_client.bucket(GCS_BUCKET_NAME)

# -------------------------------
# Flask App Configuration
# -------------------------------
def create_app():
    app = Flask(__name__)
    
    # Initialize CORS
    CORS(app, origins=["*"], supports_credentials=True, methods=["GET", "POST", "OPTIONS", "DELETE", "PUT"])
    
    # Initialize Compress for response compression
    compress = Compress()
    compress.init_app(app)
    
    # Define a custom key function for organization-aware rate limiting
    def get_tenant_limit_key():
        # For webhook routes, use IP address only
        if request.path.endswith('/wati-webhook') or request.path.endswith('/webhook'):
            return get_remote_address()
            
        # For all other routes, try to get organization ID
        organization_id = utils.get_user_organization_id()
        # Fallback to IP address if organization ID is not available
        if not organization_id:
            return get_remote_address()
        # Combine organization ID with IP for more granular control
        return f"{organization_id}:{request.remote_addr}"
    
    # Initialize rate limiter with organization-aware key function
    limiter = Limiter(
        key_func=get_tenant_limit_key,
        app=app,
        default_limits=["300 per day", "60 per hour"],
        storage_uri="memory://",
    )
    
    # Exempt webhook routes from rate limiting
    limiter.exempt(lambda: request.path.endswith('/wati-webhook') or request.path.endswith('/webhook'))
    
    # Configure file uploads
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'txt'}
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Configure timeouts for external API calls
    app.config['EXTERNAL_API_TIMEOUT'] = 30  # 30 seconds timeout for external API calls

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.document_routes import document_bp
    from routes.query_routes import query_bp
    from routes.whatsapp_routes import whatsapp_bp
    from routes.utility_routes import utility_bp
    from routes.member_routes import member_bp
    from routes.mcp_routes import mcp_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(document_bp)
    app.register_blueprint(query_bp)
    app.register_blueprint(whatsapp_bp)
    app.register_blueprint(utility_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(mcp_bp)

    return app

app = create_app()

if __name__ == '__main__':
    # Use Gunicorn for production - this is for local development only
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
