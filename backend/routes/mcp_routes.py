"""
MCP Routes

This module provides Flask routes for interacting with the MCP server.
It exposes the enhanced RAG capabilities to the frontend.
"""

import os
import logging
import json
from flask import Blueprint, request, jsonify
from firebase_admin import firestore
import asyncio

# Import MCP integration
from mcp_integration import (
    MCPIntegration,
    enhance_rag_response,
    process_document_with_enhanced_chunking
)

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
mcp_bp = Blueprint('mcp', __name__)

# Get database instance
db = firestore.client()

@mcp_bp.route('/query', methods=['POST'])
def query_knowledge_base():
    """
    Query the knowledge base with enhanced context management.
    
    Request body:
    {
        "query": "Query string",
        "conversation_history": "Previous conversation history",
        "context_preferences": {
            "allocation": {
                "global": 0.3,
                "task": 0.4,
                "conversation": 0.3
            }
        },
        "organization_id": "Organization ID"
    }
    
    Returns:
        JSON response with the query result
    """
    try:
        # Get request data
        data = request.json
        
        # Validate required fields
        if not data or not data.get('query'):
            return jsonify({'error': 'Query is required'}), 400
        
        # Get parameters
        query = data.get('query')
        conversation_history = data.get('conversation_history', '')
        context_preferences = data.get('context_preferences', {})
        organization_id = data.get('organization_id')
        
        # Validate organization ID
        if not organization_id:
            return jsonify({'error': 'Organization ID is required'}), 400
        
        # Initialize MCP integration
        mcp = MCPIntegration()
        
        # Run query asynchronously
        async def run_query():
            try:
                result = await mcp.query_knowledge_base(
                    query=query,
                    conversation_history=conversation_history,
                    context_preferences=context_preferences
                )
                return result
            except Exception as e:
                logger.error(f"Error querying knowledge base: {str(e)}")
                raise
        
        # Run the query
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_query())
        loop.close()
        
        # Store the query in Firestore
        query_id = db.collection('queries').document().id
        query_data = {
            'query': query,
            'response': result.get('answer', ''),
            'sources': result.get('sources', []),
            'reasoning_trace': result.get('reasoning_trace', []),
            'context_usage': result.get('context_usage', {}),
            'confidence': result.get('confidence', 0.0),
            'enhanced': True,
            'organizationId': organization_id,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'status': 'completed'
        }
        
        db.collection('queries').document(query_id).set(query_data)
        
        # Return the result
        return jsonify({
            'id': query_id,
            'answer': result.get('answer', ''),
            'sources': result.get('sources', []),
            'reasoning_trace': result.get('reasoning_trace', []),
            'context_usage': result.get('context_usage', {}),
            'confidence': result.get('confidence', 0.0)
        })
    except Exception as e:
        logger.error(f"Error in query_knowledge_base: {str(e)}")
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/process-document', methods=['POST'])
def process_document():
    """
    Process a document with enhanced semantic chunking.
    
    Request body:
    {
        "document_content": "Document content",
        "metadata": {
            "title": "Document title",
            "organization_id": "Organization ID"
        },
        "processing_preferences": {
            "max_chunk_size": 1000,
            "overlap": 200
        }
    }
    
    Returns:
        JSON response with the processing result
    """
    try:
        # Get request data
        data = request.json
        
        # Validate required fields
        if not data or not data.get('document_content'):
            return jsonify({'error': 'Document content is required'}), 400
        
        # Get parameters
        document_content = data.get('document_content')
        metadata = data.get('metadata', {})
        processing_preferences = data.get('processing_preferences', {})
        
        # Validate organization ID
        organization_id = metadata.get('organization_id')
        if not organization_id:
            return jsonify({'error': 'Organization ID is required in metadata'}), 400
        
        # Run document processing asynchronously
        async def run_processing():
            try:
                result = await process_document_with_enhanced_chunking(
                    document_content=document_content,
                    metadata=metadata,
                    processing_preferences=processing_preferences
                )
                return result
            except Exception as e:
                logger.error(f"Error processing document: {str(e)}")
                raise
        
        # Run the processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_processing())
        loop.close()
        
        # Store the document in Firestore
        document_id = result.get('document_id', '')
        document_data = {
            'content': document_content,
            'metadata': metadata,
            'summary': result.get('summary', ''),
            'vectors_stored': result.get('vectors_stored', 0),
            'processing_stats': result.get('processing_stats', {}),
            'organizationId': organization_id,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'status': 'processed',
            'enhanced': True
        }
        
        db.collection('documents').document(document_id).set(document_data)
        
        # Return the result
        return jsonify({
            'document_id': document_id,
            'vectors_stored': result.get('vectors_stored', 0),
            'summary': result.get('summary', ''),
            'processing_stats': result.get('processing_stats', {})
        })
    except Exception as e:
        logger.error(f"Error in process_document: {str(e)}")
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/manage-context', methods=['POST'])
def manage_context():
    """
    Manage the context window for RAG operations.
    
    Request body:
    {
        "operation": "add|remove|optimize|clear",
        "context_data": {
            "context_id": "Context ID",
            "content": "Content to add",
            "query": "Query for optimization",
            "current_context": "Current context for optimization",
            "history": "Conversation history for optimization"
        }
    }
    
    Returns:
        JSON response with the operation result
    """
    try:
        # Get request data
        data = request.json
        
        # Validate required fields
        if not data or not data.get('operation'):
            return jsonify({'error': 'Operation is required'}), 400
        
        # Get parameters
        operation = data.get('operation')
        context_data = data.get('context_data', {})
        
        # Initialize MCP integration
        mcp = MCPIntegration()
        
        # Run context management asynchronously
        async def run_context_management():
            try:
                result = await mcp.manage_context(
                    operation=operation,
                    context_data=context_data
                )
                return result
            except Exception as e:
                logger.error(f"Error managing context: {str(e)}")
                raise
        
        # Run the context management
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_context_management())
        loop.close()
        
        # Return the result
        return jsonify({
            'message': result.get('message', ''),
            'context_size': result.get('context_size', {}),
            'token_usage': result.get('token_usage', {}),
            'operation_result': result.get('operation_result', {})
        })
    except Exception as e:
        logger.error(f"Error in manage_context: {str(e)}")
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/orchestrate-agents', methods=['POST'])
def orchestrate_agents():
    """
    Orchestrate multiple specialized agents for complex tasks.
    
    Request body:
    {
        "task": "Task to perform",
        "agent_preferences": {
            "include": ["retriever", "reasoner", "generator"],
            "exclude": []
        },
        "execution_parameters": {
            "max_tokens": 1000,
            "temperature": 0.7
        }
    }
    
    Returns:
        JSON response with the orchestration result
    """
    try:
        # Get request data
        data = request.json
        
        # Validate required fields
        if not data or not data.get('task'):
            return jsonify({'error': 'Task is required'}), 400
        
        # Get parameters
        task = data.get('task')
        agent_preferences = data.get('agent_preferences', {})
        execution_parameters = data.get('execution_parameters', {})
        
        # Initialize MCP integration
        mcp = MCPIntegration()
        
        # Run agent orchestration asynchronously
        async def run_orchestration():
            try:
                result = await mcp.orchestrate_agents(
                    task=task,
                    agent_preferences=agent_preferences,
                    execution_parameters=execution_parameters
                )
                return result
            except Exception as e:
                logger.error(f"Error orchestrating agents: {str(e)}")
                raise
        
        # Run the orchestration
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_orchestration())
        loop.close()
        
        # Return the result
        return jsonify({
            'response': result.get('response', ''),
            'agents_used': result.get('agents_used', []),
            'confidence_scores': result.get('confidence_scores', {}),
            'reasoning_traces': result.get('reasoning_traces', []),
            'execution_stats': result.get('execution_stats', {})
        })
    except Exception as e:
        logger.error(f"Error in orchestrate_agents: {str(e)}")
        return jsonify({'error': str(e)}), 500

@mcp_bp.route('/enhance-response', methods=['POST'])
def enhance_response():
    """
    Enhance an existing RAG response.
    
    Request body:
    {
        "query": "Query string",
        "existing_response": {
            "answer": "Existing answer",
            "sources": []
        },
        "conversation_history": "Previous conversation history"
    }
    
    Returns:
        JSON response with the enhanced response
    """
    try:
        # Get request data
        data = request.json
        
        # Validate required fields
        if not data or not data.get('query') or not data.get('existing_response'):
            return jsonify({'error': 'Query and existing response are required'}), 400
        
        # Get parameters
        query = data.get('query')
        existing_response = data.get('existing_response', {})
        conversation_history = data.get('conversation_history', '')
        
        # Run enhancement asynchronously
        async def run_enhancement():
            try:
                result = await enhance_rag_response(
                    query=query,
                    existing_response=existing_response,
                    conversation_history=conversation_history
                )
                return result
            except Exception as e:
                logger.error(f"Error enhancing response: {str(e)}")
                raise
        
        # Run the enhancement
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_enhancement())
        loop.close()
        
        # Return the result
        return jsonify({
            'answer': result.get('answer', ''),
            'sources': result.get('sources', []),
            'reasoning_trace': result.get('reasoning_trace', []),
            'context_usage': result.get('context_usage', {}),
            'confidence': result.get('confidence', 0.0),
            'enhanced': result.get('enhanced', False)
        })
    except Exception as e:
        logger.error(f"Error in enhance_response: {str(e)}")
        return jsonify({'error': str(e)}), 500
