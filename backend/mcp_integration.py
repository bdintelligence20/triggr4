"""
MCP Integration

This module provides integration with the MCP server for enhanced RAG capabilities.
It serves as a bridge between the Flask application and the MCP server.
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

# Import MCP server components
from mcp_server.context_manager import ContextManager
from mcp_server.knowledge_store import VectorizedStore
from mcp_server.relevance_engine import RelevanceEngine
from mcp_server.agent_orchestration import AgentOrchestrator

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
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

class MCPIntegration:
    """
    MCP Integration
    
    This class provides integration with the MCP server for enhanced RAG capabilities.
    It serves as a bridge between the Flask application and the MCP server.
    """
    
    def __init__(self):
        """Initialize the MCP integration."""
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
        
        logger.info("MCP integration initialized")
    
    async def query_knowledge_base(
        self,
        query: str,
        conversation_history: str = "",
        context_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the knowledge base with enhanced context management.
        
        Args:
            query: The query string
            conversation_history: The conversation history
            context_preferences: Context allocation preferences
            
        Returns:
            Dict containing the query result
        """
        if not query:
            raise ValueError("Query is required")
        
        # Set default context preferences if not provided
        if context_preferences is None:
            context_preferences = {
                "allocation": {
                    "global": 0.3,
                    "task": 0.4,
                    "conversation": 0.3
                }
            }
        
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
        response = await self.agent_orchestrator.generate_response(
            query,
            context.get("operation_result", {}).get("context", ""),
            conversation_history
        )
        
        return response
    
    async def process_document(
        self,
        document_content: str,
        metadata: Optional[Dict[str, Any]] = None,
        processing_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a document with enhanced semantic chunking.
        
        Args:
            document_content: The document content
            metadata: Document metadata
            processing_preferences: Processing preferences
            
        Returns:
            Dict containing the processing result
        """
        if not document_content:
            raise ValueError("Document content is required")
        
        # Process document with semantic chunking
        result = await self.vectorized_store.process_document(
            document_content,
            metadata,
            processing_preferences
        )
        
        return result
    
    async def manage_context(
        self,
        operation: str,
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Manage the context window for RAG operations.
        
        Args:
            operation: The operation to perform (add, remove, optimize, clear)
            context_data: Context data
            
        Returns:
            Dict containing the operation result
        """
        if not operation:
            raise ValueError("Operation is required")
        
        # Set default context data if not provided
        if context_data is None:
            context_data = {}
        
        # Perform context operation
        result = await self.context_manager.perform_operation(operation, context_data)
        
        return {
            "message": f"Context operation '{operation}' completed successfully",
            "context_size": result.get("context_size", {}),
            "token_usage": result.get("token_usage", {}),
            "operation_result": result.get("operation_result", {})
        }
    
    async def orchestrate_agents(
        self,
        task: str,
        agent_preferences: Optional[Dict[str, List[str]]] = None,
        execution_parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate multiple specialized agents for complex tasks.
        
        Args:
            task: The task to perform
            agent_preferences: Preferences for which agents to include/exclude
            execution_parameters: Parameters for agent execution
            
        Returns:
            Dict containing the orchestration result
        """
        if not task:
            raise ValueError("Task is required")
        
        # Orchestrate agents
        result = await self.agent_orchestrator.orchestrate(
            task,
            agent_preferences,
            execution_parameters
        )
        
        return result

async def process_document_with_enhanced_chunking(
    document_content: str,
    metadata: Optional[Dict[str, Any]] = None,
    processing_preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a document with enhanced semantic chunking.
    
    Args:
        document_content: The document content
        metadata: Document metadata
        processing_preferences: Processing preferences
        
    Returns:
        Dict containing the processing result
    """
    if not document_content:
        raise ValueError("Document content is required")
    
    # Initialize MCP integration
    mcp = MCPIntegration()
    
    # Process document with semantic chunking
    result = await mcp.process_document(
        document_content,
        metadata,
        processing_preferences
    )
    
    return result

async def enhance_rag_response(
    query: str,
    existing_response: Dict[str, Any],
    conversation_history: str = ""
) -> Dict[str, Any]:
    """
    Enhance an existing RAG response.
    
    Args:
        query: The query string
        existing_response: The existing response
        conversation_history: The conversation history
        
    Returns:
        Dict containing the enhanced response
    """
    if not query or not existing_response:
        raise ValueError("Query and existing response are required")
    
    # Initialize MCP integration
    mcp = MCPIntegration()
    
    # Extract existing answer and sources
    existing_answer = existing_response.get("answer", "")
    existing_sources = existing_response.get("sources", [])
    
    # Prepare task for agent orchestration
    task = f"""
    Enhance the following RAG response:
    
    Query: {query}
    
    Existing Answer: {existing_answer}
    
    Existing Sources: {existing_sources}
    
    Conversation History: {conversation_history}
    
    Please provide a more comprehensive and accurate response.
    """
    
    # Orchestrate agents
    result = await mcp.orchestrate_agents(
        task=task,
        agent_preferences={
            "include": ["reasoner", "generator"],
            "exclude": ["retriever"]
        },
        execution_parameters={
            "max_tokens": 1000,
            "temperature": 0.7
        }
    )
    
    # Extract enhanced response
    enhanced_answer = result.get("response", existing_answer)
    
    # Return enhanced response
    return {
        "answer": enhanced_answer,
        "sources": existing_sources,
        "reasoning_trace": result.get("reasoning_traces", []),
        "context_usage": {
            "context_length": len(existing_answer) + len(conversation_history),
            "history_length": len(conversation_history)
        },
        "confidence": sum(result.get("confidence_scores", {}).values()) / len(result.get("confidence_scores", {})) if result.get("confidence_scores") else 0.5,
        "enhanced": True
    }
