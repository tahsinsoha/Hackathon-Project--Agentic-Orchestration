# agents/executor.py
"""Executor Agent: Applies mitigations with guardrails (context-driven, demo-friendly)."""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from .base import BaseAgent
from core.models import (
    Mitigation, MitigationType, ExperimentResult,
    IncidentType
)
from core.guardrails import GuardrailEngine
from integrations.retool import RetoolClient
from integrations.freepik import FreepikClient


class ExecutorAgent(BaseAgent):
    """Executor agent proposes and executes safe mitigations using context-driven values."""

    def __init__(self, guardrail_engine: GuardrailEngine):
        super().__init__("Executor")
        self.guardrails = guardrail_engine
        self.retool = RetoolClient()
        self.freepik = FreepikClient()

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Propose mitigation based on validated hypothesis + evidence + runbooks."""
        incident = context.get("incident")
        most_likely: ExperimentResult = context.get("most_likely_cause")
        hypotheses = context.get("hypotheses", [])

        # Pick hypothesis referenced by experiment result (fallback to first)
        hypothesis = None
        if most_likely and hypotheses and 0 <= most_likely.hypothesis_id < len(hypotheses):
            hypothesis = hypotheses[most_likely.hypothesis_id]
        elif hypotheses:
            hypothesis = hypotheses[0]

        root_cause = hypothesis.description if hypothesis else ""
        mitigation = self._propose_mitigation(
            incident_type=incident.incident_type,
            root_cause=root_cause,
            context=context,
        )

        # Guardrail checks may mutate requires_approval; they can also block
        guardrail_check = self.guardrails.check_mitigation(
            mitigation=mitigation,
            severity=incident.severity,
            service_name=incident.service_name,
        )

        if not guardrail_check.passed:
            return {
                "mitigation": None,
                "guardrail_check": guardrail_check,
                "status": "blocked",
                "reason": guardrail_check.reason,
            }

        # Approval request to Retool if required
        if mitigation.requires_approval:
            print(f"\n   🔔 Mitigation requires approval - Calling Retool API...")
            mitigation_dict = {
                "type": mitigation.type.value,
                "description": mitigation.description,
                "parameters": mitigation.parameters,
                "risk_level": mitigation.risk_level,
            }
            approval_sent = self.retool.send_approval_request(incident.id, mitigation_dict)
            if approval_sent:
                print(f"   ✅ Retool approval workflow triggered successfully!")

        # Visualization (demo)
        incident_data = {
            "id": incident.id,
            "service": incident.service_name,
            "severity": incident.severity.value,
            "type": incident.incident_type.value,
        }
        visual_url = self.freepik.generate_incident_card(incident_data)
        print(f"   🎨 Generated incident visualization: {visual_url}")

        return {
            "mitigation": mitigation,
            "guardrail_check": guardrail_check,
            "status": "proposed",
            "requires_approval": mitigation.requires_approval,
            "visual_url": visual_url,
        }

    # -----------------------------
    # Mitigation proposal (context-driven)
    # -----------------------------
    def _propose_mitigation(self, incident_type: IncidentType, root_cause: str, context: Dict[str, Any]) -> Mitigation:
        evidence = context.get("evidence")
        metrics = evidence.metrics if evidence else {}
        deploys = evidence.recent_deploys if evidence else []

        # Context: service state
        service_state = context.get("service_state", {}) or {}
        current_replicas = int(service_state.get("replicas", 3))
        env = (service_state.get("environment") or "demo").lower()

        # Context: runbooks (Scout already stores them in context)
        runbooks = context.get("runbooks", {}) or {}
        rb_text = self._flatten_runbooks(runbooks)

        # Determine "preferences" from runbook text (tie-breakers)
        prefer_rollback = "rollback" in rb_text or "roll back" in rb_text
        prefer_scale = ("scale" in rb_text) or ("replica" in rb_text) or ("autoscal" in rb_text)
        prefer_disable = ("feature flag" in rb_text) or ("disable" in rb_text) or ("degrade" in rb_text)

        # --- 1) Deployment regression -> rollback (use deploy history)
        if self._mentions_deploy(root_cause) or (prefer_rollback and deploys):
            current_v, prev_v = self._current_and_previous_versions(deploys)

            # If we can’t confidently identify previous version, fall back to conservative scale-up
            if prev_v:
                m = Mitigation(
                    type=MitigationType.ROLLBACK,
                    description=f"Rollback {context.get('incident').service_name} from {current_v} to {prev_v}",
                    parameters={
                        "current_version": current_v,
                        "target_version": prev_v,
                        "deploy_ref": deploys[0].get("commit") if deploys else None,
                    },
                    reversible=True,
                    estimated_impact="Return service to last known stable version (may briefly impact traffic).",
                    risk_level="medium",
                    requires_approval=False,  # guardrails will set True if policy says so
                )
                # Production can force approval (guardrails already checks prod/prod-like)
                if env in ("prod", "production"):
                    m.requires_approval = True
                return m

        # --- 2) Resource saturation -> scale up (computed target)
        if incident_type == IncidentType.RESOURCE_SATURATION or ("resource" in root_cause.lower()) or ("memory" in root_cause.lower()) or prefer_scale:
            target_replicas = self._compute_scale_target(metrics, current_replicas)
            m = Mitigation(
                type=MitigationType.SCALE_UP,
                description=f"Scale {context.get('incident').service_name} from {current_replicas} to {target_replicas} replicas to reduce saturation",
                parameters={
                    "current_replicas": current_replicas,
                    "target_replicas": target_replicas,
                    "scale_factor": round(target_replicas / max(current_replicas, 1), 2),
                    "signal": self._scale_signal(metrics),
                },
                reversible=True,
                estimated_impact="Adds capacity to distribute load and reduce latency/errors.",
                risk_level="low",
                requires_approval=False,
            )
            return m

        # --- 3) Dependency failure -> feature flag disable / degrade mode (context-driven flag)
        if ("dependency" in root_cause.lower()) or ("downstream" in root_cause.lower()) or prefer_disable:
            feature, fallback = self._choose_feature_flag(service_state, rb_text)

            return Mitigation(
                type=MitigationType.FEATURE_FLAG_DISABLE,
                description=f"Disable feature '{feature}' to reduce dependency pressure and use fallback '{fallback}'",
                parameters={
                    "feature": feature,
                    "fallback": fallback,
                    "previous_state": (service_state.get("feature_flags") or {}).get(feature, True),
                },
                reversible=True,
                estimated_impact="Reduces calls to failing dependency; may degrade non-critical functionality.",
                risk_level="low",
                requires_approval=False,
            )

        # --- 4) Elevated error rate -> restart service (treat as reversible in guardrails)
        if incident_type == IncidentType.ERROR_RATE:
            # Strategy derived from context (defaults are safe)
            strategy = service_state.get("restart_strategy", "rolling")
            max_unavailable = int(service_state.get("max_unavailable", 1))

            return Mitigation(
                type=MitigationType.RESTART_SERVICE,
                description="Rolling restart of service pods to clear transient connection issues",
                parameters={
                    "strategy": strategy,
                    "max_unavailable": max_unavailable,
                    "reason": "high_error_rate",
                },
                reversible=True,  # IMPORTANT: keep reversible so guardrails don't hard-block
                estimated_impact="Brief interruption per pod; may clear stuck connections/pools.",
                risk_level="medium",
                requires_approval=False,  # guardrails can set True
            )

        # --- 5) Default: conservative scale-up (computed)
        target_replicas = self._compute_scale_target(metrics, current_replicas, default_bump=1)
        return Mitigation(
            type=MitigationType.SCALE_UP,
            description=f"Conservative scale-up of {context.get('incident').service_name} from {current_replicas} to {target_replicas} replicas",
            parameters={
                "current_replicas": current_replicas,
                "target_replicas": target_replicas,
                "scale_factor": round(target_replicas / max(current_replicas, 1), 2),
                "signal": "conservative_default",
            },
            reversible=True,
            estimated_impact="Adds a small amount of capacity as a safe first step.",
            risk_level="low",
            requires_approval=False,
        )

    # -----------------------------
    # Apply mitigation (demo, but stateful + time-aware)
    # -----------------------------
    async def apply_mitigation(self, mitigation: Mitigation, service_name: str) -> Dict[str, Any]:
        """Execute the mitigation (simulated) and update context-like state if provided."""
        print(f"[EXECUTOR] Applying {mitigation.type.value} to {service_name}")
        print(f"[EXECUTOR] Parameters: {mitigation.parameters}")

        applied_at = datetime.now(timezone.utc).isoformat()

        # In a real system you'd call: K8s API / ArgoCD / LaunchDarkly / Service Mesh.
        # For demo we just succeed and return a structured result.
        return {
            "success": True,
            "mitigation_type": mitigation.type.value,
            "applied_at": applied_at,
            "message": f"Successfully applied {mitigation.type.value}",
        }

    # -----------------------------
    # Helpers
    # -----------------------------
    def _mentions_deploy(self, text: str) -> bool:
        t = (text or "").lower()
        return ("deploy" in t) or ("deployment" in t) or ("rollout" in t) or ("release" in t)

    def _current_and_previous_versions(self, deploys: list) -> Tuple[str, Optional[str]]:
        """Assumes deploys[0] is most recent (Scout sim) and deploys[1] is previous if present."""
        current_v = deploys[0].get("version", "unknown") if deploys else "unknown"
        prev_v = deploys[1].get("version") if len(deploys) > 1 else None
        return current_v, prev_v

    def _compute_scale_target(self, metrics: dict, current_replicas: int, default_bump: int = 2) -> int:
        """Compute target replicas from metrics, respecting guardrail max."""
        cpu = float(metrics.get("cpu_usage", 0) or 0)
        mem = float(metrics.get("memory_usage", 0) or 0)
        lat = float(metrics.get("latency_p99", 0) or 0)
        q = float(metrics.get("queue_depth", 0) or 0)
        err = float(metrics.get("error_rate", 0) or 0)

        bump = default_bump

        # Resource pressure
        if cpu > 90 or mem > 90:
            bump = max(bump, 3)
        elif cpu > 85 or mem > 85:
            bump = max(bump, 2)

        # Latency pressure
        if lat > 3000:
            bump = max(bump, 3)
        elif lat > 2000:
            bump = max(bump, 2)

        # Queue pressure
        if q > 2000:
            bump = max(bump, 3)
        elif q > 1000:
            bump = max(bump, 2)

        # Error pressure (mild bump)
        if err > 5:
            bump = max(bump, 2)

        target = current_replicas + bump

        # Respect guardrail max replicas if present
        max_repl = int(getattr(self.guardrails, "config", {}).get("max_scale_replicas", 10))
        target = min(target, max_repl)

        # Also respect max_scale_factor (if current is 0, avoid div by zero)
        max_factor = float(getattr(self.guardrails, "config", {}).get("max_scale_factor", 3))
        if current_replicas > 0:
            max_target_by_factor = int(current_replicas * max_factor)
            target = min(target, max_target_by_factor)

        return max(target, current_replicas + 1)  # always increase at least by 1

    def _scale_signal(self, metrics: dict) -> str:
        cpu = float(metrics.get("cpu_usage", 0) or 0)
        mem = float(metrics.get("memory_usage", 0) or 0)
        lat = float(metrics.get("latency_p99", 0) or 0)
        q = float(metrics.get("queue_depth", 0) or 0)

        if cpu > 85 or mem > 85:
            return "resource_saturation"
        if q > 1000:
            return "queue_pressure"
        if lat > 1500:
            return "latency_pressure"
        return "mixed_signals"

    def _choose_feature_flag(self, service_state: dict, rb_text: str) -> Tuple[str, str]:
        """
        Pick a feature flag to disable.
        Priority:
        1) If runbook mentions something like 'cache', disable cache integration
        2) Else pick first flag in service_state.feature_flags
        3) Else default names
        """
        flags = (service_state.get("feature_flags") or {})
        rb = rb_text or ""

        if "cache" in rb or "redis" in rb:
            return "cache-integration", "direct-db-access"

        if flags:
            first = next(iter(flags.keys()))
            return first, "safe-fallback"

        return "noncritical-feature", "safe-fallback"

    def _flatten_runbooks(self, runbooks: Dict[str, Any]) -> str:
        """Flatten runbook dict to lowercase text for simple keyword biasing."""
        parts = []
        for k, v in (runbooks or {}).items():
            if k in ("source", "full_content"):
                continue
            parts.append(str(v))
        return " ".join(parts).lower()
