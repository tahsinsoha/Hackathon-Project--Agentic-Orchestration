"""Hypothesis Agent: Proposes root cause hypotheses."""
from typing import Dict, Any, List
from .base import BaseAgent
from core.models import Hypothesis, IncidentType, Evidence


class HypothesisAgent(BaseAgent):
    """Generates 2-3 plausible root cause hypotheses."""
    
    def __init__(self):
        super().__init__("Hypothesis")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate root cause hypotheses based on incident type and evidence."""
        incident_type = context.get("incident_type")
        evidence: Evidence = context.get("evidence")
        
        # Generate hypotheses based on incident type
        hypotheses = self._generate_hypotheses(incident_type, evidence)
        
        return {
            "hypotheses": hypotheses,
            "summary": f"Generated {len(hypotheses)} hypotheses for investigation"
        }
    
    def _generate_hypotheses(self, incident_type: IncidentType, 
                            evidence: Evidence) -> List[Hypothesis]:
        """Generate hypotheses based on incident type."""
        
        if incident_type == IncidentType.LATENCY_SPIKE:
            return [
                Hypothesis(
                    description="Recent deployment introduced slow database queries",
                    confidence=0.8,
                    evidence_needed=["query execution times", "deployment correlation"],
                    validation_criteria="Compare query performance pre/post deploy"
                ),
                Hypothesis(
                    description="Database connection pool exhaustion",
                    confidence=0.6,
                    evidence_needed=["connection pool metrics", "active connections"],
                    validation_criteria="Check connection pool utilization and wait times"
                ),
                Hypothesis(
                    description="Downstream service degradation",
                    confidence=0.5,
                    evidence_needed=["dependency health checks", "cascade timing"],
                    validation_criteria="Check health and latency of dependent services"
                )
            ]
        
        elif incident_type == IncidentType.ERROR_RATE:
            return [
                Hypothesis(
                    description="Downstream dependency failure",
                    confidence=0.85,
                    evidence_needed=["dependency error logs", "network connectivity"],
                    validation_criteria="Check health of redis-cache and auth-service"
                ),
                Hypothesis(
                    description="Configuration error in recent deployment",
                    confidence=0.7,
                    evidence_needed=["config diff", "deployment timing"],
                    validation_criteria="Compare configuration before/after deployment"
                ),
                Hypothesis(
                    description="Database connection failures",
                    confidence=0.6,
                    evidence_needed=["database logs", "connection metrics"],
                    validation_criteria="Check database connectivity and error logs"
                )
            ]
        
        elif incident_type == IncidentType.RESOURCE_SATURATION:
            return [
                Hypothesis(
                    description="Memory leak in recent code changes",
                    confidence=0.75,
                    evidence_needed=["heap dumps", "memory growth pattern"],
                    validation_criteria="Profile memory usage over time, check for growing allocations"
                ),
                Hypothesis(
                    description="Insufficient resource limits for load",
                    confidence=0.65,
                    evidence_needed=["traffic patterns", "resource history"],
                    validation_criteria="Compare current load to historical capacity"
                ),
                Hypothesis(
                    description="Resource-intensive operation without backpressure",
                    confidence=0.55,
                    evidence_needed=["CPU profiling", "request patterns"],
                    validation_criteria="Identify CPU-intensive code paths in traces"
                )
            ]
        
        elif incident_type == IncidentType.QUEUE_DEPTH:
            return [
                Hypothesis(
                    description="Consumer service down or degraded",
                    confidence=0.8,
                    evidence_needed=["consumer health", "processing rate"],
                    validation_criteria="Check consumer service status and throughput"
                ),
                Hypothesis(
                    description="Sudden spike in message production",
                    confidence=0.6,
                    evidence_needed=["producer metrics", "message rates"],
                    validation_criteria="Compare message production rate to baseline"
                ),
                Hypothesis(
                    description="Processing slowdown due to payload changes",
                    confidence=0.5,
                    evidence_needed=["message processing time", "payload samples"],
                    validation_criteria="Analyze recent messages for complexity changes"
                )
            ]
        
        else:
            return [
                Hypothesis(
                    description="Unknown root cause - requires manual investigation",
                    confidence=0.3,
                    evidence_needed=["full system review"],
                    validation_criteria="Manual investigation by on-call engineer"
                )
            ]

