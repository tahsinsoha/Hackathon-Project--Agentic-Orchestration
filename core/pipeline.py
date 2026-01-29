import time
from typing import Dict, Any, Optional
from datetime import datetime

from .models import Incident, AgentStage
from .guardrails import GuardrailEngine
from .state import incident_store

from agents.scout import ScoutAgent
from agents.triage import TriageAgent
from agents.hypothesis import HypothesisAgent
from agents.experiment import ExperimentAgent
from agents.executor import ExecutorAgent
from agents.postcheck import PostcheckAgent


class IncidentPipeline:

    def __init__(self, guardrail_config: Optional[Dict[str, Any]] = None):
        self.guardrails = GuardrailEngine(guardrail_config)

        # Initialize all agents
        self.scout = ScoutAgent()
        self.triage = TriageAgent()
        self.hypothesis = HypothesisAgent()
        self.experiment = ExperimentAgent()
        self.executor = ExecutorAgent(self.guardrails)
        self.postcheck = PostcheckAgent()

    async def run(
        self,
        incident: Incident,
        current_metrics: Dict[str, Any],
        baseline_metrics: Dict[str, Any],
        auto_approve: bool = False
    ) -> Incident:
        detection_start = time.time()

        print(f"\n{'='*60}")
        print(f"INCIDENT PIPELINE STARTED: {incident.id}")
        print(f"Service: {incident.service_name}")
        print(f"{'='*60}\n")

        # Always persist initial state quickly
        incident_store.update_incident(incident.id, incident)

        context = {
            "incident": incident,
            "current_metrics": current_metrics,
            "baseline_metrics": baseline_metrics,
            "detection_start": detection_start,  # used for time_to_mitigation calc
        }

        try:
            # Stage 1: Scout
            incident = await self._run_scout(incident, context)

            # Stage 2: Triage
            incident = await self._run_triage(incident, context)

            # Stage 3: Hypothesis
            incident = await self._run_hypothesis(incident, context)

            # Stage 4: Experiment
            incident = await self._run_experiment(incident, context)

            # Stage 5: Executor
            incident = await self._run_executor(incident, context, auto_approve)

            if (
                incident.proposed_mitigation
                and incident.proposed_mitigation.requires_approval
                and not incident.mitigation_approved
                and not auto_approve
            ):
                incident.stage = AgentStage.EXECUTOR
                incident.add_timeline_event("paused", "Pipeline paused — awaiting human approval")
                incident_store.update_incident(incident.id, incident)

                print(f"\n{'='*60}")
                print(f"⏸️  PIPELINE PAUSED (Awaiting Approval): {incident.id}")
                print(f"Proposed mitigation: {incident.proposed_mitigation.type.value}")
                print(f"{'='*60}\n")

                return incident

            # Stage 6: Postcheck (only after mitigation applied)
            incident = await self._run_postcheck(incident, context)

            # Mark as completed/failed based on recovery
            incident.end_time = datetime.utcnow()
            incident.stage = AgentStage.COMPLETED if incident.metrics_recovered else AgentStage.FAILED

            # Final metrics
            incident.metrics.detection_latency_seconds = 2.5  # demo
            if not incident.metrics.time_to_mitigation_seconds:
                # If mitigation never applied (shouldn’t happen unless blocked)
                incident.metrics.time_to_mitigation_seconds = time.time() - detection_start
            incident.metrics.mitigation_success = incident.metrics_recovered

            incident.add_timeline_event(
                "completed" if incident.metrics_recovered else "failed",
                "Incident pipeline completed" if incident.metrics_recovered else "Incident pipeline finished but not recovered"
            )

        except Exception as e:
            print(f"Pipeline failed: {e}")
            incident.stage = AgentStage.FAILED
            incident.add_timeline_event("failed", f"Pipeline failed: {str(e)}")

        # Save incident
        incident_store.update_incident(incident.id, incident)

        # Print summary safely
        ttm = incident.metrics.time_to_mitigation_seconds or 0.0
        print(f"\n{'='*60}")
        print(f"INCIDENT PIPELINE FINISHED: {incident.id}")
        print(f"Stage: {incident.stage.value}")
        print(f"Time to mitigation: {ttm:.1f}s")
        print(f"Success: {incident.metrics.mitigation_success}")
        print(f"{'='*60}\n")

        return incident

    async def _run_scout(self, incident: Incident, context: Dict[str, Any]) -> Incident:
        print("[SCOUT] Gathering evidence...")
        incident.stage = AgentStage.SCOUT

        result = await self.scout.execute(context)
        incident.evidence = result["evidence"]
        context["evidence"] = result["evidence"]
        context["runbooks"] = result.get("runbooks", {})

        incident.add_timeline_event("scout", result["summary"], {
            "metrics_count": len(result["evidence"].metrics),
            "logs_count": len(result["evidence"].logs),
        })

        incident_store.update_incident(incident.id, incident)

        print(f"   ✓ {result['summary']}")
        return incident

    async def _run_triage(self, incident: Incident, context: Dict[str, Any]) -> Incident:
        print("[TRIAGE] Classifying incident type...")
        incident.stage = AgentStage.TRIAGE

        result = await self.triage.execute(context)
        incident.incident_type = result["incident_type"]
        context["incident_type"] = result["incident_type"]
        context["reasoning"] = result["reasoning"]

        incident.metrics.triage_accuracy = result["confidence"]

        incident.add_timeline_event("triage", result["reasoning"], {
            "type": result["incident_type"].value,
            "confidence": result["confidence"],
        })

        incident_store.update_incident(incident.id, incident)

        print(f"Type: {result['incident_type'].value} (confidence: {result['confidence']:.0%})")
        print(f"{result['reasoning']}")
        return incident

    async def _run_hypothesis(self, incident: Incident, context: Dict[str, Any]) -> Incident:
        print("[HYPOTHESIS] Generating root cause hypotheses...")
        incident.stage = AgentStage.HYPOTHESIS

        result = await self.hypothesis.execute(context)
        incident.hypotheses = result["hypotheses"]
        context["hypotheses"] = result["hypotheses"]

        incident.add_timeline_event("hypothesis", result["summary"], {
            "count": len(result["hypotheses"]),
        })

        incident_store.update_incident(incident.id, incident)

        print(f"   ✓ Generated {len(result['hypotheses'])} hypotheses:")
        for i, h in enumerate(result["hypotheses"], 1):
            print(f"{i}. {h.description} (confidence: {h.confidence:.0%})")
        return incident

    async def _run_experiment(self, incident: Incident, context: Dict[str, Any]) -> Incident:
        print("[EXPERIMENT] Validating hypotheses...")
        incident.stage = AgentStage.EXPERIMENT

        result = await self.experiment.execute(context)
        incident.experiments = result["experiment_results"]
        context["most_likely_cause"] = result["most_likely_cause"]

        incident.add_timeline_event("experiment", result["summary"], {
            "validated_count": sum(1 for r in result["experiment_results"] if r.validated),
        })

        incident_store.update_incident(incident.id, incident)

        print(f"{result['summary']}")
        best = result["most_likely_cause"]
        print(f"Most likely: {best.findings}")
        return incident

    async def _run_executor(self, incident: Incident, context: Dict[str, Any], auto_approve: bool) -> Incident:
        print(f"[EXECUTOR] Proposing mitigation...")
        incident.stage = AgentStage.EXECUTOR

        result = await self.executor.execute(context)

        if result["status"] == "blocked":
            print(f"Mitigation blocked by guardrails: {result['reason']}")
            incident.add_timeline_event("executor", "Mitigation blocked by guardrails", {
                "reason": result["reason"],
            })
            incident_store.update_incident(incident.id, incident)
            return incident

        mitigation = result["mitigation"]
        incident.proposed_mitigation = mitigation

        print(f"Proposed: {mitigation.type.value}")
        print(f"{mitigation.description}")
        print(f"Risk: {mitigation.risk_level}, Reversible: {mitigation.reversible}")

        if mitigation.requires_approval and not auto_approve:
            print("Waiting for human approval...")
            incident.add_timeline_event(
                "executor",
                "Mitigation proposed — awaiting human approval",
                {"mitigation_type": mitigation.type.value},
            )
            incident_store.update_incident(incident.id, incident)
            return incident

        # Apply mitigation
        print("Applying mitigation...")
        apply_result = await self.executor.apply_mitigation(mitigation, incident.service_name)

        if apply_result["success"]:
            mitigation_time = time.time() - context.get("detection_start", time.time())
            incident.metrics.time_to_mitigation_seconds = mitigation_time

            incident.applied_mitigation = mitigation
            incident.mitigation_approved = True

            incident.add_timeline_event("executor", "Mitigation applied successfully", {
                "mitigation_type": mitigation.type.value,
                "time_to_mitigation": f"{mitigation_time:.1f}s",
                "applied_at": apply_result.get("applied_at"),
            })

            print(f"Mitigation applied successfully (time: {mitigation_time:.1f}s)")
        else:
            print(f"Mitigation failed: {apply_result.get('message')}")
            incident.add_timeline_event("executor", "Mitigation apply failed", apply_result)

        incident_store.update_incident(incident.id, incident)
        return incident

    async def _run_postcheck(self, incident: Incident, context: Dict[str, Any]) -> Incident:
        print("[POSTCHECK] Verifying recovery...")
        incident.stage = AgentStage.POSTCHECK

        # Simulate metrics improving after mitigation
        recovered_metrics = self._simulate_recovery(context.get("current_metrics", {}))
        context["current_metrics"] = recovered_metrics

        result = await self.postcheck.execute(context)
        incident.metrics_recovered = result["metrics_recovered"]
        incident.incident_summary = result["incident_summary"]

        incident.add_timeline_event("postcheck", "Recovery verification complete", {
            "recovered": result["metrics_recovered"],
        })

        if result["metrics_recovered"]:
            print("Metrics recovered successfully")
        else:
            print("Metrics not fully recovered")

        print("Generated incident report")

        incident_store.update_incident(incident.id, incident)
        return incident

    def _simulate_recovery(self, current_metrics: Dict[str, float]) -> Dict[str, float]:
        """Simulate metrics returning to normal after mitigation."""
        return {
            "latency_p50": 150,
            "latency_p95": 250,
            "latency_p99": 400,
            "error_rate": 0.2,
            "cpu_usage": 45,
            "memory_usage": 60,
            "request_rate": current_metrics.get("request_rate", 100),
            "queue_depth": 50,
        }
    
    
