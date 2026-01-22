"""Base agent class with LLM integration."""
import os
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Base class for all agents in the pipeline."""
    
    def __init__(self, name: str, model: str = "gemini-pro"):
        """Initialize agent.
        
        Args:
            name: Agent name for logging
            model: AI model to use (default: gemini-pro)
        """
        self.name = name
        self.model = model
        
        # Try to initialize AI client
        self.ai_client = self._initialize_ai_client()
    
    def _initialize_ai_client(self):
        """Initialize AI client (Gemini preferred, fallback to others)."""
        # Try Google Gemini first (free!)
        google_key = os.getenv("GOOGLE_API_KEY", "")
        if google_key and google_key != "your_key_here":
            try:
                from integrations.gemini import GeminiClient
                return GeminiClient(google_key)
            except ImportError:
                print(f"   ⚠️  [AGENT] google-generativeai not installed")
        
        # Fallback to Anthropic if available
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        if anthropic_key and anthropic_key != "your_key_here":
            print(f"   ℹ️  [AGENT] Using Anthropic Claude as fallback")
            # Keep existing Anthropic code as fallback
            return None  # Will use old method
        
        print(f"   ⚠️  [AGENT] No AI API key found")
        return None
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task.
        
        Args:
            context: Current incident context
            
        Returns:
            Dict with agent's output
        """
        pass
    
    def call_llm(self, prompt: str, 
                 temperature: float = 0.7,
                 max_tokens: int = 1000) -> Optional[str]:
        """Call LLM for text generation.
        
        Args:
            prompt: The prompt to send
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text or None
        """
        if self.ai_client:
            return self.ai_client.generate_content(prompt, temperature, max_tokens)
        
        print(f"   ℹ️  [{self.name}] No AI client available")
        return None
    
    def call_llm_json(self, prompt: str,
                     temperature: float = 0.3,
                     max_tokens: int = 1000) -> Optional[Dict[str, Any]]:
        """Call LLM for JSON generation.
        
        Args:
            prompt: The prompt requesting JSON output
            temperature: Sampling temperature (lower for JSON)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Parsed JSON dict or None
        """
        if self.ai_client:
            return self.ai_client.generate_json(prompt, temperature, max_tokens)
        
        print(f"   ℹ️  [{self.name}] No AI client available")
        return None