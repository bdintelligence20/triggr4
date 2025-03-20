import os
import logging
from typing import List, Dict, Any, Callable
import anthropic
import time
from embedding_utils import EmbeddingService, chunk_text
from pinecone_client import PineconeClient

# Import CrossEncoder for re-ranking (install via: pip install sentence-transformers)
from sentence_transformers import CrossEncoder
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def re_rank_passages(query: str, passages: List[str]) -> List[str]:
    """
    Re-rank a list of passages based on their relevance to the query using a cross-encoder.
    """
    pairs = [(query, passage) for passage in passages]
    scores = cross_encoder.predict(pairs)
    ranked = sorted(zip(passages, scores), key=lambda x: x[1], reverse=True)
    return [passage for passage, score in ranked]

def re_rank_matched_docs(query: str, matched_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Re-rank matched documents (each with a 'text' field) based on their relevance to the query.
    """
    passages = [doc['text'] for doc in matched_docs]
    ranked_passages = re_rank_passages(query, passages)
    
    ranked_docs = []
    for passage in ranked_passages:
        for doc in matched_docs:
            if doc['text'] == passage:
                ranked_docs.append(doc)
                break
    return ranked_docs

class RAGSystem:
    def __init__(self, openai_api_key=None, anthropic_api_key=None, pinecone_api_key=None, index_name="knowledge-hub-vectors", organization_id=None):
        """Initialize the RAG system with necessary components."""
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.pinecone_api_key = pinecone_api_key or os.environ.get("PINECONE_API_KEY")
        self.organization_id = organization_id
        
        if not all([self.openai_api_key, self.anthropic_api_key, self.pinecone_api_key]):
            missing = []
            if not self.openai_api_key: missing.append("OpenAI")
            if not self.anthropic_api_key: missing.append("Anthropic")
            if not self.pinecone_api_key: missing.append("Pinecone")
            raise ValueError(f"Missing API keys: {', '.join(missing)}")
        
        self.embedding_service = EmbeddingService(api_key=self.openai_api_key)
        self.pinecone_client = PineconeClient(
            api_key=self.pinecone_api_key, 
            index_name=index_name,
            organization_id=organization_id
        )
        self.anthropic_client = anthropic.Client(api_key=self.anthropic_api_key)
        
        logger.info(f"RAG system initialized successfully for organization: {organization_id or 'global'}")
        
    def process_document(self, doc_text, source_id, namespace=None):
        """Process a document and store it in the vector database."""
        logger.info(f"Processing document: {source_id}")
        
        # Step 1: Chunk the document using semantic-aware chunking
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
        
    def query(self, user_query, namespace=None, top_k=5, category=None, stream_callback=None, history=""):
        """
        Query the system with a user question and return an AI response using retrieved context.
        The optional 'history' parameter is used to include conversation context for follow-up questions.
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
            
        # Remove category filter to ensure all documents in the namespace are searched
        filter_dict = None
        
        # Step 2: Query Pinecone with extra candidates
        extended_top_k = min(top_k + 3, 10)  # Get a few extra candidates
        matched_docs = self.pinecone_client.query_vectors(
            query_embedding, 
            namespace=namespace,
            top_k=extended_top_k,
            filter_dict=filter_dict
        )
        
        if not matched_docs:
            logger.info("No relevant documents found")
            return {
                "answer": "I couldn't find any relevant information in our knowledge base.",
                "sources": []
            }
            
        logger.info(f"Found {len(matched_docs)} relevant documents before re-ranking")
        
        # Re-rank the documents using a cross-encoder
        matched_docs = re_rank_matched_docs(user_query, matched_docs)
        logger.info("Documents re-ranked based on query relevance")
        
        # Step 3: Prepare context from the top_k documents
        context_chunks = []
        for i, doc in enumerate(matched_docs[:top_k]):
            context_chunks.append(f"Document {i+1}:\n{doc['text']}")
        context_text = "\n\n---\n\n".join(context_chunks)
        
        # Prepare source information for citation
        sources = []
        for i, doc in enumerate(matched_docs[:top_k]):
            sources.append({
                "id": doc.get('source_id', 'unknown'),
                "relevance_score": doc.get('score', 0)
            })
        
        try:
            if stream_callback is None:
                # Non-streaming response: include conversation history in the prompt
                response = self.generate_response(context_text, user_query, lambda _: None, conversation_history=history)
                return {
                    "answer": response,
                    "sources": sources
                }
            else:
                # Streaming response: pass conversation history as well
                self.generate_streaming_response(context_text, user_query, stream_callback, conversation_history=history)
                return {
                    "answer": "",  # Content streamed via callback
                    "sources": sources
                }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "answer": "I found some relevant information but had trouble generating a response.",
                "sources": sources
            }

            
    def generate_response(self, context, query, callback: Callable[[str], None], conversation_history=""):
        prompt = f"""
        You are a helpful, knowledgeable, and friendly AI assistant.
        
        Conversation History:
        {conversation_history}
        
        Context information:
        ```
        {context}
        ```
        
        User Question: {query}
        
        Guidelines:
        1. Answer the question based on the provided context and conversation history.
        2. If the context does not fully answer the question, supplement with relevant additional knowledge.
        3. Use a warm and personable tone with a friendly greeting.
        4. Structure your response with clear section breaks.
        5. Use bullet points or numbering for clarity.
        6. Conclude with a friendly sign-off.
        """
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=8000,
                temperature=1,
                messages=[{"role": "user", "content": prompt}]
            )
            full_text = response.content[0].text
            chunk_size = 10
            for i in range(0, len(full_text), chunk_size):
                chunk = full_text[i:i+chunk_size]
                callback(chunk)
                time.sleep(0.01)
            return full_text
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            callback("\n\nI'm sorry, I encountered an error while generating a response. Please try again.")
            raise

    def generate_streaming_response(self, context, query, callback: Callable[[str], None], conversation_history=""):
        prompt = f"""
        You are a helpful, knowledgeable, and friendly AI assistant.
        
        Conversation History:
        {conversation_history}
        
        Context information:
        ```
        {context}
        ```
        
        User Question: {query}
        
        Guidelines:
        1. Answer the question based on the provided context and conversation history.
        2. If the context does not fully answer the question, supplement with additional relevant knowledge.
        3. Use a warm and personable tone with a friendly greeting.
        4. Structure your response with clear section breaks.
        5. Use bullet points or numbering for clarity.
        6. Conclude with a friendly sign-off.
        """
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.anthropic_client.messages.stream(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=8000,
                    temperature=1,
                    messages=[{"role": "user", "content": prompt}]
                ) as stream:
                    for chunk in stream:
                        if chunk.type == "content_block_delta" and chunk.delta.text:
                            callback(chunk.delta.text)
                    return
            except Exception as e:
                logger.error(f"Error from Claude API streaming (attempt {attempt+1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    callback("\n\nI'm sorry, I encountered an error while generating a response. Please try again.")
                    raise
