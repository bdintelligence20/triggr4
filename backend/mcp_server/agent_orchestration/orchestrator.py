"""
Agent Orchestrator

This module provides functionality for coordinating multiple specialized agents for complex tasks.
It handles agent selection, task decomposition, and response generation.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Union
import asyncio
import uuid
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Agent Orchestrator
    
    This class provides functionality for:
    - Coordinating multiple specialized agents for complex tasks
    - Task decomposition and planning
    - Response generation with reasoning traces
    """
    
    def __init__(
        self,
        anthropic_api_key: str,
        openai_api_key: str,
        default_model: str = "claude-3-opus-20240229"
    ):
        """
        Initialize the agent orchestrator.
        
        Args:
            anthropic_api_key: Anthropic API key
            openai_api_key: OpenAI API key
            default_model: Default model to use
        """
        self.anthropic_api_key = anthropic_api_key
        self.openai_api_key = openai_api_key
        self.default_model = default_model
        
        # Define agent types
        self.agent_types = {
            "retriever": {
                "description": "Specialized in retrieving relevant information from the knowledge base",
                "capabilities": ["information_retrieval", "document_search", "semantic_search"],
                "model": "claude-3-haiku-20240307",
            },
            "reasoner": {
                "description": "Specialized in logical reasoning and analysis",
                "capabilities": ["logical_reasoning", "analysis", "inference", "planning"],
                "model": "claude-3-opus-20240229",
            },
            "generator": {
                "description": "Specialized in generating coherent responses",
                "capabilities": ["response_generation", "summarization", "explanation"],
                "model": "claude-3-sonnet-20240229",
            },
            "orchestrator": {
                "description": "Specialized in coordinating other agents and managing workflows",
                "capabilities": ["agent_coordination", "task_decomposition", "workflow_management"],
                "model": "claude-3-opus-20240229",
            },
        }
        
        logger.info("Initialized agent orchestrator")
    
    async def orchestrate(
        self,
        task: str,
        agent_preferences: Optional[Dict[str, List[str]]] = None,
        execution_parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate multiple specialized agents for a complex task.
        
        Args:
            task: The task to perform
            agent_preferences: Preferences for which agents to include/exclude
            execution_parameters: Parameters for agent execution
            
        Returns:
            Dict containing the orchestration result
        """
        if not task:
            raise ValueError("Task is required")
        
        # Set default agent preferences if not provided
        if agent_preferences is None:
            agent_preferences = {
                "include": ["retriever", "reasoner", "generator"],
                "exclude": [],
            }
        
        # Set default execution parameters if not provided
        if execution_parameters is None:
            execution_parameters = {
                "max_tokens": 1000,
                "temperature": 0.7,
            }
        
        # Select agents based on preferences
        selected_agents = self._select_agents(agent_preferences)
        
        # Decompose task
        subtasks = await self._decompose_task(task, selected_agents)
        
        # Execute subtasks
        subtask_results = []
        for subtask in subtasks:
            agent_type = subtask["agent_type"]
            subtask_description = subtask["description"]
            
            # Execute subtask with the appropriate agent
            result = await self._execute_subtask(
                agent_type,
                subtask_description,
                task,
                execution_parameters
            )
            
            subtask_results.append({
                "agent_type": agent_type,
                "subtask": subtask_description,
                "result": result,
            })
        
        # Generate final response
        response = await self._generate_response(
            task,
            subtask_results,
            execution_parameters
        )
        
        # Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(subtask_results)
        
        # Extract reasoning traces
        reasoning_traces = [
            {
                "agent_type": result["agent_type"],
                "subtask": result["subtask"],
                "reasoning": result["result"].get("reasoning", ""),
            }
            for result in subtask_results
        ]
        
        # Prepare execution stats
        execution_stats = {
            "subtask_count": len(subtasks),
            "agent_count": len(selected_agents),
            "execution_time": datetime.now().isoformat(),
        }
        
        return {
            "response": response,
            "agents_used": selected_agents,
            "confidence_scores": confidence_scores,
            "reasoning_traces": reasoning_traces,
            "execution_stats": execution_stats,
        }
    
    def _select_agents(self, agent_preferences: Dict[str, List[str]]) -> List[str]:
        """
        Select agents based on preferences.
        
        Args:
            agent_preferences: Preferences for which agents to include/exclude
            
        Returns:
            List of selected agent types
        """
        include = agent_preferences.get("include", [])
        exclude = agent_preferences.get("exclude", [])
        
        # Start with all agent types if include is empty
        if not include:
            selected_agents = list(self.agent_types.keys())
        else:
            # Start with included agents
            selected_agents = [
                agent_type for agent_type in include
                if agent_type in self.agent_types
            ]
        
        # Remove excluded agents
        selected_agents = [
            agent_type for agent_type in selected_agents
            if agent_type not in exclude
        ]
        
        # Always include at least one agent
        if not selected_agents:
            selected_agents = ["generator"]
        
        return selected_agents
    
    async def _decompose_task(
        self,
        task: str,
        selected_agents: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Decompose a task into subtasks for different agents.
        
        Args:
            task: The task to decompose
            selected_agents: The selected agent types
            
        Returns:
            List of subtasks
        """
        # In a real implementation, this would use a language model to decompose the task
        # For this implementation, we'll use a simple rule-based approach
        
        subtasks = []
        
        # Check if retriever is selected
        if "retriever" in selected_agents:
            subtasks.append({
                "agent_type": "retriever",
                "description": f"Retrieve relevant information for: {task}",
            })
        
        # Check if reasoner is selected
        if "reasoner" in selected_agents:
            subtasks.append({
                "agent_type": "reasoner",
                "description": f"Analyze and reason about: {task}",
            })
        
        # Check if generator is selected
        if "generator" in selected_agents:
            subtasks.append({
                "agent_type": "generator",
                "description": f"Generate a response for: {task}",
            })
        
        # Check if orchestrator is selected
        if "orchestrator" in selected_agents:
            subtasks.append({
                "agent_type": "orchestrator",
                "description": f"Coordinate the workflow for: {task}",
            })
        
        return subtasks
    
    async def _execute_subtask(
        self,
        agent_type: str,
        subtask: str,
        original_task: str,
        execution_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a subtask with the appropriate agent.
        
        Args:
            agent_type: The agent type
            subtask: The subtask description
            original_task: The original task
            execution_parameters: Parameters for agent execution
            
        Returns:
            Dict containing the subtask result
        """
        # Get agent configuration
        agent_config = self.agent_types.get(agent_type, {})
        model = agent_config.get("model", self.default_model)
        
        # Prepare prompt
        prompt = self._prepare_agent_prompt(agent_type, subtask, original_task)
        
        # Execute prompt with the appropriate model
        try:
            if "claude" in model:
                result = await self._execute_with_anthropic(prompt, model, execution_parameters)
            else:
                result = await self._execute_with_openai(prompt, model, execution_parameters)
            
            return result
        except Exception as e:
            logger.error(f"Error executing subtask with {agent_type}: {str(e)}")
            return {
                "response": f"Error executing subtask: {str(e)}",
                "reasoning": "Error occurred during execution",
                "confidence": 0.0,
            }
    
    def _prepare_agent_prompt(
        self,
        agent_type: str,
        subtask: str,
        original_task: str
    ) -> str:
        """
        Prepare a prompt for an agent.
        
        Args:
            agent_type: The agent type
            subtask: The subtask description
            original_task: The original task
            
        Returns:
            The prompt
        """
        agent_config = self.agent_types.get(agent_type, {})
        agent_description = agent_config.get("description", "")
        agent_capabilities = agent_config.get("capabilities", [])
        
        prompt = f"""
        You are a specialized {agent_type} agent with the following capabilities:
        {', '.join(agent_capabilities)}
        
        Agent description: {agent_description}
        
        Original task: {original_task}
        
        Your subtask: {subtask}
        
        Please complete this subtask and provide:
        1. Your response to the subtask
        2. Your reasoning process
        3. Your confidence level (0.0 to 1.0)
        
        Format your response as JSON with the following structure:
        {{
            "response": "Your response to the subtask",
            "reasoning": "Your step-by-step reasoning process",
            "confidence": 0.9 // Your confidence level from 0.0 to 1.0
        }}
        """
        
        return prompt
    
    async def _execute_with_anthropic(
        self,
        prompt: str,
        model: str,
        execution_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a prompt with Anthropic API.
        
        Args:
            prompt: The prompt
            model: The model to use
            execution_parameters: Parameters for execution
            
        Returns:
            Dict containing the result
        """
        try:
            # Import Anthropic
            import anthropic
            
            # Create client
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
            # Get parameters
            max_tokens = execution_parameters.get("max_tokens", 1000)
            temperature = execution_parameters.get("temperature", 0.7)
            
            # Call API
            response = await asyncio.to_thread(
                client.messages.create,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract response
            response_text = response.content[0].text
            
            # Parse JSON response
            try:
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError:
                # If response is not valid JSON, extract it using regex
                response_match = re.search(r'"response"\s*:\s*"([^"]*)"', response_text)
                reasoning_match = re.search(r'"reasoning"\s*:\s*"([^"]*)"', response_text)
                confidence_match = re.search(r'"confidence"\s*:\s*([0-9.]+)', response_text)
                
                return {
                    "response": response_match.group(1) if response_match else response_text,
                    "reasoning": reasoning_match.group(1) if reasoning_match else "",
                    "confidence": float(confidence_match.group(1)) if confidence_match else 0.5,
                }
        except ImportError:
            logger.error("Anthropic package not installed")
            raise ImportError("Anthropic package not installed. Install with: pip install anthropic")
        except Exception as e:
            logger.error(f"Error executing with Anthropic: {str(e)}")
            raise
    
    async def _execute_with_openai(
        self,
        prompt: str,
        model: str,
        execution_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a prompt with OpenAI API.
        
        Args:
            prompt: The prompt
            model: The model to use
            execution_parameters: Parameters for execution
            
        Returns:
            Dict containing the result
        """
        try:
            # Import OpenAI
            import openai
            
            # Set API key
            openai.api_key = self.openai_api_key
            
            # Get parameters
            max_tokens = execution_parameters.get("max_tokens", 1000)
            temperature = execution_parameters.get("temperature", 0.7)
            
            # Call API
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract response
            response_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError:
                # If response is not valid JSON, extract it using regex
                response_match = re.search(r'"response"\s*:\s*"([^"]*)"', response_text)
                reasoning_match = re.search(r'"reasoning"\s*:\s*"([^"]*)"', response_text)
                confidence_match = re.search(r'"confidence"\s*:\s*([0-9.]+)', response_text)
                
                return {
                    "response": response_match.group(1) if response_match else response_text,
                    "reasoning": reasoning_match.group(1) if reasoning_match else "",
                    "confidence": float(confidence_match.group(1)) if confidence_match else 0.5,
                }
        except ImportError:
            logger.error("OpenAI package not installed")
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        except Exception as e:
            logger.error(f"Error executing with OpenAI: {str(e)}")
            raise
    
    async def _generate_response(
        self,
        task: str,
        subtask_results: List[Dict[str, Any]],
        execution_parameters: Dict[str, Any]
    ) -> str:
        """
        Generate a final response based on subtask results.
        
        Args:
            task: The original task
            subtask_results: The subtask results
            execution_parameters: Parameters for execution
            
        Returns:
            The final response
        """
        # Prepare prompt
        prompt = f"""
        Task: {task}
        
        Subtask results:
        """
        
        for i, result in enumerate(subtask_results):
            agent_type = result["agent_type"]
            subtask = result["subtask"]
            response = result["result"].get("response", "")
            
            prompt += f"""
            Subtask {i+1} ({agent_type}): {subtask}
            Response: {response}
            """
        
        prompt += """
        Based on the above subtask results, generate a comprehensive and coherent response to the original task.
        """
        
        # Execute prompt with the default model
        try:
            if "claude" in self.default_model:
                result = await self._execute_with_anthropic(prompt, self.default_model, execution_parameters)
            else:
                result = await self._execute_with_openai(prompt, self.default_model, execution_parameters)
            
            return result.get("response", "")
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            
            # Fallback to simple concatenation
            responses = [result["result"].get("response", "") for result in subtask_results]
            return "\n\n".join(responses)
    
    def _calculate_confidence_scores(
        self,
        subtask_results: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate confidence scores for each agent type.
        
        Args:
            subtask_results: The subtask results
            
        Returns:
            Dict containing confidence scores
        """
        confidence_scores = {}
        
        for result in subtask_results:
            agent_type = result["agent_type"]
            confidence = result["result"].get("confidence", 0.5)
            
            if agent_type not in confidence_scores:
                confidence_scores[agent_type] = []
            
            confidence_scores[agent_type].append(confidence)
        
        # Calculate average confidence for each agent type
        for agent_type, scores in confidence_scores.items():
            confidence_scores[agent_type] = sum(scores) / len(scores)
        
        return confidence_scores
    
    async def generate_response(
        self,
        query: str,
        context: str,
        conversation_history: str = ""
    ) -> Dict[str, Any]:
        """
        Generate a response to a query using the orchestrator.
        
        Args:
            query: The query
            context: The context
            conversation_history: The conversation history
            
        Returns:
            Dict containing the response
        """
        # Prepare task
        task = f"""
        Generate a response to the following query:
        
        Query: {query}
        
        Context:
        {context}
        
        Conversation History:
        {conversation_history}
        """
        
        # Orchestrate agents
        result = await self.orchestrate(
            task=task,
            agent_preferences={
                "include": ["retriever", "reasoner", "generator"],
                "exclude": [],
            },
            execution_parameters={
                "max_tokens": 1000,
                "temperature": 0.7,
            }
        )
        
        # Extract sources from context
        sources = self._extract_sources(context)
        
        return {
            "answer": result["response"],
            "sources": sources,
            "reasoning_trace": result["reasoning_traces"],
            "context_usage": {
                "context_length": len(context),
                "history_length": len(conversation_history),
            },
            "confidence": sum(result["confidence_scores"].values()) / len(result["confidence_scores"]) if result["confidence_scores"] else 0.5,
        }
    
    def _extract_sources(self, context: str) -> List[Dict[str, Any]]:
        """
        Extract sources from context.
        
        Args:
            context: The context
            
        Returns:
            List of sources
        """
        # In a real implementation, this would extract source information from the context
        # For this implementation, we'll return a placeholder
        
        return [
            {
                "id": str(uuid.uuid4()),
                "title": "Source Document",
                "relevance": 0.9,
            }
        ]
