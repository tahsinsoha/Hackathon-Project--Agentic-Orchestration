"""Google Gemini (GenAI SDK) client for incident classification."""
import os
import json
from typing import Dict, Any, Optional

from google import genai


class GeminiClient:
    """Wrapper for Google Gemini API using the new Google GenAI SDK."""

    def __init__(self, api_key: str = None, model: str = None):
        """
        Args:
            api_key: Google API key (or loads from env GOOGLE_API_KEY)
            model: Gemini model name (default: a safe modern model)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY", "")
        # Pick a modern default; adjust if you want another
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

        if self.api_key and self.api_key != "your_key_here":
            self.client = genai.Client(api_key=self.api_key)
            print("   ✅ [GEMINI] Initialized (google-genai)")
        else:
            self.client = None
            print("   ⚠️  [GEMINI] No API key - AI features disabled")

    def generate_content(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Optional[str]:
        """Generate text using Gemini."""
        if not self.client:
            print("   ⚠️  [GEMINI] Client not initialized")
            return None

        try:
            resp = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            text = getattr(resp, "text", None)
            if text:
                return text
            print("   ⚠️  [GEMINI] Empty response from API")
            return None

        except Exception as e:
            print(f"   ❌ [GEMINI] API call failed: {e}")
            return None

    def generate_json(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> Optional[Dict[str, Any]]:
        """Generate JSON response using Gemini."""
        response_text = self.generate_content(prompt, temperature, max_tokens)
        if not response_text:
            return None

        cleaned = response_text.strip()

        # Remove markdown code fences if model returns them
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"   ❌ [GEMINI] Failed to parse JSON: {e}")
            print(f"   Response was: {response_text[:300]}")
            return None
