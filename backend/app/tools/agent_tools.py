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
            'web_search': self.web_search
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
                'description': 'Search web for current info (simulated). Use for recent events not in documents.',
                'parameters': {
                    'query': 'Search query'
                }
            }
        ]
    
    def get_tool(self, tool_name: str) -> Callable:
        """Get a tool by name.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool function
        """
        return self.tools.get(tool_name)
    
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
        """Simulate web search (placeholder for actual implementation).
        
        Args:
            query: Search query
            
        Returns:
            Search results
        """
        # This is a placeholder - in production, you'd integrate with a real search API
        return f"Web search for '{query}': This is a simulated result. In production, this would query a real search API like DuckDuckGo or SerpAPI."


# Global instance
agent_tools = AgentTools()
