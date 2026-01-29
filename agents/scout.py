"""Scout Agent: Gathers evidence about an incident."""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from .base import BaseAgent
from core.models import Evidence, IncidentType
from integrations.jina import DocumentFetcher, LogFetcher


class ScoutAgent(BaseAgent):
    """Scout agent pulls evidence: metrics, logs, traces, recent deploys."""

    def __init__(self):
        super().__init__("Scout")
        self.doc_fetcher = DocumentFetcher()  # GitHub-based runbooks
        self.log_fetcher = LogFetcher()       # GitHub-based logs

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all available evidence about the incident."""
        incident = context.get("incident")
        current_metrics = context.get("current_metrics", {}) or {}
        baseline_metrics = context.get("baseline_metrics", {}) or {}

        # Gather metrics evidence
        metrics_evidence = self._gather_metrics(current_metrics)

        # Determine incident type string for fetching logs/runbooks
        incident_type_str = self._resolve_incident_type_str(
            incident=incident,
            current=current_metrics,
            baseline=baseline_metrics,
        )
        context["scout_inferred_incident_type"] = incident_type_str  # helpful for debugging

        # Gather logs from GitHub
        logs = await self._gather_logs(incident.service_name, incident_type_str)

        # Check recent deployments (simulated)
        recent_deploys = await self._check_recent_deploys(incident.service_name)

        # Check dependencies (simulated)
        dependencies = self._check_dependencies(incident.service_name)

        # Fetch runbooks from GitHub
        runbooks = await self._fetch_runbooks(incident.service_name, incident_type_str)

        evidence = Evidence(
            metrics=metrics_evidence,
            logs=logs,
            recent_deploys=recent_deploys,
            traces=[],  # Would integrate with Jaeger/Zipkin in production
            dependencies=dependencies
        )

        # Add runbook info to context
        context["runbooks"] = runbooks

        return {
            "evidence": evidence,
            "runbooks": runbooks,
            "summary": (
                f"Collected {len(logs)} log entries, "
                f"found {len(recent_deploys)} recent deploys, "
                f"fetched runbooks for type='{incident_type_str}'"
            )
        }

    def _gather_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Process and structure metrics data."""
        return {
            "latency_p50": metrics.get("latency_p50", 0),
            "latency_p95": metrics.get("latency_p95", 0),
            "latency_p99": metrics.get("latency_p99", 0),
            "error_rate": metrics.get("error_rate", 0),
            "cpu_usage": metrics.get("cpu_usage", 0),
            "memory_usage": metrics.get("memory_usage", 0),
            "request_rate": metrics.get("request_rate", 0),
            "queue_depth": metrics.get("queue_depth", 0),
        }

    def _resolve_incident_type_str(
        self,
        incident: Any,
        current: Dict[str, Any],
        baseline: Dict[str, Any],
    ) -> str:
        # If incident already has a non-unknown type, use it
        if hasattr(incident, "incident_type") and incident.incident_type:
            try:
                if incident.incident_type != IncidentType.UNKNOWN:
                    return incident.incident_type.value
            except Exception:
                pass

        # Otherwise infer from metrics
        inferred = self._infer_incident_type(current, baseline)
        return inferred.value

    def _infer_incident_type(
        self,
        current: Dict[str, Any],
        baseline: Dict[str, Any],
    ) -> IncidentType:
        """
        Simple heuristic classifier (fast + deterministic):
        - latency_spike if p99 > max(1000ms, 2x baseline)
        - error_rate_increase if error_rate > max(5%, 2x baseline)
        - resource_saturation if cpu>85 or mem>85
        - queue_depth_growth if queue > max(1000, 2x baseline)
        """
        cur_p99 = float(current.get("latency_p99", 0) or 0)
        base_p99 = float(baseline.get("latency_p99", 0) or 0)

        cur_err = float(current.get("error_rate", 0) or 0)
        base_err = float(baseline.get("error_rate", 0) or 0)

        cur_cpu = float(current.get("cpu_usage", 0) or 0)
        cur_mem = float(current.get("memory_usage", 0) or 0)

        cur_q = float(current.get("queue_depth", 0) or 0)
        base_q = float(baseline.get("queue_depth", 0) or 0)

        # Latency spike
        latency_threshold = max(1000.0, (base_p99 * 2.0) if base_p99 > 0 else 1000.0)
        if cur_p99 >= latency_threshold:
            return IncidentType.LATENCY_SPIKE

        # Error rate increase
        err_threshold = max(5.0, (base_err * 2.0) if base_err > 0 else 5.0)
        if cur_err >= err_threshold:
            return IncidentType.ERROR_RATE

        # Resource saturation
        if cur_cpu >= 85.0 or cur_mem >= 85.0:
            return IncidentType.RESOURCE_SATURATION

        # Queue depth growth
        queue_threshold = max(1000.0, (base_q * 2.0) if base_q > 0 else 1000.0)
        if cur_q >= queue_threshold:
            return IncidentType.QUEUE_DEPTH

        return IncidentType.UNKNOWN

    async def _gather_logs(self, service_name: str, incident_type: Optional[str] = None) -> list:
        """Fetch logs for demo from GitHub."""
        incident_type = incident_type or "latency_spike"
        return self.log_fetcher.fetch_logs(service_name, incident_type)

    async def _check_recent_deploys(self, service_name: str) -> list:
        """Check for recent deployments (simulated)."""
        now = datetime.utcnow()
        return [
            {
                "service": service_name,
                "version": "v1.2.3",
                "deployed_at": (now - timedelta(minutes=15)).isoformat(),
                "deployed_by": "deploy-bot",
                "commit": "abc123f",
            }
        ]

    def _check_dependencies(self, service_name: str) -> list:
        """Check service dependencies (simulated)."""
        dependencies_map = {
            "api-service": ["database", "redis-cache", "auth-service"],
            "database": [],
            "redis-cache": [],
            "auth-service": ["database"],
        }
        return dependencies_map.get(service_name, [])

    async def _fetch_runbooks(self, service_name: str, incident_type: str = "latency_spike") -> Dict[str, str]:
        """Fetch runbooks from GitHub for demo."""
        try:
            runbooks = self.doc_fetcher.fetch_runbook(service_name, incident_type)
            if runbooks.get("source") != "Default Demo Runbooks":
                print(f"Fetched runbooks from {runbooks.get('source')}")
            else:
                print(f"Using default runbooks")
            return runbooks
        except Exception as e:
            print(f"Runbook fetch failed: {e}, using defaults")
            return self.doc_fetcher._get_default_runbooks()
