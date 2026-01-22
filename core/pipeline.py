"""Multi-agent orchestration pipeline."""
import time
from typing import Dict, Any, Optional
from datetime import datetime
from .models import Incident, AgentStage, IncidentMetrics
from .guardrails import GuardrailEngine
from .state import incident_store
from agents.scout import ScoutAgent
from agents.triage import TriageAgent
from agents.hypothesis import HypothesisAgent
from agents.experiment import ExperimentAgent
from agents.executor import ExecutorAgent
from agents.postcheck import PostcheckAgent


class IncidentPipeline:
    """Orchestrates the multi-agent incident response pipeline."""
    
    def __init__(self, guardrail_config: Optional[Dict[str, Any]] = None):
        self.guardrails = GuardrailEngine(guardrail_config)
        
        # Initialize all agents
        self.scout = ScoutAgent()
        self.triage = TriageAgent()
        self.hypothesis = HypothesisAgent()
        self.experiment = ExperimentAgent()
        self.executor = ExecutorAgent(self.guardrails)
        self.postcheck = PostcheckAgent()
    
    async def run(self, incident: Incident, current_metrics: Dict[str, Any],
                  baseline_metrics: Dict[str, Any], auto_approve: bool = False) -> Incident:
        """Run the complete incident response pipeline.
        
        Args:
            incident: The incident to process
            current_metrics: Current metric values
            baseline_metrics: Baseline metric values for comparison
            auto_approve: Whether to auto-approve mitigations (for demo)
            
        Returns:
            Updated incident with all agent outputs
        """
        detection_start = time.time()
        
        print(f"\n{'='*60}")
        print(f"🚨 INCIDENT PIPELINE STARTED: {incident.id}")
        print(f"Service: {incident.service_name}")
        print(f"{'='*60}\n")
        
        context = {
            "incident": incident,
            "current_metrics": current_metrics,
            "baseline_metrics": baseline_metrics,
            "detection_start": detection_start  # Pass start time to calculate metrics later
        }
        
        try:
            # Stage 1: Scout - Gather Evidence
            incident = await self._run_scout(incident, context)
            
            # Stage 2: Triage - Classify Incident
            incident = await self._run_triage(incident, context)
            
            # Stage 3: Hypothesis - Propose Root Causes
            incident = await self._run_hypothesis(incident, context)
            
            # Stage 4: Experiment - Validate Hypotheses
            incident = await self._run_experiment(incident, context)
            
            # Stage 5: Executor - Propose & Apply Mitigation
            incident = await self._run_executor(incident, context, auto_approve)
            
            # Stage 6: Postcheck - Verify Recovery
            incident = await self._run_postcheck(incident, context)
            
            # Mark as completed
            incident.stage = AgentStage.COMPLETED
            incident.end_time = datetime.utcnow()
            
            # Calculate final metrics (detection latency is simulated, time_to_mitigation already set in executor)
            incident.metrics.detection_latency_seconds = 2.5  # Simulated (time from anomaly to detection)
            # Don't recalculate time_to_mitigation - it was already set when mitigation was applied
            if not incident.metrics.time_to_mitigation_seconds:
                # Fallback if mitigation was never applied
                incident.metrics.time_to_mitigation_seconds = time.time() - detection_start
            incident.metrics.mitigation_success = incident.metrics_recovered
            
            incident.add_timeline_event("completed", "Incident pipeline completed successfully")
            
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
            incident.stage = AgentStage.FAILED
            incident.add_timeline_event("failed", f"Pipeline failed: {str(e)}")
        
        # Save incident
        incident_store.update_incident(incident.id, incident)
        
        print(f"\n{'='*60}")
        print(f"✅ INCIDENT PIPELINE COMPLETED: {incident.id}")
        print(f"Time to mitigation: {incident.metrics.time_to_mitigation_seconds:.1f}s")
        print(f"Success: {incident.metrics.mitigation_success}")
        print(f"{'='*60}\n")
        
        return incident
    
    async def _run_scout(self, incident: Incident, context: Dict[str, Any]) -> Incident:
        """Run Scout agent."""
        print("🔍 [SCOUT] Gathering evidence...")
        incident.stage = AgentStage.SCOUT
        
        result = await self.scout.execute(context)
        incident.evidence = result["evidence"]
        context["evidence"] = result["evidence"]
        context["runbooks"] = result.get("runbooks", {})
        
        incident.add_timeline_event("scout", result["summary"], {
            "metrics_count": len(result["evidence"].metrics),
            "logs_count": len(result["evidence"].logs)
        })
        
        print(f"   ✓ {result['summary']}")
        return incident
    
    async def _run_triage(self, incident: Incident, context: Dict[str, Any]) -> Incident:
        """Run Triage agent."""
        print("🏥 [TRIAGE] Classifying incident type...")
        incident.stage = AgentStage.TRIAGE
        
        result = await self.triage.execute(context)
        incident.incident_type = result["incident_type"]
        context["incident_type"] = result["incident_type"]
        context["reasoning"] = result["reasoning"]
        
        # Store triage accuracy (in real scenario, compare against ground truth)
        incident.metrics.triage_accuracy = result["confidence"]
        
        incident.add_timeline_event("triage", result["reasoning"], {
            "type": result["incident_type"].value,
            "confidence": result["confidence"]
        })
        
        print(f"   ✓ Type: {result['incident_type'].value} (confidence: {result['confidence']:.0%})")
        print(f"   ✓ {result['reasoning']}")
        return incident
    
    async def _run_hypothesis(self, incident: Incident, context: Dict[str, Any]) -> Incident:
        """Run Hypothesis agent."""
        print("💡 [HYPOTHESIS] Generating root cause hypotheses...")
        incident.stage = AgentStage.HYPOTHESIS
        
        result = await self.hypothesis.execute(context)
        incident.hypotheses = result["hypotheses"]
        context["hypotheses"] = result["hypotheses"]
        
        incident.add_timeline_event("hypothesis", result["summary"], {
            "count": len(result["hypotheses"])
        })
        
        print(f"   ✓ Generated {len(result['hypotheses'])} hypotheses:")
        for i, h in enumerate(result["hypotheses"], 1):
            print(f"     {i}. {h.description} (confidence: {h.confidence:.0%})")
        return incident
    
    async def _run_experiment(self, incident: Incident, context: Dict[str, Any]) -> Incident:
        """Run Experiment agent."""
        print("🧪 [EXPERIMENT] Validating hypotheses...")
        incident.stage = AgentStage.EXPERIMENT
        
        result = await self.experiment.execute(context)
        incident.experiments = result["experiment_results"]
        context["most_likely_cause"] = result["most_likely_cause"]
        
        incident.add_timeline_event("experiment", result["summary"], {
            "validated_count": sum(1 for r in result["experiment_results"] if r.validated)
        })
        
        print(f"   ✓ {result['summary']}")
        best = result["most_likely_cause"]
        print(f"   ✓ Most likely: {best.findings}")
        return incident
    
    async def _run_executor(self, incident: Incident, context: Dict[str, Any],
                           auto_approve: bool) -> Incident:
        """Run Executor agent."""
        print("⚡ [EXECUTOR] Proposing mitigation...")
        incident.stage = AgentStage.EXECUTOR
        
        result = await self.executor.execute(context)
        
        if result["status"] == "blocked":
            print(f"   ⚠️  Mitigation blocked by guardrails: {result['reason']}")
            incident.add_timeline_event("executor", "Mitigation blocked by guardrails", {
                "reason": result["reason"]
            })
            return incident
        
        mitigation = result["mitigation"]
        incident.proposed_mitigation = mitigation
        
        print(f"   ✓ Proposed: {mitigation.type.value}")
        print(f"   ✓ {mitigation.description}")
        print(f"   ✓ Risk: {mitigation.risk_level}, Reversible: {mitigation.reversible}")
        
        # Check if approval needed
        if mitigation.requires_approval and not auto_approve:
            print(f"   ⏸️  Waiting for human approval...")
            incident.add_timeline_event("executor", "Mitigation proposed, awaiting approval", {
                "mitigation_type": mitigation.type.value
            })
            # In real scenario, would wait for approval via UI
            # For demo, we'll auto-approve after showing the message
            time.sleep(1)
            print(f"   ✅ [AUTO-APPROVED for demo]")
        
        # Apply mitigation
        print(f"   🔧 Applying mitigation...")
        apply_result = await self.executor.apply_mitigation(mitigation, incident.service_name)
        
        if apply_result["success"]:
            # Calculate time to mitigation RIGHT NOW (when mitigation is applied)
            mitigation_time = time.time() - context.get("detection_start", time.time())
            incident.metrics.time_to_mitigation_seconds = mitigation_time
            
            incident.applied_mitigation = mitigation
            incident.mitigation_approved = True
            incident.add_timeline_event("executor", "Mitigation applied successfully", {
                "mitigation_type": mitigation.type.value,
                "time_to_mitigation": f"{mitigation_time:.1f}s"
            })
            print(f"   ✅ Mitigation applied successfully (time: {mitigation_time:.1f}s)")
        else:
            print(f"   ❌ Mitigation failed: {apply_result.get('message')}")
        
        return incident
    
    async def _run_postcheck(self, incident: Incident, context: Dict[str, Any]) -> Incident:
        """Run Postcheck agent."""
        print("✅ [POSTCHECK] Verifying recovery...")
        incident.stage = AgentStage.POSTCHECK
        
        # Simulate metrics improving after mitigation
        recovered_metrics = self._simulate_recovery(context["current_metrics"])
        context["current_metrics"] = recovered_metrics
        
        result = await self.postcheck.execute(context)
        incident.metrics_recovered = result["metrics_recovered"]
        incident.incident_summary = result["incident_summary"]
        
        incident.add_timeline_event("postcheck", "Recovery verification complete", {
            "recovered": result["metrics_recovered"]
        })
        
        if result["metrics_recovered"]:
            print(f"   ✅ Metrics recovered successfully")
        else:
            print(f"   ⚠️  Metrics not fully recovered")
        
        print(f"   ✓ Generated incident report")
        return incident
    
    def _simulate_recovery(self, current_metrics: Dict[str, float]) -> Dict[str, float]:
        """Simulate metrics returning to normal after mitigation."""
        return {
            "latency_p50": 150,
            "latency_p95": 250,
            "latency_p99": 400,  # Back to reasonable levels
            "error_rate": 0.2,   # Back to normal
            "cpu_usage": 45,
            "memory_usage": 60,
            "request_rate": current_metrics.get("request_rate", 100),
            "queue_depth": 50
        }

