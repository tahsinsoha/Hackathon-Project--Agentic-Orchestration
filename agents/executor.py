"""Executor Agent: Applies mitigations with guardrails."""
from typing import Dict, Any
from .base import BaseAgent
from core.models import (
    Mitigation, MitigationType, ExperimentResult, 
    IncidentType, IncidentSeverity
)
from core.guardrails import GuardrailEngine


class ExecutorAgent(BaseAgent):
    """Executor agent proposes and executes safe mitigations."""
    
    def __init__(self, guardrail_engine: GuardrailEngine):
        super().__init__("Executor")
        self.guardrails = guardrail_engine
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Propose mitigation based on validated hypothesis."""
        incident = context.get("incident")
        most_likely_cause: ExperimentResult = context.get("most_likely_cause")
        hypotheses = context.get("hypotheses", [])
        
        # Get the validated hypothesis
        if most_likely_cause and most_likely_cause.hypothesis_id < len(hypotheses):
            hypothesis = hypotheses[most_likely_cause.hypothesis_id]
        else:
            hypothesis = hypotheses[0] if hypotheses else None
        
        # Propose mitigation based on root cause
        mitigation = self._propose_mitigation(
            incident.incident_type,
            hypothesis.description if hypothesis else "",
            context
        )
        
        # Check guardrails
        guardrail_check = self.guardrails.check_mitigation(
            mitigation,
            incident.severity,
            incident.service_name
        )
        
        if not guardrail_check.passed:
            return {
                "mitigation": None,
                "guardrail_check": guardrail_check,
                "status": "blocked",
                "reason": guardrail_check.reason
            }
        
        return {
            "mitigation": mitigation,
            "guardrail_check": guardrail_check,
            "status": "proposed",
            "requires_approval": mitigation.requires_approval
        }
    
    def _propose_mitigation(self, incident_type: IncidentType, 
                           root_cause: str, context: Dict[str, Any]) -> Mitigation:
        """Propose appropriate mitigation based on incident type and root cause."""
        
        # Recent deployment issues -> rollback
        if "deployment" in root_cause.lower() or "deploy" in root_cause.lower():
            evidence = context.get("evidence")
            recent_deploy = evidence.recent_deploys[0] if evidence and evidence.recent_deploys else {}
            
            return Mitigation(
                type=MitigationType.ROLLBACK,
                description=f"Rollback to previous version before deployment {recent_deploy.get('version', 'unknown')}",
                parameters={
                    "target_version": "v1.2.2",  # previous version
                    "current_version": recent_deploy.get('version', 'v1.2.3')
                },
                reversible=True,
                estimated_impact="Service will return to previous stable state",
                risk_level="medium",
                requires_approval=True
            )
        
        # Resource saturation -> scale up
        if incident_type == IncidentType.RESOURCE_SATURATION:
            return Mitigation(
                type=MitigationType.SCALE_UP,
                description="Scale up replicas to handle increased load",
                parameters={
                    "current_replicas": 3,
                    "target_replicas": 5,
                    "scale_factor": 1.67
                },
                reversible=True,
                estimated_impact="Will add 2 more replicas to distribute load",
                risk_level="low",
                requires_approval=False
            )
        
        # Dependency failure -> disable feature or shed traffic
        if "dependency" in root_cause.lower() or "downstream" in root_cause.lower():
            return Mitigation(
                type=MitigationType.FEATURE_FLAG_DISABLE,
                description="Disable non-critical feature that depends on failed service",
                parameters={
                    "feature": "cache-integration",
                    "fallback": "direct-db-access"
                },
                reversible=True,
                estimated_impact="Will use slower fallback path, but reduce errors",
                risk_level="low",
                requires_approval=False
            )
        
        # High error rate -> restart if quick fix needed
        if incident_type == IncidentType.ERROR_RATE:
            return Mitigation(
                type=MitigationType.RESTART_SERVICE,
                description="Rolling restart of service pods to clear connection issues",
                parameters={
                    "strategy": "rolling",
                    "max_unavailable": 1
                },
                reversible=False,  # Can't "undo" a restart
                estimated_impact="Brief interruption per pod, should clear connection pools",
                risk_level="medium",
                requires_approval=True
            )
        
        # Default: scale up as conservative mitigation
        return Mitigation(
            type=MitigationType.SCALE_UP,
            description="Conservative scale-up to add capacity",
            parameters={
                "current_replicas": 3,
                "target_replicas": 4
            },
            reversible=True,
            estimated_impact="Add one replica for additional capacity",
            risk_level="low",
            requires_approval=False
        )
    
    async def apply_mitigation(self, mitigation: Mitigation, 
                              service_name: str) -> Dict[str, Any]:
        """Actually execute the mitigation (simulated for demo)."""
        
        # In production, integrate with:
        # - Kubernetes API for scaling/rolling restarts
        # - ArgoCD/FluxCD for rollbacks
        # - LaunchDarkly for feature flags
        # - Service mesh for traffic management
        
        print(f"[EXECUTOR] Applying {mitigation.type.value} to {service_name}")
        print(f"[EXECUTOR] Parameters: {mitigation.parameters}")
        
        # Simulate execution
        return {
            "success": True,
            "mitigation_type": mitigation.type.value,
            "applied_at": "2026-01-16T12:34:56Z",
            "message": f"Successfully applied {mitigation.type.value}"
        }

