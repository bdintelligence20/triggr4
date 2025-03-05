import nltk
import logging
import os
from openai import OpenAI
import time
import tiktoken

# Download NLTK’s Punkt sentence tokenizer if not already present
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
from nltk.tokenize import sent_tokenize

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize tokenizer and model settings
TOKENIZER = tiktoken.get_encoding("cl100k_base")  # Used for text splitting
EMBEDDING_MODEL = "text-embedding-3-large"         # OpenAI's embedding model
MAX_TOKENS = 1500                                  # Max tokens per chunk
OVERLAP_TOKENS = 100                               # Token overlap between chunks

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
    """
    Semantic-Aware Chunking:
    Split text into coherent chunks based on sentence boundaries using NLTK.
    This method groups sentences so that each chunk is roughly within the max_tokens limit,
    and ensures natural break points for better context retrieval.
    """
    if not text:
        return []
        
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk_sentences = []
    current_token_count = 0
    
    for sentence in sentences:
        sentence_tokens = TOKENIZER.encode(sentence)
        sentence_token_count = len(sentence_tokens)
        
        # If adding this sentence exceeds the max token limit and we already have some content:
        if current_token_count + sentence_token_count > max_tokens and current_chunk_sentences:
            # Create a chunk from the current sentences
            chunk_text_val = " ".join(current_chunk_sentences)
            chunks.append(chunk_text_val)
            
            # For overlap, retain the last sentence(s)
            overlap = current_chunk_sentences[-1:]
            current_chunk_sentences = overlap.copy()
            current_token_count = len(TOKENIZER.encode(" ".join(current_chunk_sentences)))
        
        current_chunk_sentences.append(sentence)
        current_token_count += sentence_token_count

    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))
    
    logger.info(f"Split text into {len(chunks)} semantic chunks")
    return chunks
