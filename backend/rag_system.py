import os
import logging
from typing import List, Dict, Any
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
        
    def process_document(self, doc_text, source_id, namespace="knowledge_base"):
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
        
    def query(self, user_query, namespace="knowledge_base", top_k=5, category=None):
        """Query the system with a user question and get an AI response."""
        logger.info(f"Processing query: '{user_query}'")
        
        # Step 1: Generate embedding for the query
        query_embedding = self.embedding_service.get_embedding(user_query)
        if not query_embedding:
            logger.error("Failed to generate embedding for query")
            return {
                "answer": "Sorry, I'm having trouble processing your question. Please try again.",
                "sources": []
            }
            
        # Step 2: Query Pinecone with category filter if provided
        filter_dict = {"category": category} if category else None
        matched_docs = self.pinecone_client.query_vectors(
            query_embedding, 
            namespace=namespace,
            top_k=top_k,
            filter_dict=filter_dict
        )
        
        if not matched_docs:
            logger.info("No relevant documents found")
            return {
                "answer": "I couldn't find any relevant information in our knowledge base.",
                "sources": []
            }
            
        logger.info(f"Found {len(matched_docs)} relevant documents")
        
        # Step 3: Generate response using Claude
        context_text = "\n\n---\n\n".join([doc['text'] for doc in matched_docs])
        
        # Create source information for citation
        sources = []
        for i, doc in enumerate(matched_docs, start=1):
            sources.append({
                "id": doc['source_id'],
                "relevance_score": doc['score']
            })
            
        try:
            response = self.generate_response(context_text, user_query)
            
            return {
                "answer": response,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "answer": "I found some relevant information but had trouble generating a response.",
                "sources": sources
            }
            
    def generate_response(self, context, query):
        """Generate a response using Claude based on retrieved context."""
        prompt = f"""
        You are a helpful AI assistant tasked with answering questions based on provided context.
        
        Context:
        {context}
        
        User Question:
        {query}
        
        Answer the question based only on the provided context. If the context doesn't contain relevant information, say so.
        Be concise but thorough in your answer.
        """
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4096,
                    temperature=0.7,
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