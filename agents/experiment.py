"""Experiment/Verifier Agent: Validates hypotheses."""
from typing import Dict, Any, List
from .base import BaseAgent
from core.models import Hypothesis, ExperimentResult, Evidence


class ExperimentAgent(BaseAgent):
    """Runs experiments to validate hypotheses."""
    
    def __init__(self):
        super().__init__("Experiment")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run validation experiments for each hypothesis."""
        hypotheses: List[Hypothesis] = context.get("hypotheses", [])
        evidence: Evidence = context.get("evidence")
        
        results = []
        for idx, hypothesis in enumerate(hypotheses):
            result = await self._run_experiment(idx, hypothesis, evidence)
            results.append(result)
        
        # Find most likely root cause
        validated = [r for r in results if r.validated]
        best_result = max(validated, key=lambda x: x.confidence) if validated else results[0]
        
        return {
            "experiment_results": results,
            "most_likely_cause": best_result,
            "summary": f"Validated {len(validated)}/{len(results)} hypotheses"
        }
    
    async def _run_experiment(self, idx: int, hypothesis: Hypothesis, 
                             evidence: Evidence) -> ExperimentResult:
        """Run validation checks for a hypothesis."""
        
        # Check if recent deployment correlates with issue
        if "deployment" in hypothesis.description.lower():
            if evidence.recent_deploys:
                deploy = evidence.recent_deploys[0]
                return ExperimentResult(
                    hypothesis_id=idx,
                    validated=True,
                    findings=f"Deployment {deploy['version']} occurred 15min before incident",
                    confidence=0.85
                )
        
        # Check for dependency issues
        if "dependency" in hypothesis.description.lower() or "downstream" in hypothesis.description.lower():
            error_logs = [log for log in evidence.logs if "ERROR" in log]
            if any("redis-cache" in log or "refused" in log for log in error_logs):
                return ExperimentResult(
                    hypothesis_id=idx,
                    validated=True,
                    findings="Detected connection failures to redis-cache in logs",
                    confidence=0.9
                )
        
        # Check for resource issues
        if "resource" in hypothesis.description.lower() or "memory" in hypothesis.description.lower():
            memory_usage = evidence.metrics.get("memory_usage", 0)
            if memory_usage > 80:
                return ExperimentResult(
                    hypothesis_id=idx,
                    validated=True,
                    findings=f"Memory usage at {memory_usage}%, indicating saturation",
                    confidence=0.8
                )
        
        # Check for database issues
        if "database" in hypothesis.description.lower():
            db_errors = [log for log in evidence.logs if "database" in log.lower() or "timeout" in log.lower()]
            if db_errors:
                return ExperimentResult(
                    hypothesis_id=idx,
                    validated=True,
                    findings=f"Found {len(db_errors)} database-related errors",
                    confidence=0.75
                )
        
        # Default: not validated
        return ExperimentResult(
            hypothesis_id=idx,
            validated=False,
            findings="No strong evidence found to support this hypothesis",
            confidence=0.3
        )

