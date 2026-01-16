"""Triage Agent: Classifies incident type."""
import json
from typing import Dict, Any
from .base import BaseAgent
from core.models import IncidentType, Evidence


class TriageAgent(BaseAgent):
    """Triage agent classifies incident type and determines severity."""
    
    def __init__(self):
        super().__init__("Triage")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Classify the incident type based on evidence."""
        evidence: Evidence = context.get("evidence")
        incident = context.get("incident")
        
        # Build context for LLM
        system_prompt = """You are an expert SRE triaging incidents. Classify the incident type based on the evidence.

Possible types:
- latency_spike: High p95/p99 latency
- error_rate_increase: Increased error percentage
- resource_saturation: CPU/memory exhaustion
- queue_depth_growth: Message queue backlog growing

Provide your classification and confidence level."""

        user_message = f"""Incident: {incident.service_name}

Metrics:
- Latency p95: {evidence.metrics.get('latency_p95')}ms
- Latency p99: {evidence.metrics.get('latency_p99')}ms  
- Error rate: {evidence.metrics.get('error_rate')}%
- CPU usage: {evidence.metrics.get('cpu_usage')}%
- Memory usage: {evidence.metrics.get('memory_usage')}%
- Queue depth: {evidence.metrics.get('queue_depth')}

Recent logs:
{chr(10).join(evidence.logs[:5])}

Recent deployments:
{json.dumps(evidence.recent_deploys, indent=2)}

Classify this incident."""

        # Get LLM classification (or use rule-based fallback)
        classification = await self._classify_incident(evidence)
        
        return {
            "incident_type": classification["type"],
            "confidence": classification["confidence"],
            "reasoning": classification["reasoning"]
        }
    
    async def _classify_incident(self, evidence: Evidence) -> Dict[str, Any]:
        """Classify incident using rules or LLM."""
        metrics = evidence.metrics
        
        # Rule-based classification for demo reliability
        if metrics.get("latency_p99", 0) > 1000:  # >1s
            return {
                "type": IncidentType.LATENCY_SPIKE,
                "confidence": 0.9,
                "reasoning": "P99 latency significantly elevated above baseline"
            }
        
        if metrics.get("error_rate", 0) > 5.0:  # >5%
            return {
                "type": IncidentType.ERROR_RATE,
                "confidence": 0.95,
                "reasoning": "Error rate exceeds acceptable threshold"
            }
        
        if metrics.get("cpu_usage", 0) > 85 or metrics.get("memory_usage", 0) > 85:
            return {
                "type": IncidentType.RESOURCE_SATURATION,
                "confidence": 0.85,
                "reasoning": "Resource utilization critically high"
            }
        
        if metrics.get("queue_depth", 0) > 1000:
            return {
                "type": IncidentType.QUEUE_DEPTH,
                "confidence": 0.8,
                "reasoning": "Message queue backlog growing rapidly"
            }
        
        return {
            "type": IncidentType.UNKNOWN,
            "confidence": 0.5,
            "reasoning": "No clear pattern detected in metrics"
        }

