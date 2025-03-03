import os
from pinecone import Pinecone, ServerlessSpec
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PineconeClient:
    def __init__(self, api_key, index_name, dimension=3072):
        """Initialize Pinecone client with retries."""
        self.api_key = api_key
        self.index_name = index_name
        self.dimension = dimension
        self.pc = None
        self.index = None
        self.initialize_with_retry()

    def initialize_with_retry(self, max_retries=3):
        """Initialize Pinecone with retry logic."""
        for attempt in range(max_retries):
            try:
                logger.info(f"Initializing Pinecone client, attempt {attempt+1}")
                # Initialize the client
                self.pc = Pinecone(api_key=self.api_key)
                
                # Check if the index exists
                indexes = self.pc.list_indexes()
                
                # Create index if it doesn't exist
                if self.index_name not in indexes.names():
                    logger.info(f"Creating new index: {self.index_name}")
                    self.pc.create_index(
                        name=self.index_name,
                        dimension=self.dimension,
                        metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1")
                    )
                
                # Connect to the index
                self.index = self.pc.Index(self.index_name)
                logger.info(f"Successfully connected to Pinecone index: {self.index_name}")
                return
            
            except Exception as e:
                logger.error(f"Pinecone initialization failed (attempt {attempt+1}): {str(e)}")
                if attempt < max_retries - 1:
                    sleep_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error("Max retries reached. Failed to initialize Pinecone.")
                    raise

    def store_vectors(self, source_id, chunks, embeddings, namespace="knowledge_base", batch_size=10):
        """Store embeddings and chunks in Pinecone with batching and retries."""
        if not self.index:
            raise ValueError("Pinecone index not initialized")
            
        if len(chunks) != len(embeddings):
            raise ValueError(f"Number of chunks ({len(chunks)}) must match number of embeddings ({len(embeddings)})")
            
        vectors_to_upsert = []
        max_retries = 3
        total_vectors = 0
        
        logger.info(f"Preparing to store {len(chunks)} vectors for source: {source_id}")
        
        try:
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                # Create vector with metadata
                vector_id = f"{source_id}_{i}"
                metadata = {
                    "text": chunk,
                    "source_id": source_id,
                    "chunk_index": i
                }
                vectors_to_upsert.append((vector_id, embedding, metadata))
                
                # If batch is full or this is the last chunk, upsert
                if len(vectors_to_upsert) >= batch_size or i == len(chunks) - 1:
                    for retry in range(max_retries):
                        try:
                            logger.info(f"Upserting batch of {len(vectors_to_upsert)} vectors (batch {i//batch_size + 1})")
                            self.index.upsert(vectors=vectors_to_upsert, namespace=namespace)
                            total_vectors += len(vectors_to_upsert)
                            vectors_to_upsert = []  # Clear the batch
                            time.sleep(0.5)  # Small delay between batches
                            break
                        except Exception as e:
                            logger.error(f"Error during batch upsert (attempt {retry+1}): {str(e)}")
                            if retry < max_retries - 1:
                                time.sleep(2 ** retry)  # Exponential backoff
                            else:
                                logger.error("Failed to upsert batch after multiple retries")
                                # Continue to next batch rather than failing completely
                                vectors_to_upsert = []
            
            logger.info(f"Successfully stored {total_vectors} vectors in Pinecone")
            return total_vectors
            
        except Exception as e:
            logger.error(f"Error in store_vectors: {str(e)}")
            # Try to upsert any remaining vectors
            if vectors_to_upsert:
                try:
                    self.index.upsert(vectors=vectors_to_upsert, namespace=namespace)
                    total_vectors += len(vectors_to_upsert)
                except Exception as e:
                    logger.error(f"Error upserting final batch: {str(e)}")
            
            return total_vectors
    
    def query_vectors(self, query_embedding, namespace="knowledge_base", top_k=5, filter_dict=None):
        """Query Pinecone for the most similar vectors with retry logic."""
        if not self.index:
            raise ValueError("Pinecone index not initialized")
            
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Querying Pinecone (attempt {attempt+1})")
                
                # Include metadata in results
                results = self.index.query(
                    vector=query_embedding,
                    top_k=top_k,
                    namespace=namespace,
                    include_metadata=True,
                    filter=filter_dict
                )
                
                matches = results.get('matches', [])
                logger.info(f"Found {len(matches)} matches in Pinecone")
                
                # Extract text and metadata from matches
                matched_docs = []
                for match in matches:
                    if 'metadata' in match and 'text' in match['metadata']:
                        matched_docs.append({
                            'text': match['metadata']['text'],
                            'source_id': match['metadata'].get('source_id', 'unknown'),
                            'score': match.get('score', 0)
                        })
                
                return matched_docs
                
            except Exception as e:
                logger.error(f"Query failed (attempt {attempt+1}): {str(e)}")
                if attempt < max_retries - 1:
                    sleep_time = 2 ** attempt
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error("Max retries reached. Failed to query Pinecone.")
                    return []