"""Agentic system using ReAct (Reasoning + Acting) pattern."""
import logging
import json
import re
from typing import List, Dict, Any, Optional

from app.agents.llm_client import llm_client
from app.tools.agent_tools import agent_tools
from app.config import settings

logger = logging.getLogger(__name__)


class ReactAgent:
    """Agent that can reason and take actions using the ReAct pattern."""
    
    SYSTEM_PROMPT = """You are a precise AI assistant with access to tools and a knowledge base. Follow the ReAct pattern carefully.

CRITICAL RULES:
1. For any questions first search documents. IF about people, experiences, skills, projects, or specific topics → ALWAYS search documents FIRST
2. Keep answers brief, direct, and factual
3. Only use "Answer:" when you have all needed information
4. If you need more information, use another tool - don't guess

REASONING PATTERN:
Thought: [Briefly analyze what you need]
Action: [tool_name]
Action Input: {{"parameter": "value"}}

[Wait for Observation]

Thought: [Analyze the observation, decide if you need more info]
Action: [another_tool if needed]
OR
Answer: [Concise 2-4 sentence response based on facts]

Available tools:
{tool_descriptions}

EXAMPLES:
Q: "Tell me about John's experience"
✓ Thought: Need to search documents for John's experience
✓ Action: search_documents
✓ Action Input: {{"query": "John experience work history"}}
[After observation]
✓ Answer: John has 5 years of experience in software engineering...

Q: "What's 15 + 27?"
✓ Thought: Simple calculation needed
✓ Action: calculate
✓ Action Input: {{"expression": "15 + 27"}}
[After observation]
✓ Answer: The result is 42.

For greetings (hi/hello), respond directly with "Answer: Hello! How can I help you today?"
"""
    
    def __init__(self):
        """Initialize the ReAct agent."""
        self.max_iterations = settings.MAX_ITERATIONS
        self.tools = agent_tools
        self.tool_descriptions = self._format_tool_descriptions()
        logger.info("ReactAgent initialized")
    
    def _format_tool_descriptions(self) -> str:
        """Format tool descriptions for the prompt."""
        descriptions = []
        for tool in self.tools.get_tool_descriptions():
            params = ", ".join([f"{k}: {v}" for k, v in tool['parameters'].items()])
            desc = f"- **{tool['name']}**: {tool['description']}"
            if params:
                desc += f"\n  Parameters: {params}"
            descriptions.append(desc)
        return "\n".join(descriptions)
    
    async def run(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Run the agent to process a user message.
        
        Args:
            user_message: The user's message
            conversation_history: Previous conversation messages
            
        Returns:
            Agent response with reasoning trace
        """
        if conversation_history is None:
            conversation_history = []
        
        # Prepare the system prompt with tool descriptions
        system_prompt = self.SYSTEM_PROMPT.format(
            tool_descriptions=self.tool_descriptions
        )
        
        # Build messages
        messages = [
            {'role': 'system', 'content': system_prompt},
            *conversation_history,
            {'role': 'user', 'content': user_message}
        ]
        
        reasoning_trace = []
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            logger.info(f"Agent iteration {iteration}")
            
            # Get agent response
            response = await llm_client.chat_completion(messages)
            content = response['content']
            
            # Parse the response
            action_match = re.search(r'Action:\s*(\w+)', content)
            action_input_match = re.search(r'Action Input:\s*({.*?})', content, re.DOTALL)
            answer_match = re.search(r'Answer:\s*(.*)', content, re.DOTALL)
            
            # Record the thought process
            thought = self._extract_thought(content)
            if thought:
                reasoning_trace.append({
                    'type': 'thought',
                    'content': thought,
                    'iteration': iteration
                })
            
            # Check if agent wants to use a tool
            if action_match and action_input_match:
                tool_name = action_match.group(1)
                try:
                    action_input = json.loads(action_input_match.group(1))
                except json.JSONDecodeError:
                    action_input = {}
                
                logger.info(f"Agent using tool: {tool_name} with input: {action_input}")
                
                reasoning_trace.append({
                    'type': 'action',
                    'tool': tool_name,
                    'input': action_input,
                    'iteration': iteration
                })
                
                # Execute the tool
                observation = await self._execute_tool(tool_name, action_input)
                
                reasoning_trace.append({
                    'type': 'observation',
                    'content': observation,
                    'iteration': iteration
                })
                
                # Add observation to messages and continue reasoning
                messages.append({'role': 'assistant', 'content': content})
                messages.append({'role': 'user', 'content': f"Observation: {observation}"})
                
            # Check if agent provided an answer
            elif answer_match:
                answer = answer_match.group(1).strip()
                reasoning_trace.append({
                    'type': 'answer',
                    'content': answer,
                    'iteration': iteration
                })
                
                return {
                    'answer': answer,
                    'reasoning_trace': reasoning_trace,
                    'iterations': iteration
                }
            
            # No clear action or answer, use the full response
            else:
                reasoning_trace.append({
                    'type': 'answer',
                    'content': content,
                    'iteration': iteration
                })
                
                return {
                    'answer': content,
                    'reasoning_trace': reasoning_trace,
                    'iterations': iteration
                }
        
        # Max iterations reached
        logger.warning(f"Max iterations ({self.max_iterations}) reached")
        return {
            'answer': "I've reached my reasoning limit. Let me provide what I know so far based on my analysis.",
            'reasoning_trace': reasoning_trace,
            'iterations': iteration
        }
    
    def _extract_thought(self, content: str) -> Optional[str]:
        """Extract thought from agent response."""
        thought_match = re.search(r'Thought:\s*(.*?)(?=\n(?:Action|Answer|$))', content, re.DOTALL)
        if thought_match:
            return thought_match.group(1).strip()
        return None
    
    async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a tool and return the result.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            
        Returns:
            Tool execution result
        """
        tool_func = self.tools.get_tool(tool_name)
        
        if not tool_func:
            return f"Error: Tool '{tool_name}' not found. Available tools: {', '.join(self.tools.tools.keys())}"
        
        try:
            result = await tool_func(**tool_input)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing tool: {str(e)}"


# Global instance
react_agent = ReactAgent()
