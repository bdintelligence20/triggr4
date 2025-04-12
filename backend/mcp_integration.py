"""
MCP Server Integration

This module provides utilities for integrating the MCP server with the existing Flask application.
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPIntegration:
    """
    Integration utilities for the MCP server.
    
    This class provides methods for interacting with the MCP server from the Flask application.
    """
    
    def __init__(self, server_name: str = "agentic-rag"):
        """
        Initialize the MCP integration.
        
        Args:
            server_name: Name of the MCP server in the configuration
        """
        self.server_name = server_name
        logger.info(f"Initialized MCP integration for server: {server_name}")
    
    async def query_knowledge_base(
        self, 
        query: str, 
        conversation_history: str = "", 
        context_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Query the knowledge base using the MCP server.
        
        Args:
            query: The user's query
            conversation_history: Previous conversation history
            context_preferences: Preferences for context management
        
        Returns:
            Query response
        """
        try:
            # Import the MCP client
            from modelcontextprotocol.client import Client
            
            # Create a client
            client = Client()
            
            # Call the query_knowledge_base tool
            result = await client.call_tool(
                self.server_name,
                "query_knowledge_base",
                {
                    "query": query,
                    "conversation_history": conversation_history,
                    "context_preferences": context_preferences or {}
                }
            )
            
            # Extract the response
            response = {
                "answer": result["content"][0]["text"] if result.get("content") else "",
                "sources": result.get("metadata", {}).get("sources", []),
                "reasoning_trace": result.get("metadata", {}).get("reasoning_trace", []),
                "context_usage": result.get("metadata", {}).get("context_usage", {})
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error querying knowledge base via MCP: {str(e)}")
            return {
                "answer": f"Error querying knowledge base: {str(e)}",
                "sources": [],
                "error": str(e)
            }
    
    async def process_document(
        self, 
        document_content: str, 
        metadata: Dict[str, Any] = None, 
        processing_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process a document using the MCP server.
        
        Args:
            document_content: The document content to process
            metadata: Document metadata
            processing_preferences: Preferences for document processing
        
        Returns:
            Processing results
        """
        try:
            # Import the MCP client
            from modelcontextprotocol.client import Client
            
            # Create a client
            client = Client()
            
            # Call the process_document tool
            result = await client.call_tool(
                self.server_name,
                "process_document",
                {
                    "document_content": document_content,
                    "metadata": metadata or {},
                    "processing_preferences": processing_preferences or {}
                }
            )
            
            # Extract the response
            response = {
                "message": result["content"][0]["text"] if result.get("content") else "",
                "document_id": result.get("metadata", {}).get("document_id", ""),
                "vectors_stored": result.get("metadata", {}).get("vectors_stored", 0),
                "summary": result.get("metadata", {}).get("summary", ""),
                "processing_stats": result.get("metadata", {}).get("processing_stats", {})
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing document via MCP: {str(e)}")
            return {
                "message": f"Error processing document: {str(e)}",
                "error": str(e)
            }
    
    async def manage_context(
        self, 
        operation: str, 
        context_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Manage the context window using the MCP server.
        
        Args:
            operation: The operation to perform (add, remove, prioritize, clear)
            context_data: Data for the operation
        
        Returns:
            Operation result
        """
        try:
            # Import the MCP client
            from modelcontextprotocol.client import Client
            
            # Create a client
            client = Client()
            
            # Call the manage_context tool
            result = await client.call_tool(
                self.server_name,
                "manage_context",
                {
                    "operation": operation,
                    "context_data": context_data or {}
                }
            )
            
            # Extract the response
            response = {
                "message": result["content"][0]["text"] if result.get("content") else "",
                "context_size": result.get("metadata", {}).get("context_size", 0),
                "token_usage": result.get("metadata", {}).get("token_usage", 0),
                "operation_result": result.get("metadata", {}).get("operation_result", {})
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error managing context via MCP: {str(e)}")
            return {
                "message": f"Error managing context: {str(e)}",
                "error": str(e)
            }
    
    async def orchestrate_agents(
        self, 
        task: str, 
        agent_preferences: Dict[str, Any] = None, 
        execution_parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate multiple agents using the MCP server.
        
        Args:
            task: Task description
            agent_preferences: Agent selection preferences
            execution_parameters: Parameters for execution
        
        Returns:
            Task execution result
        """
        try:
            # Import the MCP client
            from modelcontextprotocol.client import Client
            
            # Create a client
            client = Client()
            
            # Call the orchestrate_agents tool
            result = await client.call_tool(
                self.server_name,
                "orchestrate_agents",
                {
                    "task": task,
                    "agent_preferences": agent_preferences or {},
                    "execution_parameters": execution_parameters or {}
                }
            )
            
            # Extract the response
            response = {
                "response": result["content"][0]["text"] if result.get("content") else "",
                "agents_used": result.get("metadata", {}).get("agents_used", []),
                "confidence_scores": result.get("metadata", {}).get("confidence_scores", {}),
                "reasoning_traces": result.get("metadata", {}).get("reasoning_traces", []),
                "execution_stats": result.get("metadata", {}).get("execution_stats", {})
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error orchestrating agents via MCP: {str(e)}")
            return {
                "response": f"Error orchestrating agents: {str(e)}",
                "error": str(e)
            }
    
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """
        Get agent capabilities from the MCP server.
        
        Returns:
            Agent capabilities
        """
        try:
            # Import the MCP client
            from modelcontextprotocol.client import Client
            
            # Create a client
            client = Client()
            
            # Access the agent_capabilities resource
            result = await client.read_resource(
                self.server_name,
                "rag://agents/capabilities"
            )
            
            # Extract the response
            if result and result.get("contents"):
                capabilities = result["contents"][0]["text"]
                return {
                    "capabilities": capabilities,
                    "status": "success"
                }
            else:
                return {
                    "capabilities": {},
                    "status": "error",
                    "message": "No capabilities returned"
                }
            
        except Exception as e:
            logger.error(f"Error getting agent capabilities via MCP: {str(e)}")
            return {
                "capabilities": {},
                "status": "error",
                "message": str(e)
            }

# Example usage in a Flask route
"""
from flask import Blueprint, request, jsonify
import asyncio
from mcp_integration import MCPIntegration

mcp_bp = Blueprint('mcp', __name__)
mcp_integration = MCPIntegration()

@mcp_bp.route('/mcp/query', methods=['POST'])
def mcp_query():
    data = request.get_json()
    query = data.get('query')
    history = data.get('history', '')
    preferences = data.get('preferences', {})
    
    # Call the MCP server
    result = asyncio.run(mcp_integration.query_knowledge_base(
        query=query,
        conversation_history=history,
        context_preferences=preferences
    ))
    
    return jsonify(result)

@mcp_bp.route('/mcp/process', methods=['POST'])
def mcp_process_document():
    data = request.get_json()
    content = data.get('content')
    metadata = data.get('metadata', {})
    preferences = data.get('preferences', {})
    
    # Call the MCP server
    result = asyncio.run(mcp_integration.process_document(
        document_content=content,
        metadata=metadata,
        processing_preferences=preferences
    ))
    
    return jsonify(result)

@mcp_bp.route('/mcp/context', methods=['POST'])
def mcp_manage_context():
    data = request.get_json()
    operation = data.get('operation')
    context_data = data.get('context_data', {})
    
    # Call the MCP server
    result = asyncio.run(mcp_integration.manage_context(
        operation=operation,
        context_data=context_data
    ))
    
    return jsonify(result)

@mcp_bp.route('/mcp/orchestrate', methods=['POST'])
def mcp_orchestrate_agents():
    data = request.get_json()
    task = data.get('task')
    agent_preferences = data.get('agent_preferences', {})
    execution_parameters = data.get('execution_parameters', {})
    
    # Call the MCP server
    result = asyncio.run(mcp_integration.orchestrate_agents(
        task=task,
        agent_preferences=agent_preferences,
        execution_parameters=execution_parameters
    ))
    
    return jsonify(result)

@mcp_bp.route('/mcp/capabilities', methods=['GET'])
def mcp_get_capabilities():
    # Call the MCP server
    result = asyncio.run(mcp_integration.get_agent_capabilities())
    
    return jsonify(result)
"""
