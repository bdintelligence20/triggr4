import os
import time
import logging
from flask import Blueprint, jsonify
from firebase_admin import firestore
from pinecone_client import PineconeClient

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
utility_bp = Blueprint('utility', __name__)

# Get database instance
db = firestore.client()

# Get environment variables
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "knowledge-hub-vectors")

# Initialize Pinecone client
pinecone_client = PineconeClient(api_key=PINECONE_API_KEY, index_name=PINECONE_INDEX_NAME)

@utility_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Simple health check for Cloud Run
        # We don't want to check external services for the basic health check
        # as it might cause the container to fail to start if services are temporarily unavailable
        
        # Log the health check
        logger.info("Health check received")
        
        # Return a simple healthy response
        return jsonify({
            "status": "healthy",
            "message": "Service is running"
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@utility_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check endpoint for monitoring all services."""
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
        logger.error(f"Detailed health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@utility_bp.route('/test-pinecone', methods=['GET'])
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
