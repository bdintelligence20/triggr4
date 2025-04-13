import os
import logging
import traceback
from flask import Blueprint, request, jsonify, current_app
from firebase_admin import firestore
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from rag_system import RAGSystem
import utils
import requests

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
query_bp = Blueprint('query', __name__)

# Get database instance
db = firestore.client()

# Define a custom key function for organization-aware rate limiting
def get_tenant_limit_key():
    # Get organization ID from the authenticated user
    organization_id = utils.get_user_organization_id()
    # Fallback to IP address if organization ID is not available
    if not organization_id:
        return get_remote_address()
    # Combine organization ID with IP for more granular control
    return f"{organization_id}:{request.remote_addr}"

# Initialize limiter for this blueprint with organization-aware key function
limiter = Limiter(
    key_func=get_tenant_limit_key,
    default_limits=["150 per day", "30 per hour"],
    storage_uri="memory://"
)

# Get environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "knowledge-hub-vectors")

@query_bp.route('/query', methods=['POST'])
@limiter.limit("10 per minute")  # Stricter limit for the query endpoint
def query():
    """Query the knowledge base using custom RAG system."""
    data = request.get_json()
    query_text = data.get("query")
    category = data.get("category")
    stream_enabled = data.get("stream", False)
    conversation_history = data.get("history", "")
    
    # Log the auth header for debugging
    auth_header = request.headers.get('Authorization')
    logger.info(f"Auth header present: {bool(auth_header)}")
    if auth_header:
        logger.info(f"Auth header format valid: {auth_header.startswith('Bearer ')}")
    
    # Get organization ID from authenticated user
    organization_id = utils.get_user_organization_id()
    
    # Enforce organization ID requirement for multi-tenant isolation
    if not organization_id:
        logger.error("Organization ID is required for querying")
        return jsonify({"error": "Organization ID is required. Please ensure you are properly authenticated and assigned to an organization."}), 403
    
    logger.info(f"Query received: '{query_text}', category: '{category}', stream: {stream_enabled}, organization: {organization_id}")
    
    if not query_text or not isinstance(query_text, str) or len(query_text.strip()) < 2:
        return jsonify({"error": "Invalid or empty query"}), 400

    try:
        # Log query to Firestore
        db.collection("queries").add({
            "query": query_text,
            "category": category,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "client_ip": request.remote_addr,
            "stream_enabled": stream_enabled,
            "history": conversation_history,
            "organizationId": organization_id
        })
        
        # Initialize organization-specific RAG system
        rag_system = RAGSystem(
            openai_api_key=OPENAI_API_KEY,
            anthropic_api_key=ANTHROPIC_API_KEY,
            pinecone_api_key=PINECONE_API_KEY,
            index_name=PINECONE_INDEX_NAME,
            organization_id=organization_id
        )
        
        if not stream_enabled:
            # Non-streaming response
            result = rag_system.query(
                user_query=query_text,
                history=conversation_history
            )
            
            # Check if enhancement is requested or enabled by default
            if data.get("enhance", True):
                from mcp_integration import enhance_rag_response
                import asyncio
                
                try:
                    enhanced_result = asyncio.run(enhance_rag_response(
                        query=query_text,
                        existing_response=result,
                        conversation_history=conversation_history
                    ))
                    
                    return jsonify({
                        "response": enhanced_result["answer"],
                        "sources": enhanced_result["sources"],
                        "reasoning_trace": enhanced_result.get("reasoning_trace", []),
                        "context_usage": enhanced_result.get("context_usage", {}),
                        "enhanced": True,
                        "streaming": False,
                        "status": "completed"
                    })
                except Exception as e:
                    logger.warning(f"Enhanced RAG failed, falling back to standard RAG: {str(e)}")
                    # Fall back to standard response if enhancement fails
            
            # Standard response (if enhancement is disabled or failed)
            return jsonify({
                "response": result["answer"],
                "sources": result["sources"],
                "streaming": False,
                "status": "completed"
            })
        else:
            # Streaming response
            def generate_direct_streaming_response():
                accumulated_response = ""
                
                def stream_callback(chunk):
                    nonlocal accumulated_response
                    accumulated_response += chunk
                
                try:
                    result = rag_system.query(
                        user_query=query_text,
                        history=conversation_history,
                        stream_callback=stream_callback
                    )
                    
                    return jsonify({
                        "response": accumulated_response,
                        "sources": result["sources"],
                        "streaming": False,
                        "status": "completed"
                    })
                except Exception as e:
                    logger.error(f"Error in streaming response: {str(e)}", exc_info=True)
                    return jsonify({
                        "error": f"Failed to process query: {str(e)}",
                        "streaming": False,
                        "status": "error"
                    }), 500
                    
            return generate_direct_streaming_response()
    
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to process query: {str(e)}", "status": "error"}), 500

@query_bp.route('/chat/history', methods=['GET'])
def get_chat_history():
    """Get chat history for the current user."""
    # Get organization ID and user ID from authenticated user
    organization_id = utils.get_user_organization_id()
    user_id = utils.get_user_id()
    
    # Enforce organization ID requirement for multi-tenant isolation
    if not organization_id:
        logger.error("Organization ID is required for chat history")
        return jsonify({"error": "Organization ID is required. Please ensure you are properly authenticated and assigned to an organization."}), 403
    
    if not user_id:
        logger.error("User ID is required for chat history")
        return jsonify({"error": "User ID is required. Please ensure you are properly authenticated."}), 403
    
    try:
        # Query Firestore for chat sessions
        query = db.collection("organizations").document(organization_id) \
                .collection("users").document(user_id) \
                .collection("chat_sessions").order_by("updated_at", direction=firestore.Query.DESCENDING)
        
        # Execute query
        sessions = query.stream()
        
        # Format results
        results = []
        for session in sessions:
            session_data = session.to_dict()
            results.append({
                "id": session.id,
                "title": session_data.get("title", "Untitled Chat"),
                "last_message": session_data.get("last_message", ""),
                "updated_at": session_data.get("updated_at"),
                "created_at": session_data.get("created_at"),
                "category": session_data.get("category", "general"),
                "message_count": len(session_data.get("messages", []))
            })
        
        return jsonify({"sessions": results})
    except Exception as e:
        logger.error(f"Chat history error: {str(e)}")
        return jsonify({"error": f"Failed to retrieve chat history: {str(e)}"}), 500

@query_bp.route('/chat/save', methods=['POST'])
def save_chat_session():
    """Save a chat session."""
    data = request.get_json()
    session_id = data.get("session_id")
    title = data.get("title", "Untitled Chat")
    messages = data.get("messages", [])
    category = data.get("category", "general")
    
    # Get organization ID and user ID from authenticated user
    organization_id = utils.get_user_organization_id()
    
    # Log the auth header for debugging
    auth_header = request.headers.get('Authorization')
    logger.info(f"Auth header present: {bool(auth_header)}")
    if auth_header:
        logger.info(f"Auth header format valid: {auth_header.startswith('Bearer ')}")
    
    # Get user ID
    user_id = utils.get_user_id()
    
    logger.info(f"Organization ID: {organization_id}, User ID: {user_id}")
    
    # Enforce organization ID requirement for multi-tenant isolation
    if not organization_id:
        logger.error("Organization ID is required for saving chat session")
        return jsonify({"error": "Organization ID is required. Please ensure you are properly authenticated and assigned to an organization."}), 403
    
    if not user_id:
        logger.error("User ID is required for saving chat session")
        return jsonify({"error": "User ID is required. Please ensure you are properly authenticated."}), 403
    
    try:
        # Create or update chat session
        if session_id:
            # Update existing session
            session_ref = db.collection("organizations").document(organization_id) \
                            .collection("users").document(user_id) \
                            .collection("chat_sessions").document(session_id)
        else:
            # Create new session
            session_ref = db.collection("organizations").document(organization_id) \
                            .collection("users").document(user_id) \
                            .collection("chat_sessions").document()
            session_id = session_ref.id
        
        # Prepare session data
        last_message = messages[-1]["content"] if messages else ""
        session_data = {
            "title": title,
            "messages": messages,
            "category": category,
            "last_message": last_message,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        # Add created_at for new sessions
        if not session_ref.get().exists:
            session_data["created_at"] = firestore.SERVER_TIMESTAMP
        
        # Save session
        session_ref.set(session_data, merge=True)
        
        return jsonify({
            "message": "Chat session saved successfully",
            "session_id": session_id
        })
    except Exception as e:
        logger.error(f"Save chat session error: {str(e)}")
        return jsonify({"error": f"Failed to save chat session: {str(e)}"}), 500

@query_bp.route('/chat/session/<session_id>', methods=['GET'])
def get_chat_session(session_id):
    """Get a specific chat session."""
    # Get organization ID and user ID from authenticated user
    organization_id = utils.get_user_organization_id()
    user_id = utils.get_user_id()
    
    # Enforce organization ID requirement for multi-tenant isolation
    if not organization_id:
        logger.error("Organization ID is required for retrieving chat session")
        return jsonify({"error": "Organization ID is required. Please ensure you are properly authenticated and assigned to an organization."}), 403
    
    if not user_id:
        logger.error("User ID is required for retrieving chat session")
        return jsonify({"error": "User ID is required. Please ensure you are properly authenticated."}), 403
    
    try:
        # Get chat session
        session_ref = db.collection("organizations").document(organization_id) \
                        .collection("users").document(user_id) \
                        .collection("chat_sessions").document(session_id)
        session = session_ref.get()
        
        if not session.exists:
            return jsonify({"error": "Chat session not found"}), 404
        
        session_data = session.to_dict()
        
        return jsonify({
            "id": session.id,
            "title": session_data.get("title", "Untitled Chat"),
            "messages": session_data.get("messages", []),
            "category": session_data.get("category", "general"),
            "updated_at": session_data.get("updated_at"),
            "created_at": session_data.get("created_at")
        })
    except Exception as e:
        logger.error(f"Get chat session error: {str(e)}")
        return jsonify({"error": f"Failed to retrieve chat session: {str(e)}"}), 500

@query_bp.route('/evaluate', methods=['POST'])
@limiter.limit("5 per minute")  # Strict limit for the evaluation endpoint
def evaluate_rag():
    """Evaluate RAG system performance."""
    try:
        from evaluation import RAGEvaluator
        
        data = request.get_json()
        query = data.get("query")
        expected_answer = data.get("expected_answer")
        category = data.get("category")
        batch_mode = data.get("batch_mode", False)
        test_cases = data.get("test_cases", [])
        
        # Get organization ID from authenticated user
        organization_id = utils.get_user_organization_id()
        
        # Enforce organization ID requirement for multi-tenant isolation
        if not organization_id:
            logger.error("Organization ID is required for evaluation")
            return jsonify({"error": "Organization ID is required. Please ensure you are properly authenticated and assigned to an organization."}), 403
        
        # Initialize evaluator
        evaluator = RAGEvaluator(
            openai_api_key=OPENAI_API_KEY,
            anthropic_api_key=ANTHROPIC_API_KEY,
            pinecone_api_key=PINECONE_API_KEY,
            index_name=PINECONE_INDEX_NAME,
            organization_id=organization_id
        )
        
        if batch_mode and test_cases:
            # Batch evaluation
            result = evaluator.evaluate_batch(test_cases)
        elif query and expected_answer:
            # Single query evaluation
            result = evaluator.evaluate_query(query, expected_answer, category)
        else:
            return jsonify({"error": "Invalid request parameters"}), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Evaluation error: {str(e)}")
        return jsonify({"error": f"Failed to evaluate: {str(e)}"}), 500
