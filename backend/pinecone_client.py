import os
from pinecone import Pinecone, ServerlessSpec
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PineconeClient:
    def __init__(self, api_key, index_name, dimension=3072, organization_id=None):
        """Initialize Pinecone client with retries."""
        self.api_key = api_key
        self.index_name = index_name
        self.dimension = dimension
        self.organization_id = organization_id
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

    def get_namespace(self, custom_namespace=None):
        """
        Get the appropriate namespace based on organization_id.
        If organization_id is provided, use it as the namespace.
        Otherwise, use the provided custom_namespace or default to global.
        """
        if self.organization_id:
            return f"org_{self.organization_id}"
        elif custom_namespace:
            return custom_namespace
        else:
            return "global_knowledge_base"

    def store_vectors(self, source_id, chunks, embeddings, namespace=None, batch_size=10):
        """Store embeddings and chunks in Pinecone with batching and retries."""
        if not self.index:
            raise ValueError("Pinecone index not initialized")
            
        if len(chunks) != len(embeddings):
            raise ValueError(f"Number of chunks ({len(chunks)}) must match number of embeddings ({len(embeddings)})")
            
        vectors_to_upsert = []
        max_retries = 3
        total_vectors = 0
        
        # Get the appropriate namespace
        effective_namespace = self.get_namespace(namespace)
        
        logger.info(f"Preparing to store {len(chunks)} vectors for source: {source_id} in namespace: {effective_namespace}")
        
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
                            self.index.upsert(vectors=vectors_to_upsert, namespace=effective_namespace)
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
                    self.index.upsert(vectors=vectors_to_upsert, namespace=effective_namespace)
                    total_vectors += len(vectors_to_upsert)
                except Exception as e:
                    logger.error(f"Error upserting final batch: {str(e)}")
            
            return total_vectors
    
    def query_vectors(self, query_embedding, namespace=None, top_k=5, filter_dict=None):
        """Query Pinecone for the most similar vectors with retry logic and better filtering."""
        if not self.index:
            raise ValueError("Pinecone index not initialized")
            
        max_retries = 3
        
        # Get the appropriate namespace
        effective_namespace = self.get_namespace(namespace)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Querying Pinecone (attempt {attempt+1}) with namespace: '{effective_namespace}', filter: {filter_dict}")
                
                # Increase top_k to get more candidates for relevance filtering
                fetch_k = min(top_k * 3, 20)  # Get more candidates but cap at 20
                
                # Include metadata in results
                results = self.index.query(
                    vector=query_embedding,
                    top_k=fetch_k,  # Get more candidates
                    namespace=effective_namespace,
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
                
                # Sort by score and return top_k
                matched_docs.sort(key=lambda x: x['score'], reverse=True)
                return matched_docs[:top_k]
                
            except Exception as e:
                logger.error(f"Query failed (attempt {attempt+1}): {str(e)}")
                if attempt < max_retries - 1:
                    sleep_time = 2 ** attempt
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error("Max retries reached. Failed to query Pinecone.")
                    return []
