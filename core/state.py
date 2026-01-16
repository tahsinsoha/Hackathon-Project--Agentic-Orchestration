"""State management for incidents."""
import json
from typing import Dict, Optional, List
from datetime import datetime
from .models import Incident, AgentStage


class IncidentStore:
    """In-memory store for incidents (in production, use Redis/PostgreSQL)."""
    
    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        self.metrics_history: List[Dict] = []
    
    def create_incident(self, incident: Incident) -> str:
        """Create a new incident and return its ID."""
        self.incidents[incident.id] = incident
        return incident.id
    
    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get an incident by ID."""
        return self.incidents.get(incident_id)
    
    def update_incident(self, incident_id: str, incident: Incident):
        """Update an existing incident."""
        self.incidents[incident_id] = incident
    
    def list_incidents(self, limit: int = 100) -> List[Incident]:
        """List recent incidents."""
        incidents = list(self.incidents.values())
        incidents.sort(key=lambda x: x.start_time, reverse=True)
        return incidents[:limit]
    
    def get_active_incidents(self) -> List[Incident]:
        """Get all active (non-completed) incidents."""
        return [
            inc for inc in self.incidents.values()
            if inc.stage not in [AgentStage.COMPLETED, AgentStage.FAILED]
        ]
    
    def get_statistics(self) -> Dict:
        """Get overall statistics."""
        incidents = list(self.incidents.values())
        completed = [i for i in incidents if i.stage == AgentStage.COMPLETED]
        
        if not completed:
            return {
                "total_incidents": len(incidents),
                "completed": 0,
                "avg_detection_latency": 0,
                "avg_time_to_mitigation": 0,
                "success_rate": 0,
                "triage_accuracy": 0,
            }
        
        return {
            "total_incidents": len(incidents),
            "completed": len(completed),
            "active": len(self.get_active_incidents()),
            "avg_detection_latency": sum(i.metrics.detection_latency_seconds for i in completed) / len(completed),
            "avg_time_to_mitigation": sum(i.metrics.time_to_mitigation_seconds for i in completed) / len(completed),
            "success_rate": sum(1 for i in completed if i.metrics.mitigation_success) / len(completed) * 100,
            "triage_accuracy": sum(i.metrics.triage_accuracy for i in completed) / len(completed) * 100,
        }
    
    def record_metrics(self, incident_id: str, metrics: Dict):
        """Record time-series metrics for an incident."""
        self.metrics_history.append({
            "incident_id": incident_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics
        })


# Global store instance
incident_store = IncidentStore()

