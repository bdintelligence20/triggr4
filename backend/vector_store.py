from langchain_community.vectorstores import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from typing import List, Dict, Any, Optional
import logging
import os
import time
from pinecone import Pinecone as PineconeClient, ServerlessSpec

logger = logging.getLogger(__name__)

class EnhancedPineconeStore:
    """Enhanced Pinecone vector store with organization support."""
    
    def __init__(self, api_key: str, index_name: str, organization_id: Optional[str] = None):
        self.api_key = api_key
        self.index_name = index_name
        self.organization_id = organization_id
        self.embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
        
        # Initialize Pinecone
        self.pc = PineconeClient(api_key=self.api_key)
        self._ensure_index_exists()
        
        # Get namespace based on organization
        self.namespace = self._get_namespace()
        
        # Initialize vector store
        self.vector_store = Pinecone.from_existing_index(
            index_name=self.index_name,
            embedding=self.embedding_model,
            namespace=self.namespace
        )
        
        logger.info(f"Initialized EnhancedPineconeStore with namespace: {self.namespace}")
    
    def _ensure_index_exists(self):
        """Ensure the Pinecone index exists."""
        indexes = self.pc.list_indexes()
        
        if self.index_name not in indexes.names():
            logger.info(f"Creating new index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=3072,  # For text-embedding-3-large
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
    
    def _get_namespace(self) -> str:
        """Get the appropriate namespace based on organization_id."""
        if self.organization_id:
            return f"org_{self.organization_id}"
        else:
            return "global_knowledge_base"
    
    def add_documents(self, documents: List[Document], batch_size: int = 10) -> int:
        """Add documents to the vector store."""
        total_docs = len(documents)
        logger.info(f"Adding {total_docs} documents to namespace: {self.namespace}")
        
        # Process in batches
        for i in range(0, total_docs, batch_size):
            batch = documents[i:i+batch_size]
            try:
                self.vector_store.add_documents(batch)
                logger.info(f"Added batch {i//batch_size + 1}/{(total_docs-1)//batch_size + 1}")
                
                # Small delay between batches
                if i + batch_size < total_docs:
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error adding batch {i//batch_size + 1}: {str(e)}")
        
        return total_docs
    
    def similarity_search(self, query: str, k: int = 5, filter_dict: Optional[Dict] = None) -> List[Document]:
        """Perform similarity search."""
        try:
            return self.vector_store.similarity_search(
                query=query,
                k=k,
                filter=filter_dict
            )
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
    
    def hybrid_search(self, query: str, k: int = 5, filter_dict: Optional[Dict] = None) -> List[Document]:
        """Perform hybrid search (semantic + keyword)."""
        try:
            # Import BM25 for keyword search
            from rank_bm25 import BM25Okapi
            import numpy as np
            
            # Get all documents (limited to 1000 for performance)
            all_docs = self.vector_store.similarity_search(
                query=query,
                k=1000,
                filter=filter_dict
            )
            
            if not all_docs:
                return []
            
            # Prepare corpus for BM25
            corpus = [doc.page_content for doc in all_docs]
            tokenized_corpus = [doc.split() for doc in corpus]
            bm25 = BM25Okapi(tokenized_corpus)
            
            # Get BM25 scores
            tokenized_query = query.split()
            bm25_scores = bm25.get_scores(tokenized_query)
            
            # Get vector similarity scores
            vector_results = self.vector_store.similarity_search_with_score(
                query=query,
                k=len(all_docs),
                filter=filter_dict
            )
            vector_scores = [1.0 - score for _, score in vector_results]  # Convert distance to similarity
            
            # Normalize scores
            max_bm25 = max(bm25_scores) if bm25_scores else 1.0
            max_vector = max(vector_scores) if vector_scores else 1.0
            
            normalized_bm25 = [score/max_bm25 for score in bm25_scores]
            normalized_vector = [score/max_vector for score in vector_scores]
            
            # Combine scores (0.7 weight to vector, 0.3 to keyword)
            combined_scores = [0.7*vs + 0.3*bs for vs, bs in zip(normalized_vector, normalized_bm25)]
            
            # Sort documents by combined score
            scored_docs = list(zip(all_docs, combined_scores))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            # Return top k documents
            return [doc for doc, _ in scored_docs[:k]]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            return self.similarity_search(query, k, filter_dict)  # Fallback to regular search
    
    def delete_documents(self, document_ids: List[str]) -> int:
        """Delete documents by ID."""
        try:
            # Get the Pinecone index
            index = self.pc.Index(self.index_name)
            
            # Delete in batches
            batch_size = 100
            total_deleted = 0
            
            for i in range(0, len(document_ids), batch_size):
                batch = document_ids[i:i+batch_size]
                index.delete(ids=batch, namespace=self.namespace)
                total_deleted += len(batch)
                
                # Small delay between batches
                if i + batch_size < len(document_ids):
                    time.sleep(0.5)
            
            return total_deleted
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            return 0
