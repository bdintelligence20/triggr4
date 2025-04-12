"""
Example script for integrating the Agentic RAG system with the Knowledge Hub backend.

This script demonstrates how to use the enhanced RAG capabilities in your backend code.
"""

import asyncio
import json
from backend.mcp_integration import MCPIntegration

# Sample data for testing
SAMPLE_DOCUMENT = """
Paris is the capital and most populous city of France, with an estimated population of 2,165,423 residents in 2019 in an area of more than 105 km² (41 sq mi), making it the 34th most densely populated city in the world in 2020. Since the 17th century, Paris has been one of the world's major centres of finance, diplomacy, commerce, fashion, gastronomy, science, and arts, and has sometimes been referred to as the capital of the world or "the City of Light".
"""

SAMPLE_QUERY = "What is the capital of France and what is it known for?"

SAMPLE_CONVERSATION = """
User: Can you tell me about France?
AI: France is a country in Western Europe known for its rich history, culture, and cuisine. It's one of the world's most popular tourist destinations, famous for landmarks like the Eiffel Tower and the Louvre Museum. What would you like to know specifically about France?
"""

async def demonstrate_query():
    """Demonstrate querying the knowledge base with enhanced context management."""
    mcp = MCPIntegration()
    
    print("Querying knowledge base with enhanced context management...")
    result = await mcp.query_knowledge_base(
        query=SAMPLE_QUERY,
        conversation_history=SAMPLE_CONVERSATION,
        context_preferences={
            "allocation": {
                "global": 0.2,
                "task": 0.5,
                "conversation": 0.3
            }
        }
    )
    
    print("\nQuery Result:")
    print(f"Answer: {result['answer']}")
    print(f"Sources: {result['sources']}")
    if 'reasoning_trace' in result:
        print(f"Reasoning Trace: {json.dumps(result['reasoning_trace'], indent=2)}")
    if 'context_usage' in result:
        print(f"Context Usage: {json.dumps(result['context_usage'], indent=2)}")
    
    return result

async def demonstrate_document_processing():
    """Demonstrate document processing with enhanced semantic chunking."""
    mcp = MCPIntegration()
    
    print("\nProcessing document with enhanced semantic chunking...")
    result = await mcp.process_document(
        document_content=SAMPLE_DOCUMENT,
        metadata={
            "title": "Paris",
            "type": "text",
            "organization_id": "demo"
        },
        processing_preferences={
            "max_chunk_size": 500,
            "overlap": 50
        }
    )
    
    print("\nDocument Processing Result:")
    print(f"Message: {result['message']}")
    print(f"Document ID: {result['document_id']}")
    print(f"Vectors Stored: {result['vectors_stored']}")
    print(f"Summary: {result['summary']}")
    
    return result

async def demonstrate_context_management():
    """Demonstrate context management for improved RAG performance."""
    mcp = MCPIntegration()
    
    print("\nManaging context window...")
    result = await mcp.manage_context(
        operation="add",
        context_data={
            "type": "global",
            "content": {
                "text": "Paris is the capital of France.",
                "priority": 0.8
            }
        }
    )
    
    print("\nContext Management Result:")
    print(f"Message: {result['message']}")
    print(f"Context Size: {json.dumps(result['context_size'], indent=2)}")
    print(f"Token Usage: {json.dumps(result['token_usage'], indent=2)}")
    
    return result

async def demonstrate_agent_orchestration():
    """Demonstrate multi-agent orchestration for complex queries."""
    mcp = MCPIntegration()
    
    print("\nOrchestrating multiple agents for a complex task...")
    result = await mcp.orchestrate_agents(
        task="Explain the history and significance of Paris as the capital of France",
        agent_preferences={
            "include": ["retriever", "reasoner", "generator"],
            "exclude": []
        },
        execution_parameters={
            "max_tokens": 1000,
            "temperature": 0.7
        }
    )
    
    print("\nAgent Orchestration Result:")
    print(f"Response: {result['response']}")
    print(f"Agents Used: {result['agents_used']}")
    print(f"Confidence Scores: {json.dumps(result['confidence_scores'], indent=2)}")
    
    return result

async def demonstrate_integration_with_existing_rag():
    """Demonstrate how to integrate with the existing RAG system."""
    from backend.rag_system import process_query
    from backend.langchain_rag import get_retriever
    
    print("\nIntegrating with existing RAG system...")
    print("1. First, get results from the existing RAG system")
    
    # This is a simplified example - in reality, you would use the actual RAG system
    try:
        # Simulate getting results from the existing RAG system
        # existing_result = process_query(SAMPLE_QUERY)
        existing_result = {"answer": "Paris is the capital of France.", "sources": []}
        print(f"Existing RAG result: {existing_result['answer']}")
        
        # Now enhance with the agentic RAG system
        print("2. Now enhance with the agentic RAG system")
        mcp = MCPIntegration()
        enhanced_result = await mcp.query_knowledge_base(
            query=SAMPLE_QUERY,
            conversation_history=SAMPLE_CONVERSATION
        )
        
        print(f"Enhanced RAG result: {enhanced_result['answer']}")
        
        # Compare the results
        print("\nComparison:")
        print(f"- Existing RAG provides: Basic answer with {len(existing_result.get('sources', []))} sources")
        print(f"- Enhanced RAG provides: Comprehensive answer with {len(enhanced_result.get('sources', []))} sources")
        print(f"  Plus: Reasoning traces, context usage metrics, and confidence scores")
        
    except Exception as e:
        print(f"Note: This is a demonstration - integration with the actual RAG system would require customization")
        print(f"Error in demonstration: {str(e)}")

async def main():
    """Run all examples."""
    try:
        # Demonstrate querying with enhanced context management
        await demonstrate_query()
        
        # Demonstrate document processing with enhanced semantic chunking
        await demonstrate_document_processing()
        
        # Demonstrate context management
        await demonstrate_context_management()
        
        # Demonstrate multi-agent orchestration
        await demonstrate_agent_orchestration()
        
        # Demonstrate integration with existing RAG system
        await demonstrate_integration_with_existing_rag()
        
        print("\nThese examples demonstrate how the enhanced Agentic RAG system")
        print("can be integrated with the existing Knowledge Hub backend to")
        print("provide more contextually relevant and comprehensive responses.")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
