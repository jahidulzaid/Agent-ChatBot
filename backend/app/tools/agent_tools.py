"""Agent tools for various tasks."""
import logging
from typing import Dict, Any, List, Callable
import json
from datetime import datetime
import httpx

from app.rag.vector_store import vector_store

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
                'description': 'Search the web for current information using DuckDuckGo. Use for recent events, facts, or information not available in documents.',
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
            # Only allow safe operations
            allowed_names = {
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'sum': sum, 'pow': pow
            }
            result = eval(expression, {"__builtins__": {}}, allowed_names)
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
        try:
            # Zenserp API configuration
            api_url = "https://app.zenserp.com/api/v2/search"
            headers = {
                "apikey": "d79890a0-b22e-11f0-b1ad-73eadf9a1c39"
            }
            params = {
                "q": query
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(api_url, headers=headers, params=params)
                
                if response.status_code != 200:
                    # Fallback to DuckDuckGo link
                    search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&ia=web"
                    return f"**Web Search:** {query}\n\nSearch API unavailable (Status: {response.status_code})\nClick here to search manually: {search_url}"
                
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
                    
                    # Add search URL for more results
                    search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&ia=web"
                    results.append(f"**See all results:** {search_url}")
                    
                    return "\n".join(results)
                else:
                    # No results found
                    search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&ia=web"
                    return f"**Web Search:** {query}\n\nNo results found.\nTry searching manually: {search_url}"
                    
        except httpx.TimeoutException:
            search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&ia=web"
            return f"**Web Search:** {query}\n\nSearch timed out (15s limit exceeded).\nClick here to search manually: {search_url}"
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&ia=web"
            return f"**Web Search:** {query}\n\nError: {str(e)}\nClick here to search manually: {search_url}"

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
