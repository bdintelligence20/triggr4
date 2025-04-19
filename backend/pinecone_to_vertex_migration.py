import os
import logging
from pinecone_client import PineconeClient
from vertex_client import VertexVectorClient
import time

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_vectors():
    """Migrate vectors from Pinecone to Vertex AI Vector Search."""
    # Initialize clients
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    if not pinecone_api_key:
        logger.error("PINECONE_API_KEY environment variable not set")
        return
        
    pinecone_index_name = os.environ.get("PINECONE_INDEX_NAME", "knowledge-hub-vectors")
    vertex_index_name = os.environ.get("VERTEX_INDEX_NAME", "knowledge-hub-vectors")
    
    logger.info(f"Initializing Pinecone client with index: {pinecone_index_name}")
    pinecone_client = PineconeClient(pinecone_api_key, pinecone_index_name)
    
    logger.info(f"Initializing Vertex AI Vector Search client with index: {vertex_index_name}")
    vertex_client = VertexVectorClient(vertex_index_name)
    
    # Get all namespaces from Pinecone
    logger.info("Fetching namespaces from Pinecone")
    try:
        namespaces = pinecone_client.pc.list_indexes()[pinecone_index_name].namespaces()
        logger.info(f"Found {len(namespaces)} namespaces: {namespaces}")
    except Exception as e:
        logger.error(f"Failed to fetch namespaces: {str(e)}")
        namespaces = ["global_knowledge_base"]  # Default namespace
    
    total_vectors = 0
    
    # For each namespace, fetch and migrate vectors
    for namespace in namespaces:
        logger.info(f"Migrating namespace: {namespace}")
        
        # Fetch vectors from Pinecone (in batches)
        batch_size = 100
        offset = None
        
        while True:
            try:
                logger.info(f"Fetching batch of vectors from namespace: {namespace}, offset: {offset}")
                
                # Fetch vectors
                if offset:
                    fetch_response = pinecone_client.index.fetch(
                        ids=[], 
                        namespace=namespace,
                        limit=batch_size,
                        offset=offset
                    )
                else:
                    fetch_response = pinecone_client.index.fetch(
                        ids=[], 
                        namespace=namespace,
                        limit=batch_size
                    )
                
                vectors = fetch_response.vectors
                
                if not vectors:
                    logger.info(f"No more vectors to fetch from namespace: {namespace}")
                    break
                
                # Prepare data for Vertex AI
                chunks = []
                embeddings = []
                source_ids = set()
                
                for vector_id, vector_data in vectors.items():
                    source_id = vector_data.metadata.get('source_id', 'unknown')
                    chunks.append(vector_data.metadata.get('text', ''))
                    embeddings.append(vector_data.values)
                    source_ids.add(source_id)
                
                # Store in Vertex AI
                primary_source_id = next(iter(source_ids)) if source_ids else "unknown"
                logger.info(f"Storing {len(chunks)} vectors in Vertex AI with source_id: {primary_source_id}")
                
                vertex_client.store_vectors(
                    source_id=primary_source_id,
                    chunks=chunks,
                    embeddings=embeddings,
                    namespace=namespace
                )
                
                total_vectors += len(vectors)
                logger.info(f"Migrated {len(vectors)} vectors, total: {total_vectors}")
                
                # Get next batch
                if len(vectors) < batch_size:
                    logger.info(f"Fetched less than {batch_size} vectors, assuming end of namespace")
                    break
                    
                # Update offset for next batch
                offset = list(vectors.keys())[-1]
                
                # Small delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error during migration of namespace {namespace}: {str(e)}")
                logger.info("Continuing with next namespace")
                break
    
    logger.info(f"Migration complete. Total vectors migrated: {total_vectors}")

if __name__ == "__main__":
    migrate_vectors()
