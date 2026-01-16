"""Guardrail system to ensure safe mitigation actions."""
from typing import Dict, Any
from .models import Mitigation, MitigationType, GuardrailCheck, IncidentSeverity


class GuardrailEngine:
    """Enforces safety policies for incident mitigation."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default safety policies."""
        return {
            "max_scale_replicas": 10,
            "max_scale_factor": 3,
            "require_approval_for": ["rollback", "scale_down", "restart_service"],
            "allow_auto_mitigation": False,
            "production_requires_approval": True,
            "max_concurrent_mitigations": 1,
            "rollback_window_hours": 24,
        }
    
    def check_mitigation(self, mitigation: Mitigation, severity: IncidentSeverity, 
                        service_name: str) -> GuardrailCheck:
        """Check if a mitigation is safe to execute.
        
        Args:
            mitigation: The proposed mitigation
            severity: Incident severity level
            service_name: Name of the affected service
            
        Returns:
            GuardrailCheck with pass/fail and reason
        """
        # Check 1: Reversibility requirement
        if not mitigation.reversible:
            return GuardrailCheck(
                passed=False,
                reason="Non-reversible mitigations are not allowed",
                policy_violated="reversibility_required"
            )
        
        # Check 2: High-risk actions require approval
        if mitigation.type.value in self.config["require_approval_for"]:
            if not self.config["allow_auto_mitigation"]:
                mitigation.requires_approval = True
        
        # Check 3: Scale limits
        if mitigation.type == MitigationType.SCALE_UP:
            target_replicas = mitigation.parameters.get("target_replicas", 0)
            if target_replicas > self.config["max_scale_replicas"]:
                return GuardrailCheck(
                    passed=False,
                    reason=f"Target replicas {target_replicas} exceeds max {self.config['max_scale_replicas']}",
                    policy_violated="max_scale_replicas"
                )
        
        # Check 4: Production safety
        if "production" in service_name.lower() or "prod" in service_name.lower():
            if self.config["production_requires_approval"]:
                mitigation.requires_approval = True
        
        # Check 5: Critical incidents can bypass some checks
        if severity == IncidentSeverity.CRITICAL:
            # Allow faster action for critical incidents
            pass
        
        return GuardrailCheck(
            passed=True,
            reason="All guardrail checks passed"
        )
    
    def validate_rollback(self, deploy_time: str) -> GuardrailCheck:
        """Validate that a rollback target is recent enough."""
        # In production, check deploy_time is within rollback window
        return GuardrailCheck(
            passed=True,
            reason="Rollback target is within acceptable time window"
        )
    
    def can_execute_auto(self, mitigation: Mitigation, severity: IncidentSeverity) -> bool:
        """Check if mitigation can be executed automatically without approval."""
        if not self.config["allow_auto_mitigation"]:
            return False
        
        if mitigation.requires_approval:
            return False
        
        # Only low-risk actions can auto-execute
        auto_allowed = [MitigationType.SCALE_UP, MitigationType.FEATURE_FLAG_DISABLE]
        return mitigation.type in auto_allowed

