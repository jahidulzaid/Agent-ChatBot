"""Modern agent runtime with native tool calling and reasoning trace."""
import logging
from typing import Any, Dict, List, Optional, AsyncGenerator

from app.agents.llm_client import llm_client
from app.config import settings
from app.tools.agent_tools import agent_tools

logger = logging.getLogger(__name__)


class AgentRuntime:
    """Executes agent loops with tool calling and structured reasoning traces."""

    SYSTEM_PROMPT = """You are an advanced agentic AI assistant.

Operating principles:
- Prefer calling tools to gather facts before answering.
- Keep tool usage deliberate and minimal.
- Provide concise, factual final answers.
- Do not fabricate observations.

Reasoning output policy:
- You may include a short planning summary before tool calls.
- Keep planning summaries brief and practical.
- Never include sensitive internal chain-of-thought details.

When tools are needed:
- Use function calls with valid JSON arguments.
- After receiving tool results, continue reasoning and decide whether more tools are needed.

When ready:
- Provide a direct final answer to the user.
"""

    COMPLEX_QUERY_HINTS = (
        'research',
        'analyze',
        'compare',
        'deep',
        'multi',
        'iterate',
        'step by step',
        'comprehensive',
        'plan',
    )

    def __init__(self):
        self.max_iterations = settings.MAX_ITERATIONS
        self.tools = agent_tools

    @staticmethod
    def _sanitize_history(conversation_history: Optional[List[Dict[str, str]]]) -> List[Dict[str, str]]:
        """Keep only valid chat history messages."""
        if not conversation_history:
            return []

        cleaned: List[Dict[str, str]] = []
        for msg in conversation_history:
            role = msg.get("role")
            content = msg.get("content", "")
            if role in {"system", "user", "assistant"} and isinstance(content, str):
                cleaned.append({"role": role, "content": content})
        return cleaned

    def _build_messages(self, user_message: str, conversation_history: Optional[List[Dict[str, str]]]) -> List[Dict[str, Any]]:
        """Build model messages for the current run."""
        messages: List[Dict[str, Any]] = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        messages.extend(self._sanitize_history(conversation_history))
        messages.append({"role": "user", "content": user_message})
        return messages

    def _required_tool_calls(self, user_message: str, use_rag: bool) -> int:
        """Determine minimum tool calls required before final answer."""
        if use_rag:
            return 1

        lowered = user_message.lower()
        if any(hint in lowered for hint in self.COMPLEX_QUERY_HINTS):
            return 2

        return 0

    async def run(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        use_rag: bool = True,
    ) -> Dict[str, Any]:
        """Run the iterative agent and return only final payload."""
        final_payload: Optional[Dict[str, Any]] = None
        async for event in self.run_with_events(
            user_message=user_message,
            conversation_history=conversation_history,
            model=model,
            provider=provider,
            use_rag=use_rag,
        ):
            if event.get('event') == 'final':
                final_payload = event.get('result')

        if final_payload is None:
            return {
                'answer': 'I could not produce a complete answer.',
                'reasoning_trace': [],
                'iterations': 0,
                'provider': provider,
                'model': model,
            }

        return final_payload

    async def run_with_events(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        use_rag: bool = True,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Run iterative agent loop and yield trace/final events in real time."""
        messages = self._build_messages(user_message, conversation_history)
        reasoning_trace: List[Dict[str, Any]] = []
        active_tools = self.tools.get_openai_tool_schemas(use_rag=use_rag)

        minimum_tool_calls = self._required_tool_calls(user_message=user_message, use_rag=use_rag)
        observed_tool_calls = 0

        resolved_provider: Optional[str] = None
        resolved_model: Optional[str] = model

        for iteration in range(1, self.max_iterations + 1):
            logger.info('Agent iteration %s', iteration)

            response = await llm_client.chat_completion_with_tools(
                messages=messages,
                tools=active_tools,
                model=model,
                provider=provider,
            )

            resolved_provider = response.get('provider', resolved_provider)
            resolved_model = response.get('model', resolved_model)

            assistant_content = (response.get('content') or '').strip()
            tool_calls = response.get('tool_calls') or []

            if assistant_content:
                thought_step = {
                    'type': 'thought',
                    'content': assistant_content,
                    'iteration': iteration,
                }
                reasoning_trace.append(thought_step)
                yield {
                    'event': 'trace',
                    'step': thought_step,
                }

            if not tool_calls:
                if observed_tool_calls < minimum_tool_calls and iteration < self.max_iterations:
                    nudge = {
                        'type': 'system',
                        'content': 'Continue by calling tools to gather evidence before finalizing.',
                        'iteration': iteration,
                    }
                    reasoning_trace.append(nudge)
                    yield {
                        'event': 'trace',
                        'step': nudge,
                    }
                    messages.append({'role': 'assistant', 'content': assistant_content or ''})
                    messages.append(
                        {
                            'role': 'user',
                            'content': 'Use tools now and continue reasoning before final answer.',
                        }
                    )
                    continue

                final_answer = assistant_content or 'I could not produce a complete answer.'
                answer_step = {
                    'type': 'answer',
                    'content': final_answer,
                    'iteration': iteration,
                }
                reasoning_trace.append(answer_step)
                yield {
                    'event': 'trace',
                    'step': answer_step,
                }

                result = {
                    'answer': final_answer,
                    'reasoning_trace': reasoning_trace,
                    'iterations': iteration,
                    'provider': resolved_provider,
                    'model': resolved_model,
                }
                yield {
                    'event': 'final',
                    'result': result,
                }
                return

            assistant_tool_message: Dict[str, Any] = {
                'role': 'assistant',
                'content': assistant_content or '',
                'tool_calls': tool_calls,
            }
            messages.append(assistant_tool_message)

            for tool_call in tool_calls:
                observed_tool_calls += 1
                function_spec = tool_call.get('function', {})
                tool_name = function_spec.get('name', '')
                arguments_raw = function_spec.get('arguments', '{}')
                parsed_args = self.tools.parse_tool_arguments(arguments_raw)

                action_step = {
                    'type': 'action',
                    'tool': tool_name,
                    'input': parsed_args,
                    'iteration': iteration,
                }
                reasoning_trace.append(action_step)
                yield {
                    'event': 'trace',
                    'step': action_step,
                }

                observation = await self.tools.execute_tool_call(tool_name, arguments_raw)
                observation_step = {
                    'type': 'observation',
                    'content': observation,
                    'iteration': iteration,
                }
                reasoning_trace.append(observation_step)
                yield {
                    'event': 'trace',
                    'step': observation_step,
                }

                messages.append(
                    {
                        'role': 'tool',
                        'tool_call_id': tool_call.get('id'),
                        'content': observation,
                    }
                )

        logger.warning('Max iterations (%s) reached', self.max_iterations)
        fallback_answer = 'I reached the reasoning limit before finalizing the answer.'
        answer_step = {
            'type': 'answer',
            'content': fallback_answer,
            'iteration': self.max_iterations,
        }
        reasoning_trace.append(answer_step)
        yield {
            'event': 'trace',
            'step': answer_step,
        }

        result = {
            'answer': fallback_answer,
            'reasoning_trace': reasoning_trace,
            'iterations': self.max_iterations,
            'provider': resolved_provider,
            'model': resolved_model,
        }
        yield {
            'event': 'final',
            'result': result,
        }


agent_runtime = AgentRuntime()
