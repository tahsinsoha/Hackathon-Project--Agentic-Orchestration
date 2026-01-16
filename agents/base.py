"""Base agent class with LLM integration."""
import os
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Base class for all agents in the pipeline."""
    
    def __init__(self, name: str, model: str = "claude-3-5-sonnet-20241022"):
        self.name = name
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task.
        
        Args:
            context: Current incident context
            
        Returns:
            Dict with agent's output
        """
        pass
    
    async def call_llm(self, system_prompt: str, user_message: str) -> str:
        """Call LLM for reasoning.
        
        Args:
            system_prompt: System instructions for the agent
            user_message: User message with incident data
            
        Returns:
            LLM response text
        """
        try:
            # Try Anthropic first
            if self.api_key and self.api_key != "your_key_here":
                import anthropic
                client = anthropic.Anthropic(api_key=self.api_key)
                message = client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}]
                )
                return message.content[0].text
        except Exception as e:
            print(f"LLM call failed: {e}")
        
        # Fallback to simulated response for demo
        return self._simulate_response(user_message)
    
    def _simulate_response(self, user_message: str) -> str:
        """Simulate an LLM response for demo purposes."""
        return f"[Simulated {self.name} response based on: {user_message[:100]}...]"

