"""Freepik integration for visual generation.

Freepik provides visual assets for:
- Incident card graphics
- Timeline visualizations
- Postmortem reports
- Dashboard icons and illustrations
"""
import os
from typing import Dict, Optional


class FreepikClient:
    """Client for Freepik API integration."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("FREEPIK_API_KEY", "")
        self.base_url = "https://api.freepik.com/v1"
    
    def generate_incident_card(self, incident_data: Dict) -> str:
        """Generate a visual incident card with timeline.
        
        Args:
            incident_data: Incident details for visualization
            
        Returns:
            URL or path to generated image
        """
        # In production, use Freepik API to generate custom graphics
        # For demo, return placeholder
        
        incident_id = incident_data.get("id", "unknown")
        return f"https://cdn.freepik.com/incident-cards/{incident_id}.png"
    
    def generate_timeline_graphic(self, timeline_events: list) -> str:
        """Generate a visual timeline of incident progression.
        
        Args:
            timeline_events: List of timeline events
            
        Returns:
            URL or path to generated timeline graphic
        """
        # In production, use Freepik to generate timeline visualization
        return "https://cdn.freepik.com/timeline-graphic.png"
    
    def generate_postmortem_cover(self, incident_summary: Dict) -> str:
        """Generate a cover page for incident postmortem.
        
        Args:
            incident_summary: Summary data for the incident
            
        Returns:
            URL or path to generated cover page
        """
        # In production, use Freepik templates for professional reports
        return "https://cdn.freepik.com/postmortem-cover.png"
    
    def get_icon(self, icon_type: str) -> str:
        """Get an icon URL for dashboard/UI elements.
        
        Args:
            icon_type: Type of icon needed (alert, success, warning, etc.)
            
        Returns:
            URL to icon asset
        """
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

