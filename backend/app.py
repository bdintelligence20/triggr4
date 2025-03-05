import os
import uuid
import json
import base64
import logging
from flask import Flask, request, jsonify, Response
from werkzeug.utils import secure_filename
from flask_cors import CORS
import traceback
from openai import OpenAI
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

# Twilio Credentials
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM", "+14155238886") 

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
from firebase_admin import credentials, firestore
try:
    firebase_admin.initialize_app(credentials.Certificate(firebase_cred_info))
    db = firestore.client()
    logger.info("Firebase initialized successfully")
except Exception as e:
    logger.critical(f"Firebase initialization failed: {str(e)}")
    raise

# Google Cloud Storage
from google.cloud import storage
gcs_client = storage.Client.from_service_account_info(gcs_cred_info)
bucket = gcs_client.bucket(GCS_BUCKET_NAME)

# Initialize Twilio client
try:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    logger.info("Twilio client initialized")
except Exception as e:
    logger.error(f"Twilio initialization error: {str(e)}")
    twilio_client = None


# Import text extraction and processing utilities
import PyPDF2
import docx2txt

# Import custom modules for RAG functionality
from embedding_utils import EmbeddingService, chunk_text
from pinecone_client import PineconeClient
from rag_system import RAGSystem

# Initialize RAG components
embedding_service = EmbeddingService(api_key=OPENAI_API_KEY)
pinecone_client = PineconeClient(api_key=PINECONE_API_KEY, index_name=PINECONE_INDEX_NAME)
rag_system = RAGSystem(
    openai_api_key=OPENAI_API_KEY,
    anthropic_api_key=ANTHROPIC_API_KEY,
    pinecone_api_key=PINECONE_API_KEY,
    index_name=PINECONE_INDEX_NAME
)

# -------------------------------
# Flask App Configuration
# -------------------------------
app = Flask(__name__)
CORS(app, origins=["*"], supports_credentials=True, methods=["GET", "POST", "OPTIONS", "DELETE", "PUT"])
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'txt'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# -------------------------------
# Helper Functions
# -------------------------------

def allowed_file(filename: str) -> bool:
    """Check if a file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from a PDF file."""
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            # Process up to 50 pages to avoid memory issues
            for i in range(min(50, len(reader.pages))):
                page_text = reader.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n\n"
        return text
    except Exception as e:
        logger.error(f"PDF extraction error: {str(e)}")
        raise

def extract_text_from_docx(file_path: str) -> str:
    """Extract text content from a DOCX file."""
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        logger.error(f"DOCX extraction error: {str(e)}")
        raise

def extract_text_from_file(file_path: str, file_type: str) -> str:
    """Extract text from a file based on its type."""
    if file_type == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_type == 'doc':
        return extract_text_from_docx(file_path)
    elif file_type == 'txt':
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

# -------------------------------
# Endpoints
# -------------------------------

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Basic DB check
        db.collection("system_status").document("health").set({"last_check": firestore.SERVER_TIMESTAMP})
        
        # Pinecone check
        index_stats = pinecone_client.index.describe_index_stats()
        vector_count = index_stats.get("total_vector_count", 0)
        
        return jsonify({
            "status": "healthy",
            "services": {
                "firebase": "connected",
                "pinecone": "connected",
                "vectors_count": vector_count
            }
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process a document for the knowledge base."""
    logger.info("Upload endpoint called")
    
    if 'file' not in request.files:
        logger.info("No file in request")
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    category = request.form.get('category', 'general')
    title = request.form.get('title') or file.filename

    logger.info(f"Upload request received: {title}, category: {category}")

    if file.filename == '':
        logger.info("Empty filename")
        return jsonify({"error": "Empty filename"}), 400
        
    if not allowed_file(file.filename):
        logger.info(f"Unsupported file type: {file.filename}")
        return jsonify({"error": f"Unsupported file type. Allowed types: {', '.join(app.config['ALLOWED_EXTENSIONS'])}"}), 400

    try:
        # Save file locally
        filename = secure_filename(file.filename)
        local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(local_path)
        logger.info(f"File saved to {local_path}")
        
        # Extract text based on file type
        if filename.lower().endswith('.pdf'):
            file_type = 'pdf'
            content = extract_text_from_pdf(local_path)
        elif filename.lower().endswith(('.doc', '.docx')):
            file_type = 'doc'
            content = extract_text_from_docx(local_path)
        elif filename.lower().endswith('.txt'):
            file_type = 'txt'
            with open(local_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        else:
            return jsonify({"error": "Unsupported file type"}), 400
            
        logger.info(f"Extracted {len(content)} characters from file")
        
        if not content or len(content.strip()) < 10:
            return jsonify({"error": "Could not extract meaningful content from file"}), 400

        # Save metadata and content to Firebase Firestore
        doc_data = {
            "title": title,
            "content": content,
            "category": category,
            "file_type": file_type,
            "word_count": len(content.split()),
            "created_at": firestore.SERVER_TIMESTAMP,
            "processing_status": "processing"
        }
        doc_ref = db.collection("knowledge_items").document()
        doc_ref.set(doc_data)
        item_id = doc_ref.id
        logger.info(f"Saved document to Firestore with ID: {item_id}")

        # Skip the rag_system and directly process the document ourselves
        # to diagnose any potential issues
        try:
            # Manually create chunks
            chunks = chunk_text(content)
            logger.info(f"Split text into {len(chunks)} chunks")
            
            # Generate embeddings directly
            embeddings = []
            batch_size = 5
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                logger.info(f"Generating embeddings for batch {i//batch_size + 1}")
                response = client.embeddings.create(
                    model="text-embedding-3-large",
                    input=batch
                )
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)
                logger.info(f"Generated embeddings for batch {i//batch_size + 1}")
            
            # Create vectors
            vectors = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"{item_id}_{i}"
                metadata = {
                    "text": chunk,
                    "item_id": item_id,
                    "chunk_index": i,
                    "category": category
                }
                vectors.append((vector_id, embedding, metadata))
            
            # Store vectors directly in Pinecone
            batch_size = 10
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i+batch_size]
                logger.info(f"Upserting batch {i//batch_size + 1} to Pinecone")
                
                # Direct Pinecone upsert with retries
                for attempt in range(3):
                    try:
                        pinecone_client.index.upsert(
                            vectors=batch,
                            namespace="global_knowledge_base"
                        )
                        logger.info(f"Successfully upserted batch {i//batch_size + 1}")
                        break
                    except Exception as e:
                        logger.error(f"Pinecone upsert error (attempt {attempt+1}): {str(e)}")
                        if attempt == 2:  # Last attempt
                            raise
                        import time
                        time.sleep(1)  # Wait before retrying
            
            # Update status
            doc_ref.update({
                "processing_status": "completed",
                "vectors_stored": len(vectors)
            })
            
            logger.info(f"Successfully processed document {item_id}: {len(vectors)} vectors stored")
            
        except Exception as e:
            logger.error(f"Document processing error: {str(e)}", exc_info=True)
            doc_ref.update({
                "processing_status": "failed",
                "error": str(e)
            })
            # Don't re-raise, still return success for the upload

        # Clean up temporary file
        os.remove(local_path)

        return jsonify({
            "message": "File uploaded and processing started",
            "item_id": item_id,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        # Clean up if needed
        if 'local_path' in locals() and os.path.exists(local_path):
            os.remove(local_path)
        return jsonify({"error": f"Failed to process document: {str(e)}"}), 500

@app.route('/query', methods=['POST'])
def query():
    """Query the knowledge base using RAG with streaming support."""
    data = request.get_json()
    query_text = data.get("query")
    category = data.get("category")
    stream_enabled = data.get("stream", False)  # New parameter to enable streaming
    
    logger.info(f"Query received: '{query_text}', category: '{category}', stream: {stream_enabled}")
    
    if not query_text or not isinstance(query_text, str) or len(query_text.strip()) < 2:
        return jsonify({"error": "Invalid or empty query"}), 400

    try:
        # Log query for analytics
        db.collection("queries").add({
            "query": query_text,
            "category": category,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "client_ip": request.remote_addr,
            "stream_enabled": stream_enabled
        })
        
        if not stream_enabled:
            # Standard non-streaming response
            result = rag_system.query(
                query_text, 
                namespace="global_knowledge_base",
                top_k=5,
            )
            
            # Return response with sources
            return jsonify({
                "response": result["answer"],
                "sources": result["sources"],
                "streaming": False
            })
        else:
            # Set up streaming response using the RAG system
            def generate():
                # Send proper SSE headers
                yield "Content-Type: text/event-stream\n"
                yield "Cache-Control: no-cache\n"
                yield "Connection: keep-alive\n\n"
                
                # Create a callback to forward chunks to client
                def stream_callback(chunk):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                # Process query with streaming using RAG system
                result = rag_system.query(
                    query_text, 
                    namespace="global_knowledge_base",
                    top_k=5,
                    stream_callback=stream_callback
                )
                
                # Send sources at the end
                yield f"data: {json.dumps({'sources': result['sources']})}\n\n"
                
                # Signal completion
                yield f"data: {json.dumps({'done': True})}\n\n"
            
            return Response(generate(), mimetype="text/event-stream")
        
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to process query: {str(e)}"}), 500

@app.route('/documents', methods=['GET'])
def list_documents():
    """List all documents in the knowledge base."""
    try:
        category = request.args.get('category')
        limit = min(int(request.args.get('limit', 100)), 500)  # Cap at 500
        
        # Build query
        query = db.collection("knowledge_items")
        if category:
            query = query.where("category", "==", category)
        
        # Execute query
        docs = query.limit(limit).stream()
        
        # Format results
        results = []
        for doc in docs:
            doc_data = doc.to_dict()
            results.append({
                "id": doc.id,
                "title": doc_data.get("title", "Untitled"),
                "category": doc_data.get("category", "general"),
                "file_type": doc_data.get("file_type", "unknown"),
                "created_at": doc_data.get("created_at", None),
                "processing_status": doc_data.get("processing_status", "unknown"),
                "vectors_stored": doc_data.get("vectors_stored", 0),
                "word_count": doc_data.get("word_count", 0),
                "file_url": doc_data.get("file_url", None)
            })
        
        return jsonify({
            "documents": results,
            "count": len(results)
        })
        
    except Exception as e:
        logger.error(f"Document listing error: {str(e)}")
        return jsonify({"error": f"Failed to list documents: {str(e)}"}), 500

@app.route('/delete/<item_id>', methods=['DELETE'])
def delete_document(item_id):
    """Delete a document and its vectors from the knowledge base.
    Compatible with Pinecone Starter/Serverless plans that don't support filter-based deletion."""
    try:
        import time  # Add this import
        
        # Get the document
        doc_ref = db.collection("knowledge_items").document(item_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Document not found"}), 404
            
        doc_data = doc.to_dict()
        
        # First collect all vector IDs for this document
        vector_ids = []
        
        # Calculate how many chunks to expect based on uploaded vectors
        expected_chunks = doc_data.get("vectors_stored", 0)
        
        # Generate the pattern of vector IDs
        for i in range(max(100, expected_chunks * 2)):  # Search for more than we expect to be safe
            vector_ids.append(f"{item_id}_{i}")
        
        logger.info(f"Attempting to delete up to {len(vector_ids)} vectors for document {item_id}")
        
        # Delete in batches to avoid hitting limits
        batch_size = 100
        vectors_deleted = 0
        
        for i in range(0, len(vector_ids), batch_size):
            batch = vector_ids[i:i+batch_size]
            try:
                result = pinecone_client.index.delete(
                    ids=batch,
                    namespace="global_knowledge_base"
                )
                vectors_deleted += len(batch)
                logger.info(f"Deleted batch of {len(batch)} vectors for document {item_id}")
                
                # Small delay to avoid rate limits
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Failed to delete batch of vectors: {str(e)}")
        
        # Delete from GCS if URL exists
        if 'file_url' in doc_data:
            try:
                file_path = doc_data['file_url'].split('/')[-1]
                blob = bucket.blob(f"documents/{file_path}")
                blob.delete()
                logger.info(f"Deleted file from GCS: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete file from GCS: {str(e)}")
        
        # Delete from Firestore
        doc_ref.delete()
        
        # Return success response
        return jsonify({
            "message": "Document deleted successfully",
            "document_id": item_id,
            "vectors_attempted": len(vector_ids),
            "file_deleted": 'file_url' in doc_data
        })
        
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to delete document: {str(e)}"}), 500

@app.route('/whatsapp-webhook', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages with simplified message flow."""
    try:
        # Get the incoming message
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        
        logger.info(f"WhatsApp message received from {from_number}: {incoming_msg}")
        
        # Skip empty messages
        if not incoming_msg:
            return create_twilio_response("I couldn't understand your message. Please try again.")
        
        # Create a unique ID for this conversation
        conversation_id = str(uuid.uuid4())
        
        # Log the conversation in Firestore
        db.collection("whatsapp_conversations").document(conversation_id).set({
            "from": from_number,
            "message": incoming_msg,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "status": "received"
        })
        
        # Send initial acknowledgment message
        send_whatsapp_message(from_number, "⏳ I'm searching through our knowledge base...")
        
        try:
            # Get query embedding and search for relevant documents
            query_embedding = embedding_service.get_embedding(incoming_msg)
            matched_docs = pinecone_client.query_vectors(
                query_embedding, 
                namespace="global_knowledge_base",
                top_k=5
                
            )
            
            if not matched_docs:
                logger.info("No relevant documents found for WhatsApp query")
                return send_whatsapp_message(
                    from_number, 
                    "📚 I couldn't find any relevant information in our knowledge base. Please try asking a different question."
                )
            
            # Send intermediate message
            send_whatsapp_message(from_number, "🔍 Found relevant information! Preparing your answer...")
            
            # Prepare context from matched documents
            context_text = "\n\n---\n\n".join([doc['text'] for doc in matched_docs])
            
            # Collect the full response
            accumulated_text = []
            
            def stream_callback(chunk):
                accumulated_text.append(chunk)
            
            # Generate response with streaming (to accumulate the text)
            rag_system.generate_streaming_response(context_text, incoming_msg, stream_callback)
            
            # Get the full response
            full_text = ''.join(accumulated_text)
            
            # Send the complete answer
            if full_text:
                send_whatsapp_message(from_number, f"📋 {full_text}")
            else:
                send_whatsapp_message(from_number, "❓ I couldn't generate a clear answer from the information I found.")
            
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
                "sources": [doc.get('source_id', 'unknown') for doc in matched_docs]
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

def create_twilio_response(message):
    """Create a TwiML response with the given message."""
    resp = MessagingResponse()
    if message:
        resp.message(message)
    return str(resp)

def send_whatsapp_message(to_number, message_body):
    """Send a WhatsApp message using Twilio client."""
    try:
        # Check if Twilio client is initialized
        if not twilio_client:
            logger.error("Twilio client not initialized")
            return create_twilio_response(message_body)
        
        # Make sure the to_number has WhatsApp prefix if it doesn't already
        if not to_number.startswith('whatsapp:'):
            to_number = f"whatsapp:{to_number}"
        
        # Format the WhatsApp from number correctly - DON'T add prefix if it already has one
        from_number = TWILIO_WHATSAPP_FROM
        if not from_number.startswith('whatsapp:'):
            from_number = f"whatsapp:{from_number}"
            
        logger.info(f"Sending WhatsApp from {from_number} to {to_number}")
            
        # Send message
        message = twilio_client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        
        logger.info(f"Sent WhatsApp message, SID: {message.sid}")
        return create_twilio_response("")  # Empty response as we sent directly
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        # Fall back to TwiML response
        return create_twilio_response(message_body)

@app.route('/test-pinecone', methods=['GET'])
def test_pinecone():
    """Test endpoint to verify Pinecone connectivity."""
    try:
        # Get index stats
        stats = pinecone_client.index.describe_index_stats()
        
        # Create a test vector
        test_vector_id = f"test_{int(time.time())}"
        test_embedding = [0.1] * 1536  # Create a dummy vector 
        test_metadata = {"test": True, "timestamp": time.time()}
        
        # Try to upsert
        pinecone_client.index.upsert(
            vectors=[(test_vector_id, test_embedding, test_metadata)],
            namespace="test_namespace"
        )
        
        # Try to query it back
        query_result = pinecone_client.index.query(
            vector=test_embedding,
            top_k=1,
            include_metadata=True,
            namespace="test_namespace",
            filter={"test": True}
        )
        
        # Clean up test vector
        pinecone_client.index.delete(ids=[test_vector_id], namespace="test_namespace")
        
        return jsonify({
            "status": "success",
            "index_stats": stats,
            "test_query_result": query_result,
            "message": "Pinecone connection is working properly"
        })
    except Exception as e:
        logger.error(f"Pinecone test failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Pinecone test failed: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Use Gunicorn for production - this is for local development only
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))