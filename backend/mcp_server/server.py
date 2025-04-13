"""
Agentic RAG MCP Server

This is the main entry point for the Agentic RAG MCP server.
It initializes the server and connects it to the MCP client.
"""

import os
import sys
import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import MCP components
from context_manager.context_window import ContextManager
from knowledge_store.vectorized_store import VectorizedStore
from relevance_engine.reranker import RelevanceEngine
from agent_orchestration.orchestrator import AgentOrchestrator

# Environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "knowledge-hub-vectors")

# Validate required environment variables
if not OPENAI_API_KEY or not ANTHROPIC_API_KEY or not PINECONE_API_KEY:
    missing = []
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not PINECONE_API_KEY:
        missing.append("PINECONE_API_KEY")
    logger.error(f"Missing required environment variables: {', '.join(missing)}")
    sys.exit(1)

class AgenticRAGServer:
    """
    Agentic RAG MCP Server
    
    This server provides tools and resources for enhanced RAG capabilities:
    - Dynamic context management
    - Semantic chunking
    - Relevance reranking
    - Agent orchestration
    """
    
    def __init__(self):
        """Initialize the server components."""
        # Initialize components
        self.context_manager = ContextManager()
        self.vectorized_store = VectorizedStore(
            pinecone_api_key=PINECONE_API_KEY,
            pinecone_index_name=PINECONE_INDEX_NAME,
            openai_api_key=OPENAI_API_KEY
        )
        self.relevance_engine = RelevanceEngine()
        self.agent_orchestrator = AgentOrchestrator(
            anthropic_api_key=ANTHROPIC_API_KEY,
            openai_api_key=OPENAI_API_KEY
        )
        
        logger.info("Agentic RAG MCP server initialized")
    
    async def list_resources(self) -> Dict[str, Any]:
        """
        List available resources.
        
        Returns:
            Dict containing the available resources.
        """
        return {
            "resources": [
                {
                    "uri": "rag://agents/capabilities",
                    "name": "Agent Capabilities",
                    "mimeType": "application/json",
                    "description": "Information about available agent capabilities",
                },
            ],
        }
    
    async def list_resource_templates(self) -> Dict[str, Any]:
        """
        List resource templates.
        
        Returns:
            Dict containing the resource templates.
        """
        return {
            "resourceTemplates": [
                {
                    "uriTemplate": "rag://context/{contextId}",
                    "name": "Context Window",
                    "mimeType": "application/json",
                    "description": "Access to a specific context window",
                },
            ],
        }
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """
        Read a resource.
        
        Args:
            uri: The resource URI
            
        Returns:
            Dict containing the resource contents
            
        Raises:
            ValueError: If the URI is invalid or the resource is not found
        """
        # Handle agent capabilities resource
        if uri == "rag://agents/capabilities":
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps({
                            "retriever": ["information_retrieval", "document_search", "semantic_search"],
                            "reasoner": ["logical_reasoning", "analysis", "inference", "planning"],
                            "generator": ["response_generation", "summarization", "explanation"],
                            "orchestrator": ["agent_coordination", "task_decomposition", "workflow_management"],
                        }, indent=2),
                    },
                ],
            }
        
        # Handle context window resources
        context_match = uri.startswith("rag://context/")
        if context_match:
            context_id = uri[14:]  # Remove "rag://context/" prefix
            try:
                context = await self.context_manager.get_context(context_id)
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(context, indent=2),
                        },
                    ],
                }
            except ValueError as e:
                raise ValueError(f"Context not found: {context_id}")
        
        raise ValueError(f"Invalid URI: {uri}")
    
    async def list_tools(self) -> Dict[str, Any]:
        """
        List available tools.
        
        Returns:
            Dict containing the available tools.
        """
        return {
            "tools": [
                {
                    "name": "query_knowledge_base",
                    "description": "Query the knowledge base with enhanced context management",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Query string",
                            },
                            "conversation_history": {
                                "type": "string",
                                "description": "Previous conversation history",
                            },
                            "context_preferences": {
                                "type": "object",
                                "description": "Context allocation preferences",
                                "properties": {
                                    "allocation": {
                                        "type": "object",
                                        "properties": {
                                            "global": {"type": "number"},
                                            "task": {"type": "number"},
                                            "conversation": {"type": "number"},
                                        },
                                    },
                                },
                            },
                        },
                        "required": ["query"],
                    },
                },
                {
                    "name": "process_document",
                    "description": "Process a document with enhanced semantic chunking",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "Document content",
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Document metadata",
                            },
                            "processing_preferences": {
                                "type": "object",
                                "description": "Processing preferences",
                            },
                        },
                        "required": ["document_content"],
                    },
                },
                {
                    "name": "manage_context",
                    "description": "Manage the context window for RAG operations",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "description": "Operation to perform (add, remove, optimize)",
                                "enum": ["add", "remove", "optimize", "clear"],
                            },
                            "context_data": {
                                "type": "object",
                                "description": "Context data",
                            },
                        },
                        "required": ["operation"],
                    },
                },
                {
                    "name": "orchestrate_agents",
                    "description": "Orchestrate multiple specialized agents for complex tasks",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "Task to perform",
                            },
                            "agent_preferences": {
                                "type": "object",
                                "description": "Agent preferences",
                                "properties": {
                                    "include": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "exclude": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                            },
                            "execution_parameters": {
                                "type": "object",
                                "description": "Execution parameters",
                            },
                        },
                        "required": ["task"],
                    },
                },
            ],
        }
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool.
        
        Args:
            name: The tool name
            arguments: The tool arguments
            
        Returns:
            Dict containing the tool result
            
        Raises:
            ValueError: If the tool is unknown or the arguments are invalid
        """
        try:
            if name == "query_knowledge_base":
                return await self.handle_query_knowledge_base(arguments)
            elif name == "process_document":
                return await self.handle_process_document(arguments)
            elif name == "manage_context":
                return await self.handle_manage_context(arguments)
            elif name == "orchestrate_agents":
                return await self.handle_orchestrate_agents(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Error calling tool {name}: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error calling tool {name}: {str(e)}",
                    },
                ],
                "isError": True,
            }
    
    async def handle_query_knowledge_base(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle query_knowledge_base tool.
        
        Args:
            arguments: The tool arguments
            
        Returns:
            Dict containing the query result
        """
        query = arguments.get("query")
        conversation_history = arguments.get("conversation_history", "")
        context_preferences = arguments.get("context_preferences", {})
        
        if not query:
            raise ValueError("Query is required")
        
        # Get relevant documents from vector store
        documents = await self.vectorized_store.search(query)
        
        # Apply relevance engine to rerank documents
        reranked_documents = await self.relevance_engine.rerank(query, documents, conversation_history)
        
        # Optimize context window
        context = await self.context_manager.optimize_context(
            query,
            "\n\n".join([doc.get("text", "") for doc in reranked_documents]),
            conversation_history,
            context_preferences
        )
        
        # Generate response using the orchestrator
        response = await self.agent_orchestrator.generate_response(query, context.get("operation_result", {}).get("context", ""), conversation_history)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": response.get("answer", ""),
                },
            ],
            "metadata": {
                "sources": response.get("sources", []),
                "reasoning_trace": response.get("reasoning_trace", []),
                "context_usage": response.get("context_usage", {}),
                "confidence": response.get("confidence", 0.0),
            },
        }
    
    async def handle_process_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle process_document tool.
        
        Args:
            arguments: The tool arguments
            
        Returns:
            Dict containing the processing result
        """
        document_content = arguments.get("document_content")
        metadata = arguments.get("metadata", {})
        processing_preferences = arguments.get("processing_preferences", {})
        
        if not document_content:
            raise ValueError("Document content is required")
        
        # Process document with semantic chunking
        result = await self.vectorized_store.process_document(
            document_content,
            metadata,
            processing_preferences
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Document processed successfully. ID: {result.get('document_id', '')}",
                },
            ],
            "metadata": {
                "document_id": result.get("document_id", ""),
                "vectors_stored": result.get("vectors_stored", 0),
                "summary": result.get("summary", ""),
                "processing_stats": result.get("processing_stats", {}),
            },
        }
    
    async def handle_manage_context(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle manage_context tool.
        
        Args:
            arguments: The tool arguments
            
        Returns:
            Dict containing the operation result
        """
        operation = arguments.get("operation")
        context_data = arguments.get("context_data", {})
        
        if not operation:
            raise ValueError("Operation is required")
        
        # Perform context operation
        result = await self.context_manager.perform_operation(operation, context_data)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Context operation '{operation}' completed successfully",
                },
            ],
            "metadata": {
                "context_size": result.get("context_size", {}),
                "token_usage": result.get("token_usage", {}),
                "operation_result": result.get("operation_result", {}),
            },
        }
    
    async def handle_orchestrate_agents(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle orchestrate_agents tool.
        
        Args:
            arguments: The tool arguments
            
        Returns:
            Dict containing the orchestration result
        """
        task = arguments.get("task")
        agent_preferences = arguments.get("agent_preferences", {})
        execution_parameters = arguments.get("execution_parameters", {})
        
        if not task:
            raise ValueError("Task is required")
        
        # Orchestrate agents
        result = await self.agent_orchestrator.orchestrate(
            task,
            agent_preferences,
            execution_parameters
        )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": result.get("response", ""),
                },
            ],
            "metadata": {
                "agents_used": result.get("agents_used", []),
                "confidence_scores": result.get("confidence_scores", {}),
                "reasoning_traces": result.get("reasoning_traces", []),
                "execution_stats": result.get("execution_stats", {}),
            },
        }

async def main():
    """Run the MCP server."""
    from modelcontextprotocol.server import Server
    from modelcontextprotocol.server.stdio import StdioServerTransport
    
    # Create the server
    server = AgenticRAGServer()
    
    # Create the MCP server
    mcp_server = Server(
        {
            "name": "agentic-rag",
            "version": "0.1.0",
        },
        {
            "capabilities": {
                "resources": {},
                "tools": {},
            },
        }
    )
    
    # Set up request handlers
    mcp_server.set_request_handler("list_resources", server.list_resources)
    mcp_server.set_request_handler("list_resource_templates", server.list_resource_templates)
    mcp_server.set_request_handler("read_resource", server.read_resource)
    mcp_server.set_request_handler("list_tools", server.list_tools)
    mcp_server.set_request_handler("call_tool", server.call_tool)
    
    # Set up error handler
    mcp_server.onerror = lambda error: logger.error(f"MCP error: {error}")
    
    # Connect to the transport
    transport = StdioServerTransport()
    await mcp_server.connect(transport)
    
    logger.info("Agentic RAG MCP server running on stdio")
    
    # Keep the server running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await mcp_server.close()

if __name__ == "__main__":
    asyncio.run(main())
