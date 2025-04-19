"""
Cloud-based migration script for transferring data from Pinecone to Vertex AI Vector Search.
This script is designed to be run as part of the deployment process on Google Cloud Platform.
"""

import os
import logging
import time
import argparse
from google.cloud import aiplatform
from pinecone import Pinecone

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CloudMigration:
    def __init__(self, pinecone_api_key, pinecone_index_name, 
                 project_id, location, vertex_index_name, dimension=3072):
        """Initialize the migration tool with necessary credentials and settings."""
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_index_name = pinecone_index_name
        self.project_id = project_id
        self.location = location
        self.vertex_index_name = vertex_index_name
        self.dimension = dimension
        
        # Initialize clients
        self._init_pinecone()
        self._init_vertex()
        
    def _init_pinecone(self):
        """Initialize Pinecone client."""
        logger.info(f"Initializing Pinecone client for index: {self.pinecone_index_name}")
        try:
            self.pc = Pinecone(api_key=self.pinecone_api_key)
            self.pinecone_index = self.pc.Index(self.pinecone_index_name)
            logger.info("Pinecone client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise
            
    def _init_vertex(self):
        """Initialize Vertex AI Vector Search."""
        logger.info(f"Initializing Vertex AI for project: {self.project_id}, location: {self.location}")
        try:
            aiplatform.init(project=self.project_id, location=self.location)
            
            # Check if index exists
            try:
                self.vertex_index = aiplatform.MatchingEngineIndex(index_name=self.vertex_index_name)
                logger.info(f"Found existing Vector Search index: {self.vertex_index_name}")
            except Exception:
                logger.info(f"Creating new Vector Search index: {self.vertex_index_name}")
                self.vertex_index = aiplatform.MatchingEngineIndex.create(
                    display_name=self.vertex_index_name,
                    dimensions=self.dimension,
                    approximate_neighbors_count=20,
                    distance_measure_type="COSINE_DISTANCE",
                    description="Knowledge Hub vector index"
                )
                
            # Check if index endpoint exists
            try:
                self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
                    index_endpoint_name=f"{self.vertex_index_name}-endpoint"
                )
                logger.info(f"Found existing index endpoint: {self.vertex_index_name}-endpoint")
            except Exception:
                logger.info(f"Creating new index endpoint: {self.vertex_index_name}-endpoint")
                self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
                    display_name=f"{self.vertex_index_name}-endpoint",
                    description="Knowledge Hub vector index endpoint"
                )
                
                # Deploy index to endpoint
                self.index_endpoint.deploy_index(
                    index=self.vertex_index,
                    deployed_index_id=self.vertex_index_name
                )
                logger.info(f"Deployed index to endpoint: {self.vertex_index_name}")
                
            logger.info("Vertex AI Vector Search initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {str(e)}")
            raise
            
    def get_pinecone_namespaces(self):
        """Get all namespaces from Pinecone index."""
        try:
            namespaces = self.pc.list_indexes()[self.pinecone_index_name].namespaces()
            logger.info(f"Found {len(namespaces)} namespaces in Pinecone: {namespaces}")
            return namespaces
        except Exception as e:
            logger.error(f"Failed to get namespaces from Pinecone: {str(e)}")
            return ["global_knowledge_base"]  # Default namespace
            
    def migrate_namespace(self, namespace, batch_size=100):
        """Migrate a single namespace from Pinecone to Vertex AI."""
        logger.info(f"Migrating namespace: {namespace}")
        total_vectors = 0
        offset = None
        
        while True:
            try:
                # Fetch vectors from Pinecone
                logger.info(f"Fetching batch from namespace: {namespace}, offset: {offset}")
                if offset:
                    fetch_response = self.pinecone_index.fetch(
                        ids=[], 
                        namespace=namespace,
                        limit=batch_size,
                        offset=offset
                    )
                else:
                    fetch_response = self.pinecone_index.fetch(
                        ids=[], 
                        namespace=namespace,
                        limit=batch_size
                    )
                
                vectors = fetch_response.vectors
                
                if not vectors:
                    logger.info(f"No more vectors to fetch from namespace: {namespace}")
                    break
                
                # Prepare data for Vertex AI
                datapoints = []
                source_ids = set()
                
                for vector_id, vector_data in vectors.items():
                    source_id = vector_data.metadata.get('source_id', 'unknown')
                    source_ids.add(source_id)
                    
                    datapoints.append({
                        "id": vector_id,
                        "embedding": vector_data.values,
                        "restricts": {
                            "namespace": namespace,
                            "source_id": source_id,
                            "chunk_index": vector_data.metadata.get('chunk_index', '0')
                        },
                        "crowding_tag": source_id,
                        "numeric_restricts": {},
                        "sparse_embedding": {},
                        "string_val": vector_data.metadata.get('text', '')
                    })
                
                # Store in Vertex AI
                logger.info(f"Storing {len(datapoints)} vectors in Vertex AI")
                self.vertex_index.upsert_datapoints(datapoints=datapoints)
                
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
                
        return total_vectors
        
    def migrate_all(self):
        """Migrate all data from Pinecone to Vertex AI."""
        namespaces = self.get_pinecone_namespaces()
        total_vectors = 0
        
        for namespace in namespaces:
            namespace_vectors = self.migrate_namespace(namespace)
            total_vectors += namespace_vectors
            logger.info(f"Completed migration of namespace {namespace}: {namespace_vectors} vectors")
            
        logger.info(f"Migration complete. Total vectors migrated: {total_vectors}")
        return total_vectors

def main():
    """Main entry point for the migration script."""
    # Check if migration should be skipped
    if os.environ.get('SKIP_MIGRATION', '').lower() == 'true':
        logger.info("Migration skipped due to SKIP_MIGRATION=true environment variable")
        return
        
    parser = argparse.ArgumentParser(description='Migrate data from Pinecone to Vertex AI Vector Search')
    parser.add_argument('--pinecone-api-key', required=True, help='Pinecone API key')
    parser.add_argument('--pinecone-index', default='knowledge-hub-vectors', help='Pinecone index name')
    parser.add_argument('--project-id', required=True, help='GCP project ID')
    parser.add_argument('--location', default='us-central1', help='GCP location')
    parser.add_argument('--vertex-index', default='knowledge-hub-vectors', help='Vertex AI index name')
    parser.add_argument('--dimension', type=int, default=3072, help='Vector dimension')
    parser.add_argument('--force', action='store_true', help='Force migration even if already completed')
    
    args = parser.parse_args()
    
    # Create a flag file to track migration completion
    migration_flag_path = '/tmp/migration_completed'
    if os.path.exists(migration_flag_path) and not args.force:
        logger.info("Migration already completed. Use --force to run again.")
        return
    
    try:
        migration = CloudMigration(
            pinecone_api_key=args.pinecone_api_key,
            pinecone_index_name=args.pinecone_index,
            project_id=args.project_id,
            location=args.location,
            vertex_index_name=args.vertex_index,
            dimension=args.dimension
        )
        
        total_vectors = migration.migrate_all()
        
        # Create flag file to indicate successful migration
        if total_vectors > 0:
            with open(migration_flag_path, 'w') as f:
                f.write(f"Migration completed at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total vectors migrated: {total_vectors}\n")
            logger.info(f"Migration flag created at {migration_flag_path}")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
