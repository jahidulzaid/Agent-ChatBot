"""Agent tools for various tasks."""
import logging
import json
from typing import Dict, Any, List, Callable
from datetime import datetime
import httpx
import ast
import math

from app.rag.vector_store import vector_store
from app.config import settings

logger = logging.getLogger(__name__)


class AgentTools:
    """Collection of tools the agent can use."""
    
    def __init__(self):
        """Initialize agent tools."""
        self.tools = {
            'search_documents': self.search_documents,
            'get_current_time': self.get_current_time,
            'calculate': self.calculate,
            'summarize_documents': self.summarize_documents,
            'web_search': self.web_search,
            'greet': self.greet,
            'wish': self.wish,
            'tell_joke': self.tell_joke
        }
    
    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """Get descriptions of all available tools.
        
        Returns:
            List of tool descriptions for the agent
        """
        return [
            {
                'name': 'search_documents',
                'description': 'Search uploaded documents for information. REQUIRED for questions about people, experiences, skills, education, projects, or any topic that could be in documents.',
                'parameters': {
                    'query': 'Search query (e.g., "experience", "skills", "education")'
                }
            },
            {
                'name': 'get_current_time',
                'description': 'Get current date/time. Use when user asks about time or date.',
                'parameters': {}
            },
            {
                'name': 'calculate',
                'description': 'Evaluate math expressions. Use for any calculations.',
                'parameters': {
                    'expression': 'Python math expression (e.g., "2 + 2", "10 * 5 + 3")'
                }
            },
            {
                'name': 'summarize_documents',
                'description': 'Get count of documents in knowledge base. Use when user asks what documents are available.',
                'parameters': {}
            },
            {
                'name': 'web_search',
                'description': 'Search the web for current information using Tavily (with fallback providers). Use for recent events, facts, or information not available in documents.',
                'parameters': {
                    'query': 'Search query (e.g., "latest AI news", "Python 3.12 features")'
                }
            },
            {
                'name': 'greet',
                'description': 'Generate a personalized greeting. Use when user wants a formal greeting or introduction.',
                'parameters': {
                    'name': 'Person name (optional)'
                }
            },
            {
                'name': 'wish',
                'description': 'Generate wishes for occasions. Use when user mentions birthday, holiday, celebration, etc.',
                'parameters': {
                    'occasion': 'Occasion (e.g., "birthday", "new year", "success")'
                }
            },
            {
                'name': 'tell_joke',
                'description': 'Tell a programming or tech joke. Use when user asks for a joke or wants humor.',
                'parameters': {}
            }
        ]
    
    def get_tool(self, tool_name: str) -> Callable:
        """Get a tool by name.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool function
        """
        return self.tools.get(tool_name) # pyright: ignore[reportReturnType]

    def get_openai_tool_schemas(self, use_rag: bool = True) -> List[Dict[str, Any]]:
        """Return OpenAI-compatible function tool schemas."""
        schemas = [
            {
                'type': 'function',
                'function': {
                    'name': 'search_documents',
                    'description': 'Search uploaded documents for relevant information.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'query': {
                                'type': 'string',
                                'description': 'Search query for the document knowledge base'
                            }
                        },
                        'required': ['query'],
                        'additionalProperties': False,
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'summarize_documents',
                    'description': 'Get a count summary of the current document knowledge base.',
                    'parameters': {
                        'type': 'object',
                        'properties': {},
                        'additionalProperties': False,
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'web_search',
                    'description': 'Search the web for current information.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'query': {
                                'type': 'string',
                                'description': 'Web search query'
                            }
                        },
                        'required': ['query'],
                        'additionalProperties': False,
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'calculate',
                    'description': 'Safely evaluate a mathematical expression.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'expression': {
                                'type': 'string',
                                'description': 'Math expression such as 2 + 2 or pow(3, 2)'
                            }
                        },
                        'required': ['expression'],
                        'additionalProperties': False,
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'get_current_time',
                    'description': 'Get current local date and time.',
                    'parameters': {
                        'type': 'object',
                        'properties': {},
                        'additionalProperties': False,
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'greet',
                    'description': 'Generate a personalized greeting.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'name': {
                                'type': 'string',
                                'description': 'Optional person name for greeting'
                            }
                        },
                        'additionalProperties': False,
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'wish',
                    'description': 'Generate wishes for occasions.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'occasion': {
                                'type': 'string',
                                'description': 'Occasion such as birthday, holiday, graduation'
                            }
                        },
                        'required': ['occasion'],
                        'additionalProperties': False,
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'tell_joke',
                    'description': 'Tell a short programming or tech joke.',
                    'parameters': {
                        'type': 'object',
                        'properties': {},
                        'additionalProperties': False,
                    }
                }
            },
        ]

        if not use_rag:
            return [
                schema
                for schema in schemas
                if schema['function']['name'] not in {'search_documents', 'summarize_documents'}
            ]

        return schemas

    @staticmethod
    def parse_tool_arguments(arguments: Any) -> Dict[str, Any]:
        """Parse tool arguments from model-generated JSON payload."""
        if arguments is None:
            return {}
        if isinstance(arguments, dict):
            return arguments
        if not isinstance(arguments, str):
            return {}

        stripped = arguments.strip()
        if not stripped:
            return {}

        try:
            parsed = json.loads(stripped)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    async def execute_tool_call(self, tool_name: str, arguments: Any) -> str:
        """Execute a tool from function-calling payload."""
        tool_func = self.get_tool(tool_name)
        if not tool_func:
            return f"Error: Tool '{tool_name}' not found."

        tool_args = self.parse_tool_arguments(arguments)
        try:
            result = await tool_func(**tool_args)
            if isinstance(result, str):
                return result
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error('Error executing tool %s: %s', tool_name, e)
            return f"Error executing tool '{tool_name}': {str(e)}"
    
    async def search_documents(self, query: str, **kwargs) -> str:
        """Search documents in the vector store.
        
        Args:
            query: Search query
            
        Returns:
            Formatted search results
        """
        try:
            results = vector_store.search(query, n_results=5)
            
            if not results:
                return "No relevant documents found in the knowledge base."
            
            # Format concisely
            output = "Found relevant information:\n\n"
            for i, result in enumerate(results, 1):
                # Show first 200 chars of each result
                text_snippet = result['text'][:200].strip()
                if len(result['text']) > 200:
                    text_snippet += "..."
                output += f"{i}. {text_snippet}\n"
                output += f"   (Source: {result['metadata'].get('source', 'Unknown')})\n\n"
            
            return output
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return f"Error searching documents: {str(e)}"
    
    async def get_current_time(self, **kwargs) -> str:
        """Get current date and time.
        
        Returns:
            Current date and time as string
        """
        now = datetime.now()
        return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    async def calculate(self, expression: str, **kwargs) -> str:
        """Safely evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            Calculation result
        """
        try:
            allowed_funcs = {
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'pow': pow,
            }
            allowed_consts = {
                'pi': math.pi,
                'e': math.e,
            }

            parsed = ast.parse(expression, mode='eval')
            allowed_nodes = (
                ast.Expression,
                ast.BinOp,
                ast.UnaryOp,
                ast.Add,
                ast.Sub,
                ast.Mult,
                ast.Div,
                ast.FloorDiv,
                ast.Mod,
                ast.Pow,
                ast.USub,
                ast.UAdd,
                ast.Constant,
                ast.Call,
                ast.Name,
                ast.Load,
                ast.Tuple,
                ast.List,
            )

            for node in ast.walk(parsed):
                if not isinstance(node, allowed_nodes):
                    return "Error calculating: Unsupported operation in expression"
                if isinstance(node, ast.Call):
                    if not isinstance(node.func, ast.Name) or node.func.id not in allowed_funcs:
                        return "Error calculating: Unsupported function in expression"
                if isinstance(node, ast.Name):
                    if node.id not in allowed_funcs and node.id not in allowed_consts:
                        return f"Error calculating: Unknown identifier '{node.id}'"

            result = eval(
                compile(parsed, '<calculator>', 'eval'),
                {"__builtins__": {}},
                {**allowed_funcs, **allowed_consts},
            )
            return f"Result: {result}"
        except Exception as e:
            return f"Error calculating: {str(e)}"
    
    async def summarize_documents(self, **kwargs) -> str:
        """Get summary of documents in the knowledge base.
        
        Returns:
            Document summary
        """
        try:
            stats = vector_store.get_collection_stats()
            return f"Knowledge base contains {stats['total_documents']} document chunks."
        except Exception as e:
            logger.error(f"Error getting document summary: {e}")
            return f"Error getting document summary: {str(e)}"
    
    async def web_search(self, query: str, **kwargs) -> str:
        """Search the web for current information.
        
        Args:
            query: Search query
            
        Returns:
            Search results
        """
        if settings.WEB_SEARCH_PROVIDER == "tavily":
            if settings.TAVILY_API_KEY:
                return await self._search_with_tavily(query)
            logger.warning("WEB_SEARCH_PROVIDER is 'tavily' but TAVILY_API_KEY is not configured. Falling back to DuckDuckGo.")
            return await self._search_with_duckduckgo(query)

        if settings.WEB_SEARCH_PROVIDER == "zenserp" and settings.ZENSERP_API_KEY:
            return await self._search_with_zenserp(query)

        return await self._search_with_duckduckgo(query)

    async def _search_with_tavily(self, query: str) -> str:
        """Search using Tavily API."""
        search_url = "https://api.tavily.com/search"
        fallback_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&ia=web"

        payload = {
            "query": query,
            "search_depth": settings.TAVILY_SEARCH_DEPTH,
            "max_results": max(1, min(settings.TAVILY_MAX_RESULTS, 20)),
            "include_answer": True,
            "include_raw_content": False,
            "include_images": False,
            "include_usage": True,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.TAVILY_API_KEY}",
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(search_url, headers=headers, json=payload)

            if response.status_code != 200:
                logger.warning("Tavily search failed with status %s, falling back to DuckDuckGo", response.status_code)
                return await self._search_with_duckduckgo(query)

            data = response.json()
            lines = [f"**Web Search Results for:** {query}", ""]

            answer = data.get("answer")
            if answer:
                lines.append("**Tavily Answer:**")
                lines.append(answer)
                lines.append("")

            results = data.get("results", [])
            if results:
                lines.append("**Top Sources:**")
                for idx, item in enumerate(results[:5], 1):
                    title = item.get("title") or "Untitled"
                    url = item.get("url") or ""
                    content = (item.get("content") or "").strip()
                    score = item.get("score")

                    lines.append(f"{idx}. **{title}**")
                    if content:
                        snippet = content[:220] + "..." if len(content) > 220 else content
                        lines.append(f"   {snippet}")
                    if score is not None:
                        try:
                            lines.append(f"   Relevance: {float(score):.2f}")
                        except Exception:
                            pass
                    if url:
                        lines.append(f"   {url}")
            else:
                lines.append("No Tavily results returned.")

            response_time = data.get("response_time")
            usage = data.get("usage", {})
            credits = usage.get("credits")

            lines.append("")
            if response_time is not None:
                lines.append(f"Response time: {response_time}s")
            if credits is not None:
                lines.append(f"Credits used: {credits}")
            lines.append(f"See more: {fallback_url}")

            return "\n".join(lines)
        except httpx.TimeoutException:
            logger.warning("Tavily search timed out, falling back to DuckDuckGo")
            return await self._search_with_duckduckgo(query)
        except Exception as e:
            logger.error(f"Error performing Tavily web search: {e}")
            return await self._search_with_duckduckgo(query)

    async def _search_with_zenserp(self, query: str) -> str:
        """Search using Zenserp when configured."""
        try:
            api_url = "https://app.zenserp.com/api/v2/search"
            headers = {
                "apikey": settings.ZENSERP_API_KEY or ""
            }
            params = {
                "q": query
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(api_url, headers=headers, params=params)
                
                if response.status_code != 200:
                    return await self._search_with_duckduckgo(query)
                
                data = response.json()
                
                # Build formatted results
                results = [f"**Web Search Results for:** {query}\n"]
                
                # Get organic search results
                organic_results = data.get('organic', [])
                
                if organic_results:
                    results.append("**Top Results:**\n")
                    for i, result in enumerate(organic_results[:5], 1):
                        title = result.get('title', 'No title')
                        url = result.get('url', '')
                        description = result.get('description', '')
                        
                        results.append(f"{i}. **{title}**")
                        if description:
                            # Limit description to 150 chars
                            desc = description[:150] + "..." if len(description) > 150 else description
                            results.append(f"   {desc}")
                        if url:
                            results.append(f"  {url}")
                        results.append("")  # Empty line for spacing
                    
                    search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&ia=web"
                    results.append(f"**See all results:** {search_url}")
                    
                    return "\n".join(results)
                else:
                    return await self._search_with_duckduckgo(query)
                    
        except httpx.TimeoutException:
            return await self._search_with_duckduckgo(query)
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            return await self._search_with_duckduckgo(query)

    async def _search_with_duckduckgo(self, query: str) -> str:
        """Search using DuckDuckGo Instant Answer API with graceful fallback."""
        search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&ia=web"
        instant_url = "https://api.duckduckgo.com/"

        try:
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1",
            }
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.get(instant_url, params=params)

            if response.status_code != 200:
                return f"**Web Search:** {query}\n\nSearch service unavailable right now.\nTry manual search: {search_url}"

            data = response.json()
            lines = [f"**Web Search Results for:** {query}\n"]

            abstract = data.get("AbstractText")
            heading = data.get("Heading")
            if abstract:
                lines.append(f"**{heading or 'Summary'}**")
                lines.append(abstract)
                if data.get("AbstractURL"):
                    lines.append(f"Source: {data['AbstractURL']}")
                lines.append("")

            related_topics = data.get("RelatedTopics", [])
            snippets = []
            for topic in related_topics:
                if "Text" in topic and "FirstURL" in topic:
                    snippets.append((topic["Text"], topic["FirstURL"]))
                if "Topics" in topic:
                    for nested in topic["Topics"]:
                        if "Text" in nested and "FirstURL" in nested:
                            snippets.append((nested["Text"], nested["FirstURL"]))

            if snippets:
                lines.append("**Related Results:**")
                for idx, (text, url) in enumerate(snippets[:5], 1):
                    trimmed = text[:160] + "..." if len(text) > 160 else text
                    lines.append(f"{idx}. {trimmed}")
                    lines.append(f"   {url}")

            if len(lines) <= 2:
                return f"**Web Search:** {query}\n\nNo direct instant results found.\nTry manual search: {search_url}"

            lines.append("")
            lines.append(f"**See more results:** {search_url}")
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return f"**Web Search:** {query}\n\nUnable to fetch search results.\nTry manual search: {search_url}"

    async def greet(self, name: str = None, **kwargs) -> str: # pyright: ignore[reportArgumentType]
        """Generate a personalized greeting.
        
        Args:
            name: Optional person name
            
        Returns:
            Personalized greeting
        """
        if name:
            return f"Hello {name}! It's wonderful to meet you. I'm an AI assistant ready to help you with information retrieval, calculations, and answering your questions. How may I assist you today?"
        return "Hello! Welcome! I'm an AI assistant equipped with various tools to help you. I can search documents, perform calculations, tell jokes, and much more. What can I do for you today?"
    
    async def wish(self, occasion: str, **kwargs) -> str:
        """Generate wishes for special occasions.
        
        Args:
            occasion: The occasion (birthday, new year, etc.)
            
        Returns:
            Wishes message
        """
        occasion_lower = occasion.lower()
        
        wishes = {
            'birthday': "🎉 Happy Birthday! May this special day bring you joy, success, and wonderful memories. Wishing you a year filled with happiness and achievements!",
            'new year': "🎊 Happy New Year! May this year bring you new opportunities, success, and happiness. Here's to fresh starts and exciting adventures ahead!",
            'success': "🌟 Congratulations on your success! Your hard work and dedication have truly paid off. Wishing you continued success in all your future endeavors!",
            'graduation': "🎓 Congratulations on your graduation! This is just the beginning of an amazing journey. Wishing you all the best in your future career!",
            'wedding': "💒 Congratulations on your wedding! Wishing you a lifetime of love, laughter, and happiness together!",
            'holiday': "🎄 Happy Holidays! May this festive season bring you warmth, joy, and precious moments with loved ones!",
        }
        
        for key, wish in wishes.items():
            if key in occasion_lower:
                return wish
        
        return f"🎉 Wishing you all the best for {occasion}! May it be filled with joy, success, and wonderful moments!"
    
    async def tell_joke(self, **kwargs) -> str:
        """Tell a programming or tech joke.
        
        Returns:
            A joke
        """
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
            "Why did the programmer quit his job? Because he didn't get arrays! 💰",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem! 💡",
            "Why do Java developers wear glasses? Because they don't C#! 👓",
            "What's a programmer's favorite hangout place? Foo Bar! 🍺",
            "Why did the developer go broke? Because he used up all his cache! 💸",
            "What do you call a programmer from Finland? Nerdic! 🇫🇮",
            "Why do programmers always mix up Halloween and Christmas? Because Oct 31 == Dec 25! 🎃🎄",
            "What's the object-oriented way to become wealthy? Inheritance! 💰",
            "Why did the programmer get stuck in the shower? The shampoo bottle said: Lather, Rinse, Repeat! 🚿"
        ]
        
        import random
        return random.choice(jokes)


# Global instance
agent_tools = AgentTools()
