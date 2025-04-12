"""
Agentic RAG MCP Server

This module implements a Model Context Protocol (MCP) server for an enhanced
Retrieval-Augmented Generation (RAG) system with agentic capabilities.
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional

from modelcontextprotocol.server import Server
from modelcontextprotocol.server.stdio import StdioServerTransport
from modelcontextprotocol.types import (
    CallToolRequestSchema,
    ErrorCode,
    ListResourcesRequestSchema,
    ListResourceTemplatesRequestSchema,
    ListToolsRequestSchema,
    McpError,
    ReadResourceRequestSchema,
)

# Import components
from .context_manager.context_window import UnifiedContextManager
from .knowledge_store.vectorized_store import VectorizedKnowledgeStore
from .relevance_engine.reranker import ContextualRelevanceEngine
from .agent_orchestration.orchestrator import AgentOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgenticRAGServer:
    """
    MCP server implementation for an enhanced agentic RAG system.
    
    This server provides tools and resources for advanced RAG capabilities including:
    - Unified context management with dynamic context windows
    - Enhanced vectorized knowledge store with multi-modal support
    - Contextual relevance engine with semantic chunking
    - Agent orchestration for multi-agent workflows
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Agentic RAG MCP server with necessary components.
        
        Args:
            config: Configuration dictionary for the server and its components
        """
        self.config = config or {}
        
        # Initialize core components
        self.context_manager = UnifiedContextManager(self.config.get('context', {}))
        self.knowledge_store = VectorizedKnowledgeStore(self.config.get('knowledge_store', {}))
        self.relevance_engine = ContextualRelevanceEngine(self.config.get('relevance', {}))
        self.agent_orchestrator = AgentOrchestrator(self.config.get('agents', {}))
        
        # Initialize MCP server
        self.server = Server(
            {
                "name": "agentic-rag-server",
                "version": "0.1.0",
            },
            {
                "capabilities": {
                    "resources": {},
                    "tools": {},
                }
            }
        )
        
        # Set up request handlers
        self._setup_tool_handlers()
        self._setup_resource_handlers()
        
        # Error handling
        self.server.onerror = lambda error: logger.error(f"[MCP Error] {error}")
    
    def _setup_tool_handlers(self):
        """Set up handlers for MCP tools."""
        # List available tools
        self.server.set_request_handler(ListToolsRequestSchema, self._handle_list_tools)
        
        # Handle tool calls
        self.server.set_request_handler(CallToolRequestSchema, self._handle_call_tool)
    
    def _setup_resource_handlers(self):
        """Set up handlers for MCP resources."""
        # List available resources
        self.server.set_request_handler(ListResourcesRequestSchema, self._handle_list_resources)
        
        # List resource templates
        self.server.set_request_handler(ListResourceTemplatesRequestSchema, self._handle_list_resource_templates)
        
        # Handle resource reads
        self.server.set_request_handler(ReadResourceRequestSchema, self._handle_read_resource)
    
    async def _handle_list_tools(self, request):
        """Handle listing available tools."""
        return {
            "tools": [
                {
                    "name": "query_knowledge_base",
                    "description": "Query the knowledge base with advanced context management",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The user's question"
                            },
                            "conversation_history": {
                                "type": "string",
                                "description": "Previous conversation history"
                            },
                            "context_preferences": {
                                "type": "object",
                                "description": "Preferences for context management"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "process_document",
                    "description": "Process a document with enhanced semantic chunking and multi-modal embedding",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "The document content to process"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Document metadata"
                            },
                            "processing_preferences": {
                                "type": "object",
                                "description": "Preferences for document processing"
                            }
                        },
                        "required": ["document_content"]
                    }
                },
                {
                    "name": "manage_context",
                    "description": "Manage the context window for RAG operations",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "description": "Context operation (add, remove, prioritize)",
                                "enum": ["add", "remove", "prioritize", "clear"]
                            },
                            "context_data": {
                                "type": "object",
                                "description": "Context data for the operation"
                            }
                        },
                        "required": ["operation"]
                    }
                },
                {
                    "name": "orchestrate_agents",
                    "description": "Orchestrate multiple specialized agents for complex tasks",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "Task description"
                            },
                            "agent_preferences": {
                                "type": "object",
                                "description": "Agent selection preferences"
                            },
                            "execution_parameters": {
                                "type": "object",
                                "description": "Parameters for execution"
                            }
                        },
                        "required": ["task"]
                    }
                }
            ]
        }
    
    async def _handle_call_tool(self, request):
        """Handle tool calls."""
        tool_name = request.params.name
        arguments = request.params.arguments
        
        if tool_name == "query_knowledge_base":
            return await self._handle_query_knowledge_base(arguments)
        elif tool_name == "process_document":
            return await self._handle_process_document(arguments)
        elif tool_name == "manage_context":
            return await self._handle_manage_context(arguments)
        elif tool_name == "orchestrate_agents":
            return await self._handle_orchestrate_agents(arguments)
        
        raise McpError(ErrorCode.MethodNotFound, f"Unknown tool: {tool_name}")
    
    async def _handle_query_knowledge_base(self, arguments):
        """
        Handle knowledge base queries with enhanced context management.
        
        Args:
            arguments: Query arguments including the query text, conversation history,
                      and context preferences
        
        Returns:
            Response with answer, sources, reasoning trace, and context usage
        """
        query = arguments.get("query")
        history = arguments.get("conversation_history", "")
        preferences = arguments.get("context_preferences", {})
        
        try:
            # Process the query through our enhanced RAG pipeline
            context = await self.context_manager.prepare_context(query, history, preferences)
            relevant_docs = await self.knowledge_store.retrieve_documents(query, context)
            ranked_docs = await self.relevance_engine.rerank_documents(query, relevant_docs, context)
            response = await self.agent_orchestrator.generate_response(query, ranked_docs, context)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": response["answer"]
                    }
                ],
                "metadata": {
                    "sources": response["sources"],
                    "reasoning_trace": response["reasoning_trace"],
                    "context_usage": response["context_usage"]
                }
            }
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise McpError(ErrorCode.InternalError, f"Error processing query: {str(e)}")
    
    async def _handle_process_document(self, arguments):
        """
        Handle document processing with enhanced semantic chunking.
        
        Args:
            arguments: Document processing arguments including content, metadata,
                      and processing preferences
        
        Returns:
            Processing results including vector counts and document summary
        """
        document_content = arguments.get("document_content")
        metadata = arguments.get("metadata", {})
        preferences = arguments.get("processing_preferences", {})
        
        try:
            # Process the document through our enhanced pipeline
            result = await self.knowledge_store.process_document(
                document_content, metadata, preferences
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Document processed successfully: {result['vectors_stored']} vectors stored"
                    }
                ],
                "metadata": {
                    "document_id": result["document_id"],
                    "vectors_stored": result["vectors_stored"],
                    "summary": result["summary"],
                    "processing_stats": result["processing_stats"]
                }
            }
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise McpError(ErrorCode.InternalError, f"Error processing document: {str(e)}")
    
    async def _handle_manage_context(self, arguments):
        """
        Handle context management operations.
        
        Args:
            arguments: Context management arguments including operation and context data
        
        Returns:
            Updated context status and token usage statistics
        """
        operation = arguments.get("operation")
        context_data = arguments.get("context_data", {})
        
        try:
            # Perform the context management operation
            result = await self.context_manager.manage_context(operation, context_data)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Context {operation} operation completed successfully"
                    }
                ],
                "metadata": {
                    "context_size": result["context_size"],
                    "token_usage": result["token_usage"],
                    "operation_result": result["operation_result"]
                }
            }
        except Exception as e:
            logger.error(f"Error managing context: {str(e)}")
            raise McpError(ErrorCode.InternalError, f"Error managing context: {str(e)}")
    
    async def _handle_orchestrate_agents(self, arguments):
        """
        Handle agent orchestration for complex tasks.
        
        Args:
            arguments: Agent orchestration arguments including task description,
                      agent preferences, and execution parameters
        
        Returns:
            Combined agent responses, reasoning traces, and confidence scores
        """
        task = arguments.get("task")
        agent_preferences = arguments.get("agent_preferences", {})
        execution_parameters = arguments.get("execution_parameters", {})
        
        try:
            # Orchestrate multiple agents for the task
            result = await self.agent_orchestrator.orchestrate_task(
                task, agent_preferences, execution_parameters
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result["response"]
                    }
                ],
                "metadata": {
                    "agents_used": result["agents_used"],
                    "confidence_scores": result["confidence_scores"],
                    "reasoning_traces": result["reasoning_traces"],
                    "execution_stats": result["execution_stats"]
                }
            }
        except Exception as e:
            logger.error(f"Error orchestrating agents: {str(e)}")
            raise McpError(ErrorCode.InternalError, f"Error orchestrating agents: {str(e)}")
    
    async def _handle_list_resources(self, request):
        """Handle listing available resources."""
        return {
            "resources": [
                {
                    "uri": "rag://stats/global",
                    "name": "Global Knowledge Base Statistics",
                    "mimeType": "application/json",
                    "description": "Statistics about the global knowledge base"
                },
                {
                    "uri": "rag://context/current",
                    "name": "Current Context Window",
                    "mimeType": "application/json",
                    "description": "Current context window contents and token allocations"
                },
                {
                    "uri": "rag://agents/capabilities",
                    "name": "Agent Capabilities",
                    "mimeType": "application/json",
                    "description": "Available agent types, specializations, and performance metrics"
                }
            ]
        }
    
    async def _handle_list_resource_templates(self, request):
        """Handle listing available resource templates."""
        return {
            "resourceTemplates": [
                {
                    "uriTemplate": "rag://stats/{organization_id}",
                    "name": "Organization Knowledge Base Statistics",
                    "mimeType": "application/json",
                    "description": "Statistics about an organization's knowledge base"
                },
                {
                    "uriTemplate": "rag://context/{session_id}",
                    "name": "Session Context Window",
                    "mimeType": "application/json",
                    "description": "Context window contents and token allocations for a specific session"
                }
            ]
        }
    
    async def _handle_read_resource(self, request):
        """Handle reading resources."""
        uri = request.params.uri
        
        # Handle static resources
        if uri == "rag://stats/global":
            return await self._handle_global_stats()
        elif uri == "rag://context/current":
            return await self._handle_current_context()
        elif uri == "rag://agents/capabilities":
            return await self._handle_agent_capabilities()
        
        # Handle templated resources
        if uri.startswith("rag://stats/"):
            organization_id = uri.replace("rag://stats/", "")
            return await self._handle_organization_stats(organization_id)
        elif uri.startswith("rag://context/"):
            session_id = uri.replace("rag://context/", "")
            return await self._handle_session_context(session_id)
        
        raise McpError(ErrorCode.InvalidRequest, f"Unknown resource URI: {uri}")
    
    async def _handle_global_stats(self):
        """Handle global knowledge base statistics resource."""
        try:
            stats = await self.knowledge_store.get_global_stats()
            
            return {
                "contents": [
                    {
                        "uri": "rag://stats/global",
                        "mimeType": "application/json",
                        "text": str(stats)
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Error getting global stats: {str(e)}")
            raise McpError(ErrorCode.InternalError, f"Error getting global stats: {str(e)}")
    
    async def _handle_current_context(self):
        """Handle current context window resource."""
        try:
            context = await self.context_manager.get_current_context()
            
            return {
                "contents": [
                    {
                        "uri": "rag://context/current",
                        "mimeType": "application/json",
                        "text": str(context)
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Error getting current context: {str(e)}")
            raise McpError(ErrorCode.InternalError, f"Error getting current context: {str(e)}")
    
    async def _handle_agent_capabilities(self):
        """Handle agent capabilities resource."""
        try:
            capabilities = await self.agent_orchestrator.get_capabilities()
            
            return {
                "contents": [
                    {
                        "uri": "rag://agents/capabilities",
                        "mimeType": "application/json",
                        "text": str(capabilities)
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Error getting agent capabilities: {str(e)}")
            raise McpError(ErrorCode.InternalError, f"Error getting agent capabilities: {str(e)}")
    
    async def _handle_organization_stats(self, organization_id):
        """Handle organization knowledge base statistics resource."""
        try:
            stats = await self.knowledge_store.get_organization_stats(organization_id)
            
            return {
                "contents": [
                    {
                        "uri": f"rag://stats/{organization_id}",
                        "mimeType": "application/json",
                        "text": str(stats)
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Error getting organization stats: {str(e)}")
            raise McpError(ErrorCode.InternalError, f"Error getting organization stats: {str(e)}")
    
    async def _handle_session_context(self, session_id):
        """Handle session context window resource."""
        try:
            context = await self.context_manager.get_session_context(session_id)
            
            return {
                "contents": [
                    {
                        "uri": f"rag://context/{session_id}",
                        "mimeType": "application/json",
                        "text": str(context)
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Error getting session context: {str(e)}")
            raise McpError(ErrorCode.InternalError, f"Error getting session context: {str(e)}")
    
    async def run(self):
        """Run the MCP server."""
        transport = StdioServerTransport()
        await self.server.connect(transport)
        logger.info("Agentic RAG MCP server running")

# This would be used when running as a standalone MCP server
if __name__ == "__main__":
    import asyncio
    
    server = AgenticRAGServer()
    asyncio.run(server.run())
