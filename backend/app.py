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
import threading
import requests
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
# Pinecone
from pinecone import Pinecone
try:
    # Initialize with retries and timeout settings
    pc = Pinecone(
        api_key=PINECONE_API_KEY,
        # Add these options to help with SSL issues
        pool_threads=1,  # Use a single thread for connection stability
    )
    
    # Test connection with retry logic
    retry_count = 3
    for attempt in range(retry_count):
        try:
            index = pc.Index(PINECONE_INDEX_NAME)
            # Perform a simple operation to test connection
            stats = index.describe_index_stats()
            logger.info(f"Connected to Pinecone index: {PINECONE_INDEX_NAME}, total vectors: {stats.get('total_vector_count', 0)}")
            break
        except Exception as e:
            if attempt < retry_count - 1:
                logger.warning(f"Pinecone connection attempt {attempt+1} failed: {str(e)}. Retrying...")
                time.sleep(2)  # Wait before retrying
            else:
                raise
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
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

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
CORS(app, origins=["*"], supports_credentials=True, methods=["GET", "POST", "OPTIONS", "DELETE", "PUT"])

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

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
def get_embedding_cached(text: str) -> list:
    """Get embedding for a single text with caching."""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=[text]
    )
    return response.data[0].embedding

def get_embeddings(chunks: list) -> list:
    """Get embeddings for multiple text chunks."""
    embeddings = []
    
    # Process in batches to avoid rate limits
    batch_size = 20
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        try:
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=batch
            )
            batch_embeddings = [data.embedding for data in response.data]
            embeddings.extend(batch_embeddings)
        except Exception as e:
            logger.error(f"Error getting embeddings batch {i}-{i+batch_size}: {str(e)}")
            raise
    
    return embeddings

def call_claude_rag(context_items, question):
    """
    Enhanced RAG with structured context.
    
    Args:
        context_items: List of dictionaries with metadata and content
        question: User's question
    
    Returns:
        Formatted response from Claude
    """
    # Format context for Claude
    formatted_context = []
    for i, item in enumerate(context_items):
        meta = item.get('metadata', {})
        title = meta.get('title', 'Unknown')
        content = item.get('content', '')
        formatted_context.append(f"[{i+1}] {title}\n{content}")
    
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
def upload_document():
    """Upload document but don't process it - just store in Firestore."""
    logger.info("Upload request received")
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    category = request.form.get('category', 'general')
    title = request.form.get('title') or file.filename
    
    logger.info(f"Processing file: {title}, category: {category}")

    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
        
    try:
        # Save file locally and extract text
        filename = secure_filename(file.filename)
        local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(local_path)
        
        # Determine file type
        if filename.lower().endswith('.pdf'):
            file_type = 'pdf'
        elif filename.lower().endswith(('.doc', '.docx')):
            file_type = 'doc'
        elif filename.lower().endswith('.txt'):
            file_type = 'txt'
        else:
            return jsonify({"error": "Unsupported file type"}), 400
        
        # Extract text with very conservative memory usage
        try:
            content = extract_text_minimally(local_path, file_type)
            logger.info(f"Extracted {len(content)} characters from file")
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            content = f"Error extracting text: {str(e)}"
        
        # Save to Firestore first - WITHOUT processing embeddings
        doc_ref = db.collection("knowledge_items").document()
        doc_data = {
            "title": title,
            "content": content,
            "category": category,
            "file_type": file_type,
            "word_count": len(content.split()),
            "created_at": firestore.SERVER_TIMESTAMP,
            "processing_status": "uploaded",  # Just mark as uploaded
            "embedding_status": "not_started"
        }
        doc_ref.set(doc_data)
        item_id = doc_ref.id
        logger.info(f"Saved document to Firestore with ID: {item_id}")
        
        # Clean up local file
        os.remove(local_path)
        
        return jsonify({
            "message": "File uploaded successfully",
            "item_id": item_id,
            "status": "uploaded",
            "note": "Embeddings will be processed manually to avoid memory issues"
        })
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        if 'local_path' in locals() and os.path.exists(local_path):
            os.remove(local_path)
        return jsonify({"error": f"Failed to process document: {str(e)}"}), 500

def extract_text_minimally(file_path, file_type):
    """Extract text from files with minimal memory usage."""
    if file_type == 'pdf':
        # Process PDF page by page to minimize memory usage
        text_parts = []
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            # Only process first 30 pages to reduce memory usage
            max_pages = min(30, len(reader.pages))
            for i in range(max_pages):
                try:
                    page = reader.pages[i]
                    page_text = page.extract_text()
                    if page_text:
                        # Limit text per page to reduce memory usage
                        text_parts.append(page_text[:5000])
                except Exception as e:
                    logger.error(f"Error extracting page {i}: {str(e)}")
        
        text = "\n\n".join(text_parts)
        # Limit total text to reduce memory usage
        return text[:100000]
    
    elif file_type == 'doc':
        # For Word docs, just extract with limiting
        text = docx2txt.process(file_path)
        return text[:100000]
    
    elif file_type == 'txt':
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            # Read in chunks to minimize memory usage
            text = f.read(100000)  # Read max 100KB
        return text
    
    else:
        return "Unsupported file type"
    
@app.route('/process-one-chunk/<item_id>/<int:chunk_index>', methods=['GET'])
def process_one_chunk(item_id, chunk_index):
    """Process a single chunk for a document."""
    try:
        # Get the document
        doc_ref = db.collection("knowledge_items").document(item_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Document not found"}), 404
            
        doc_data = doc.to_dict()
        content = doc_data.get("content", "")
        category = doc_data.get("category", "general")
        title = doc_data.get("title", "Untitled")
        file_type = doc_data.get("file_type", "text")
        
        # Get chunks
        chunks = chunk_text(content, chunk_size=400, overlap=50)
        total_chunks = len(chunks)
        
        if chunk_index >= total_chunks:
            return jsonify({"error": f"Chunk index {chunk_index} out of range (total: {total_chunks})"}), 400
        
        # Update document if this is the first chunk
        if chunk_index == 0:
            doc_ref.update({
                "processing_status": "processing",
                "total_chunks": total_chunks,
                "processed_chunks": 0
            })
        
        # Process just one chunk
        chunk = chunks[chunk_index]
        
        # Get embedding
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=[chunk]
        )
        
        # Create vector
        vector_id = f"{item_id}_{chunk_index}"
        embedding = response.data[0].embedding
        metadata = {
            "item_id": item_id,
            "chunk_index": chunk_index,
            "category": category,
            "title": title,
            "file_type": file_type
        }
        
        # Upload to Pinecone
        index.upsert(vectors=[(vector_id, embedding, metadata)])
        
        # Update progress
        doc_ref.update({
            "processed_chunks": chunk_index + 1,
        })
        
        # Check if this was the last chunk
        if chunk_index == total_chunks - 1:
            doc_ref.update({
                "processing_status": "completed",
                "embedding_status": "completed",
                "completed_at": firestore.SERVER_TIMESTAMP
            })
            
        return jsonify({
            "status": "success",
            "chunk_index": chunk_index,
            "total_chunks": total_chunks
        })
        
    except Exception as e:
        logger.error(f"Error processing chunk {chunk_index} for document {item_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/process-next-chunk/<item_id>', methods=['GET'])
def process_next_chunk(item_id):
    """Process the next chunk for a document."""
    try:
        # Get the document
        doc_ref = db.collection("knowledge_items").document(item_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Document not found"}), 404
            
        doc_data = doc.to_dict()
        
        # Check if processing is already done
        if doc_data.get("processing_status") == "completed":
            return jsonify({
                "status": "completed",
                "message": "Document processing already completed"
            })
        
        # Get current progress
        processed_chunks = doc_data.get("processed_chunks", 0)
        total_chunks = doc_data.get("total_chunks")
        
        if total_chunks is None:
            # First time - calculate total chunks
            content = doc_data.get("content", "")
            chunks = chunk_text(content, chunk_size=400, overlap=50)
            total_chunks = len(chunks)
            
            # Update document
            doc_ref.update({
                "processing_status": "processing",
                "total_chunks": total_chunks,
                "processed_chunks": 0
            })
            
            processed_chunks = 0
        
        # Check if there are more chunks to process
        if processed_chunks >= total_chunks:
            # Mark as completed
            doc_ref.update({
                "processing_status": "completed",
                "embedding_status": "completed",
                "completed_at": firestore.SERVER_TIMESTAMP
            })
            
            return jsonify({
                "status": "completed",
                "message": "Document processing completed"
            })
        
        # Process the next chunk
        return process_one_chunk(item_id, processed_chunks)
        
    except Exception as e:
        logger.error(f"Error processing next chunk for document {item_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/document-status/<item_id>', methods=['GET'])
def document_status(item_id):
    """Check the processing status of a document."""
    try:
        doc = db.collection("knowledge_items").document(item_id).get()
        
        if not doc.exists:
            return jsonify({"error": "Document not found"}), 404
            
        doc_data = doc.to_dict()
        
        return jsonify({
            "item_id": item_id,
            "title": doc_data.get("title", "Untitled"),
            "processing_status": doc_data.get("processing_status", "unknown"),
            "processed_chunks": doc_data.get("processed_chunks", 0),
            "total_chunks": doc_data.get("total_chunks", 0),
            "completed_at": doc_data.get("completed_at")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def query():
    """Query the knowledge base using RAG."""
    data = request.get_json()
    query_text = data.get("query")
    category = data.get("category")
    
    if not query_text or not isinstance(query_text, str) or len(query_text.strip()) < 2:
        return jsonify({"error": "Invalid or empty query"}), 400

    try:
        # Get embedding for the query using the new OpenAI client
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=[query_text]
        )
        query_embedding = response.data[0].embedding
        
        # Build filter for category if provided
        filter_query = {"category": category} if category else None
        
        # Log query details for debugging
        logger.info(f"Querying Pinecone with category filter: {filter_query}")
        
        # Query the vector database
        query_response = index.query(
            vector=query_embedding, 
            top_k=5, 
            filter=filter_query,
            include_metadata=True
        )
        
        matches = query_response.get('matches', [])
        logger.info(f"Pinecone returned {len(matches)} matches")
        
        if not matches:
            return jsonify({
                "response": "I couldn't find any relevant information in our knowledge base.",
                "retrieved": []
            })
        
        # Get content for matches
        context_items = []
        for match in matches:
            meta = match.get('metadata', {})
            item_id = meta.get('item_id')
            chunk_index = meta.get('chunk_index')
            
            if not item_id:
                continue
                
            try:
                # Get the content from Firestore
                doc = db.collection("knowledge_items").document(item_id).get()
                if not doc.exists:
                    continue
                    
                doc_data = doc.to_dict()
                content = doc_data.get('content', '')
                
                # Split into chunks to find the specific one
                chunks = chunk_text(content)
                if chunk_index is not None and 0 <= chunk_index < len(chunks):
                    context_text = chunks[chunk_index]
                else:
                    # If chunk index is invalid, use the first part of the content
                    context_text = content[:1000] + "..."
                
                context_items.append({
                    'metadata': meta,
                    'content': context_text,
                    'score': match.get('score', 0)
                })
            except Exception as e:
                logger.error(f"Error retrieving document {item_id}: {str(e)}")
        
        if not context_items:
            return jsonify({
                "response": "I retrieved some documents, but couldn't extract their content.",
                "retrieved": []
            })
        
        # Format context for Claude
        context_text = "\n\n---\n\n".join([
            f"Document: {item['metadata'].get('title', 'Unknown')}\n{item['content']}" 
            for item in context_items
        ])
        
        # Call Claude with the context
        ai_response = call_claude_rag(context_items, query_text)
        
        # Return simplified context metadata for frontend
        simplified_context = []
        for item in context_items:
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
        return jsonify({"error": f"Failed to process query: {str(e)}"}), 500

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