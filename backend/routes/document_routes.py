import os
import logging
import traceback
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from firebase_admin import firestore
from document_loaders import DocumentLoaderFactory
from langchain_rag import LangChainRAG
from vector_store import EnhancedPineconeStore
from utils import allowed_file, get_user_organization_id

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
document_bp = Blueprint('document', __name__)

# Get database instance
db = firestore.client()

# Get environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "knowledge-hub-vectors")
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "knowledge-hub-files")

# Get Google Cloud Storage bucket
from google.cloud import storage
gcs_client = storage.Client()
bucket = gcs_client.bucket(GCS_BUCKET_NAME)

@document_bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process a document for the knowledge base using LangChain."""
    logger.info("Upload endpoint called")
    
    # Get organization ID from authenticated user
    organization_id = get_user_organization_id()
    logger.info(f"Upload request for organization: {organization_id or 'global'}")
    
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
    
    # Expanded allowed file types
    allowed_extensions = {
        'pdf', 'doc', 'docx', 'txt', 'csv', 'xlsx', 'pptx', 
        'json', 'md', 'html', 'xml', 'eml', 'msg', 
        'jpg', 'png', 'gif'
    }
        
    if not allowed_file(file.filename, allowed_extensions):
        logger.info(f"Unsupported file type: {file.filename}")
        return jsonify({"error": f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"}), 400

    try:
        # Save file locally
        filename = secure_filename(file.filename)
        local_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(local_path)
        logger.info(f"File saved to {local_path}")
        
        # Extract file type
        file_ext = os.path.splitext(filename)[1].lower().replace('.', '')
        
        # Create document ID
        doc_ref = db.collection("knowledge_items").document()
        item_id = doc_ref.id
        
        # Save initial metadata to Firestore
        doc_data = {
            "title": title,
            "category": category,
            "file_type": file_ext,
            "created_at": firestore.SERVER_TIMESTAMP,
            "processing_status": "processing",
            "organizationId": organization_id
        }
        doc_ref.set(doc_data)
        logger.info(f"Created document record with ID: {item_id}")
        
        # Process with LangChain
        try:
            # Initialize organization-specific LangChain RAG system
            org_langchain_rag = LangChainRAG(
                openai_api_key=OPENAI_API_KEY,
                anthropic_api_key=ANTHROPIC_API_KEY,
                pinecone_api_key=PINECONE_API_KEY,
                index_name=PINECONE_INDEX_NAME,
                organization_id=organization_id
            )
            
            # Process document
            vectors_stored = org_langchain_rag.process_document(
                file_path=local_path,
                source_id=item_id,
                category=category
            )
            
            # Extract text and metadata for storage
            text, metadata, _ = DocumentLoaderFactory.extract_text_and_metadata(local_path)
            
            # Update document with content and metadata
            doc_ref.update({
                "content": text,
                "word_count": len(text.split()),
                "processing_status": "completed",
                "vectors_stored": vectors_stored,
                "metadata": metadata
            })
            
            logger.info(f"Successfully processed document {item_id}: {vectors_stored} vectors stored")
            
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

@document_bp.route('/documents', methods=['GET'])
def list_documents():
    """List all documents in the knowledge base."""
    try:
        category = request.args.get('category')
        limit = min(int(request.args.get('limit', 100)), 500)  # Cap at 500
        
        # Get organization ID from authenticated user
        organization_id = get_user_organization_id()
        
        # Build query
        query = db.collection("knowledge_items")
        
        # Apply filters
        if category:
            query = query.where("category", "==", category)
            
        # Filter by organization if available
        if organization_id:
            query = query.where("organizationId", "==", organization_id)
        
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

@document_bp.route('/delete/<item_id>', methods=['DELETE'])
def delete_document(item_id):
    """Delete a document and its vectors from the knowledge base using LangChain."""
    try:
        # Get the document
        doc_ref = db.collection("knowledge_items").document(item_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Document not found"}), 404
            
        doc_data = doc.to_dict()
        
        # Get organization ID from the document or from the authenticated user
        organization_id = doc_data.get("organizationId") or get_user_organization_id()
        
        # Initialize vector store
        vector_store = EnhancedPineconeStore(
            api_key=PINECONE_API_KEY,
            index_name=PINECONE_INDEX_NAME,
            organization_id=organization_id
        )
        
        # Generate vector IDs to delete
        vector_ids = []
        expected_chunks = doc_data.get("vectors_stored", 0)
        
        for i in range(max(100, expected_chunks * 2)):  # Search for more than we expect to be safe
            vector_ids.append(f"{item_id}_{i}")
        
        # Delete vectors
        vectors_deleted = vector_store.delete_documents(vector_ids)
        
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
            "vectors_deleted": vectors_deleted,
            "file_deleted": 'file_url' in doc_data
        })
        
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to delete document: {str(e)}"}), 500
