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
CORS(app, origins=["*"])
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Extract text from files
def extract_text(file_path, file_type):
    if file_type == 'pdf':
        import PyPDF2
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            # Only process first 10 pages to save memory
            for i in range(min(10, len(reader.pages))):
                text += reader.pages[i].extract_text() or ""
            return text[:50000]  # Limit to 50K chars
    elif file_type == 'doc':
        import docx2txt
        text = docx2txt.process(file_path)
        return text[:50000]  # Limit to 50K chars
    else:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read(50000)  # Limit to 50K chars

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
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_document():
    """Upload a document to Firestore only - no embeddings."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    category = request.form.get('category', 'general')
    title = request.form.get('title') or file.filename

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
            content = f"Error extracting text: {str(e)}"[:1000]
        
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
    
    if not query_text:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        # Get all documents (for small datasets)
        if category:
            docs = db.collection("knowledge_items").where("category", "==", category).stream()
        else:
            docs = db.collection("knowledge_items").stream()
        
        # Simple keyword search
        results = []
        query_terms = query_text.lower().split()
        
        for doc in docs:
            data = doc.to_dict()
            content = data.get("content", "").lower()
            title = data.get("title", "").lower()
            
            # Simple relevance score - count term occurrences
            score = sum(content.count(term) for term in query_terms)
            score += sum(title.count(term) * 2 for term in query_terms)  # Title matches count more
            
            if score > 0:
                results.append({
                    "item_id": doc.id,
                    "title": data.get("title"),
                    "content": data.get("content")[:500] + "...",
                    "score": score
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x["score"], reverse=True)
        top_results = results[:3]  # Take top 3
        
        if not top_results:
            return jsonify({
                "response": "I couldn't find any relevant information in our knowledge base.",
                "retrieved": []
            })
        
        # Format context for Claude
        context = "\n\n---\n\n".join([
            f"Document: {item['title']}\n{item['content']}" for item in top_results
        ])
        
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
            max_tokens_to_sample=4096,
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

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))