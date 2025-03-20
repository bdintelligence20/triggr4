import os
import logging
import traceback
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from firebase_admin import firestore
from document_loaders import DocumentLoaderFactory
from rag_system import RAGSystem
from pinecone_client import PineconeClient
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
import firebase_admin
from flask import current_app

# Import the GCS client from app.py
from app import gcs_client, bucket

@document_bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process a document for the knowledge base using custom RAG system."""
    logger.info("Upload endpoint called")
    
    # Get organization ID from authenticated user
    organization_id = get_user_organization_id()
    
    # Enforce organization ID requirement for multi-tenant isolation
    if not organization_id:
        logger.error("Organization ID is required for document upload")
        return jsonify({"error": "Organization ID is required. Please ensure you are properly authenticated and assigned to an organization."}), 403
    
    logger.info(f"Upload request for organization: {organization_id}")
    
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
        
        # Upload file to GCS with organization-specific path
        gcs_filename = f"{item_id}_{filename}"
        org_path = f"documents/{organization_id or 'global'}/{gcs_filename}"
        blob = bucket.blob(org_path)
        
        with open(local_path, 'rb') as file_obj:
            blob.upload_from_file(file_obj)
        
        # Generate public URL (or signed URL if needed)
        file_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{org_path}"
        logger.info(f"File uploaded to GCS: {org_path}")
        
        # Save initial metadata to Firestore
        doc_data = {
            "title": title,
            "category": category,
            "file_type": file_ext,
            "created_at": firestore.SERVER_TIMESTAMP,
            "processing_status": "processing",
            "organizationId": organization_id,
            "file_url": file_url
        }
        doc_ref.set(doc_data)
        logger.info(f"Created document record with ID: {item_id}")
        
        # Process with custom RAG system
        try:
            # Initialize organization-specific RAG system
            rag_system = RAGSystem(
                openai_api_key=OPENAI_API_KEY,
                anthropic_api_key=ANTHROPIC_API_KEY,
                pinecone_api_key=PINECONE_API_KEY,
                index_name=PINECONE_INDEX_NAME,
                organization_id=organization_id
            )
            
            # Process document
            vectors_stored = rag_system.process_document(
                doc_text=open(local_path, 'r', encoding='utf-8', errors='replace').read(),
                source_id=item_id,
                namespace=None  # Will use organization-based namespace
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
        
        # Enforce organization ID requirement for multi-tenant isolation
        if not organization_id:
            logger.error("Organization ID is required for listing documents")
            return jsonify({"error": "Organization ID is required. Please ensure you are properly authenticated and assigned to an organization."}), 403
        
        # Build query
        query = db.collection("knowledge_items")
        
        # Apply filters
        if category:
            query = query.where("category", "==", category)
            
        # Filter by organization
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
    """Delete a document and its vectors from the knowledge base using custom RAG system."""
    try:
        # Get the document
        doc_ref = db.collection("knowledge_items").document(item_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Document not found"}), 404
            
        doc_data = doc.to_dict()
        
        # Get organization ID from authenticated user
        user_org_id = get_user_organization_id()
        
        # Enforce organization ID requirement for multi-tenant isolation
        if not user_org_id:
            logger.error("Organization ID is required for deleting documents")
            return jsonify({"error": "Organization ID is required. Please ensure you are properly authenticated and assigned to an organization."}), 403
        
        # Get organization ID from the document
        doc_org_id = doc_data.get("organizationId")
        
        # Ensure the document belongs to the user's organization
        if doc_org_id != user_org_id:
            logger.error(f"Unauthorized: User from organization {user_org_id} attempted to delete document from organization {doc_org_id}")
            return jsonify({"error": "You are not authorized to delete this document"}), 403
        
        # Use the document's organization ID
        organization_id = doc_org_id
        
        # Initialize Pinecone client
        pinecone_client = PineconeClient(
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
        vectors_deleted = pinecone_client.delete_vectors(vector_ids)
        
        # Delete from GCS if URL exists
        if 'file_url' in doc_data:
            try:
                # Extract organization ID from the document
                org_id = doc_data.get("organizationId") or "global"
                
                # Parse the filename from the URL
                file_name = doc_data['file_url'].split('/')[-1]
                
                # Use organization-specific path
                org_path = f"documents/{org_id}/{file_name}"
                blob = bucket.blob(org_path)
                blob.delete()
                logger.info(f"Deleted file from GCS: {org_path}")
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
