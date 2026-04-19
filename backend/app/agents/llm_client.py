"""Multi-provider LLM client (OpenRouter + OpenAI)."""
import logging
from typing import List, Dict, Any, Optional, Literal
from urllib.parse import urlparse

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

ProviderName = Literal["openrouter", "openai"]


class LLMClient:
    """Client for interacting with OpenRouter and OpenAI APIs."""

    OPENROUTER_MODELS = [
        {"id": "openai/gpt-4o-mini-2024-07-18", "name": "GPT-4o Mini", "provider": "OpenAI"},
        {"id": "google/gemini-flash-1.5", "name": "Gemini Flash 1.5", "provider": "Google"},
        {"id": "meta-llama/llama-3.2-3b-instruct:free", "name": "Llama 3.2 3B", "provider": "Meta"},
        {"id": "microsoft/phi-3-mini-128k-instruct:free", "name": "Phi-3 Mini", "provider": "Microsoft"},
        {"id": "mistralai/mistral-7b-instruct:free", "name": "Mistral 7B", "provider": "Mistral"},
        {"id": "qwen/qwen-2-7b-instruct:free", "name": "Qwen 2 7B", "provider": "Qwen"},
    ]

    OPENAI_MODELS = [
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "provider": "OpenAI"},
        {"id": "gpt-4.1-mini", "name": "GPT-4.1 Mini", "provider": "OpenAI"},
        {"id": "gpt-4.1", "name": "GPT-4.1", "provider": "OpenAI"},
    ]

    def __init__(self):
        """Initialize provider clients based on configured API keys."""
        self.openrouter_client: Optional[AsyncOpenAI] = None
        self.openai_client: Optional[AsyncOpenAI] = None

        if settings.has_openrouter_key:
            default_headers: Dict[str, str] = {}
            if settings.OPENROUTER_SITE_URL:
                parsed = urlparse(settings.OPENROUTER_SITE_URL)
                if parsed.scheme and parsed.netloc:
                    default_headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
            default_headers["X-Title"] = settings.OPENROUTER_APP_NAME

            self.openrouter_client = AsyncOpenAI(
                base_url=settings.OPENROUTER_BASE_URL,
                api_key=settings.OPENROUTER_API_KEY,
                default_headers=default_headers,
            )

        if settings.has_openai_key:
            self.openai_client = AsyncOpenAI(
                base_url=settings.OPENAI_BASE_URL,
                api_key=settings.OPENAI_API_KEY,
            )

        if not self.openrouter_client and not self.openai_client:
            logger.warning(
                "No LLM API keys configured. Set OPENROUTER_API_KEY (recommended) or OPENAI_API_KEY."
            )

        logger.info(
            "LLMClient initialized | preferred=%s | openrouter=%s | openai=%s",
            settings.LLM_PROVIDER,
            bool(self.openrouter_client),
            bool(self.openai_client),
        )

    def get_provider_status(self) -> Dict[str, Any]:
        """Return configured providers and defaults."""
        return {
            "preferred_provider": settings.LLM_PROVIDER,
            "has_openrouter_key": bool(self.openrouter_client),
            "has_openai_key": bool(self.openai_client),
            "default_openrouter_model": settings.OPENROUTER_MODEL,
            "default_openai_model": settings.OPENAI_MODEL,
        }

    def get_model_catalog(self) -> Dict[str, Any]:
        """Return model choices by provider for frontend selection."""
        return {
            "providers": ["auto", "openrouter", "openai"],
            "recommended_provider": self._recommend_provider(),
            "models_by_provider": {
                "openrouter": self.OPENROUTER_MODELS,
                "openai": self.OPENAI_MODELS,
            },
            "default_models": {
                "openrouter": settings.OPENROUTER_MODEL,
                "openai": settings.OPENAI_MODEL,
            },
            "provider_status": self.get_provider_status(),
        }

    def _recommend_provider(self) -> ProviderName:
        """Select best default provider from configuration and key availability."""
        preferred = settings.LLM_PROVIDER
        if preferred == "openrouter" and self.openrouter_client:
            return "openrouter"
        if preferred == "openai" and self.openai_client:
            return "openai"
        if self.openrouter_client:
            return "openrouter"
        return "openai"

    def _infer_provider_from_model(self, model: Optional[str]) -> Optional[ProviderName]:
        """Infer provider from model naming style when possible."""
        if not model:
            return None
        if "/" in model or ":free" in model:
            return "openrouter"
        return "openai"

    def _resolve_provider(self, requested_provider: Optional[str], model: Optional[str]) -> ProviderName:
        """Resolve effective provider with fallback logic."""
        if not self.openrouter_client and not self.openai_client:
            raise ValueError(
                "No LLM provider is configured. Set OPENROUTER_API_KEY (recommended) or OPENAI_API_KEY."
            )

        if requested_provider and requested_provider != "auto":
            if requested_provider == "openrouter" and self.openrouter_client:
                return "openrouter"
            if requested_provider == "openai" and self.openai_client:
                return "openai"
            raise ValueError(f"Requested provider '{requested_provider}' is unavailable. Check API key setup.")

        inferred = self._infer_provider_from_model(model)
        if inferred == "openrouter" and self.openrouter_client:
            return "openrouter"
        if inferred == "openai" and self.openai_client:
            return "openai"

        preferred = self._recommend_provider()
        if preferred == "openrouter" and self.openrouter_client:
            return "openrouter"
        if preferred == "openai" and self.openai_client:
            return "openai"

        raise ValueError("No available provider could be selected.")

    def _default_model_for_provider(self, provider: ProviderName) -> str:
        """Return default model for the resolved provider."""
        return settings.OPENROUTER_MODEL if provider == "openrouter" else settings.OPENAI_MODEL

    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        model: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a chat completion using the chosen provider."""
        try:
            if temperature is None:
                temperature = settings.TEMPERATURE
            if max_tokens is None:
                max_tokens = settings.MAX_TOKENS

            resolved_provider = self._resolve_provider(provider, model)
            resolved_model = model or self._default_model_for_provider(resolved_provider)

            client = self.openrouter_client if resolved_provider == "openrouter" else self.openai_client
            if client is None:
                raise ValueError(f"Provider '{resolved_provider}' is unavailable.")

            response = await client.chat.completions.create(
                model=resolved_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
            )

            if stream:
                return response  # type: ignore[return-value]

            result = {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "finish_reason": response.choices[0].finish_reason,
                "provider": resolved_provider,
                "model": resolved_model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
                if response.usage
                else None,
            }

            logger.info(
                "Generated completion | provider=%s model=%s usage=%s",
                resolved_provider,
                resolved_model,
                result.get("usage"),
            )
            return result
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        provider: Optional[str] = None,
    ) -> str:
        """Generate a simple text response."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        result = await self.chat_completion(messages, temperature=temperature, provider=provider)
        return result["content"]

    async def stream_completion(
        self,
        messages: List[Dict[str, Any]],
        temperature: Optional[float] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
    ):
        """Stream a chat completion."""
        try:
            stream = await self.chat_completion(
                messages=messages,
                temperature=temperature,
                stream=True,
                model=model,
                provider=provider,
            )

            async for chunk in stream:  # type: ignore[attr-defined]
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error streaming completion: {e}")
            raise

    async def chat_completion_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a completion with native function-calling support."""
        if temperature is None:
            temperature = settings.TEMPERATURE
        if max_tokens is None:
            max_tokens = settings.MAX_TOKENS

        resolved_provider = self._resolve_provider(provider, model)
        resolved_model = model or self._default_model_for_provider(resolved_provider)

        client = self.openrouter_client if resolved_provider == "openrouter" else self.openai_client
        if client is None:
            raise ValueError(f"Provider '{resolved_provider}' is unavailable.")

        try:
            response = await client.chat.completions.create(
                model=resolved_model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as tool_error:
            logger.warning(
                "Tool-calling request failed for provider=%s model=%s; falling back to plain completion. Error: %s",
                resolved_provider,
                resolved_model,
                tool_error,
            )
            fallback = await self.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                model=resolved_model,
                provider=resolved_provider,
            )
            fallback["tool_calls"] = []
            return fallback

        message = response.choices[0].message

        normalized_tool_calls: List[Dict[str, Any]] = []
        for call in message.tool_calls or []:
            normalized_tool_calls.append(
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments or "{}",
                    },
                }
            )

        result = {
            "content": message.content or "",
            "role": message.role,
            "finish_reason": response.choices[0].finish_reason,
            "provider": resolved_provider,
            "model": resolved_model,
            "tool_calls": normalized_tool_calls,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            if response.usage
            else None,
        }

        logger.info(
            "Generated tool-call completion | provider=%s model=%s tool_calls=%s usage=%s",
            resolved_provider,
            resolved_model,
            len(normalized_tool_calls),
            result.get("usage"),
        )
        return result


# Global instance
llm_client = LLMClient()
