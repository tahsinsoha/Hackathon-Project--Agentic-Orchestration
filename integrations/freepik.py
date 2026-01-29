import os
import requests
from typing import Dict, Optional


class FreepikClient:
    """Client for Freepik API integration."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("FREEPIK_API_KEY", "")
        self.base_url = "https://api.freepik.com/v1"
    
    def generate_incident_card(self, incident_data: Dict) -> str:
        """Generate a visual incident card with timeline using Freepik AI.
        
        Args:
            incident_data: Incident details for visualization
            
        Returns:
            URL or path to generated image
        """
        if not self.api_key:
            incident_id = incident_data.get("id", "unknown")
            print(f"[FREEPIK] No API key - returning placeholder image")
            return f"https://cdn.freepik.com/incident-cards/{incident_id}.png"
        
        print(f"   🔑 [FREEPIK] API key detected, generating AI image...")
        
        try:
            # Real Freepik API call for AI image generation
            incident_type = incident_data.get("type", "incident")
            severity = incident_data.get("severity", "high")
            
            prompt = f"Technical incident alert card, {severity} severity {incident_type}, minimalist infographic style, red and orange gradient"
            
            response = requests.post(
                f"{self.base_url}/ai/text-to-image",
                headers={
                    "x-freepik-api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "num_images": 1,
                    "image_size": "square_1_1"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                image_url = result.get("data", [{}])[0].get("url", "")
                print(f"[FREEPIK] Successfully generated AI image via REAL API!")
                print(f"[FREEPIK] Image URL: {image_url}")
                return image_url
            else:
                print(f"[FREEPIK] API returned {response.status_code}, using placeholder")
                return f"https://cdn.freepik.com/fallback.png"
                
        except Exception as e:
            print(f"[FREEPIK] API call failed: {e}")
            return f"https://cdn.freepik.com/error.png"
    
    def generate_timeline_graphic(self, timeline_events: list) -> str:
        # In production, use Freepik to generate timeline visualization
        return "https://cdn.freepik.com/timeline-graphic.png"
    
    def generate_postmortem_cover(self, incident_summary: Dict) -> str:
        # In production, use Freepik templates for professional reports
        return "https://cdn.freepik.com/postmortem-cover.png"
    
    def get_icon(self, icon_type: str) -> str:
        icons = {
            "alert": "🚨",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "info": "ℹ️",
            "time": "⏱️",
            "chart": "📊"
        }
        return icons.get(icon_type, "📄")

