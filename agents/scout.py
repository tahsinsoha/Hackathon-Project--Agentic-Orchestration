"""Scout Agent: Gathers evidence about an incident."""
import json
from typing import Dict, Any
from datetime import datetime, timedelta
from .base import BaseAgent
from core.models import Evidence
from integrations.jina import DocumentFetcher, LogFetcher


class ScoutAgent(BaseAgent):
    """Scout agent pulls evidence: metrics, logs, traces, recent deploys."""

    def __init__(self):
        super().__init__("Scout")
        self.doc_fetcher = DocumentFetcher()  # GitHub-based runbooks
        self.log_fetcher = LogFetcher()      # GitHub-based logs

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all available evidence about the incident."""
        incident = context.get("incident")
        metrics = context.get("current_metrics", {})

        # Gather metrics evidence
        metrics_evidence = self._gather_metrics(metrics)

        # Determine incident type string
        incident_type_str = incident.incident_type.value if hasattr(incident, 'incident_type') else "latency_spike"

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
            "summary": f"Collected {len(logs)} log entries, found {len(recent_deploys)} recent deploys, fetched runbooks"
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

    async def _gather_logs(self, service_name: str, incident_type: str = None) -> list:
        """Fetch logs for demo from GitHub."""
        incident_type = incident_type or "latency_spike"
        logs = self.log_fetcher.fetch_logs(service_name, incident_type)
        return logs

    async def _check_recent_deploys(self, service_name: str) -> list:
        """Check for recent deployments (simulated)."""
        now = datetime.utcnow()
        return [
            {
                "service": service_name,
                "version": "v1.2.3",
                "deployed_at": (now - timedelta(minutes=15)).isoformat(),
                "deployed_by": "deploy-bot",
                "commit": "abc123f"
            }
        ]

    def _check_dependencies(self, service_name: str) -> list:
        """Check service dependencies (simulated)."""
        dependencies_map = {
            "api-service": ["database", "redis-cache", "auth-service"],
            "database": [],
            "redis-cache": [],
            "auth-service": ["database"]
        }
        return dependencies_map.get(service_name, [])

    async def _fetch_runbooks(self, service_name: str, incident_type: str = "latency_spike") -> Dict[str, str]:
        """Fetch runbooks from GitHub for demo."""
        try:
            runbooks = self.doc_fetcher.fetch_runbook(service_name, incident_type)
            if runbooks.get("source") != "Default Demo Runbooks":
                print(f"   📚 Fetched runbooks from {runbooks.get('source')}")
            else:
                print(f"   ℹ️  Using default runbooks")
            return runbooks
        except Exception as e:
            print(f"   ⚠️  Runbook fetch failed: {e}, using defaults")
            return self.doc_fetcher._get_default_runbooks()
