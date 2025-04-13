# Agentic RAG MCP Server

This Model Context Protocol (MCP) server provides enhanced RAG capabilities for the Knowledge Hub application. It implements a flexible, efficient, and contextually relevant architecture for AI agents.

## Architecture Overview

The Agentic RAG MCP Server is built around four core components:

1. **Unified Context Management Layer**
   - Maintains a dynamic context window that combines retrieved information, agent state, and user interactions
   - Implements priority-based context management to optimize token usage
   - Supports hierarchical context structuring (global/task/conversation levels)

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

## Key Innovations

- **Adaptive Context Windows**: Dynamically resize context windows based on task complexity and agent needs
- **Bidirectional Context Flow**: Allow agents to not only consume but also update and enrich the shared knowledge base
- **Memory Management Protocol**: Implement forgetting mechanisms with importance scoring to prevent context pollution
- **Reasoning Trace Integration**: Include agent reasoning steps as queryable context for improved transparency and debugging

## Directory Structure

```
backend/mcp_server/
├── __init__.py                  # Package initialization
├── server.py                    # Main server implementation
├── context_manager/             # Context management components
│   ├── __init__.py
│   └── context_window.py        # Dynamic context window implementation
├── knowledge_store/             # Knowledge store components
│   ├── __init__.py
│   └── vectorized_store.py      # Vector database integration
├── relevance_engine/            # Relevance engine components
│   ├── __init__.py
│   └── reranker.py              # Document reranking implementation
└── agent_orchestration/         # Agent orchestration components
    ├── __init__.py
    └── orchestrator.py          # Multi-agent orchestration
```

## API Endpoints

The MCP server exposes the following tools through the MCP protocol:

1. **query_knowledge_base**
   - Query the knowledge base with enhanced context management
   - Parameters: query, conversation_history, context_preferences

2. **process_document**
   - Process a document with enhanced semantic chunking
   - Parameters: document_content, metadata, processing_preferences

3. **manage_context**
   - Manage the context window for RAG operations
   - Parameters: operation (add, remove, optimize, clear), context_data

4. **orchestrate_agents**
   - Orchestrate multiple specialized agents for complex tasks
   - Parameters: task, agent_preferences, execution_parameters

## Resources

The MCP server also provides the following resources:

1. **Agent Capabilities**
   - URI: `rag://agents/capabilities`
   - Information about available agent capabilities

2. **Context Window**
   - URI Template: `rag://context/{contextId}`
   - Access to a specific context window

## Integration with Knowledge Hub

The MCP server integrates with the Knowledge Hub application through the following components:

1. **MCP Integration Module**
   - `backend/mcp_integration.py`
   - Provides a bridge between the Flask application and the MCP server

2. **MCP Routes**
   - `backend/routes/mcp_routes.py`
   - Exposes the MCP server capabilities through the Flask API

## Environment Variables

The MCP server requires the following environment variables:

- `OPENAI_API_KEY`: OpenAI API key for embeddings and completions
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude models
- `PINECONE_API_KEY`: Pinecone API key for vector database
- `PINECONE_INDEX_NAME`: Pinecone index name (default: "knowledge-hub-vectors")

## Usage Examples

### Querying the Knowledge Base

```python
from mcp_integration import MCPIntegration

async def query_example():
    mcp = MCPIntegration()
    result = await mcp.query_knowledge_base(
        query="What is the capital of France?",
        conversation_history="We were discussing European countries.",
        context_preferences={
            "allocation": {
                "global": 0.3,
                "task": 0.4,
                "conversation": 0.3
            }
        }
    )
    print(result["answer"])
```

### Processing a Document

```python
from mcp_integration import process_document_with_enhanced_chunking

async def process_document_example():
    result = await process_document_with_enhanced_chunking(
        document_content="This is a sample document...",
        metadata={
            "title": "Sample Document",
            "organization_id": "org-123"
        },
        processing_preferences={
            "max_chunk_size": 1000,
            "overlap": 200
        }
    )
    print(f"Document processed with ID: {result['document_id']}")
```

### Orchestrating Agents

```python
from mcp_integration import MCPIntegration

async def orchestrate_agents_example():
    mcp = MCPIntegration()
    result = await mcp.orchestrate_agents(
        task="Analyze the financial report and summarize key findings.",
        agent_preferences={
            "include": ["retriever", "reasoner", "generator"],
            "exclude": []
        },
        execution_parameters={
            "max_tokens": 1000,
            "temperature": 0.7
        }
    )
    print(result["response"])
```

## Dependencies

- `modelcontextprotocol`: MCP SDK for server implementation
- `pinecone-client`: Pinecone client for vector database
- `openai`: OpenAI client for embeddings and completions
- `anthropic`: Anthropic client for Claude models
- `asyncio`: Asynchronous I/O for concurrent operations

## License

This project is licensed under the MIT License - see the LICENSE file for details.
