"""OpenRouter LLM client for API interactions."""
import logging
from typing import List, Dict, Any, Optional
import httpx
from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""
    
    def __init__(self):
        """Initialize OpenRouter client."""
        self.client = OpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.model = settings.OPENROUTER_MODEL
        logger.info(f"OpenRouterClient initialized with model: {self.model}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate a chat completion.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Completion response
        """
        try:
            if temperature is None:
                temperature = settings.TEMPERATURE
            if max_tokens is None:
                max_tokens = settings.MAX_TOKENS
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                return response
            
            result = {
                'content': response.choices[0].message.content,
                'role': response.choices[0].message.role,
                'finish_reason': response.choices[0].finish_reason,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                } if response.usage else None
            }
            
            logger.info(f"Generated completion: {result.get('usage')}")
            return result
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise
    
    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = None
    ) -> str:
        """Generate a simple text response.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        
        result = await self.chat_completion(messages, temperature=temperature)
        return result['content']
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None
    ):
        """Stream a chat completion.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            
        Yields:
            Completion chunks
        """
        try:
            stream = await self.chat_completion(
                messages=messages,
                temperature=temperature,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error streaming completion: {e}")
            raise


# Global instance
llm_client = OpenRouterClient()
