import os
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseAgent(ABC):
   
    def __init__(self, name: str, model: str = "gemini-pro"):
        self.name = name
        self.model = model
        
        # Try to initialize AI client
        self.ai_client = self._initialize_ai_client()
    
    def _initialize_ai_client(self):
        """Initialize AI client"""
        google_key = os.getenv("GOOGLE_API_KEY", "")
        if google_key and google_key != "your_key_here":
            try:
                from integrations.gemini import GeminiClient
                return GeminiClient(google_key)
            except ImportError:
                print(f"[AGENT] google-generativeai not installed")
        print(f"[AGENT] No AI API key found")
        return None
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    def call_llm(self, prompt: str, 
                 temperature: float = 0.7,
                 max_tokens: int = 1000) -> Optional[str]:
        if self.ai_client:
            return self.ai_client.generate_content(prompt, temperature, max_tokens)
        
        print(f"[{self.name}] No AI client available")
        return None
    
    def call_llm_json(self, prompt: str,
                     temperature: float = 0.3,
                     max_tokens: int = 1000) -> Optional[Dict[str, Any]]:
        if self.ai_client:
            return self.ai_client.generate_json(prompt, temperature, max_tokens)
        
        print(f"[{self.name}] No AI client available")
        return None