"""
Vectorized Knowledge Store

This module provides enhanced document processing and retrieval capabilities.
It handles semantic chunking, vector storage, and hybrid retrieval.
"""

import os
import uuid
import logging
import json
import re
from typing import Dict, List, Any, Optional, Union
import asyncio
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class VectorizedStore:
    """
    Vectorized Knowledge Store
    
    This class provides functionality for:
    - Processing documents with semantic chunking
    - Storing document vectors in Pinecone
    - Hybrid retrieval combining dense and sparse embeddings
    """
    
    def __init__(
        self,
        pinecone_api_key: str,
        pinecone_index_name: str,
        openai_api_key: str,
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        Initialize the vectorized store.
        
        Args:
            pinecone_api_key: Pinecone API key
            pinecone_index_name: Pinecone index name
            openai_api_key: OpenAI API key
            embedding_model: OpenAI embedding model name
        """
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_index_name = pinecone_index_name
        self.openai_api_key = openai_api_key
        self.embedding_model = embedding_model
        
        # Initialize Pinecone client lazily
        self.pinecone_client = None
        self.pinecone_index = None
        
        logger.info(f"Initialized vectorized store with index: {pinecone_index_name}")
    
    async def _ensure_pinecone_initialized(self):
        """
        Ensure Pinecone client and index are initialized.
        
        This is done lazily to avoid initializing Pinecone on import.
        """
        if self.pinecone_client is None:
            try:
                # Import Pinecone
                import pinecone
                
                # Initialize Pinecone
                pinecone.init(api_key=self.pinecone_api_key, environment="gcp-starter")
                
                # Get the index
                self.pinecone_client = pinecone
                self.pinecone_index = pinecone.Index(self.pinecone_index_name)
                
                logger.info(f"Connected to Pinecone index: {self.pinecone_index_name}")
            except ImportError:
                logger.error("Pinecone package not installed")
                raise ImportError("Pinecone package not installed. Install with: pip install pinecone-client")
            except Exception as e:
                logger.error(f"Error initializing Pinecone: {str(e)}")
                raise
    
    async def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text using OpenAI API.
        
        Args:
            text: The text to embed
            
        Returns:
            The embedding vector
        """
        try:
            # Import OpenAI
            import openai
            
            # Set API key
            openai.api_key = self.openai_api_key
            
            # Get embedding
            response = await openai.Embedding.acreate(
                input=text,
                model=self.embedding_model
            )
            
            # Return embedding
            return response["data"][0]["embedding"]
        except ImportError:
            logger.error("OpenAI package not installed")
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            raise
    
    async def _get_sparse_embedding(self, text: str) -> Dict[str, Any]:
        """
        Get sparse embedding for text.
        
        This is a simple BM25-style sparse embedding.
        
        Args:
            text: The text to embed
            
        Returns:
            Dict with indices and values for sparse embedding
        """
        # Tokenize text
        tokens = re.findall(r'\b\w+\b', text.lower())
        
        # Count token frequencies
        token_counts = {}
        for token in tokens:
            if token not in token_counts:
                token_counts[token] = 0
            token_counts[token] += 1
        
        # Calculate BM25-style weights
        k1 = 1.2
        b = 0.75
        avg_doc_len = 300  # Assumed average document length
        doc_len = len(tokens)
        
        # Get indices and values
        indices = []
        values = []
        
        for i, (token, count) in enumerate(token_counts.items()):
            # Hash the token to get a stable index
            token_hash = hash(token) % 10000
            indices.append(token_hash)
            
            # Calculate BM25-style weight
            tf = count / doc_len
            weight = tf * (k1 + 1) / (tf + k1 * (1 - b + b * doc_len / avg_doc_len))
            values.append(float(weight))
        
        return {
            "indices": indices,
            "values": values
        }
    
    async def _semantic_chunk(
        self,
        text: str,
        max_chunk_size: int = 1000,
        overlap: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Split text into semantic chunks.
        
        Args:
            text: The text to split
            max_chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks in characters
            
        Returns:
            List of chunks with text and metadata
        """
        # Split text into paragraphs
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Initialize chunks
        chunks = []
        current_chunk = ""
        current_chunk_size = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            paragraph_size = len(paragraph)
            
            # If paragraph is too large, split it into sentences
            if paragraph_size > max_chunk_size:
                sentences = re.findall(r'[^.!?]+[.!?]+', paragraph)
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    sentence_size = len(sentence)
                    
                    # If adding this sentence would exceed max_chunk_size,
                    # save the current chunk and start a new one
                    if current_chunk_size + sentence_size > max_chunk_size and current_chunk:
                        chunks.append({
                            "text": current_chunk.strip(),
                            "size": current_chunk_size,
                        })
                        
                        # Start new chunk with overlap
                        overlap_text = current_chunk[-overlap:] if overlap < current_chunk_size else current_chunk
                        current_chunk = overlap_text + " " + sentence
                        current_chunk_size = len(current_chunk)
                    else:
                        # Add sentence to current chunk
                        if current_chunk:
                            current_chunk += " " + sentence
                        else:
                            current_chunk = sentence
                        current_chunk_size += sentence_size
            else:
                # If adding this paragraph would exceed max_chunk_size,
                # save the current chunk and start a new one
                if current_chunk_size + paragraph_size > max_chunk_size and current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "size": current_chunk_size,
                    })
                    
                    # Start new chunk with overlap
                    overlap_text = current_chunk[-overlap:] if overlap < current_chunk_size else current_chunk
                    current_chunk = overlap_text + "\n\n" + paragraph
                    current_chunk_size = len(current_chunk)
                else:
                    # Add paragraph to current chunk
                    if current_chunk:
                        current_chunk += "\n\n" + paragraph
                    else:
                        current_chunk = paragraph
                    current_chunk_size += paragraph_size
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "size": current_chunk_size,
            })
        
        return chunks
    
    async def process_document(
        self,
        document_content: str,
        metadata: Optional[Dict[str, Any]] = None,
        processing_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a document with enhanced semantic chunking.
        
        Args:
            document_content: The document content
            metadata: Document metadata
            processing_preferences: Processing preferences
            
        Returns:
            Dict containing the processing result
        """
        if not document_content:
            raise ValueError("Document content is required")
        
        # Set default metadata if not provided
        if metadata is None:
            metadata = {}
        
        # Set default processing preferences if not provided
        if processing_preferences is None:
            processing_preferences = {}
        
        # Get processing parameters
        max_chunk_size = processing_preferences.get("max_chunk_size", 1000)
        overlap = processing_preferences.get("overlap", 200)
        
        # Generate document ID if not provided
        document_id = metadata.get("document_id", str(uuid.uuid4()))
        
        # Add timestamp to metadata
        metadata["processed_at"] = datetime.now().isoformat()
        
        # Split document into semantic chunks
        chunks = await self._semantic_chunk(document_content, max_chunk_size, overlap)
        
        # Initialize Pinecone
        await self._ensure_pinecone_initialized()
        
        # Process each chunk
        vectors = []
        for i, chunk in enumerate(chunks):
            # Generate chunk ID
            chunk_id = f"{document_id}_chunk_{i}"
            
            # Get embeddings
            try:
                dense_embedding = await self._get_embedding(chunk["text"])
                sparse_embedding = await self._get_sparse_embedding(chunk["text"])
                
                # Create vector
                vector = {
                    "id": chunk_id,
                    "values": dense_embedding,
                    "sparse_values": sparse_embedding,
                    "metadata": {
                        **metadata,
                        "chunk_index": i,
                        "chunk_count": len(chunks),
                        "text": chunk["text"],
                        "document_id": document_id,
                    }
                }
                
                vectors.append(vector)
            except Exception as e:
                logger.error(f"Error processing chunk {i}: {str(e)}")
                # Continue with other chunks
        
        # Upsert vectors to Pinecone
        try:
            # Upsert in batches of 100
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i+batch_size]
                await asyncio.to_thread(self.pinecone_index.upsert, vectors=batch)
            
            logger.info(f"Upserted {len(vectors)} vectors for document {document_id}")
        except Exception as e:
            logger.error(f"Error upserting vectors: {str(e)}")
            raise
        
        # Generate summary
        summary = await self._generate_summary(document_content)
        
        return {
            "document_id": document_id,
            "vectors_stored": len(vectors),
            "summary": summary,
            "processing_stats": {
                "chunk_count": len(chunks),
                "avg_chunk_size": sum(chunk["size"] for chunk in chunks) / len(chunks) if chunks else 0,
                "max_chunk_size": max(chunk["size"] for chunk in chunks) if chunks else 0,
                "min_chunk_size": min(chunk["size"] for chunk in chunks) if chunks else 0,
            },
        }
    
    async def _generate_summary(self, text: str, max_length: int = 200) -> str:
        """
        Generate a summary of the text.
        
        Args:
            text: The text to summarize
            max_length: Maximum summary length in characters
            
        Returns:
            The summary
        """
        # Simple extractive summarization
        # In a real implementation, this would use a more sophisticated approach
        
        # Split text into sentences
        sentences = re.findall(r'[^.!?]+[.!?]+', text)
        
        if not sentences:
            return ""
        
        # Take the first few sentences as a summary
        summary = ""
        for sentence in sentences:
            if len(summary) + len(sentence) <= max_length:
                summary += sentence
            else:
                break
        
        return summary.strip()
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        alpha: float = 0.5  # Weight for hybrid search (0 = sparse only, 1 = dense only)
    ) -> List[Dict[str, Any]]:
        """
        Search the vector store.
        
        Args:
            query: The query string
            top_k: Number of results to return
            filter: Filter for metadata
            alpha: Weight for hybrid search
            
        Returns:
            List of search results
        """
        if not query:
            raise ValueError("Query is required")
        
        # Initialize Pinecone
        await self._ensure_pinecone_initialized()
        
        # Get embeddings
        try:
            dense_embedding = await self._get_embedding(query)
            sparse_embedding = await self._get_sparse_embedding(query)
        except Exception as e:
            logger.error(f"Error getting embeddings: {str(e)}")
            raise
        
        # Search Pinecone
        try:
            response = await asyncio.to_thread(
                self.pinecone_index.query,
                vector=dense_embedding,
                sparse_vector=sparse_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter,
                alpha=alpha
            )
            
            # Extract results
            results = []
            for match in response.get("matches", []):
                result = {
                    "id": match.get("id", ""),
                    "score": match.get("score", 0.0),
                    "text": match.get("metadata", {}).get("text", ""),
                    "document_id": match.get("metadata", {}).get("document_id", ""),
                    "metadata": match.get("metadata", {}),
                }
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error searching Pinecone: {str(e)}")
            raise
