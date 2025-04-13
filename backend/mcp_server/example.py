"""
Example Usage of Agentic RAG MCP Server

This script demonstrates how to use the Agentic RAG MCP Server for various tasks.
It provides examples of querying the knowledge base, processing documents, and orchestrating agents.
"""

import os
import asyncio
import json
from typing import Dict, List, Any, Optional

# Import MCP integration
from mcp_integration import (
    MCPIntegration,
    enhance_rag_response,
    process_document_with_enhanced_chunking
)

# Sample document content
SAMPLE_DOCUMENT = """
# Knowledge Management Best Practices

Knowledge management (KM) is the process of creating, sharing, using and managing the knowledge and information of an organization. It refers to a multidisciplinary approach to achieve organizational objectives by making the best use of knowledge.

## Key Components of Knowledge Management

1. **People**: The most important component of KM. People create, share, and use knowledge.
2. **Processes**: The methods to acquire, create, organize, share, and transfer knowledge.
3. **Technology**: The tools that support KM, such as document management systems, wikis, and search engines.
4. **Culture**: The environment that fosters knowledge sharing and collaboration.

## Benefits of Knowledge Management

- Improved decision-making
- Enhanced organizational learning
- Increased innovation
- Better customer service
- Reduced duplication of work
- Preserved institutional knowledge

## Challenges in Knowledge Management

- Resistance to sharing knowledge
- Information overload
- Lack of time and resources
- Difficulty in capturing tacit knowledge
- Measuring the value of KM initiatives

## Best Practices for Implementing Knowledge Management

1. **Align KM with business objectives**: Ensure that KM initiatives support the organization's goals.
2. **Start small and scale gradually**: Begin with pilot projects and expand based on success.
3. **Foster a knowledge-sharing culture**: Encourage collaboration and recognize knowledge sharing.
4. **Provide adequate training**: Ensure that employees know how to use KM tools and processes.
5. **Measure and evaluate**: Establish metrics to assess the effectiveness of KM initiatives.
6. **Continuously improve**: Regularly review and refine KM processes and tools.
7. **Secure executive support**: Obtain buy-in from leadership to ensure resources and commitment.

## Conclusion

Effective knowledge management is essential for organizations to leverage their intellectual assets and maintain a competitive advantage. By implementing these best practices, organizations can create a culture of knowledge sharing and continuous learning.
"""

# Sample query
SAMPLE_QUERY = "What are the key components of knowledge management?"

# Sample conversation history
SAMPLE_CONVERSATION_HISTORY = """
User: What is knowledge management?
Assistant: Knowledge management (KM) is the process of creating, sharing, using and managing the knowledge and information of an organization. It refers to a multidisciplinary approach to achieve organizational objectives by making the best use of knowledge.
"""

async def query_knowledge_base_example():
    """Example of querying the knowledge base."""
    print("\n=== Querying Knowledge Base Example ===\n")
    
    # Initialize MCP integration
    mcp = MCPIntegration()
    
    # Query knowledge base
    result = await mcp.query_knowledge_base(
        query=SAMPLE_QUERY,
        conversation_history=SAMPLE_CONVERSATION_HISTORY,
        context_preferences={
            "allocation": {
                "global": 0.3,
                "task": 0.4,
                "conversation": 0.3
            }
        }
    )
    
    # Print result
    print(f"Query: {SAMPLE_QUERY}")
    print(f"Answer: {result.get('answer', '')}")
    print(f"Sources: {json.dumps(result.get('sources', []), indent=2)}")
    print(f"Confidence: {result.get('confidence', 0.0)}")
    
    return result

async def process_document_example():
    """Example of processing a document."""
    print("\n=== Processing Document Example ===\n")
    
    # Process document
    result = await process_document_with_enhanced_chunking(
        document_content=SAMPLE_DOCUMENT,
        metadata={
            "title": "Knowledge Management Best Practices",
            "author": "John Doe",
            "organization_id": "org-123"
        },
        processing_preferences={
            "max_chunk_size": 1000,
            "overlap": 200
        }
    )
    
    # Print result
    print(f"Document ID: {result.get('document_id', '')}")
    print(f"Vectors Stored: {result.get('vectors_stored', 0)}")
    print(f"Summary: {result.get('summary', '')}")
    print(f"Processing Stats: {json.dumps(result.get('processing_stats', {}), indent=2)}")
    
    return result

async def manage_context_example():
    """Example of managing context."""
    print("\n=== Managing Context Example ===\n")
    
    # Initialize MCP integration
    mcp = MCPIntegration()
    
    # Create a new context
    result = await mcp.manage_context(
        operation="add",
        context_data={
            "content": SAMPLE_DOCUMENT,
            "metadata": {
                "title": "Knowledge Management Best Practices",
                "author": "John Doe"
            }
        }
    )
    
    context_id = result.get("context_id", "")
    
    print(f"Created Context ID: {context_id}")
    print(f"Context Size: {json.dumps(result.get('context_size', {}), indent=2)}")
    print(f"Token Usage: {json.dumps(result.get('token_usage', {}), indent=2)}")
    
    # Add to context
    result = await mcp.manage_context(
        operation="add",
        context_data={
            "context_id": context_id,
            "content": SAMPLE_QUERY,
            "level": "task"
        }
    )
    
    print(f"\nAdded to Context")
    print(f"Context Size: {json.dumps(result.get('context_size', {}), indent=2)}")
    print(f"Token Usage: {json.dumps(result.get('token_usage', {}), indent=2)}")
    
    # Optimize context
    result = await mcp.manage_context(
        operation="optimize",
        context_data={
            "context_id": context_id,
            "allocation": {
                "global": 0.3,
                "task": 0.4,
                "conversation": 0.3
            }
        }
    )
    
    print(f"\nOptimized Context")
    print(f"Context Size: {json.dumps(result.get('context_size', {}), indent=2)}")
    print(f"Token Usage: {json.dumps(result.get('token_usage', {}), indent=2)}")
    
    return result

async def orchestrate_agents_example():
    """Example of orchestrating agents."""
    print("\n=== Orchestrating Agents Example ===\n")
    
    # Initialize MCP integration
    mcp = MCPIntegration()
    
    # Orchestrate agents
    result = await mcp.orchestrate_agents(
        task=f"Analyze the following document and answer the question: {SAMPLE_QUERY}\n\nDocument: {SAMPLE_DOCUMENT}",
        agent_preferences={
            "include": ["retriever", "reasoner", "generator"],
            "exclude": []
        },
        execution_parameters={
            "max_tokens": 1000,
            "temperature": 0.7
        }
    )
    
    # Print result
    print(f"Response: {result.get('response', '')}")
    print(f"Agents Used: {result.get('agents_used', [])}")
    print(f"Confidence Scores: {json.dumps(result.get('confidence_scores', {}), indent=2)}")
    print(f"Execution Stats: {json.dumps(result.get('execution_stats', {}), indent=2)}")
    
    return result

async def enhance_response_example():
    """Example of enhancing a response."""
    print("\n=== Enhancing Response Example ===\n")
    
    # Create a simple response
    existing_response = {
        "answer": "Knowledge management has several components.",
        "sources": [
            {
                "id": "doc-123",
                "title": "Knowledge Management Best Practices",
                "relevance": 0.9
            }
        ]
    }
    
    # Enhance response
    result = await enhance_rag_response(
        query=SAMPLE_QUERY,
        existing_response=existing_response,
        conversation_history=SAMPLE_CONVERSATION_HISTORY
    )
    
    # Print result
    print(f"Original Answer: {existing_response.get('answer', '')}")
    print(f"Enhanced Answer: {result.get('answer', '')}")
    print(f"Confidence: {result.get('confidence', 0.0)}")
    
    return result

async def run_all_examples():
    """Run all examples."""
    try:
        # Query knowledge base
        await query_knowledge_base_example()
        
        # Process document
        await process_document_example()
        
        # Manage context
        await manage_context_example()
        
        # Orchestrate agents
        await orchestrate_agents_example()
        
        # Enhance response
        await enhance_response_example()
        
        print("\nAll examples completed successfully!")
    except Exception as e:
        print(f"Error running examples: {str(e)}")

if __name__ == "__main__":
    # Run all examples
    asyncio.run(run_all_examples())
