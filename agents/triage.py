"""Triage Agent: Classifies incident type."""
import json
import os
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
        """Classify incident using Anthropic Claude or fallback to rules."""
        
        # Try Anthropic Claude first if API key is available
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            try:
                return await self._classify_with_anthropic(evidence, anthropic_key)
            except Exception as e:
                print(f"[TRIAGE] Anthropic API failed, using rule-based fallback: {e}")
        
        # Fallback to rule-based classification
        return self._classify_with_rules(evidence)
    
    async def _classify_with_anthropic(self, evidence: Evidence, api_key: str) -> Dict[str, Any]:
        """Use Anthropic Claude for classification."""
        from anthropic import Anthropic
        
        client = Anthropic(api_key=api_key)
        metrics = evidence.metrics
        
        prompt = f"""You are an expert SRE triaging a production incident. Classify the incident type.

Metrics:
- Latency p99: {metrics.get('latency_p99')}ms
- Error rate: {metrics.get('error_rate')}%
- CPU usage: {metrics.get('cpu_usage')}%
- Memory usage: {metrics.get('memory_usage')}%
- Queue depth: {metrics.get('queue_depth')}

Recent logs:
{chr(10).join(evidence.logs[:3])}

Classify as ONE of:
- latency_spike: High p95/p99 latency
- error_rate_increase: Increased error percentage  
- resource_saturation: CPU/memory exhaustion
- queue_depth_growth: Message queue backlog

Respond in JSON format:
{{"type": "latency_spike", "confidence": 0.9, "reasoning": "explanation"}}"""

        message = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse Claude's response
        response_text = message.content[0].text
        import json
        result = json.loads(response_text)
        
        # Map type string to enum
        type_map = {
            "latency_spike": IncidentType.LATENCY_SPIKE,
            "error_rate_increase": IncidentType.ERROR_RATE,
            "resource_saturation": IncidentType.RESOURCE_SATURATION,
            "queue_depth_growth": IncidentType.QUEUE_DEPTH
        }
        
        return {
            "type": type_map.get(result["type"], IncidentType.UNKNOWN),
            "confidence": result["confidence"],
            "reasoning": result["reasoning"]
        }
    
    def _classify_with_rules(self, evidence: Evidence) -> Dict[str, Any]:
        """Rule-based classification fallback."""
        metrics = evidence.metrics
        
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

