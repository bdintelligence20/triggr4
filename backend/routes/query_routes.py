import os
import logging
import traceback
from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from langchain_rag import LangChainRAG
from utils import get_user_organization_id

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
query_bp = Blueprint('query', __name__)

# Get database instance
db = firestore.client()

# Get environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "knowledge-hub-vectors")

@query_bp.route('/query', methods=['POST'])
def query():
    """Query the knowledge base using LangChain RAG."""
    data = request.get_json()
    query_text = data.get("query")
    category = data.get("category")
    stream_enabled = data.get("stream", False)
    conversation_history = data.get("history", "")
    
    # Get organization ID from authenticated user
    organization_id = get_user_organization_id()
    
    logger.info(f"Query received: '{query_text}', category: '{category}', stream: {stream_enabled}, organization: {organization_id or 'global'}")
    
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
        
        # Initialize organization-specific LangChain RAG system
        org_langchain_rag = LangChainRAG(
            openai_api_key=OPENAI_API_KEY,
            anthropic_api_key=ANTHROPIC_API_KEY,
            pinecone_api_key=PINECONE_API_KEY,
            index_name=PINECONE_INDEX_NAME,
            organization_id=organization_id
        )
        
        if not stream_enabled:
            # Non-streaming response
            result = org_langchain_rag.query(
                query_text=query_text,
                category=category,
                history=conversation_history
            )
            
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
                    result = org_langchain_rag.query(
                        query_text=query_text,
                        category=category,
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

@query_bp.route('/evaluate', methods=['POST'])
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
        organization_id = get_user_organization_id()
        
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
