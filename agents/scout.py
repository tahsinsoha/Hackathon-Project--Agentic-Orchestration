"""Scout Agent: Gathers evidence about an incident."""
import json
from typing import Dict, Any
from datetime import datetime, timedelta
from .base import BaseAgent
from core.models import Evidence


class ScoutAgent(BaseAgent):
    """Scout agent pulls evidence: metrics, logs, traces, recent deploys."""
    
    def __init__(self):
        super().__init__("Scout")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all available evidence about the incident."""
        incident = context.get("incident")
        metrics = context.get("current_metrics", {})
        
        # Gather metrics evidence
        metrics_evidence = self._gather_metrics(metrics)
        
        # Gather logs (simulated)
        logs = await self._gather_logs(incident.service_name)
        
        # Check recent deployments
        recent_deploys = await self._check_recent_deploys(incident.service_name)
        
        # Check dependencies
        dependencies = self._check_dependencies(incident.service_name)
        
        # Use TinyFish/Yutori to pull runbooks if available
        runbooks = await self._fetch_runbooks(incident.service_name)
        
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
            "summary": f"Collected {len(logs)} log entries, found {len(recent_deploys)} recent deploys"
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
    
    async def _gather_logs(self, service_name: str) -> list:
        """Gather relevant log entries (simulated)."""
        # In production, query ElasticSearch, Loki, or CloudWatch
        return [
            f"[ERROR] {service_name}: Connection timeout to database",
            f"[WARN] {service_name}: High memory usage detected (85%)",
            f"[INFO] {service_name}: Request processing took 4.5s",
            f"[ERROR] {service_name}: Failed to connect to redis-cache: connection refused",
        ]
    
    async def _check_recent_deploys(self, service_name: str) -> list:
        """Check for recent deployments (simulated)."""
        # In production, query CI/CD system (GitHub Actions, ArgoCD, etc.)
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
        # In production, query service mesh or service registry
        dependencies_map = {
            "api-service": ["database", "redis-cache", "auth-service"],
            "database": [],
            "redis-cache": [],
            "auth-service": ["database"]
        }
        return dependencies_map.get(service_name, [])
    
    async def _fetch_runbooks(self, service_name: str) -> Dict[str, str]:
        """Fetch runbooks using TinyFish/Yutori web agent."""
        # In production, integrate with TinyFish API to scrape internal wiki
        # or external documentation
        return {
            "high_latency": "Check database connection pool, review recent queries, check for long-running transactions",
            "high_error_rate": "Check dependency health, review recent deployments, check for configuration changes",
            "resource_saturation": "Check for memory leaks, review container limits, check for resource-intensive operations"
        }

