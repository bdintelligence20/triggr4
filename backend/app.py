import os
import uuid
import json
import base64
import logging
from typing import List, Dict, Any, Tuple, Optional
from functools import lru_cache
from flask import Flask, request, jsonify, Response
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import asyncio
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------------------------------
# Load External Service Credentials from Environment Variables
# -------------------------------

# Twilio Credentials
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM")

# Pinecone Credentials
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "knowledge-hub-vectors"

# AI Model Keys
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Firebase and Google Cloud Storage credentials
firebase_cred_b64 = os.environ.get("FIREBASE_CRED_B64")
gcs_cred_b64 = os.environ.get("GCS_CRED_B64")
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "knowledge-hub-files")

# Environment check
required_env_vars = [
    "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_FROM",
    "PINECONE_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY",
    "FIREBASE_CRED_B64", "GCS_CRED_B64"
]

missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
    logger.critical(error_msg)
    raise EnvironmentError(error_msg)

try:
    # Decode Base64 credentials
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

# Pinecone
from pinecone import Pinecone
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    logger.info(f"Connected to Pinecone index: {PINECONE_INDEX_NAME}")
except Exception as e:
    logger.critical(f"Pinecone initialization failed: {str(e)}")
    raise

# Twilio Client
from twilio.rest import Client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Google Cloud Storage
from google.cloud import storage
gcs_client = storage.Client.from_service_account_info(gcs_cred_info)
bucket = gcs_client.bucket(GCS_BUCKET_NAME)

# OpenAI
import openai
openai.api_key = OPENAI_API_KEY

# Anthropic
import anthropic
anthropic_client = anthropic.Client(api_key=ANTHROPIC_API_KEY)

# Libraries for text extraction
import PyPDF2
import docx2txt

# -------------------------------
# Flask App Configuration
# -------------------------------
app = Flask(__name__)
CORS(app, origins=["https://triggr4.onrender.com"])

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'txt'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# -------------------------------
# Helper Functions
# -------------------------------

def allowed_file(filename: str) -> bool:
    """Check if a file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from a PDF file."""
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
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
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Chunk text with overlap for better context preservation."""
    if not text:
        return []
        
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        # If we're not at the end, try to find a good break point
        if end < text_length:
            # Try to break at sentence or paragraph
            for break_char in ['\n\n', '\n', '. ', '? ', '! ']:
                last_break = text.rfind(break_char, start, end)
                if last_break != -1:
                    end = last_break + len(break_char)
                    break
        
        chunks.append(text[start:end])
        start = end - overlap  # Create overlap with previous chunk
    
    return chunks

@lru_cache(maxsize=128)
def get_embedding_cached(text: str) -> List[float]:
    """Get embedding for a single text with caching."""
    response = openai.Embedding.create(input=[text], model="text-embedding-ada-002")
    return response['data'][0]['embedding']

async def get_embeddings_async(chunks: List[str]) -> List[List[float]]:
    """Get embeddings for multiple chunks asynchronously."""
    embeddings = []
    
    # Process in batches to avoid rate limits
    batch_size = 20
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        try:
            response = openai.Embedding.create(input=batch, model="text-embedding-ada-002")
            batch_embeddings = [data['embedding'] for data in response['data']]
            embeddings.extend(batch_embeddings)
            # Small delay to avoid rate limits
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Error getting embeddings batch {i}-{i+batch_size}: {str(e)}")
            raise
    
    return embeddings

def call_claude_rag(context: List[Dict[str, Any]], question: str) -> str:
    """
    Enhanced RAG with structured context and source attribution.
    
    Args:
        context: List of context chunks with metadata
        question: User's question
    
    Returns:
        Formatted response from Claude
    """
    # Format context with metadata for better traceability
    formatted_context = []
    for i, item in enumerate(context):
        meta = item.get('metadata', {})
        title = meta.get('title', 'Unknown')
        content = item.get('content', '')
        formatted_context.append(f"[{i+1}] {title}\n{content}\n")
    
    context_text = "\n---\n".join(formatted_context)
    
    template = """
You are a helpful AI assistant tasked with answering questions based on provided context. 
Your goal is to provide accurate and relevant answers using only the information given to you.

First, carefully read and analyze the following context from our knowledge base:

<context>
{{CONTEXT}}
</context>

Now, answer this question using only the information in the context above:

<question>
{{QUESTION}}
</question>

Guidelines:
1. Only use information from the provided context.
2. If the context doesn't contain enough information to answer fully, say so clearly.
3. Cite your sources using the number format [1], [2], etc. from the context.
4. Provide a concise, accurate answer without adding information beyond what's in the context.
5. If appropriate, note which parts of the context were most helpful.

Format your response as follows:
<answer>
Your clear, concise answer with source citations where appropriate.
</answer>

<explanation>
A brief explanation of how you arrived at your answer, referencing specific parts of the context.
</explanation>
    """
    
    prompt_text = template.replace("{{CONTEXT}}", context_text).replace("{{QUESTION}}", question)
    
    try:
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens_to_sample=8192,
            temperature=0.7,  # Slightly reduced temperature for more consistent responses
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text,
                        }
                    ]
                }
            ]
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Claude API error: {str(e)}")
        raise

async def retrieve_context_for_query(query_text: str, category: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
    """Retrieve relevant context for a query."""
    # Get embedding for the query
    query_embedding = get_embedding_cached(query_text)
    
    # Build filter for category if provided
    filter_query = {"category": category} if category else None
    
    # Query the vector database
    query_response = index.query(vector=query_embedding, top_k=top_k, filter=filter_query, include_metadata=True)
    matches = query_response.get('matches', [])
    
    # Enhance context with actual content from Firestore
    enhanced_context = []
    for match in matches:
        meta = match.get('metadata', {})
        item_id = meta.get('item_id')
        chunk_index = meta.get('chunk_index')
        
        # Skip if missing essential metadata
        if not (item_id and chunk_index is not None):
            continue
            
        # Get the document from Firestore
        try:
            doc = db.collection("knowledge_items").document(item_id).get()
            if doc.exists:
                doc_data = doc.to_dict()
                content = doc_data.get('content', '')
                
                # Get the specific chunk from the content
                chunks = chunk_text(content)
                if 0 <= chunk_index < len(chunks):
                    chunk_content = chunks[chunk_index]
                    
                    enhanced_context.append({
                        'metadata': meta,
                        'content': chunk_content,
                        'score': match.get('score', 0)
                    })
        except Exception as e:
            logger.warning(f"Error retrieving document {item_id}: {str(e)}")
            continue
    
    return enhanced_context

# -------------------------------
# Endpoints
# -------------------------------

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Basic DB check
        db.collection("system_status").document("health").set({"last_check": firestore.SERVER_TIMESTAMP})
        
        # Simplified Pinecone check - just verify connection
        pc.describe_index(PINECONE_INDEX_NAME)
        
        return jsonify({
            "status": "healthy",
            "services": {
                "firebase": "connected",
                "pinecone": "connected",
            }
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/upload', methods=['POST'])
@limiter.limit("10 per minute")
async def upload_document():
    """Upload and process a document for the knowledge base."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    category = request.form.get('category', 'general')
    title = request.form.get('title') or file.filename

    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"error": f"Unsupported file type. Allowed types: {', '.join(app.config['ALLOWED_EXTENSIONS'])}"}), 400

    try:
        # Save file locally
        filename = secure_filename(file.filename)
        local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(local_path)
        
        # Determine file type and extract text
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
            
        if not content or len(content.strip()) < 10:
            return jsonify({"error": "Could not extract meaningful content from file"}), 400

        # Upload file to Google Cloud Storage
        gcs_filename = f"documents/{uuid.uuid4()}_{filename}"
        blob = bucket.blob(gcs_filename)
        blob.upload_from_filename(local_path)
        file_url = blob.public_url

        # Save metadata and content to Firebase Firestore
        doc_data = {
            "title": title,
            "content": content,
            "category": category,
            "file_type": file_type,
            "file_url": file_url,
            "word_count": len(content.split()),
            "created_at": firestore.SERVER_TIMESTAMP
        }
        doc_ref = db.collection("knowledge_items").document()
        doc_ref.set(doc_data)
        item_id = doc_ref.id

        # Partition content and compute embeddings
        chunks = chunk_text(content, chunk_size=500, overlap=50)
        if not chunks:
            return jsonify({"error": "No content to process for embeddings"}), 400

        # Get embeddings async
        embeddings = await get_embeddings_async(chunks)

        # Prepare vectors for Pinecone
        vectors = []
        for idx, embedding in enumerate(embeddings):
            vector_id = f"{item_id}_{idx}"
            metadata = {
                "item_id": item_id,
                "chunk_index": idx,
                "category": category,
                "title": title,
                "file_type": file_type
            }
            vectors.append((vector_id, embedding, metadata))
            
        # Upload vectors in batches to avoid timeouts
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            index.upsert(vectors=batch)

        # Clean up temporary file
        os.remove(local_path)

        return jsonify({
            "message": "File uploaded and processed successfully",
            "item_id": item_id,
            "file_url": file_url,
            "chunks_processed": len(chunks)
        })
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        # Clean up if needed
        if os.path.exists(local_path):
            os.remove(local_path)
        return jsonify({"error": "Failed to process document", "details": str(e)}), 500

@app.route('/query', methods=['POST'])
@limiter.limit("30 per minute")
async def query():
    """Query the knowledge base using RAG."""
    data = request.get_json()
    query_text = data.get("query")
    category = data.get("category")
    
    if not query_text or not isinstance(query_text, str) or len(query_text.strip()) < 2:
        return jsonify({"error": "Invalid or empty query"}), 400

    try:
        # Log query for analytics
        db.collection("queries").add({
            "query": query_text,
            "category": category,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "client_ip": request.remote_addr
        })
        
        # Retrieve context
        context = await retrieve_context_for_query(query_text, category)
        
        if not context:
            return jsonify({
                "response": "I couldn't find any relevant information in our knowledge base.",
                "retrieved": []
            })
        
        # Call Claude with the enhanced context
        ai_response = call_claude_rag(context, query_text)
        
        # Return simplified context metadata for frontend
        simplified_context = []
        for item in context:
            meta = item.get('metadata', {})
            simplified_context.append({
                "title": meta.get('title', 'Unknown'),
                "category": meta.get('category', 'general'),
                "score": item.get('score', 0)
            })
        
        return jsonify({
            "response": ai_response,
            "retrieved": simplified_context
        })
        
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        return jsonify({"error": "Failed to process query", "details": str(e)}), 500

@app.route('/whatsapp-webhook', methods=['POST'])
async def whatsapp_webhook():
    """Handle incoming WhatsApp messages."""
    from twilio.twiml.messaging_response import MessagingResponse
    
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    category = request.values.get('ProfileName', 'default')  # Using ProfileName as category fallback
    
    if not incoming_msg:
        resp = MessagingResponse()
        resp.message("I couldn't understand your message. Please try again.")
        return str(resp)
    
    try:
        # Log the incoming message
        db.collection("whatsapp_conversations").add({
            "from": from_number,
            "message": incoming_msg,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "status": "received"
        })
        
        # Get context for the query
        context = await retrieve_context_for_query(incoming_msg, None)  # No category filter for WhatsApp
        
        if not context:
            ai_response = "I don't have enough information to answer that question. Please try another question or contact support."
        else:
            # Call Claude with the context
            ai_response = call_claude_rag(context, incoming_msg)
        
        # Log the response
        conversation_data = {
            "from": from_number,
            "message": incoming_msg,
            "response": ai_response,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "status": "responded"
        }
        db.collection("whatsapp_conversations").add(conversation_data)
        
        # Send response via Twilio
        resp = MessagingResponse()
        msg = resp.message()
        msg.body(ai_response[:1600])  # WhatsApp message limit
        
        # If response is too long, send a second message
        if len(ai_response) > 1600:
            twilio_client.messages.create(
                body="(Continued) " + ai_response[1600:],
                from_=TWILIO_WHATSAPP_FROM,
                to=from_number
            )
        
        return str(resp)
        
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {str(e)}")
        # Provide a friendly error message
        resp = MessagingResponse()
        resp.message("I'm sorry, I encountered an error processing your request. Please try again later.")
        return str(resp)

@app.route('/delete/<item_id>', methods=['DELETE'])
def delete_document(item_id):
    """Delete a document and its vectors from the knowledge base."""
    try:
        # Get the document
        doc_ref = db.collection("knowledge_items").document(item_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Document not found"}), 404
            
        doc_data = doc.to_dict()
        
        # Delete from Pinecone
        # First, get all vector IDs associated with this document
        vector_ids = []
        prefix = f"{item_id}_"
        
        # We don't have a direct way to query by prefix in Pinecone, so we'll delete them all at once
        index.delete(filter={"item_id": item_id})
        
        # Delete from GCS if URL exists
        if 'file_url' in doc_data:
            try:
                filename = doc_data['file_url'].split('/')[-1]
                blob = bucket.blob(f"documents/{filename}")
                blob.delete()
            except Exception as e:
                logger.warning(f"Failed to delete file from GCS: {str(e)}")
        
        # Delete from Firestore
        doc_ref.delete()
        
        return jsonify({"message": "Document deleted successfully"})
        
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        return jsonify({"error": "Failed to delete document", "details": str(e)}), 500

@app.route('/categories', methods=['GET'])
def list_categories():
    """List all available categories in the knowledge base."""
    try:
        # Query Firestore for unique categories
        docs = db.collection("knowledge_items").stream()
        categories = set()
        
        for doc in docs:
            doc_data = doc.to_dict()
            if 'category' in doc_data and doc_data['category']:
                categories.add(doc_data['category'])
        
        return jsonify({
            "categories": sorted(list(categories))
        })
        
    except Exception as e:
        logger.error(f"Category listing error: {str(e)}")
        return jsonify({"error": "Failed to list categories", "details": str(e)}), 500

@app.route('/documents', methods=['GET'])
def list_documents():
    """List documents in the knowledge base with optional filtering."""
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
                "word_count": doc_data.get("word_count", 0),
                "file_url": doc_data.get("file_url", None)
            })
        
        return jsonify({
            "documents": results,
            "count": len(results)
        })
        
    except Exception as e:
        logger.error(f"Document listing error: {str(e)}")
        return jsonify({"error": "Failed to list documents", "details": str(e)}), 500

if __name__ == '__main__':
    # Use Gunicorn for production - this is for local development only
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))