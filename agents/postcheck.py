from typing import Dict, Any
from datetime import datetime
from .base import BaseAgent
from core.models import Incident, AgentStage


class PostcheckAgent(BaseAgent):
    """Verifies that mitigation worked and generates incident summary."""
    
    def __init__(self):
        super().__init__("Postcheck")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Verify metrics recovered and generate incident report."""
        incident: Incident = context.get("incident")
        baseline_metrics = context.get("baseline_metrics", {})
        current_metrics = context.get("current_metrics", {})
        
        # Check if metrics have recovered
        recovery_status = self._check_recovery(baseline_metrics, current_metrics)
        
        # Generate incident summary
        summary = self._generate_summary(incident, recovery_status, context)
        
        # Calculate final metrics
        if incident.end_time:
            time_to_mitigation = (incident.end_time - incident.start_time).total_seconds()
        else:
            incident.end_time = datetime.utcnow()
            time_to_mitigation = (incident.end_time - incident.start_time).total_seconds()
        
        return {
            "metrics_recovered": recovery_status["recovered"],
            "recovery_details": recovery_status,
            "incident_summary": summary,
            "time_to_mitigation": time_to_mitigation,
            "success": recovery_status["recovered"]
        }
    
    def _check_recovery(self, baseline: Dict[str, float], 
                       current: Dict[str, float]) -> Dict[str, Any]:
        """Check if metrics have returned to acceptable levels."""
        
        checks = {}
        recovered = True
        
        # Check latency
        if "latency_p99" in current:
            baseline_p99 = baseline.get("latency_p99", 200)
            current_p99 = current.get("latency_p99", 0)
            latency_ok = current_p99 <= baseline_p99 * 1.2  # Within 20% of baseline
            checks["latency"] = {
                "recovered": latency_ok,
                "baseline": baseline_p99,
                "current": current_p99
            }
            recovered = recovered and latency_ok
        
        # Check error rate
        if "error_rate" in current:
            baseline_errors = baseline.get("error_rate", 0.1)
            current_errors = current.get("error_rate", 0)
            errors_ok = current_errors <= baseline_errors * 2  # Within 2x baseline
            checks["error_rate"] = {
                "recovered": errors_ok,
                "baseline": baseline_errors,
                "current": current_errors
            }
            recovered = recovered and errors_ok
        
        # Check resource usage
        if "cpu_usage" in current:
            current_cpu = current.get("cpu_usage", 0)
            cpu_ok = current_cpu < 80
            checks["cpu"] = {
                "recovered": cpu_ok,
                "current": current_cpu
            }
            recovered = recovered and cpu_ok
        
        if "memory_usage" in current:
            current_memory = current.get("memory_usage", 0)
            memory_ok = current_memory < 80
            checks["memory"] = {
                "recovered": memory_ok,
                "current": current_memory
            }
            recovered = recovered and memory_ok
        
        return {
            "recovered": recovered,
            "checks": checks
        }
    
    def _generate_summary(self, incident: Incident, recovery_status: Dict[str, Any],
                         context: Dict[str, Any]) -> str:
        """Generate a human-readable incident summary."""
        
        lines = [
            f"# Incident Report: {incident.id}",
            f"",
            f"**Service**: {incident.service_name}",
            f"**Type**: {incident.incident_type.value}",
            f"**Severity**: {incident.severity.value}",
            f"**Start Time**: {incident.start_time.isoformat()}",
            f"**End Time**: {incident.end_time.isoformat() if incident.end_time else 'ongoing'}",
            f"**Duration**: {(incident.end_time - incident.start_time).total_seconds():.0f}s" if incident.end_time else "ongoing",
            f"",
            f"## Timeline",
        ]
        
        for event in incident.timeline:
            lines.append(f"- **{event['stage']}**: {event['message']}")
        
        # Get root cause findings
        most_likely = context.get('most_likely_cause')
        root_cause_text = most_likely.findings if most_likely and hasattr(most_likely, 'findings') else 'Unknown'
        
        lines.extend([
            f"",
            f"## Root Cause",
            f"{root_cause_text}",
            f"",
            f"## Mitigation Applied",
            f"{incident.applied_mitigation.description if incident.applied_mitigation else 'None'}",
            f"",
            f"## Recovery Status",
            f"{' Metrics recovered' if recovery_status['recovered'] else 'Metrics not fully recovered'}",
            f"",
            f"## Metrics",
        ])
        
        for check_name, check_data in recovery_status.get("checks", {}).items():
            status = "Recovered" if check_data.get("recovered") else "Not Recovered"
            lines.append(f"- {status} {check_name}: {check_data}")
        
        lines.extend([
            f"",
            f"## Recommendations",
            f"- Review deployment process to catch issues in canary phase",
            f"- Add more comprehensive monitoring for early detection",
            f"- Update runbooks based on this incident",
        ])
        return "\n".join(lines)

