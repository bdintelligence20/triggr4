import os
import logging
import time
from google.cloud import aiplatform
import json
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VertexVectorClient:
    def __init__(self, index_name, dimension=3072, organization_id=None, project_id="knowledge-hub-8eaaf", location="us-central1"):
        """Initialize Vertex AI Vector Search client."""
        self.index_name = index_name
        self.dimension = dimension
        self.organization_id = organization_id
        self.project_id = project_id
        self.location = location
        self.initialize_client()

    def initialize_client(self):
        """Initialize the Vertex AI client."""
        try:
            logger.info("Initializing Vertex AI Vector Search client")
            
            # Initialize Vertex AI
            aiplatform.init(project=self.project_id, location=self.location)
            
            # Get or create index
            try:
                self.index = aiplatform.MatchingEngineIndex(index_name=self.index_name)
                logger.info(f"Connected to existing Vector Search index: {self.index_name}")
            except Exception as e:
                logger.info(f"Creating new Vector Search index: {self.index_name}")
                self.index = aiplatform.MatchingEngineIndex.create(
                    display_name=self.index_name,
                    dimensions=self.dimension,
                    approximate_neighbors_count=20,
                    distance_measure_type="COSINE_DISTANCE",
                    description="Knowledge Hub vector index"
                )
                logger.info(f"Created new Vector Search index: {self.index_name}")
                
            # Create index endpoint if it doesn't exist
            try:
                self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=f"{self.index_name}-endpoint")
                logger.info(f"Connected to existing index endpoint: {self.index_name}-endpoint")
            except Exception as e:
                logger.info(f"Creating new index endpoint: {self.index_name}-endpoint")
                self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
                    display_name=f"{self.index_name}-endpoint",
                    description="Knowledge Hub vector index endpoint"
                )
                
                # Deploy index to endpoint
                self.index_endpoint.deploy_index(
                    index=self.index,
                    deployed_index_id=self.index_name
                )
                logger.info(f"Deployed index to endpoint: {self.index_name}")
                
        except Exception as e:
            logger.error(f"Vertex AI initialization failed: {str(e)}")
            raise

    def get_namespace(self, custom_namespace=None):
        """
        Get the appropriate namespace based on organization_id.
        """
        if self.organization_id:
            return f"org_{self.organization_id}"
        elif custom_namespace:
            return custom_namespace
        else:
            return "global_knowledge_base"

    def store_vectors(self, source_id, chunks, embeddings, namespace=None, batch_size=10):
        """Store embeddings and chunks in Vertex AI Vector Search."""
        if len(chunks) != len(embeddings):
            raise ValueError(f"Number of chunks ({len(chunks)}) must match number of embeddings ({len(embeddings)})")
            
        total_vectors = 0
        effective_namespace = self.get_namespace(namespace)
        
        logger.info(f"Preparing to store {len(chunks)} vectors for source: {source_id} in namespace: {effective_namespace}")
        
        try:
            # Prepare datapoints
            datapoints = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"{source_id}_{i}"
                datapoints.append({
                    "id": vector_id,
                    "embedding": embedding,
                    "restricts": {
                        "namespace": effective_namespace,
                        "source_id": source_id,
                        "chunk_index": str(i)
                    },
                    "crowding_tag": source_id,
                    "numeric_restricts": {},
                    "sparse_embedding": {},
                    "string_val": chunk
                })
                
                # If batch is full or this is the last chunk, upsert
                if len(datapoints) >= batch_size or i == len(chunks) - 1:
                    logger.info(f"Upserting batch of {len(datapoints)} vectors (batch {i//batch_size + 1})")
                    self.index.upsert_datapoints(datapoints=datapoints)
                    total_vectors += len(datapoints)
                    datapoints = []  # Clear the batch
                    time.sleep(0.5)  # Small delay between batches
            
            logger.info(f"Successfully stored {total_vectors} vectors in Vertex AI Vector Search")
            return total_vectors
            
        except Exception as e:
            logger.error(f"Error in store_vectors: {str(e)}")
            return total_vectors
    
    def query_vectors(self, query_embedding, namespace=None, top_k=5, filter_dict=None):
        """Query Vertex AI Vector Search for the most similar vectors."""
        effective_namespace = self.get_namespace(namespace)
        
        try:
            logger.info(f"Querying Vertex AI with namespace: '{effective_namespace}', filter: {filter_dict}")
            
            # Prepare filter
            filter_str = f"namespace: {effective_namespace}"
            if filter_dict:
                for key, value in filter_dict.items():
                    filter_str += f" AND {key}: {value}"
            
            # Query the index
            response = self.index_endpoint.find_neighbors(
                deployed_index_id=self.index_name,
                queries=[query_embedding],
                num_neighbors=top_k,
                filter=filter_str
            )
            
            # Process results
            matched_docs = []
            if response and response.neighbor_texts:
                for i, neighbor in enumerate(response.neighbor_texts[0]):
                    matched_docs.append({
                        'text': neighbor.text,
                        'source_id': neighbor.restricts.get('source_id', 'unknown'),
                        'score': response.neighbor_distances[0][i]
                    })
            
            logger.info(f"Found {len(matched_docs)} matches in Vertex AI Vector Search")
            return matched_docs
                
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return []
