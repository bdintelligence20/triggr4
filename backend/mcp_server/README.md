# Agentic RAG System for Knowledge Hub Backend

This directory contains an implementation of an enhanced Retrieval-Augmented Generation (RAG) system with agentic capabilities for the Knowledge Hub backend.

## Overview

The Agentic RAG system significantly improves the existing RAG capabilities of the Knowledge Hub by implementing the following key components:

1. **Unified Context Management Layer**
   - Dynamic context windows that resize based on query complexity
   - Priority-based token allocation
   - Hierarchical context structuring (global/task/conversation levels)

2. **Vectorized Knowledge Store**
   - Multi-modal vector database with versioning support
   - Hybrid retrieval combining dense and sparse embeddings
   - Support for customizable similarity metrics and retrieval algorithms

3. **Contextual Relevance Engine**
   - Real-time reranking of retrieved documents based on conversation flow
   - Attention-based filtering to identify the most relevant passages
   - Semantic chunking that preserves document coherence

4. **Agent Orchestration Protocol**
   - Standardized API for agent-to-agent communication
   - State management for complex multi-agent workflows
   - Role-based context sharing with granular permission controls

## Integration with Existing Backend

This enhanced RAG system integrates seamlessly with the existing Knowledge Hub backend:

1. **API Routes**: New Flask routes in `backend/routes/mcp_routes.py` provide access to the enhanced RAG capabilities
2. **Integration Utilities**: The `backend/mcp_integration.py` module provides utilities for integrating with the existing backend
3. **Existing RAG Enhancement**: The system enhances the existing RAG system without replacing it, allowing for gradual adoption

## Usage

### From the Backend API

The enhanced RAG capabilities are exposed through the following API endpoints:

1. **`/mcp/query`**: Query the knowledge base with advanced context management
2. **`/mcp/process`**: Process a document with enhanced semantic chunking
3. **`/mcp/context`**: Manage the context window for RAG operations
4. **`/mcp/orchestrate`**: Orchestrate multiple specialized agents for complex tasks
5. **`/mcp/capabilities`**: Get information about available agent capabilities

### Direct Integration

You can also integrate directly with the RAG components in your Python code:

```python
from backend.mcp_integration import MCPIntegration

# Initialize the integration
mcp = MCPIntegration()

# Query the knowledge base
result = await mcp.query_knowledge_base(
    query="What is the capital of France?",
    conversation_history="",
    context_preferences={}
)

# Process a document
result = await mcp.process_document(
    document_content="Document text here...",
    metadata={"organization_id": "org123"},
    processing_preferences={}
)
```

## Architecture

The enhanced RAG system is organized into the following components:

- `server.py`: Main server implementation
- `context_manager/`: Unified context management layer
- `knowledge_store/`: Vectorized knowledge store
- `relevance_engine/`: Contextual relevance engine
- `agent_orchestration/`: Agent orchestration protocol

## Key Improvements Over Standard RAG

1. **Adaptive Context Windows**
   - Dynamically resize context windows based on query complexity
   - Prioritize different types of context based on the query

2. **Bidirectional Context Flow**
   - Allow agents to update and enrich the shared knowledge base
   - Maintain context across multiple queries in a conversation

3. **Memory Management Protocol**
   - Implement forgetting mechanisms with importance scoring
   - Prevent context pollution while retaining critical information

4. **Reasoning Trace Integration**
   - Include agent reasoning steps as queryable context
   - Improve transparency and debugging of RAG responses

5. **Multi-Agent Orchestration**
   - Coordinate multiple specialized agents for complex queries
   - Combine strengths of different agent types for better responses
