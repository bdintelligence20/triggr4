import os
import logging
from typing import List, Dict, Any, Iterator, Callable
import anthropic
import time
from embedding_utils import EmbeddingService, chunk_text
from pinecone_client import PineconeClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self, openai_api_key=None, anthropic_api_key=None, pinecone_api_key=None, index_name="knowledge-hub-vectors"):
        """Initialize the RAG system with necessary components."""
        # Get API keys from environment if not provided
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.pinecone_api_key = pinecone_api_key or os.environ.get("PINECONE_API_KEY")
        
        # Validate API keys
        if not all([self.openai_api_key, self.anthropic_api_key, self.pinecone_api_key]):
            missing = []
            if not self.openai_api_key: missing.append("OpenAI")
            if not self.anthropic_api_key: missing.append("Anthropic")
            if not self.pinecone_api_key: missing.append("Pinecone")
            raise ValueError(f"Missing API keys: {', '.join(missing)}")
        
        # Initialize components
        self.embedding_service = EmbeddingService(api_key=self.openai_api_key)
        self.pinecone_client = PineconeClient(api_key=self.pinecone_api_key, index_name=index_name)
        self.anthropic_client = anthropic.Client(api_key=self.anthropic_api_key)
        
        logger.info("RAG system initialized successfully")
        
    def process_document(self, doc_text, source_id, namespace="global_knowledge_base"):
        """Process a document and store it in the vector database."""
        logger.info(f"Processing document: {source_id}")
        
        # Step 1: Chunk the document
        chunks = chunk_text(doc_text)
        if not chunks:
            logger.warning(f"No chunks created for document: {source_id}")
            return 0
            
        logger.info(f"Created {len(chunks)} chunks")
        
        # Step 2: Generate embeddings for all chunks
        embeddings = self.embedding_service.get_embeddings_batch(chunks)
        if not embeddings:
            logger.error(f"Failed to generate embeddings for document: {source_id}")
            return 0
            
        # Step 3: Store vectors in Pinecone
        vectors_stored = self.pinecone_client.store_vectors(source_id, chunks, embeddings, namespace)
        logger.info(f"Stored {vectors_stored} vectors in Pinecone for document: {source_id}")
        
        return vectors_stored
        
    def query(self, user_query, namespace="global_knowledge_base", top_k=5, category=None, stream_callback=None):
        """
        Query the system with a user question and get an AI response.
        
        Args:
            user_query: The user's question
            namespace: The Pinecone namespace to query
            top_k: Number of top results to retrieve
            category: Optional category filter
            stream_callback: Optional callback function to handle streaming responses
            
        Returns:
            If stream_callback is None: dict containing the full response
            If stream_callback is provided: dict with empty answer and sources
        """
        logger.info(f"Processing query: '{user_query}'")
        
        # Step 1: Generate embedding for the query
        query_embedding = self.embedding_service.get_embedding(user_query)
        if not query_embedding:
            logger.error("Failed to generate embedding for query")
            return {
                "answer": "Sorry, I'm having trouble processing your question. Please try again.",
                "sources": []
            }
            
        # Step 2: Query Pinecone with NO category filter to find all relevant matches
        logger.info(f"Querying with namespace: {namespace}, top_k: {top_k}, with no category filter")
        
        matched_docs = self.pinecone_client.query_vectors(
            query_embedding, 
            namespace=namespace,
            top_k=top_k,
            filter_dict=None  # Remove category filter to find all matches
        )
        
        if not matched_docs:
            logger.info("No relevant documents found")
            return {
                "answer": "I couldn't find any relevant information in our knowledge base.",
                "sources": []
            }
            
        logger.info(f"Found {len(matched_docs)} relevant documents")
        
        # Step 3: Prepare context for Claude
        context_text = "\n\n---\n\n".join([doc['text'] for doc in matched_docs])
        
        # Create source information for citation
        sources = []
        for i, doc in enumerate(matched_docs, start=1):
            sources.append({
                "id": doc.get('source_id', 'unknown'),
                "relevance_score": doc.get('score', 0)
            })
            
        try:
            if stream_callback is None:
                # Non-streaming response
                response = self.generate_response(context_text, user_query)
                return {
                    "answer": response,
                    "sources": sources
                }
            else:
                # Streaming response
                self.generate_streaming_response(context_text, user_query, stream_callback)
                return {
                    "answer": "",  # Empty because content was streamed via callback
                    "sources": sources
                }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "answer": "I found some relevant information but had trouble generating a response.",
                "sources": sources
            }
            
    def generate_response(self, context, query):
        """Generate a well-structured response using Claude based on retrieved context."""
        prompt = f"""
        You are a helpful AI assistant tasked with answering questions based on provided context.
        
        Context:
        {context}
        
        User Question:
        {query}
        
        Answer the question based only on the provided context. If the context doesn't contain relevant information, say so.
        
        Structure your response using proper formatting:
        1. Begin with a clear heading (using markdown ## ) that summarizes the answer
        2. Use bullet points (• or - ) for listing items or features
        3. Use numbered lists (1. 2. 3.) for sequential steps or prioritized points
        4. Use bold text (**text**) for emphasis on important terms or concepts
        5. Use subheadings (using markdown ### ) to organize different parts of your answer
        6. Include a brief summary at the end if the answer is lengthy
        
        Make sure your answer is well-organized, concise, and easy to read while being thorough and accurate.
        """
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=8000,
                    temperature=1,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                return response.content[0].text
                
            except Exception as e:
                logger.error(f"Error from Claude API (attempt {attempt+1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
                    
    def generate_streaming_response(self, context, query, callback: Callable[[str], None]):
        """
        Generate a response with streaming using Claude based on retrieved context.
        Optimized for progressive messaging with clear section breaks.
        
        Args:
            context: The context information
            query: The user's question
            callback: Function that accepts each chunk of text as it's received
        """
        prompt = f"""
        You are a helpful, knowledgeable AI assistant tasked with answering questions based on provided context information.
        
        Context information:
        ```
        {context}
        ```
        
        User Question: {query}
        
        Guidelines:
        1. Answer the question based ONLY on the provided context information.
        2. If the context doesn't contain relevant information, clearly state this.
        3. Be precise, clear, and factual.
        4. Structure your response with clear section breaks - use double newlines between paragraphs and sections.
        5. Start with a brief summary of the answer.
        6. Use clear headings (## Heading) for different sections.
        7. When listing steps or items, put each on a new line with proper numbering or bullet points.
        8. Use clear formatting to make your response easy to read in small chunks.
        9. Make sure each paragraph or section can stand alone and make sense if read separately.
        10. If discussing policies or procedures, clearly separate different aspects.
        
        Format your response with clear section breaks to make it easy to read in chunks.
        """
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.anthropic_client.messages.stream(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=8000,
                    temperature=1,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                ) as stream:
                    for chunk in stream:
                        if chunk.type == "content_block_delta" and chunk.delta.text:
                            callback(chunk.delta.text)
                    
                # Stream completed successfully
                return
                
            except Exception as e:
                logger.error(f"Error from Claude API streaming (attempt {attempt+1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    # On final failure, send error message through callback
                    callback("\n\nI'm sorry, I encountered an error while generating a response. Please try again.")
                    raise