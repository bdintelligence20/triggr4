import os
import logging
import re
import threading
import hashlib
from typing import List, Dict, Any, Callable, Optional
import anthropic
import time
from embedding_utils import EmbeddingService, chunk_text, TOKENIZER
from pinecone_client import PineconeClient
from vertex_client import VertexVectorClient

# Import CrossEncoder for re-ranking (install via: pip install sentence-transformers)
from sentence_transformers import CrossEncoder
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token budget constants
MAX_TOTAL_TOKENS = 30000  # Set a safe limit below the 40,000/min rate limit
MAX_CONTEXT_TOKENS = 20000  # Reserve tokens for context
MAX_HISTORY_TOKENS = 8000  # Reserve tokens for history

def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken."""
    if not text:
        return 0
    return len(TOKENIZER.encode(text))

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

class TokenRateLimiter:
    def __init__(self, tokens_per_minute=40000):
        self.tokens_per_minute = tokens_per_minute
        self.token_bucket = tokens_per_minute
        self.last_refill = time.time()
        self.lock = threading.Lock()
        
    def consume(self, tokens):
        """Try to consume tokens from the bucket. Returns True if successful."""
        with self.lock:
            # Refill the bucket based on elapsed time
            now = time.time()
            elapsed = now - self.last_refill
            refill = min(self.tokens_per_minute, 
                         self.token_bucket + int(elapsed * (self.tokens_per_minute / 60)))
            self.token_bucket = refill
            self.last_refill = now
            
            # Check if we can consume tokens
            if tokens <= self.token_bucket:
                self.token_bucket -= tokens
                return True
            return False
            
    def wait_for_tokens(self, tokens, timeout=30):
        """Wait until tokens are available. Returns False if timeout reached."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.consume(tokens):
                return True
            time.sleep(0.5)
        return False

class ResponseCache:
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
        self.lock = threading.Lock()
        
    def get(self, query, context_hash):
        """Get cached response for query+context combination."""
        key = self._make_key(query, context_hash)
        with self.lock:
            return self.cache.get(key)
            
    def set(self, query, context_hash, response):
        """Cache a response."""
        key = self._make_key(query, context_hash)
        with self.lock:
            # Implement LRU eviction if needed
            if len(self.cache) >= self.max_size:
                # Remove oldest key
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            self.cache[key] = response
            
    def _make_key(self, query, context_hash):
        """Create a cache key from query and context hash."""
        return f"{query.strip().lower()}:{context_hash}"
        
    def _hash_context(self, context):
        """Create a hash of the context text."""
        return hashlib.md5(context.encode()).hexdigest()

class RAGSystem:
    def __init__(self, openai_api_key=None, anthropic_api_key=None, pinecone_api_key=None, index_name="knowledge-hub-vectors", organization_id=None, use_vertex=True):
        """Initialize the RAG system with necessary components."""
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.pinecone_api_key = pinecone_api_key or os.environ.get("PINECONE_API_KEY")
        self.organization_id = organization_id
        self.use_vertex = use_vertex
        self.index_name = index_name
        
        # Set timeouts for external API calls
        self.api_timeout = int(os.environ.get("EXTERNAL_API_TIMEOUT", 30))  # Default 30 seconds
        
        if not all([self.openai_api_key, self.anthropic_api_key]):
            missing = []
            if not self.openai_api_key: missing.append("OpenAI")
            if not self.anthropic_api_key: missing.append("Anthropic")
            raise ValueError(f"Missing API keys: {', '.join(missing)}")
        
        self.embedding_service = EmbeddingService(api_key=self.openai_api_key)
        
        # Initialize vector store client (Vertex AI or Pinecone)
        self.vector_client = self._initialize_vector_client()
        
        self.anthropic_client = anthropic.Client(api_key=self.anthropic_api_key)
        self.rate_limiter = TokenRateLimiter()
        self.response_cache = ResponseCache()
        
        logger.info(f"RAG system initialized successfully for organization: {organization_id or 'global'}")
    
    def _initialize_vector_client(self):
        """Initialize the appropriate vector store client based on configuration."""
        if self.use_vertex:
            try:
                logger.info("Attempting to initialize Vertex AI Vector Search client")
                return VertexVectorClient(
                    index_name=self.index_name,
                    organization_id=self.organization_id
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Vertex AI Vector Search: {str(e)}")
                logger.info("Falling back to Pinecone")
                if not self.pinecone_api_key:
                    self.pinecone_api_key = os.environ.get("PINECONE_API_KEY")
                    if not self.pinecone_api_key:
                        raise ValueError("Pinecone API key is required when Vertex AI initialization fails")
        
        # Initialize Pinecone client (either as primary or fallback)
        logger.info("Initializing Pinecone client")
        return PineconeClient(
            api_key=self.pinecone_api_key, 
            index_name=self.index_name,
            organization_id=self.organization_id
        )
        
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
            
        # Step 3: Store vectors in vector store (Vertex AI or Pinecone)
        vectors_stored = self.vector_client.store_vectors(source_id, chunks, embeddings, namespace)
        logger.info(f"Stored {vectors_stored} vectors in vector store for document: {source_id}")
        
        return vectors_stored
        
    def _is_follow_up_question(self, query, history):
        """Detect if this is a follow-up question."""
        follow_up_patterns = [
            r"(?i)what about",
            r"(?i)can you",
            r"(?i)how about",
            r"(?i)tell me more",
            r"(?i)elaborate",
            r"(?i)explain",
            r"(?i)why",
            r"(?i)^and ",
            r"(?i)^but ",
            r"(?i)^so ",
        ]
        
        # Check for pronouns that suggest follow-up
        pronoun_patterns = [
            r"(?i)\bthat\b",
            r"(?i)\bit\b",
            r"(?i)\bthis\b",
            r"(?i)\bthese\b",
            r"(?i)\bthose\b",
            r"(?i)\bthem\b",
        ]
        
        # Check if history exists (indicating ongoing conversation)
        has_history = bool(history.strip())
        
        # Check for follow-up patterns
        for pattern in follow_up_patterns:
            if re.search(pattern, query):
                return True
                
        # Check for pronouns (only if history exists)
        if has_history:
            for pattern in pronoun_patterns:
                if re.search(pattern, query):
                    return True
                    
        return False

    def _is_clarification_question(self, query):
        """Detect if this is asking for clarification of previous answer."""
        clarification_patterns = [
            r"(?i)what do you mean",
            r"(?i)can you clarify",
            r"(?i)don't understand",
            r"(?i)put .* in a table",
            r"(?i)summarize",
            r"(?i)simplify",
            r"(?i)rephrase",
        ]
        
        for pattern in clarification_patterns:
            if re.search(pattern, query):
                return True
                
        return False
        
    def _truncate_history(self, history, max_tokens):
        """Truncate history while preserving most recent exchanges."""
        if not history:
            return ""
            
        lines = history.split('\n')
        
        # Always keep the most recent user-AI exchange
        preserved_lines = []
        i = len(lines) - 1
        
        # Find and preserve the most recent exchange
        user_found = False
        while i >= 0 and not user_found:
            if lines[i].startswith('User:'):
                user_found = True
                # Add this user message and look for corresponding AI response
                preserved_lines.insert(0, lines[i])
            elif lines[i].startswith('AI:') and not user_found:
                # Add the most recent AI message
                preserved_lines.insert(0, lines[i])
            i -= 1
        
        # Add as many previous exchanges as the token budget allows
        remaining_lines = []
        remaining_tokens = max_tokens - count_tokens('\n'.join(preserved_lines))
        
        current_exchange = []
        for j in range(i, -1, -1):
            line = lines[j]
            line_tokens = count_tokens(line)
            
            if line.startswith('User:'):
                current_exchange.insert(0, line)
            elif line.startswith('AI:'):
                current_exchange.insert(0, line)
                
                # Check if we can add this complete exchange
                exchange_text = '\n'.join(current_exchange)
                exchange_tokens = count_tokens(exchange_text)
                
                if exchange_tokens <= remaining_tokens:
                    remaining_lines = current_exchange + remaining_lines
                    remaining_tokens -= exchange_tokens
                    current_exchange = []
                else:
                    # Can't fit this exchange, stop adding more
                    break
        
        # Combine preserved and remaining lines
        return '\n'.join(remaining_lines + preserved_lines)

    def _is_complex_query(self, query):
        """Detect if this is a complex query that would benefit from agent orchestration."""
        complex_patterns = [
            r"(?i)compare .+ and",
            r"(?i)what are the pros and cons",
            r"(?i)analyze .+ from multiple perspectives",
            r"(?i)summarize .+ different viewpoints",
            r"(?i)explain the relationship between",
            r"(?i)what are the different approaches",
            r"(?i)how does .+ contrast with",
        ]
        
        for pattern in complex_patterns:
            if re.search(pattern, query):
                return True
                
        # Check for multiple questions in one query
        question_marks = query.count('?')
        if question_marks > 1:
            return True
            
        return False
        
    def query(self, user_query, namespace=None, top_k=5, category=None, stream_callback=None, history="", language="en", organization_id=None, user_id=None):
        """
        Query the system with a user question and return an AI response using retrieved context.
        
        Parameters:
            user_query (str): The user's question
            namespace (str, optional): The namespace to search in
            top_k (int, optional): Number of results to retrieve
            category (str, optional): Category filter
            stream_callback (callable, optional): Callback for streaming responses
            history (str, optional): Conversation history for follow-up questions
            language (str, optional): Language code for the response (e.g., 'en', 'fr', 'es')
            organization_id (str, optional): Organization ID for filtering
            user_id (str, optional): User ID for tracking
        """
        # Override the instance organization_id if provided in the query
        if organization_id:
            self.organization_id = organization_id
            
        # Log user information if available
        if user_id:
            logger.info(f"Processing query for user: {user_id}")
        logger.info(f"Processing query: '{user_query}'")
        
        # Determine query complexity and adjust top_k
        is_follow_up = self._is_follow_up_question(user_query, history)
        is_clarification = self._is_clarification_question(user_query)
        is_complex = self._is_complex_query(user_query)
        
        if is_complex:
            logger.info("Detected complex query, using agent orchestration")
            try:
                from mcp_integration import MCPIntegration
                import asyncio
                
                mcp = MCPIntegration()
                orchestration_result = asyncio.run(mcp.orchestrate_agents(
                    task=user_query,
                    agent_preferences={
                        "include": ["retriever", "reasoner", "generator"],
                        "exclude": []
                    },
                    execution_parameters={
                        "max_tokens": 1000,
                        "temperature": 0.7
                    }
                ))
                
                if orchestration_result.get("response"):
                    # Get sources for the response
                    query_embedding = self.embedding_service.get_embedding(user_query)
                    if query_embedding:
                        effective_namespace = None
                        if organization_id:
                            effective_namespace = f"org_{organization_id}"
                        elif self.organization_id:
                            effective_namespace = f"org_{self.organization_id}"
                        else:
                            effective_namespace = namespace
                            
                        matched_docs = self.vector_client.query_vectors(
                            query_embedding, 
                            namespace=effective_namespace,
                            top_k=5
                        )
                        
                        # Format sources
                        sources = []
                        for doc in matched_docs:
                            source_id = doc.get('source_id', 'unknown')
                            sources.append({
                                "id": source_id,
                                "relevance_score": doc.get('score', 0)
                            })
                    else:
                        sources = []
                    
                    return {
                        "answer": orchestration_result["response"],
                        "sources": sources,
                        "agents_used": orchestration_result.get("agents_used", []),
                        "reasoning_traces": orchestration_result.get("reasoning_traces", [])
                    }
            except Exception as e:
                logger.warning(f"Agent orchestration failed, falling back to standard RAG: {str(e)}")
                # Fall back to standard RAG if agent orchestration fails
        
        if is_clarification:
            effective_top_k = 2  # Minimal context for clarifications
            logger.info(f"Detected clarification question, using reduced context (top_k={effective_top_k})")
        elif is_follow_up:
            effective_top_k = 3  # Moderate context for follow-ups
            logger.info(f"Detected follow-up question, using moderate context (top_k={effective_top_k})")
        else:
            effective_top_k = top_k  # Full context for new queries
            logger.info(f"Detected new question, using full context (top_k={effective_top_k})")

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
        
        # Use organization_id to determine the namespace
        # If organization_id is provided in the query, use it to override the namespace
        effective_namespace = None
        if organization_id:
            effective_namespace = f"org_{organization_id}"
            logger.info(f"Using organization-specific namespace: {effective_namespace}")
        elif self.organization_id:
            effective_namespace = f"org_{self.organization_id}"
            logger.info(f"Using instance organization namespace: {effective_namespace}")
        else:
            effective_namespace = namespace
            logger.info(f"Using provided namespace: {effective_namespace or 'global_knowledge_base'}")
        
        # Step 2: Query vector store with extra candidates
        extended_top_k = min(effective_top_k + 3, 10)  # Get a few extra candidates
        matched_docs = self.vector_client.query_vectors(
            query_embedding, 
            namespace=effective_namespace,
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
        
        # Deduplicate sources by source_id while preserving the highest relevance score
        deduplicated_sources = {}
        for doc in matched_docs[:effective_top_k]:
            source_id = doc.get('source_id', 'unknown')
            current_score = doc.get('score', 0)
            
            if source_id not in deduplicated_sources or current_score > deduplicated_sources[source_id].get('relevance_score', 0):
                # Get document metadata from Firestore
                try:
                    from firebase_admin import firestore
                    db = firestore.client()
                    doc_ref = db.collection("knowledge_items").document(source_id)
                    doc_data = doc_ref.get().to_dict() if doc_ref.get().exists else {}
                    
                    deduplicated_sources[source_id] = {
                        "id": source_id,
                        "score": current_score,
                        "relevance_score": current_score,  # Keep both for compatibility
                        "document": {
                            "title": doc_data.get('title', 'Unknown Document'),
                            "file_type": doc_data.get('file_type', 'unknown'),
                            "file_url": doc_data.get('file_url', None)
                        },
                        "text": doc['text']  # Keep the text for context
                    }
                except Exception as e:
                    logger.warning(f"Error fetching document metadata for {source_id}: {str(e)}")
                    # Fallback to basic source info if metadata fetch fails
                    deduplicated_sources[source_id] = {
                        "id": source_id,
                        "score": current_score,
                        "relevance_score": current_score,  # Keep both for compatibility
                        "text": doc['text']  # Keep the text for context
                    }
        
        # Apply token budget to context
        context_chunks = []
        context_tokens = 0
        
        for i, (source_id, source) in enumerate(deduplicated_sources.items()):
            chunk_tokens = count_tokens(source['text'])
            
            # Check if adding this chunk would exceed our context token budget
            if context_tokens + chunk_tokens > MAX_CONTEXT_TOKENS:
                logger.info(f"Token budget reached after {i} chunks, stopping context addition")
                break
                
            context_chunks.append(f"Document {i+1}:\n{source['text']}")
            context_tokens += chunk_tokens
        
        context_text = "\n\n---\n\n".join(context_chunks)
        logger.info(f"Context prepared with {len(context_chunks)} chunks, {context_tokens} tokens")
        
        # For follow-up or clarification questions, use the MCP context manager
        if is_follow_up or is_clarification:
            try:
                from mcp_integration import MCPIntegration
                import asyncio
                
                logger.info("Using MCP context manager for follow-up/clarification question")
                
                mcp = MCPIntegration()
                context_operation = asyncio.run(mcp.manage_context(
                    operation="optimize",
                    context_data={
                        "query": user_query,
                        "history": history,
                        "current_context": context_text
                    }
                ))
                
                # Use the optimized context if available
                if context_operation.get("operation_result", {}).get("success", False):
                    optimized_context = context_operation.get("operation_result", {}).get("context", "")
                    if optimized_context:
                        context_text = optimized_context
                        logger.info("Using optimized context from MCP")
            except Exception as e:
                logger.warning(f"MCP context management failed, using standard context: {str(e)}")
                # Fall back to standard context if MCP context management fails
        
        # Smart history truncation
        history_tokens = count_tokens(history)
        if history_tokens > MAX_HISTORY_TOKENS:
            logger.info(f"History exceeds token budget ({history_tokens} > {MAX_HISTORY_TOKENS}), truncating")
            history = self._truncate_history(history, MAX_HISTORY_TOKENS)
            history_tokens = count_tokens(history)
            logger.info(f"History truncated to {history_tokens} tokens")
        
        # Convert deduplicated_sources dict to list for the response
        sources = []
        for source_id, source_data in deduplicated_sources.items():
            source_info = {
                "id": source_id,
                "relevance_score": source_data["relevance_score"]
            }
            
            if "document" in source_data:
                source_info["document"] = source_data["document"]
                
            sources.append(source_info)
        
        # Check total token count
        prompt_tokens = context_tokens + history_tokens + count_tokens(user_query) + 500  # 500 for prompt template
        logger.info(f"Total estimated prompt tokens: {prompt_tokens}")
        
        # Check if we have enough tokens in our rate limit budget
        if not self.rate_limiter.consume(prompt_tokens):
            logger.warning(f"Rate limit would be exceeded with {prompt_tokens} tokens, waiting for token availability")
            if not self.rate_limiter.wait_for_tokens(prompt_tokens, timeout=10):
                logger.error("Timeout waiting for token availability")
                return {
                    "answer": "I'm currently handling too many requests. Please try again in a moment.",
                    "sources": sources
                }
        
        # Check response cache for similar queries
        context_hash = hashlib.md5(context_text.encode()).hexdigest()
        cached_response = self.response_cache.get(user_query, context_hash)
        if cached_response:
            logger.info("Using cached response for similar query")
            return {
                "answer": cached_response,
                "sources": sources
            }
        
        try:
            if stream_callback is None:
                # Non-streaming response: include conversation history and language in the prompt
                response = self.generate_response(
                    context=context_text, 
                    query=user_query, 
                    callback=lambda _: None, 
                    conversation_history=history,
                    language=language
                )
                # Cache the response
                self.response_cache.set(user_query, context_hash, response)
                return {
                    "answer": response,
                    "sources": sources
                }
            else:
                # Streaming response: pass conversation history and language as well
                self.generate_streaming_response(
                    context=context_text, 
                    query=user_query, 
                    callback=stream_callback, 
                    conversation_history=history,
                    language=language
                )
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

            
    def generate_response(self, context, query, callback: Callable[[str], None], conversation_history="", language="en"):
        # Detect language if not provided
        if language == "en":
            # Check for non-Latin scripts first (Arabic, Chinese, Japanese, Korean, etc.)
            if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\u1100-\u11FF\u3040-\u309F\u30A0-\u30FF\u3400-\u4DBF\u4E00-\u9FFF\uAC00-\uD7AF]', query):
                # Arabic script
                if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', query):
                    language = "ar"  # Arabic
                # Korean Hangul
                elif re.search(r'[\u1100-\u11FF\uAC00-\uD7AF]', query):
                    language = "ko"  # Korean
                # Japanese Hiragana/Katakana
                elif re.search(r'[\u3040-\u309F\u30A0-\u30FF]', query):
                    language = "ja"  # Japanese
                # Chinese characters (also used in Japanese and Korean)
                elif re.search(r'[\u4E00-\u9FFF]', query):
                    # Simple heuristic: if there are Hiragana/Katakana, it's Japanese
                    if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', query):
                        language = "ja"  # Japanese
                    # If there are Hangul characters, it's Korean
                    elif re.search(r'[\uAC00-\uD7AF]', query):
                        language = "ko"  # Korean
                    # Otherwise, assume Chinese
                    else:
                        language = "zh"  # Chinese
                # Thai script
                elif re.search(r'[\u0E00-\u0E7F]', query):
                    language = "th"  # Thai
                # Hindi/Devanagari script
                elif re.search(r'[\u0900-\u097F]', query):
                    language = "hi"  # Hindi
            # Then check for Latin-based languages with special characters
            elif re.search(r'[àáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆŠŽ]', query):
                # Check for common words in various languages
                if any(word in query.lower() for word in ['bonjour', 'merci', 'comment', 'pourquoi', 'quand', 'où']):
                    language = "fr"  # French
                elif any(word in query.lower() for word in ['hola', 'gracias', 'cómo', 'por qué', 'cuándo', 'dónde', 'buenos días', 'buenas tardes', 'buenas noches', 'qué', 'quién', 'cómo']):
                    language = "es"  # Spanish
                elif any(word in query.lower() for word in ['guten', 'danke', 'wie', 'warum', 'wann', 'wo']):
                    language = "de"  # German
                elif any(word in query.lower() for word in ['ciao', 'grazie', 'come', 'perché', 'quando', 'dove']):
                    language = "it"  # Italian
                elif any(word in query.lower() for word in ['olá', 'obrigado', 'como', 'por que', 'quando', 'onde']):
                    language = "pt"  # Portuguese
        
        # Language-specific instructions
        language_instruction = ""
        if language != "en":
            language_map = {
                # European languages
                "fr": "Please respond in French.",
                "es": "Please respond in Spanish.",
                "de": "Please respond in German.",
                "it": "Please respond in Italian.",
                "pt": "Please respond in Portuguese.",
                
                # Middle Eastern languages
                "ar": "Please respond in Arabic.",
                "he": "Please respond in Hebrew.",
                "fa": "Please respond in Farsi/Persian.",
                
                # Asian languages
                "zh": "Please respond in Chinese.",
                "ja": "Please respond in Japanese.",
                "ko": "Please respond in Korean.",
                "hi": "Please respond in Hindi.",
                "th": "Please respond in Thai.",
                "vi": "Please respond in Vietnamese.",
                "id": "Please respond in Indonesian.",
                "ms": "Please respond in Malay.",
                
                # African languages
                "af": "Please respond in Afrikaans.",
                "zu": "Please respond in Zulu.",
                "xh": "Please respond in Xhosa.",
                "st": "Please respond in Sesotho.",
                "tn": "Please respond in Setswana.",
                "sw": "Please respond in Swahili."
            }
            language_instruction = language_map.get(language, f"Please respond in {language}.")
        
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
        {language_instruction}
        """
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=8000,
                temperature=1,
                messages=[{"role": "user", "content": prompt}],
                timeout=self.api_timeout  # Add timeout for API calls
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

    def generate_streaming_response(self, context, query, callback: Callable[[str], None], conversation_history="", language="en"):
        # Detect language if not provided
        if language == "en":
            # Check for non-Latin scripts first (Arabic, Chinese, Japanese, Korean, etc.)
            if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\u1100-\u11FF\u3040-\u309F\u30A0-\u30FF\u3400-\u4DBF\u4E00-\u9FFF\uAC00-\uD7AF]', query):
                # Arabic script
                if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', query):
                    language = "ar"  # Arabic
                # Korean Hangul
                elif re.search(r'[\u1100-\u11FF\uAC00-\uD7AF]', query):
                    language = "ko"  # Korean
                # Japanese Hiragana/Katakana
                elif re.search(r'[\u3040-\u309F\u30A0-\u30FF]', query):
                    language = "ja"  # Japanese
                # Chinese characters (also used in Japanese and Korean)
                elif re.search(r'[\u4E00-\u9FFF]', query):
                    # Simple heuristic: if there are Hiragana/Katakana, it's Japanese
                    if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', query):
                        language = "ja"  # Japanese
                    # If there are Hangul characters, it's Korean
                    elif re.search(r'[\uAC00-\uD7AF]', query):
                        language = "ko"  # Korean
                    # Otherwise, assume Chinese
                    else:
                        language = "zh"  # Chinese
                # Thai script
                elif re.search(r'[\u0E00-\u0E7F]', query):
                    language = "th"  # Thai
                # Hindi/Devanagari script
                elif re.search(r'[\u0900-\u097F]', query):
                    language = "hi"  # Hindi
            # Then check for Latin-based languages with special characters
            elif re.search(r'[àáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆŠŽ]', query):
                # Check for common words in various languages
                if any(word in query.lower() for word in ['bonjour', 'merci', 'comment', 'pourquoi', 'quand', 'où']):
                    language = "fr"  # French
                elif any(word in query.lower() for word in ['hola', 'gracias', 'cómo', 'por qué', 'cuándo', 'dónde', 'buenos días', 'buenas tardes', 'buenas noches', 'qué', 'quién', 'cómo']):
                    language = "es"  # Spanish
                elif any(word in query.lower() for word in ['guten', 'danke', 'wie', 'warum', 'wann', 'wo']):
                    language = "de"  # German
                elif any(word in query.lower() for word in ['ciao', 'grazie', 'come', 'perché', 'quando', 'dove']):
                    language = "it"  # Italian
                elif any(word in query.lower() for word in ['olá', 'obrigado', 'como', 'por que', 'quando', 'onde']):
                    language = "pt"  # Portuguese
        
        # Language-specific instructions
        language_instruction = ""
        if language != "en":
            language_map = {
                # European languages
                "fr": "Please respond in French.",
                "es": "Please respond in Spanish.",
                "de": "Please respond in German.",
                "it": "Please respond in Italian.",
                "pt": "Please respond in Portuguese.",
                
                # Middle Eastern languages
                "ar": "Please respond in Arabic.",
                "he": "Please respond in Hebrew.",
                "fa": "Please respond in Farsi/Persian.",
                
                # Asian languages
                "zh": "Please respond in Chinese.",
                "ja": "Please respond in Japanese.",
                "ko": "Please respond in Korean.",
                "hi": "Please respond in Hindi.",
                "th": "Please respond in Thai.",
                "vi": "Please respond in Vietnamese.",
                "id": "Please respond in Indonesian.",
                "ms": "Please respond in Malay.",
                
                # African languages
                "af": "Please respond in Afrikaans.",
                "zu": "Please respond in Zulu.",
                "xh": "Please respond in Xhosa.",
                "st": "Please respond in Sesotho.",
                "tn": "Please respond in Setswana.",
                "sw": "Please respond in Swahili."
            }
            language_instruction = language_map.get(language, f"Please respond in {language}.")
        
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
        {language_instruction}
        """
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.anthropic_client.messages.stream(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=8000,
                    temperature=1,
                    messages=[{"role": "user", "content": prompt}],
                    timeout=self.api_timeout  # Add timeout for streaming API calls
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
