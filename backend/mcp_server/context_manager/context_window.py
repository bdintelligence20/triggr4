"""
Context Window Manager

This module provides functionality for managing dynamic context windows that adapt to query complexity.
It handles priority-based context management and hierarchical context structuring.
"""

import logging
import json
import re
import uuid
from typing import Dict, List, Any, Optional, Union
import asyncio
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class ContextManager:
    """
    Context Manager
    
    This class provides functionality for:
    - Maintaining a dynamic context window that combines retrieved information, agent state, and user interactions
    - Implementing priority-based context management to optimize token usage
    - Supporting hierarchical context structuring (global/task/conversation levels)
    """
    
    def __init__(self):
        """Initialize the context manager."""
        # Initialize context store
        self.contexts = {}
        
        # Default token limits
        self.default_token_limits = {
            "global": 1000,
            "task": 2000,
            "conversation": 1000
        }
        
        logger.info("Initialized context manager")
    
    async def get_context(self, context_id: str) -> Dict[str, Any]:
        """
        Get a context by ID.
        
        Args:
            context_id: The context ID
            
        Returns:
            Dict containing the context
            
        Raises:
            ValueError: If the context is not found
        """
        if context_id not in self.contexts:
            raise ValueError(f"Context not found: {context_id}")
        
        return self.contexts[context_id]
    
    async def create_context(
        self,
        initial_content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new context.
        
        Args:
            initial_content: Initial content for the context
            metadata: Context metadata
            
        Returns:
            Dict containing the new context
        """
        # Generate context ID
        context_id = str(uuid.uuid4())
        
        # Set default metadata if not provided
        if metadata is None:
            metadata = {}
        
        # Add timestamp to metadata
        metadata["created_at"] = datetime.now().isoformat()
        
        # Create context
        context = {
            "id": context_id,
            "metadata": metadata,
            "content": {
                "global": initial_content or "",
                "task": "",
                "conversation": ""
            },
            "token_usage": {
                "global": self._estimate_tokens(initial_content or ""),
                "task": 0,
                "conversation": 0
            }
        }
        
        # Store context
        self.contexts[context_id] = context
        
        logger.info(f"Created context: {context_id}")
        
        return context
    
    async def add_to_context(
        self,
        context_id: str,
        content: str,
        level: str = "global"
    ) -> Dict[str, Any]:
        """
        Add content to a context.
        
        Args:
            context_id: The context ID
            content: The content to add
            level: The context level (global, task, conversation)
            
        Returns:
            Dict containing the updated context
            
        Raises:
            ValueError: If the context is not found or the level is invalid
        """
        if context_id not in self.contexts:
            raise ValueError(f"Context not found: {context_id}")
        
        if level not in ["global", "task", "conversation"]:
            raise ValueError(f"Invalid context level: {level}")
        
        # Get context
        context = self.contexts[context_id]
        
        # Add content to the specified level
        context["content"][level] += f"\n\n{content}"
        
        # Update token usage
        context["token_usage"][level] += self._estimate_tokens(content)
        
        # Trim context if needed
        await self._trim_context(context_id, level)
        
        logger.info(f"Added content to context {context_id} at level {level}")
        
        return context
    
    async def remove_from_context(
        self,
        context_id: str,
        content: str,
        level: str = "global"
    ) -> Dict[str, Any]:
        """
        Remove content from a context.
        
        Args:
            context_id: The context ID
            content: The content to remove
            level: The context level (global, task, conversation)
            
        Returns:
            Dict containing the updated context
            
        Raises:
            ValueError: If the context is not found or the level is invalid
        """
        if context_id not in self.contexts:
            raise ValueError(f"Context not found: {context_id}")
        
        if level not in ["global", "task", "conversation"]:
            raise ValueError(f"Invalid context level: {level}")
        
        # Get context
        context = self.contexts[context_id]
        
        # Remove content from the specified level
        updated_content = context["content"][level].replace(content, "")
        
        # Update content
        context["content"][level] = updated_content
        
        # Update token usage
        context["token_usage"][level] = self._estimate_tokens(updated_content)
        
        logger.info(f"Removed content from context {context_id} at level {level}")
        
        return context
    
    async def clear_context(
        self,
        context_id: str,
        level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Clear a context.
        
        Args:
            context_id: The context ID
            level: The context level to clear (global, task, conversation, or None for all)
            
        Returns:
            Dict containing the updated context
            
        Raises:
            ValueError: If the context is not found
        """
        if context_id not in self.contexts:
            raise ValueError(f"Context not found: {context_id}")
        
        # Get context
        context = self.contexts[context_id]
        
        if level is None:
            # Clear all levels
            context["content"] = {
                "global": "",
                "task": "",
                "conversation": ""
            }
            context["token_usage"] = {
                "global": 0,
                "task": 0,
                "conversation": 0
            }
            logger.info(f"Cleared all levels of context {context_id}")
        elif level in ["global", "task", "conversation"]:
            # Clear specified level
            context["content"][level] = ""
            context["token_usage"][level] = 0
            logger.info(f"Cleared level {level} of context {context_id}")
        else:
            raise ValueError(f"Invalid context level: {level}")
        
        return context
    
    async def optimize_context(
        self,
        query: str,
        documents: str,
        conversation_history: str,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize context for a query.
        
        Args:
            query: The query
            documents: The retrieved documents
            conversation_history: The conversation history
            preferences: Context allocation preferences
            
        Returns:
            Dict containing the optimized context
        """
        # Set default preferences if not provided
        if preferences is None:
            preferences = {}
        
        # Get allocation preferences
        allocation = preferences.get("allocation", {
            "global": 0.3,
            "task": 0.4,
            "conversation": 0.3
        })
        
        # Create a new context
        context = await self.create_context(
            metadata={
                "query": query,
                "allocation": allocation
            }
        )
        
        context_id = context["id"]
        
        # Add documents to global context
        await self.add_to_context(context_id, documents, "global")
        
        # Add query to task context
        await self.add_to_context(context_id, f"Query: {query}", "task")
        
        # Add conversation history to conversation context
        if conversation_history:
            await self.add_to_context(context_id, conversation_history, "conversation")
        
        # Optimize context
        optimized_context = await self._optimize_context_allocation(context_id, allocation)
        
        return {
            "context_id": context_id,
            "operation_result": {
                "context": self._combine_context_levels(optimized_context),
                "token_usage": optimized_context["token_usage"]
            }
        }
    
    async def perform_operation(
        self,
        operation: str,
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform a context operation.
        
        Args:
            operation: The operation to perform (add, remove, optimize, clear)
            context_data: Context data
            
        Returns:
            Dict containing the operation result
            
        Raises:
            ValueError: If the operation is invalid
        """
        if operation == "add":
            # Add content to context
            context_id = context_data.get("context_id")
            content = context_data.get("content")
            level = context_data.get("level", "global")
            
            if not context_id:
                # Create a new context
                context = await self.create_context(content, context_data.get("metadata"))
                context_id = context["id"]
            else:
                # Add to existing context
                context = await self.add_to_context(context_id, content, level)
            
            return {
                "context_id": context_id,
                "context_size": {
                    "global": len(context["content"]["global"]),
                    "task": len(context["content"]["task"]),
                    "conversation": len(context["content"]["conversation"])
                },
                "token_usage": context["token_usage"],
                "operation_result": {
                    "context": self._combine_context_levels(context)
                }
            }
        elif operation == "remove":
            # Remove content from context
            context_id = context_data.get("context_id")
            content = context_data.get("content")
            level = context_data.get("level", "global")
            
            if not context_id or not content:
                raise ValueError("Context ID and content are required for remove operation")
            
            context = await self.remove_from_context(context_id, content, level)
            
            return {
                "context_id": context_id,
                "context_size": {
                    "global": len(context["content"]["global"]),
                    "task": len(context["content"]["task"]),
                    "conversation": len(context["content"]["conversation"])
                },
                "token_usage": context["token_usage"],
                "operation_result": {
                    "context": self._combine_context_levels(context)
                }
            }
        elif operation == "optimize":
            # Optimize context
            context_id = context_data.get("context_id")
            query = context_data.get("query")
            current_context = context_data.get("current_context")
            history = context_data.get("history", "")
            allocation = context_data.get("allocation", {
                "global": 0.3,
                "task": 0.4,
                "conversation": 0.3
            })
            
            if not context_id and not current_context:
                raise ValueError("Either context ID or current context is required for optimize operation")
            
            if not context_id:
                # Create a new context
                context = await self.create_context(
                    current_context,
                    {
                        "query": query,
                        "allocation": allocation
                    }
                )
                context_id = context["id"]
                
                # Add history to conversation context
                if history:
                    await self.add_to_context(context_id, history, "conversation")
            
            # Optimize context
            context = await self._optimize_context_allocation(context_id, allocation)
            
            return {
                "context_id": context_id,
                "context_size": {
                    "global": len(context["content"]["global"]),
                    "task": len(context["content"]["task"]),
                    "conversation": len(context["content"]["conversation"])
                },
                "token_usage": context["token_usage"],
                "operation_result": {
                    "context": self._combine_context_levels(context)
                }
            }
        elif operation == "clear":
            # Clear context
            context_id = context_data.get("context_id")
            level = context_data.get("level")
            
            if not context_id:
                raise ValueError("Context ID is required for clear operation")
            
            context = await self.clear_context(context_id, level)
            
            return {
                "context_id": context_id,
                "context_size": {
                    "global": len(context["content"]["global"]),
                    "task": len(context["content"]["task"]),
                    "conversation": len(context["content"]["conversation"])
                },
                "token_usage": context["token_usage"],
                "operation_result": {
                    "context": self._combine_context_levels(context)
                }
            }
        else:
            raise ValueError(f"Invalid operation: {operation}")
    
    async def _trim_context(
        self,
        context_id: str,
        level: str
    ) -> None:
        """
        Trim context to fit within token limits.
        
        Args:
            context_id: The context ID
            level: The context level to trim
            
        Raises:
            ValueError: If the context is not found or the level is invalid
        """
        if context_id not in self.contexts:
            raise ValueError(f"Context not found: {context_id}")
        
        if level not in ["global", "task", "conversation"]:
            raise ValueError(f"Invalid context level: {level}")
        
        # Get context
        context = self.contexts[context_id]
        
        # Get token limit for the level
        token_limit = self.default_token_limits[level]
        
        # Check if trimming is needed
        if context["token_usage"][level] <= token_limit:
            return
        
        # Trim content
        content = context["content"][level]
        
        # Split content into paragraphs
        paragraphs = re.split(r'\n\s*\n', content)
        
        # Remove paragraphs from the beginning until we're under the token limit
        while paragraphs and context["token_usage"][level] > token_limit:
            removed_paragraph = paragraphs.pop(0)
            removed_tokens = self._estimate_tokens(removed_paragraph)
            context["token_usage"][level] -= removed_tokens
        
        # Join remaining paragraphs
        context["content"][level] = "\n\n".join(paragraphs)
        
        logger.info(f"Trimmed context {context_id} at level {level} to fit within token limit")
    
    async def _optimize_context_allocation(
        self,
        context_id: str,
        allocation: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Optimize context allocation based on preferences.
        
        Args:
            context_id: The context ID
            allocation: Context allocation preferences
            
        Returns:
            Dict containing the optimized context
            
        Raises:
            ValueError: If the context is not found
        """
        if context_id not in self.contexts:
            raise ValueError(f"Context not found: {context_id}")
        
        # Get context
        context = self.contexts[context_id]
        
        # Calculate total token limit
        total_token_limit = sum(self.default_token_limits.values())
        
        # Calculate token limits for each level based on allocation
        token_limits = {
            level: int(total_token_limit * allocation.get(level, 0.0))
            for level in ["global", "task", "conversation"]
        }
        
        # Ensure minimum token limits
        for level in token_limits:
            token_limits[level] = max(token_limits[level], 100)
        
        # Trim each level to fit within its token limit
        for level, limit in token_limits.items():
            # Skip empty levels
            if not context["content"][level]:
                continue
            
            # Check if trimming is needed
            if context["token_usage"][level] <= limit:
                continue
            
            # Split content into paragraphs
            content = context["content"][level]
            paragraphs = re.split(r'\n\s*\n', content)
            
            # Remove paragraphs from the beginning until we're under the token limit
            while paragraphs and context["token_usage"][level] > limit:
                removed_paragraph = paragraphs.pop(0)
                removed_tokens = self._estimate_tokens(removed_paragraph)
                context["token_usage"][level] -= removed_tokens
            
            # Join remaining paragraphs
            context["content"][level] = "\n\n".join(paragraphs)
            
            logger.info(f"Optimized context {context_id} at level {level} to fit within allocation")
        
        return context
    
    def _combine_context_levels(self, context: Dict[str, Any]) -> str:
        """
        Combine context levels into a single string.
        
        Args:
            context: The context
            
        Returns:
            Combined context string
        """
        combined = []
        
        # Add global context
        if context["content"]["global"]:
            combined.append("# Global Context\n\n" + context["content"]["global"])
        
        # Add task context
        if context["content"]["task"]:
            combined.append("# Task Context\n\n" + context["content"]["task"])
        
        # Add conversation context
        if context["content"]["conversation"]:
            combined.append("# Conversation Context\n\n" + context["content"]["conversation"])
        
        return "\n\n".join(combined)
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text.
        
        Args:
            text: The text
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        # Simple estimation: 1 token ≈ 4 characters
        return len(text) // 4
