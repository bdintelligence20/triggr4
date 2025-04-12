"""
MCP Routes

This module provides Flask routes for interacting with the MCP server.
"""

import os
import logging
import asyncio
from flask import Blueprint, request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils import get_user_organization_id, get_user_id

# Import MCP integration
from mcp_integration import MCPIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
mcp_bp = Blueprint('mcp', __name__)

# Initialize MCP integration
mcp_integration = MCPIntegration()

# Define a custom key function for organization-aware rate limiting
def get_tenant_limit_key():
    # Get organization ID from the authenticated user
    organization_id = get_user_organization_id()
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

@mcp_bp.route('/mcp/query', methods=['POST'])
@limiter.limit("10 per minute")  # Stricter limit for the query endpoint
def mcp_query():
    """Query the knowledge base using the MCP server."""
    data = request.get_json()
    query_text = data.get("query")
    conversation_history = data.get("history", "")
    context_preferences = data.get("preferences", {})
    
    # Get organization ID from authenticated user
    organization_id = get_user_organization_id()
    
    # Enforce organization ID requirement for multi-tenant isolation
    if not organization_id:
        logger.error("Organization ID is required for querying")
        return jsonify({"error": "Organization ID is required. Please ensure you are properly authenticated and assigned to an organization."}), 403
    
    logger.info(f"MCP query received: '{query_text}', organization: {organization_id}")
    
    if not query_text or not isinstance(query_text, str) or len(query_text.strip()) < 2:
        return jsonify({"error": "Invalid or empty query"}), 400

    try:
        # Log query to Firestore
        from firebase_admin import firestore
        db = firestore.client()
        db.collection("queries").add({
            "query": query_text,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "client_ip": request.remote_addr,
            "history": conversation_history,
            "organizationId": organization_id,
            "source": "mcp"
        })
        
        # Add organization ID to context preferences
        if 'context_preferences' not in context_preferences:
            context_preferences['context_preferences'] = {}
        context_preferences['context_preferences']['organization_id'] = organization_id
        
        # Call the MCP server
        result = asyncio.run(mcp_integration.query_knowledge_base(
            query=query_text,
            conversation_history=conversation_history,
            context_preferences=context_preferences
        ))
        
        return jsonify({
            "response": result["answer"],
            "sources": result["sources"],
            "reasoning_trace": result.get("reasoning_trace", []),
            "context_usage": result.get("context_usage", {}),
            "status": "completed"
        })
    
    except Exception as e:
        logger.error(f"MCP query error: {str(e)}")
        return jsonify({"error": f"Failed to process query: {str(e)}", "status": "error"}), 500

@mcp_bp.route('/mcp/process', methods=['POST'])
@limiter.limit("5 per minute")  # Stricter limit for document processing
def mcp_process_document():
    """Process a document using the MCP server."""
    data = request.get_json()
    document_content = data.get("content")
    metadata = data.get("metadata", {})
    processing_preferences = data.get("preferences", {})
    
    # Get organization ID from authenticated user
    organization_id = get_user_organization_id()
    
    # Enforce organization ID requirement for multi-tenant isolation
    if not organization_id:
        logger.error("Organization ID is required for document processing")
        return jsonify({"error": "Organization ID is required. Please ensure you are properly authenticated and assigned to an organization."}), 403
    
    logger.info(f"MCP document processing request received, organization: {organization_id}")
    
    if not document_content or not isinstance(document_content, str) or len(document_content.strip()) < 10:
        return jsonify({"error": "Invalid or empty document content"}), 400

    try:
        # Add organization ID to metadata
        if not metadata:
            metadata = {}
        metadata['organization_id'] = organization_id
        
        # Call the MCP server
        result = asyncio.run(mcp_integration.process_document(
            document_content=document_content,
            metadata=metadata,
            processing_preferences=processing_preferences
        ))
        
        return jsonify({
            "message": result["message"],
            "document_id": result["document_id"],
            "vectors_stored": result["vectors_stored"],
            "summary": result["summary"],
            "processing_stats": result["processing_stats"],
            "status": "completed"
        })
    
    except Exception as e:
        logger.error(f"MCP document processing error: {str(e)}")
        return jsonify({"error": f"Failed to process document: {str(e)}", "status": "error"}), 500

@mcp_bp.route('/mcp/context', methods=['POST'])
@limiter.limit("20 per minute")
def mcp_manage_context():
    """Manage the context window using the MCP server."""
    data = request.get_json()
    operation = data.get("operation")
    context_data = data.get("context_data", {})
    
    # Get organization ID from authenticated user
    organization_id = get_user_organization_id()
    
    # Enforce organization ID requirement for multi-tenant isolation
    if not organization_id:
        logger.error("Organization ID is required for context management")
        return jsonify({"error": "Organization ID is required. Please ensure you are properly authenticated and assigned to an organization."}), 403
    
    logger.info(f"MCP context management request received: {operation}, organization: {organization_id}")
    
    if not operation or not isinstance(operation, str):
        return jsonify({"error": "Invalid or empty operation"}), 400

    try:
        # Add organization ID to context data
        if not context_data:
            context_data = {}
        context_data['organization_id'] = organization_id
        
        # Call the MCP server
        result = asyncio.run(mcp_integration.manage_context(
            operation=operation,
            context_data=context_data
        ))
        
        return jsonify({
            "message": result["message"],
            "context_size": result["context_size"],
            "token_usage": result["token_usage"],
            "operation_result": result["operation_result"],
            "status": "completed"
        })
    
    except Exception as e:
        logger.error(f"MCP context management error: {str(e)}")
        return jsonify({"error": f"Failed to manage context: {str(e)}", "status": "error"}), 500

@mcp_bp.route('/mcp/orchestrate', methods=['POST'])
@limiter.limit("5 per minute")
def mcp_orchestrate_agents():
    """Orchestrate multiple agents using the MCP server."""
    data = request.get_json()
    task = data.get("task")
    agent_preferences = data.get("agent_preferences", {})
    execution_parameters = data.get("execution_parameters", {})
    
    # Get organization ID from authenticated user
    organization_id = get_user_organization_id()
    
    # Enforce organization ID requirement for multi-tenant isolation
    if not organization_id:
        logger.error("Organization ID is required for agent orchestration")
        return jsonify({"error": "Organization ID is required. Please ensure you are properly authenticated and assigned to an organization."}), 403
    
    logger.info(f"MCP agent orchestration request received: '{task}', organization: {organization_id}")
    
    if not task or not isinstance(task, str) or len(task.strip()) < 5:
        return jsonify({"error": "Invalid or empty task"}), 400

    try:
        # Add organization ID to execution parameters
        if not execution_parameters:
            execution_parameters = {}
        execution_parameters['organization_id'] = organization_id
        
        # Call the MCP server
        result = asyncio.run(mcp_integration.orchestrate_agents(
            task=task,
            agent_preferences=agent_preferences,
            execution_parameters=execution_parameters
        ))
        
        return jsonify({
            "response": result["response"],
            "agents_used": result["agents_used"],
            "confidence_scores": result["confidence_scores"],
            "reasoning_traces": result.get("reasoning_traces", []),
            "execution_stats": result["execution_stats"],
            "status": "completed"
        })
    
    except Exception as e:
        logger.error(f"MCP agent orchestration error: {str(e)}")
        return jsonify({"error": f"Failed to orchestrate agents: {str(e)}", "status": "error"}), 500

@mcp_bp.route('/mcp/capabilities', methods=['GET'])
def mcp_get_capabilities():
    """Get agent capabilities from the MCP server."""
    try:
        # Call the MCP server
        result = asyncio.run(mcp_integration.get_agent_capabilities())
        
        return jsonify({
            "capabilities": result["capabilities"],
            "status": result["status"],
            "message": result.get("message", "")
        })
    
    except Exception as e:
        logger.error(f"MCP capabilities error: {str(e)}")
        return jsonify({"error": f"Failed to get capabilities: {str(e)}", "status": "error"}), 500
