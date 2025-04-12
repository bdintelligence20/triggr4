"""
Contextual Relevance Engine

This module implements an advanced reranking system for RAG with
attention-based filtering, semantic chunking, and coherence preservation.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextualRelevanceEngine:
    """
    Advanced reranking system for RAG.
    
    This class provides:
    - Real-time reranking of retrieved documents based on conversation flow
    - Attention-based filtering to identify the most relevant passages
    - Semantic chunking that preserves document coherence
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Contextual Relevance Engine.
        
        Args:
            config: Configuration dictionary for the relevance engine
        """
        self.config = config or {}
        
        # Default configuration
        self.reranking_model = self.config.get('reranking_model', 'cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.attention_threshold = self.config.get('attention_threshold', 0.5)
        self.coherence_weight = self.config.get('coherence_weight', 0.3)
        self.recency_weight = self.config.get('recency_weight', 0.2)
        
        logger.info(f"Initialized ContextualRelevanceEngine with reranking model: {self.reranking_model}")
    
    async def rerank_documents(
        self, 
        query: str, 
        documents: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Rerank retrieved documents based on contextual relevance.
        
        Args:
            query: The query text
            documents: Retrieved documents with scores
            context: Query context
        
        Returns:
            Reranked documents with updated scores
        """
        start_time = time.time()
        
        if not documents:
            logger.info("No documents to rerank")
            return []
        
        # Extract query complexity from context
        query_complexity = context.get('query_complexity', 0.5)
        
        # Apply attention-based filtering
        filtered_docs = await self._apply_attention_filter(query, documents, query_complexity)
        
        # Apply semantic coherence preservation
        coherent_docs = await self._preserve_coherence(filtered_docs)
        
        # Apply conversation flow awareness
        if 'conversation' in context:
            conversation_aware_docs = await self._apply_conversation_awareness(
                query, coherent_docs, context['conversation']
            )
        else:
            conversation_aware_docs = coherent_docs
        
        # Final reranking
        reranked_docs = await self._final_rerank(query, conversation_aware_docs, context)
        
        processing_time = time.time() - start_time
        logger.info(f"Reranked {len(documents)} documents in {processing_time:.2f}s")
        
        return reranked_docs
    
    async def _apply_attention_filter(
        self, 
        query: str, 
        documents: List[Dict[str, Any]], 
        query_complexity: float
    ) -> List[Dict[str, Any]]:
        """
        Apply attention-based filtering to identify the most relevant passages.
        
        Args:
            query: The query text
            documents: Retrieved documents with scores
            query_complexity: Query complexity score (0.0 to 1.0)
        
        Returns:
            Filtered documents with attention scores
        """
        # In a real implementation, this would use a sophisticated attention mechanism
        # For now, we'll use a simplified approach
        
        # Adjust attention threshold based on query complexity
        adjusted_threshold = self.attention_threshold * (1.0 - 0.3 * query_complexity)
        
        # Calculate attention scores
        docs_with_attention = []
        for doc in documents:
            # Simple attention score based on term overlap
            query_terms = set(query.lower().split())
            doc_terms = set(doc['text'].lower().split())
            term_overlap = len(query_terms.intersection(doc_terms)) / max(1, len(query_terms))
            
            # Combine with original score
            attention_score = 0.7 * doc['score'] + 0.3 * term_overlap
            
            # Only keep documents above the threshold
            if attention_score >= adjusted_threshold:
                docs_with_attention.append({
                    **doc,
                    'attention_score': attention_score
                })
        
        logger.info(f"Attention filter: {len(documents)} -> {len(docs_with_attention)} documents")
        return docs_with_attention
    
    async def _preserve_coherence(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply semantic coherence preservation to maintain document context.
        
        Args:
            documents: Documents with attention scores
        
        Returns:
            Documents with coherence scores
        """
        # In a real implementation, this would use a sophisticated coherence model
        # For now, we'll use a simplified approach
        
        # Group documents by source
        docs_by_source = {}
        for doc in documents:
            source_id = doc.get('document_id', 'unknown')
            if source_id not in docs_by_source:
                docs_by_source[source_id] = []
            docs_by_source[source_id].append(doc)
        
        # Apply coherence scoring
        coherent_docs = []
        for source_id, source_docs in docs_by_source.items():
            # Sort by chunk index if available
            source_docs.sort(key=lambda d: d.get('metadata', {}).get('chunk_index', 0))
            
            # Apply coherence boost to adjacent chunks
            for i, doc in enumerate(source_docs):
                coherence_boost = 0.0
                
                # Boost for being part of a sequence
                if len(source_docs) > 1:
                    coherence_boost += 0.1
                
                # Additional boost for chunks with adjacent chunks
                if i > 0:
                    coherence_boost += 0.1
                if i < len(source_docs) - 1:
                    coherence_boost += 0.1
                
                # Apply coherence boost
                coherence_score = doc.get('attention_score', doc.get('score', 0)) * (1.0 + self.coherence_weight * coherence_boost)
                
                coherent_docs.append({
                    **doc,
                    'coherence_score': coherence_score
                })
        
        logger.info(f"Coherence preservation applied to {len(coherent_docs)} documents")
        return coherent_docs
    
    async def _apply_conversation_awareness(
        self, 
        query: str, 
        documents: List[Dict[str, Any]], 
        conversation: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Apply conversation flow awareness to adapt to the ongoing conversation.
        
        Args:
            query: The query text
            documents: Documents with coherence scores
            conversation: Conversation history
        
        Returns:
            Documents with conversation-aware scores
        """
        # In a real implementation, this would analyze the conversation flow
        # For now, we'll use a simplified approach
        
        # Extract recent conversation terms
        recent_terms = set()
        for item in conversation[-3:]:  # Consider last 3 exchanges
            content = item.get('content', '')
            recent_terms.update(content.lower().split())
        
        # Apply conversation awareness
        conversation_aware_docs = []
        for doc in documents:
            # Calculate term overlap with recent conversation
            doc_terms = set(doc['text'].lower().split())
            term_overlap = len(recent_terms.intersection(doc_terms)) / max(1, len(recent_terms))
            
            # Apply recency boost
            recency_boost = self.recency_weight * term_overlap
            conversation_score = doc.get('coherence_score', doc.get('attention_score', doc.get('score', 0))) * (1.0 + recency_boost)
            
            conversation_aware_docs.append({
                **doc,
                'conversation_score': conversation_score
            })
        
        logger.info(f"Conversation awareness applied to {len(conversation_aware_docs)} documents")
        return conversation_aware_docs
    
    async def _final_rerank(
        self, 
        query: str, 
        documents: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Perform final reranking of documents.
        
        Args:
            query: The query text
            documents: Documents with various scores
            context: Query context
        
        Returns:
            Final reranked documents
        """
        # Get the most appropriate score for each document
        for doc in documents:
            if 'conversation_score' in doc:
                doc['final_score'] = doc['conversation_score']
            elif 'coherence_score' in doc:
                doc['final_score'] = doc['coherence_score']
            elif 'attention_score' in doc:
                doc['final_score'] = doc['attention_score']
            else:
                doc['final_score'] = doc['score']
        
        # Sort by final score
        reranked = sorted(documents, key=lambda d: d['final_score'], reverse=True)
        
        # Get top_k from context
        top_k = context.get('top_k', 5)
        result = reranked[:top_k]
        
        # Add reasoning trace
        for doc in result:
            doc['reasoning_trace'] = self._generate_reasoning_trace(doc)
        
        return result
    
    def _generate_reasoning_trace(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a reasoning trace for document selection.
        
        Args:
            document: Document with scores
        
        Returns:
            Reasoning trace
        """
        trace = {
            'base_score': document.get('score', 0),
            'selection_factors': []
        }
        
        # Add attention factor if available
        if 'attention_score' in document:
            attention_factor = {
                'name': 'attention',
                'score': document['attention_score'],
                'description': 'Term overlap with query'
            }
            trace['selection_factors'].append(attention_factor)
        
        # Add coherence factor if available
        if 'coherence_score' in document:
            coherence_factor = {
                'name': 'coherence',
                'score': document['coherence_score'],
                'description': 'Document coherence and context preservation'
            }
            trace['selection_factors'].append(coherence_factor)
        
        # Add conversation factor if available
        if 'conversation_score' in document:
            conversation_factor = {
                'name': 'conversation',
                'score': document['conversation_score'],
                'description': 'Relevance to conversation flow'
            }
            trace['selection_factors'].append(conversation_factor)
        
        # Add final score
        trace['final_score'] = document.get('final_score', document.get('score', 0))
        
        return trace
