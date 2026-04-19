"""Compatibility wrapper for the modern agent runtime."""
from typing import Any, Dict, List, Optional

from app.agents.agent_runtime import agent_runtime


class ReactAgent:
    """Facade that preserves the previous interface."""

    async def run(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        use_rag: bool = True,
    ) -> Dict[str, Any]:
        """Delegate to the new runtime."""
        return await agent_runtime.run(
            user_message=user_message,
            conversation_history=conversation_history,
            model=model,
            provider=provider,
            use_rag=use_rag,
        )


react_agent = ReactAgent()
