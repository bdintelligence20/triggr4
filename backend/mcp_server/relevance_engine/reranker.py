"""
Relevance Engine Reranker

This module provides functionality for reranking search results based on query and conversation context.
It improves document ranking with attention-based filtering and semantic similarity scoring.
"""

import logging
import re
import math
from typing import Dict, List, Any, Optional, Union
import asyncio

# Configure logging
logger = logging.getLogger(__name__)

class RelevanceEngine:
    """
    Relevance Engine
    
    This class provides functionality for:
    - Reranking search results based on query and conversation context
    - Attention-based filtering to identify the most relevant passages
    - Semantic similarity scoring that considers both query and conversation context
    """
    
    def __init__(self):
        """Initialize the relevance engine."""
        logger.info("Initialized relevance engine")
    
    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        conversation_history: str = "",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rerank search results based on query and conversation context.
        
        Args:
            query: The query string
            documents: The search results to rerank
            conversation_history: The conversation history
            top_k: Number of results to return
            
        Returns:
            Reranked search results
        """
        if not documents:
            return []
        
        # Extract query terms
        query_terms = self._extract_terms(query)
        
        # Extract conversation terms if available
        conversation_terms = self._extract_terms(conversation_history) if conversation_history else []
        
        # Calculate attention scores
        attention_scores = self._calculate_attention_scores(documents, query_terms, conversation_terms)
        
        # Calculate semantic similarity scores
        similarity_scores = self._calculate_similarity_scores(documents, query, conversation_history)
        
        # Combine scores
        combined_scores = self._combine_scores(documents, attention_scores, similarity_scores)
        
        # Sort documents by combined score
        reranked_documents = sorted(
            zip(documents, combined_scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return top_k documents
        return [doc for doc, score in reranked_documents[:top_k]]
    
    def _extract_terms(self, text: str) -> List[str]:
        """
        Extract terms from text.
        
        Args:
            text: The text to extract terms from
            
        Returns:
            List of terms
        """
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Split into words
        words = text.split()
        
        # Remove stop words
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with',
            'by', 'about', 'as', 'of', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'can', 'could', 'will',
            'would', 'should', 'shall', 'may', 'might', 'must',
        }
        
        terms = [word for word in words if word not in stop_words and len(word) > 1]
        
        return terms
    
    def _calculate_attention_scores(
        self,
        documents: List[Dict[str, Any]],
        query_terms: List[str],
        conversation_terms: List[str]
    ) -> List[float]:
        """
        Calculate attention scores for documents.
        
        Args:
            documents: The documents to score
            query_terms: The query terms
            conversation_terms: The conversation terms
            
        Returns:
            List of attention scores
        """
        attention_scores = []
        
        for doc in documents:
            text = doc.get("text", "").lower()
            
            # Count query term occurrences
            query_term_count = 0
            for term in query_terms:
                query_term_count += len(re.findall(r'\b' + re.escape(term) + r'\b', text))
            
            # Count conversation term occurrences
            conversation_term_count = 0
            for term in conversation_terms:
                conversation_term_count += len(re.findall(r'\b' + re.escape(term) + r'\b', text))
            
            # Calculate attention score
            # Query terms are weighted more heavily than conversation terms
            attention_score = (query_term_count * 2.0 + conversation_term_count * 0.5) / (len(text) + 1) * 1000
            
            attention_scores.append(attention_score)
        
        return attention_scores
    
    def _calculate_similarity_scores(
        self,
        documents: List[Dict[str, Any]],
        query: str,
        conversation_history: str
    ) -> List[float]:
        """
        Calculate semantic similarity scores for documents.
        
        Args:
            documents: The documents to score
            query: The query string
            conversation_history: The conversation history
            
        Returns:
            List of similarity scores
        """
        # In a real implementation, this would use embeddings or a language model
        # For this implementation, we'll use a simple TF-IDF-like approach
        
        # Extract terms from query and conversation
        query_terms = set(self._extract_terms(query))
        conversation_terms = set(self._extract_terms(conversation_history)) if conversation_history else set()
        
        # Calculate IDF for all terms
        term_counts = {}
        for term in query_terms.union(conversation_terms):
            term_counts[term] = 0
            for doc in documents:
                text = doc.get("text", "").lower()
                if re.search(r'\b' + re.escape(term) + r'\b', text):
                    term_counts[term] += 1
        
        # Calculate IDF
        num_docs = len(documents)
        idf = {}
        for term, count in term_counts.items():
            idf[term] = math.log((num_docs + 1) / (count + 1)) + 1
        
        # Calculate similarity scores
        similarity_scores = []
        
        for doc in documents:
            text = doc.get("text", "").lower()
            doc_terms = set(self._extract_terms(text))
            
            # Calculate query similarity
            query_similarity = 0
            for term in query_terms:
                if term in doc_terms:
                    query_similarity += idf.get(term, 1.0)
            
            # Normalize by query length
            query_similarity = query_similarity / (len(query_terms) + 1)
            
            # Calculate conversation similarity
            conversation_similarity = 0
            if conversation_terms:
                for term in conversation_terms:
                    if term in doc_terms:
                        conversation_similarity += idf.get(term, 1.0)
                
                # Normalize by conversation length
                conversation_similarity = conversation_similarity / (len(conversation_terms) + 1)
            
            # Combine similarities (query similarity is weighted more heavily)
            similarity_score = query_similarity * 0.8 + conversation_similarity * 0.2
            
            similarity_scores.append(similarity_score)
        
        return similarity_scores
    
    def _combine_scores(
        self,
        documents: List[Dict[str, Any]],
        attention_scores: List[float],
        similarity_scores: List[float]
    ) -> List[float]:
        """
        Combine attention and similarity scores.
        
        Args:
            documents: The documents to score
            attention_scores: The attention scores
            similarity_scores: The similarity scores
            
        Returns:
            List of combined scores
        """
        # Normalize scores
        max_attention = max(attention_scores) if attention_scores else 1.0
        max_similarity = max(similarity_scores) if similarity_scores else 1.0
        
        normalized_attention = [score / max_attention for score in attention_scores]
        normalized_similarity = [score / max_similarity for score in similarity_scores]
        
        # Combine scores
        # We weight similarity more heavily than attention
        combined_scores = [
            0.3 * attention + 0.7 * similarity + 0.1 * original_score
            for attention, similarity, original_score in zip(
                normalized_attention,
                normalized_similarity,
                [doc.get("score", 0.0) for doc in documents]
            )
        ]
        
        return combined_scores
