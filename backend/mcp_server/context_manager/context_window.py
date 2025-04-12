"""
Unified Context Manager

This module implements a dynamic context window manager for RAG systems
with priority-based token allocation and hierarchical context structuring.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedContextManager:
    """
    Unified Context Manager with dynamic context windows.
    
    This class manages the context window for RAG operations, implementing:
    - Hierarchical context structuring (global/task/conversation levels)
    - Priority-based token allocation
    - Dynamic resizing based on query complexity
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Unified Context Manager.
        
        Args:
            config: Configuration dictionary for the context manager
        """
        self.config = config or {}
        
        # Default token limits
        self.max_total_tokens = self.config.get('max_total_tokens', 30000)
        self.max_context_tokens = self.config.get('max_context_tokens', 20000)
        self.max_history_tokens = self.config.get('max_history_tokens', 8000)
        
        # Initialize context pools
        self.global_context = []
        self.task_context = []
        self.conversation_context = []
        
        # Context session management
        self.active_session_id = None
        self.sessions = {}
        
        logger.info(f"Initialized UnifiedContextManager with max tokens: {self.max_total_tokens}")
    
    async def prepare_context(self, query: str, history: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare the context for a query based on the conversation history and preferences.
        
        Args:
            query: The user's query
            history: The conversation history
            preferences: Context preferences
        
        Returns:
            Prepared context with global, task, and conversation components
        """
        # Analyze query complexity to determine context allocation
        query_complexity = await self._analyze_query_complexity(query)
        
        # Adjust token allocations based on query complexity
        context_allocation = await self._allocate_tokens(query_complexity, preferences)
        
        # Prepare context components
        global_context = await self._prepare_global_context(
            query, context_allocation['global_tokens']
        )
        
        task_context = await self._prepare_task_context(
            query, context_allocation['task_tokens']
        )
        
        conversation_context = await self._prepare_conversation_context(
            query, history, context_allocation['conversation_tokens']
        )
        
        # Combine context components
        combined_context = {
            'global': global_context,
            'task': task_context,
            'conversation': conversation_context,
            'token_usage': {
                'global': len(global_context),
                'task': len(task_context),
                'conversation': len(conversation_context),
                'total': len(global_context) + len(task_context) + len(conversation_context)
            },
            'query_complexity': query_complexity
        }
        
        logger.info(f"Prepared context with {combined_context['token_usage']['total']} total tokens")
        return combined_context
    
    async def _analyze_query_complexity(self, query: str) -> float:
        """
        Analyze the complexity of a query to determine context allocation.
        
        Args:
            query: The user's query
        
        Returns:
            Complexity score between 0.0 and 1.0
        """
        # Simple complexity analysis based on query length and structure
        # In a real implementation, this would use more sophisticated analysis
        
        # Length-based complexity (longer queries are more complex)
        length_score = min(len(query) / 200, 1.0)
        
        # Structure-based complexity
        has_multiple_questions = '?' in query and query.count('?') > 1
        has_complex_operators = any(op in query.lower() for op in ['compare', 'difference', 'versus', 'vs', 'between'])
        has_constraints = any(term in query.lower() for term in ['only', 'except', 'excluding', 'not including'])
        
        structure_score = 0.0
        if has_multiple_questions:
            structure_score += 0.3
        if has_complex_operators:
            structure_score += 0.3
        if has_constraints:
            structure_score += 0.2
        
        # Combined complexity score
        complexity = min(0.2 + (length_score * 0.3) + (structure_score * 0.5), 1.0)
        
        logger.info(f"Query complexity analysis: {complexity:.2f}")
        return complexity
    
    async def _allocate_tokens(
        self, 
        query_complexity: float, 
        preferences: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Allocate tokens to different context components based on query complexity.
        
        Args:
            query_complexity: Query complexity score (0.0 to 1.0)
            preferences: User preferences for context allocation
        
        Returns:
            Token allocation for each context component
        """
        # Default allocation ratios
        default_allocation = {
            'global': 0.2,  # 20% to global context
            'task': 0.5,    # 50% to task-specific context
            'conversation': 0.3  # 30% to conversation history
        }
        
        # Apply user preferences if provided
        allocation = preferences.get('allocation', default_allocation)
        
        # Adjust allocation based on query complexity
        if query_complexity > 0.7:  # High complexity
            # For complex queries, prioritize task context
            allocation['task'] += 0.1
            allocation['global'] -= 0.05
            allocation['conversation'] -= 0.05
        elif query_complexity < 0.3:  # Low complexity
            # For simple queries, prioritize conversation context
            allocation['conversation'] += 0.1
            allocation['task'] -= 0.1
        
        # Normalize allocation to ensure sum is 1.0
        total = sum(allocation.values())
        if total != 1.0:
            for key in allocation:
                allocation[key] /= total
        
        # Calculate token allocations
        token_allocation = {
            'global_tokens': int(self.max_context_tokens * allocation['global']),
            'task_tokens': int(self.max_context_tokens * allocation['task']),
            'conversation_tokens': int(self.max_context_tokens * allocation['conversation'])
        }
        
        logger.info(f"Token allocation: {token_allocation}")
        return token_allocation
    
    async def _prepare_global_context(self, query: str, max_tokens: int) -> List[Dict[str, Any]]:
        """
        Prepare global context relevant to the query.
        
        Args:
            query: The user's query
            max_tokens: Maximum tokens to allocate to global context
        
        Returns:
            List of global context items
        """
        # In a real implementation, this would retrieve global context from a knowledge base
        # For now, we'll return a placeholder
        return self.global_context[:max_tokens]
    
    async def _prepare_task_context(self, query: str, max_tokens: int) -> List[Dict[str, Any]]:
        """
        Prepare task-specific context relevant to the query.
        
        Args:
            query: The user's query
            max_tokens: Maximum tokens to allocate to task context
        
        Returns:
            List of task context items
        """
        # In a real implementation, this would retrieve task-specific context
        # For now, we'll return a placeholder
        return self.task_context[:max_tokens]
    
    async def _prepare_conversation_context(
        self, 
        query: str, 
        history: str, 
        max_tokens: int
    ) -> List[Dict[str, Any]]:
        """
        Prepare conversation context from history.
        
        Args:
            query: The user's query
            history: The conversation history
            max_tokens: Maximum tokens to allocate to conversation context
        
        Returns:
            List of conversation context items
        """
        # In a real implementation, this would process and truncate the conversation history
        # For now, we'll return a placeholder
        
        # Simple history truncation to fit within token budget
        if not history:
            return []
            
        # Convert history to a list of items
        history_items = []
        for line in history.split('\n'):
            if line.startswith('User:') or line.startswith('AI:'):
                role, content = line.split(':', 1)
                history_items.append({
                    'role': 'user' if role == 'User' else 'assistant',
                    'content': content.strip()
                })
        
        # Truncate history to fit within token budget
        truncated_items = []
        token_count = 0
        
        # Always include the most recent exchanges
        for item in reversed(history_items):
            item_tokens = len(item['content'].split())  # Simple word count as token estimate
            if token_count + item_tokens <= max_tokens:
                truncated_items.insert(0, item)
                token_count += item_tokens
            else:
                break
        
        return truncated_items
    
    async def manage_context(self, operation: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage the context window with operations like add, remove, prioritize, or clear.
        
        Args:
            operation: The operation to perform (add, remove, prioritize, clear)
            context_data: Data for the operation
        
        Returns:
            Result of the operation
        """
        result = {
            'operation': operation,
            'success': True,
            'context_size': 0,
            'token_usage': 0,
            'operation_result': {}
        }
        
        if operation == 'add':
            # Add context to the appropriate pool
            context_type = context_data.get('type', 'task')
            content = context_data.get('content', {})
            
            if context_type == 'global':
                self.global_context.append(content)
                result['operation_result'] = {'added_to': 'global', 'content_id': len(self.global_context) - 1}
            elif context_type == 'task':
                self.task_context.append(content)
                result['operation_result'] = {'added_to': 'task', 'content_id': len(self.task_context) - 1}
            elif context_type == 'conversation':
                self.conversation_context.append(content)
                result['operation_result'] = {'added_to': 'conversation', 'content_id': len(self.conversation_context) - 1}
            
        elif operation == 'remove':
            # Remove context from the appropriate pool
            context_type = context_data.get('type', 'task')
            content_id = context_data.get('content_id', -1)
            
            if context_type == 'global' and 0 <= content_id < len(self.global_context):
                removed = self.global_context.pop(content_id)
                result['operation_result'] = {'removed_from': 'global', 'content': removed}
            elif context_type == 'task' and 0 <= content_id < len(self.task_context):
                removed = self.task_context.pop(content_id)
                result['operation_result'] = {'removed_from': 'task', 'content': removed}
            elif context_type == 'conversation' and 0 <= content_id < len(self.conversation_context):
                removed = self.conversation_context.pop(content_id)
                result['operation_result'] = {'removed_from': 'conversation', 'content': removed}
            else:
                result['success'] = False
                result['operation_result'] = {'error': 'Invalid content_id or context_type'}
            
        elif operation == 'prioritize':
            # Prioritize context in the appropriate pool
            context_type = context_data.get('type', 'task')
            content_id = context_data.get('content_id', -1)
            priority = context_data.get('priority', 1.0)
            
            if context_type == 'global' and 0 <= content_id < len(self.global_context):
                self.global_context[content_id]['priority'] = priority
                result['operation_result'] = {'prioritized': 'global', 'content_id': content_id, 'priority': priority}
            elif context_type == 'task' and 0 <= content_id < len(self.task_context):
                self.task_context[content_id]['priority'] = priority
                result['operation_result'] = {'prioritized': 'task', 'content_id': content_id, 'priority': priority}
            elif context_type == 'conversation' and 0 <= content_id < len(self.conversation_context):
                self.conversation_context[content_id]['priority'] = priority
                result['operation_result'] = {'prioritized': 'conversation', 'content_id': content_id, 'priority': priority}
            else:
                result['success'] = False
                result['operation_result'] = {'error': 'Invalid content_id or context_type'}
            
        elif operation == 'clear':
            # Clear context from the appropriate pool
            context_type = context_data.get('type', 'all')
            
            if context_type == 'global' or context_type == 'all':
                self.global_context = []
            if context_type == 'task' or context_type == 'all':
                self.task_context = []
            if context_type == 'conversation' or context_type == 'all':
                self.conversation_context = []
                
            result['operation_result'] = {'cleared': context_type}
            
        else:
            result['success'] = False
            result['operation_result'] = {'error': f'Unknown operation: {operation}'}
        
        # Update context size and token usage
        result['context_size'] = {
            'global': len(self.global_context),
            'task': len(self.task_context),
            'conversation': len(self.conversation_context)
        }
        
        # Simple token usage estimation
        global_tokens = sum(len(str(item)) for item in self.global_context) // 4
        task_tokens = sum(len(str(item)) for item in self.task_context) // 4
        conversation_tokens = sum(len(str(item)) for item in self.conversation_context) // 4
        
        result['token_usage'] = {
            'global': global_tokens,
            'task': task_tokens,
            'conversation': conversation_tokens,
            'total': global_tokens + task_tokens + conversation_tokens
        }
        
        return result
    
    async def get_current_context(self) -> Dict[str, Any]:
        """
        Get the current context window contents and token allocations.
        
        Returns:
            Current context window state
        """
        # Calculate token usage
        global_tokens = sum(len(str(item)) for item in self.global_context) // 4
        task_tokens = sum(len(str(item)) for item in self.task_context) // 4
        conversation_tokens = sum(len(str(item)) for item in self.conversation_context) // 4
        
        return {
            'global_context': self.global_context,
            'task_context': self.task_context,
            'conversation_context': self.conversation_context,
            'token_usage': {
                'global': global_tokens,
                'task': task_tokens,
                'conversation': conversation_tokens,
                'total': global_tokens + task_tokens + conversation_tokens,
                'max': self.max_total_tokens
            },
            'active_session_id': self.active_session_id
        }
    
    async def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get the context window for a specific session.
        
        Args:
            session_id: The session ID
        
        Returns:
            Session context window state
        """
        if session_id not in self.sessions:
            return {
                'error': f'Session not found: {session_id}',
                'available_sessions': list(self.sessions.keys())
            }
        
        session = self.sessions[session_id]
        
        # Calculate token usage
        global_tokens = sum(len(str(item)) for item in session.get('global_context', [])) // 4
        task_tokens = sum(len(str(item)) for item in session.get('task_context', [])) // 4
        conversation_tokens = sum(len(str(item)) for item in session.get('conversation_context', [])) // 4
        
        return {
            'session_id': session_id,
            'global_context': session.get('global_context', []),
            'task_context': session.get('task_context', []),
            'conversation_context': session.get('conversation_context', []),
            'token_usage': {
                'global': global_tokens,
                'task': task_tokens,
                'conversation': conversation_tokens,
                'total': global_tokens + task_tokens + conversation_tokens,
                'max': self.max_total_tokens
            },
            'created_at': session.get('created_at'),
            'last_updated': session.get('last_updated')
        }
