import tiktoken
import logging
import os
from openai import OpenAI
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize tokenizer and model settings
TOKENIZER = tiktoken.get_encoding("cl100k_base")  # Used for text splitting
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI's embedding model
MAX_TOKENS = 1500  # Max tokens per chunk
OVERLAP_TOKENS = 100  # Token overlap between chunks

class EmbeddingService:
    def __init__(self, api_key=None):
        """Initialize the embedding service with an OpenAI API key."""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
            
        self.client = OpenAI(api_key=self.api_key)
        
    def get_embedding(self, text):
        """Generate an embedding for a single text with retries."""
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.embeddings.create(
                    input=[text],
                    model=EMBEDDING_MODEL
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"Error generating embedding (attempt {attempt+1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("Max retries reached. Failed to generate embedding.")
                    return None
    
    def get_embeddings_batch(self, texts, batch_size=20):
        """Generate embeddings for multiple texts in batches."""
        if not texts:
            logger.warning("No texts provided for embeddings")
            return []
            
        embeddings = []
        
        # Process in batches to avoid rate limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            try:
                logger.info(f"Processing embedding batch {i//batch_size + 1} of {(len(texts)-1)//batch_size + 1}")
                response = self.client.embeddings.create(
                    input=batch,
                    model=EMBEDDING_MODEL
                )
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)
                
                # Add delay between batches to avoid rate limits
                if i + batch_size < len(texts):
                    time.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"Error processing batch {i//batch_size + 1}: {str(e)}")
                # Return partial results for completed batches
                if embeddings:
                    return embeddings
                return None
                
        return embeddings
            
def chunk_text(text, max_tokens=MAX_TOKENS, overlap_tokens=OVERLAP_TOKENS):
    """Split text into chunks with token overlap for better context preservation."""
    if not text:
        return []
        
    tokens = TOKENIZER.encode(text)
    chunks = []
    i = 0
    
    while i < len(tokens):
        # Get chunk with specified max tokens
        chunk_end = min(i + max_tokens, len(tokens))
        chunk = tokens[i:chunk_end]
        
        # If not at the end and chunk is long enough, find a good break point
        if chunk_end < len(tokens) and len(chunk) > 200:
            # Try to break at a sentence or paragraph boundary
            text_chunk = TOKENIZER.decode(chunk)
            for delimiter in ['\n\n', '\n', '.', '!', '?', ';', ':', ' ']:
                # Find the last occurrence of the delimiter
                last_delimiter = text_chunk.rfind(delimiter)
                if last_delimiter > max(0, len(text_chunk) - 100):  # Ensure we're not breaking too early
                    # Recalculate chunk_end based on this delimiter position
                    adjusted_text = text_chunk[:last_delimiter + 1]
                    adjusted_tokens = TOKENIZER.encode(adjusted_text)
                    chunk = adjusted_tokens
                    chunk_end = i + len(adjusted_tokens)
                    break
                    
        # Add the chunk
        chunks.append(TOKENIZER.decode(chunk))
        
        # Move to next chunk with overlap
        i = max(i + 1, chunk_end - overlap_tokens)
    
    logger.info(f"Split text into {len(chunks)} chunks")
    return chunks