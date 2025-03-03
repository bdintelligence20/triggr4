import os
import uuid
import json
import base64
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load credentials from environment
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Firebase credentials
firebase_cred_b64 = os.environ.get("FIREBASE_CRED_B64")
firebase_cred_json_str = base64.b64decode(firebase_cred_b64).decode("utf-8")
firebase_cred_info = json.loads(firebase_cred_json_str)

# Initialize Firebase
import firebase_admin
from firebase_admin import credentials, firestore
firebase_admin.initialize_app(credentials.Certificate(firebase_cred_info))
db = firestore.client()

# Initialize OpenAI
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize Anthropic
import anthropic
anthropic_client = anthropic.Client(api_key=ANTHROPIC_API_KEY)

# Initialize Flask
app = Flask(__name__)
CORS(app, origins=["*"], supports_credentials=True, methods=["GET", "POST", "OPTIONS", "DELETE", "PUT"])
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Extract text from files
def extract_text(file_path, file_type):
    if file_type == 'pdf':
        import PyPDF2
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            # Process up to 20 pages to save memory but get more content
            for i in range(min(200, len(reader.pages))):
                try:
                    page_text = reader.pages[i].extract_text() or ""
                    text += page_text + "\n\n"
                except Exception as e:
                    logger.error(f"Error extracting PDF page {i}: {str(e)}")
            return text[:10000000]  # Limit to 100K chars
    elif file_type == 'doc':
        import docx2txt
        try:
            text = docx2txt.process(file_path)
            return text[:10000000]  # Limit to 100K chars
        except Exception as e:
            logger.error(f"Error extracting DOCX: {str(e)}")
            return "Error extracting document text"
    else:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read(10000000)  # Limit to 100K chars
        except Exception as e:
            logger.error(f"Error reading text file: {str(e)}")
            with open(file_path, 'rb') as f:
                return f.read(10000000).decode('utf-8', errors='replace')  # Try binary read

# Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

@app.route('/documents', methods=['GET'])
def list_documents():
    """List all documents in Firestore."""
    try:
        docs = db.collection("knowledge_items").stream()
        items = []
        for doc in docs:
            data = doc.to_dict()
            items.append({
                "id": doc.id,
                "title": data.get("title", "Untitled"),
                "category": data.get("category", "general"),
                "file_type": data.get("file_type", "text"),
                "created_at": data.get("created_at"),
                "has_embeddings": data.get("has_embeddings", False)
            })
        return jsonify({"documents": items})
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_document():
    """Upload a document to Firestore only - no embeddings."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    category = request.form.get('category', 'general')
    title = request.form.get('title') or file.filename

    logger.info(f"Upload request received: {title}, category: {category}")

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save file locally
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
        
        # Extract text with conservative memory usage
        try:
            content = extract_text(local_path, file_type)
            logger.info(f"Extracted {len(content)} characters from file")
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            content = f"Error extracting text: {str(e)}"[:1000000]
        
        # Store in Firestore
        doc_ref = db.collection("knowledge_items").document()
        doc_data = {
            "title": title,
            "content": content,
            "category": category,
            "file_type": file_type,
            "created_at": firestore.SERVER_TIMESTAMP,
            "has_embeddings": False
        }
        doc_ref.set(doc_data)
        logger.info(f"Saved document to Firestore with ID: {doc_ref.id}")
        
        # Clean up
        os.remove(local_path)
        
        return jsonify({
            "message": "File uploaded successfully",
            "item_id": doc_ref.id
        })
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        if 'local_path' in locals() and os.path.exists(local_path):
            os.remove(local_path)
        return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def query():
    """Query documents using simple keyword search (no vectors)."""
    data = request.get_json()
    query_text = data.get("query")
    category = data.get("category")
    
    logger.info(f"Query received: '{query_text}', category: '{category}'")
    
    if not query_text:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        # Get all documents with flexible category matching
        if category:
            logger.info(f"Filtering documents by category: {category}")
            # Try multiple ways to match the category
            category_docs = list(db.collection("knowledge_items").where("category", "==", category).stream())
            
            if not category_docs:
                # Try another approach since the previous match might have failed
                logger.info(f"No exact category match, trying with more flexible matching")
                all_docs = list(db.collection("knowledge_items").stream())
                docs = []
                
                # Manually filter to be more flexible
                for doc in all_docs:
                    doc_data = doc.to_dict()
                    doc_category = str(doc_data.get("category", "")).lower()
                    
                    # Try to match in various ways
                    if (category.lower() in doc_category or 
                        doc_category in category.lower() or
                        # For numeric categories that might be stored as strings or numbers
                        str(category) == doc_category):
                        docs.append(doc)
                
                if not docs:
                    logger.info("Still no matches, searching all documents")
                    docs = all_docs
            else:
                docs = category_docs
        else:
            logger.info("Getting all documents")
            docs = db.collection("knowledge_items").stream()
        
        # Simple keyword search
        results = []
        query_terms = query_text.lower().split()
        logger.info(f"Query terms: {query_terms}")
        
        doc_count = 0
        for doc in docs:
            doc_count += 1
            data = doc.to_dict()
            content = data.get("content", "").lower()
            title = data.get("title", "").lower()
            
            # Log title for debugging
            logger.info(f"Checking document: {title} (ID: {doc.id})")
            
            # More forgiving search logic
            score = 0
            
            # First, try exact matches
            for term in query_terms:
                term_in_content = content.count(term)
                term_in_title = title.count(term) * 2  # Title matches count more
                score += term_in_content + term_in_title
                
                # Debug individual term matches
                if term_in_content > 0 or term_in_title > 0:
                    logger.info(f"  Term '{term}' found: {term_in_content} in content, {term_in_title} in title")
            
            # If no exact matches, try partial matching for longer terms
            if score == 0:
                for term in query_terms:
                    # If term length is at least 4 characters, try partial matching
                    if len(term) >= 4:
                        for word in content.split():
                            if term in word:
                                score += 1
                        for word in title.split():
                            if term in word:
                                score += 2
            
            logger.info(f"  Document score: {score}")
            
            if score > 0:
                # Get a snippet of content around the first matching term for better context
                snippet = content
                for term in query_terms:
                    if term in content:
                        start_idx = max(0, content.find(term) - 200)
                        end_idx = min(len(content), content.find(term) + 700)
                        snippet = content[start_idx:end_idx]
                        break
                
                results.append({
                    "item_id": doc.id,
                    "title": data.get("title"),
                    "content": snippet + "..." if len(snippet) < len(content) else snippet,
                    "score": score
                })
        
        logger.info(f"Total documents checked: {doc_count}")
        logger.info(f"Documents with matches: {len(results)}")
        
        # Sort by relevance
        results.sort(key=lambda x: x["score"], reverse=True)
        top_results = results[:3]  # Take top 3
        
        if not top_results:
            logger.info("No relevant documents found")
            return jsonify({
                "response": "I couldn't find any relevant information in our knowledge base.",
                "retrieved": []
            })
        
        # Format context for Claude
        context = "\n\n---\n\n".join([
            f"Document: {item['title']}\n{item['content']}" for item in top_results
        ])
        
        logger.info(f"Sending query to Claude with {len(top_results)} documents")
        
        # Call Claude
        prompt = f"""
        You are a helpful AI assistant tasked with answering questions based on provided context.
        
        Context:
        {context}
        
        Question:
        {query_text}
        
        Answer the question based only on the provided context. If the context doesn't contain relevant information, say so.
        """
        
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return jsonify({
            "response": response.content[0].text,
            "retrieved": [{"title": item["title"]} for item in top_results]
        })
        
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/delete/<item_id>', methods=['DELETE'])
def delete_document(item_id):
    """Delete a document from Firestore."""
    try:
        db.collection("knowledge_items").document(item_id).delete()
        return jsonify({"message": "Document deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/test-pinecone', methods=['GET'])
def test_pinecone():
    """Test endpoint to verify if Pinecone is working."""
    try:
        # Initialize Pinecone with retry
        from pinecone import Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Just check if we can list indexes
        indexes = pc.list_indexes()
        
        return jsonify({
            "status": "success",
            "indexes": indexes
        })
    except Exception as e:
        logger.error(f"Pinecone test error: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))