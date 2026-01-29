import json
from typing import Dict, Any, Optional
from .base import BaseAgent
from core.models import IncidentType, Evidence


class TriageAgent(BaseAgent):
    """Triage agent classifies incident type using Google Gemini AI (with runbook context)."""

    def __init__(self):
        super().__init__("Triage", model="gemini-2.0-flash")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Classify the incident type based on evidence + runbooks."""
        evidence: Evidence = context.get("evidence")
        # runbooks were added by Scout: context["runbooks"] = {...}
        runbooks: Dict[str, Any] = context.get("runbooks", {}) or {}

        classification = await self._classify_incident(evidence, runbooks, context)

        return {
            "incident_type": classification["type"],
            "confidence": classification["confidence"],
            "reasoning": classification["reasoning"],
        }

    async def _classify_incident(
        self,
        evidence: Evidence,
        runbooks: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Classify incident using Google Gemini or fallback to rules."""
        if self.ai_client:
            print("[TRIAGE] Google Gemini API available, attempting AI classification...")
            try:
                result = await self._classify_with_gemini(evidence, runbooks, context)
                if result:
                    print("[TRIAGE] Using Google Gemini AI for classification")
                    return result
                print("[TRIAGE] Gemini returned empty result, using fallback")
            except Exception as e:
                print(f"[TRIAGE] Gemini API failed: {e}, using rule-based fallback")
        else:
            print("[TRIAGE] No AI client available, using rule-based classification")

        return self._classify_with_rules(evidence, runbooks, context)

    def _format_runbook_context(
        self,
        runbooks: Dict[str, Any],
        max_chars: int = 1200
    ) -> str:

        if not runbooks:
            return "No runbook content available."

        source = runbooks.get("source", "Unknown")
        # Try to include whichever section looks like the runbook body
        # Exclude metadata keys
        sections = []
        for k, v in runbooks.items():
            if k in ("source",):
                continue
            if k == "full_content":
                continue
            # k is typically incident_type (latency_spike / etc.)
            if isinstance(v, str) and v.strip():
                sections.append((k, v.strip()))

        # Prefer a per-incident section if present; else use whatever exists
        body = ""
        if sections:
            # join all sections (usually one)
            parts = [f"[{k}]\n{txt}" for k, txt in sections]
            body = "\n\n".join(parts)

        # If we have full_content, add a trimmed chunk (often richer)
        full_content = runbooks.get("full_content")
        if isinstance(full_content, str) and full_content.strip():
            fc = full_content.strip()
            if len(fc) > max_chars:
                fc = fc[:max_chars] + "..."
            if body:
                body = body + "\n\n[full_content]\n" + fc
            else:
                body = fc

        if not body:
            return f"Runbook source: {source} (no readable content found)."

        # Final trim to avoid huge prompts
        if len(body) > max_chars:
            body = body[:max_chars] + "..."

        return f"Runbook source: {source}\n\n{body}"

    async def _classify_with_gemini(
        self,
        evidence: Evidence,
        runbooks: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Use Google Gemini for classification, including runbook guidance."""
        metrics = evidence.metrics
        baseline = context.get("baseline_metrics", {})

        runbook_snippet = self._format_runbook_context(runbooks, max_chars=1200)

        prompt = f"""You are an expert Site Reliability Engineer (SRE) analyzing a production incident.
Your task is to classify the incident type based on all available evidence.

CURRENT METRICS:
- Latency p95: {metrics.get('latency_p95')}ms
- Latency p99: {metrics.get('latency_p99')}ms
- Error rate: {metrics.get('error_rate')}%
- CPU usage: {metrics.get('cpu_usage')}%
- Memory usage: {metrics.get('memory_usage')}%
- Request rate: {metrics.get('request_rate')} req/s
- Queue depth: {metrics.get('queue_depth')}

BASELINE METRICS (normal operating state):
- Latency p99: {baseline.get('latency_p99', 'unknown')}ms
- Error rate: {baseline.get('error_rate', 'unknown')}%
- CPU usage: {baseline.get('cpu_usage', 'unknown')}%
- Queue depth: {baseline.get('queue_depth', 'unknown')}

RECENT ERROR LOGS:
{chr(10).join(evidence.logs[:8])}

RECENT DEPLOYMENTS:
{json.dumps(evidence.recent_deploys, indent=2)}

SERVICE DEPENDENCIES:
{', '.join(evidence.dependencies) if evidence.dependencies else 'None listed'}

RUNBOOK GUIDANCE (may help identify patterns / symptoms):
{runbook_snippet}

ANALYSIS INSTRUCTIONS:
1. Compare current metrics to baseline to identify anomalies
2. Use logs to identify the dominant failure symptom (timeouts, 5xx, saturation, queue backlog)
3. Consider deployment timing vs incident onset
4. Use runbook symptom patterns as supporting evidence (not as the only signal)

CLASSIFICATION OPTIONS - Choose exactly ONE:
- latency_spike: Significantly high p95/p99 latency (typically >2x baseline)
- error_rate_increase: Elevated error percentage (typically >2x baseline)
- resource_saturation: CPU or memory exhaustion (typically >85%)
- queue_depth_growth: Message queue backlog growing rapidly (typically >2x baseline)

RESPONSE FORMAT:
Respond ONLY with a valid JSON object in this exact format (no markdown, no extra text):

{{"type": "latency_spike", "confidence": 0.92, "reasoning": "Detailed explanation based on evidence"}}
"""

        result = self.ai_client.generate_json(
            prompt=prompt,
            temperature=0.3,
            max_tokens=1000,
        )

        if not result:
            return None

        if "type" not in result or "confidence" not in result or "reasoning" not in result:
            print(f"[TRIAGE] Missing required fields in Gemini response: {result}")
            return None

        type_map = {
            "latency_spike": IncidentType.LATENCY_SPIKE,
            "error_rate_increase": IncidentType.ERROR_RATE,
            "resource_saturation": IncidentType.RESOURCE_SATURATION,
            "queue_depth_growth": IncidentType.QUEUE_DEPTH,
        }

        incident_type = type_map.get(result["type"], IncidentType.UNKNOWN)
        if incident_type == IncidentType.UNKNOWN:
            print(f"[TRIAGE] Unknown incident type from Gemini: {result['type']}")

        return {
            "type": incident_type,
            "confidence": float(result["confidence"]),
            "reasoning": result["reasoning"],
        }

    def _classify_with_rules(
        self,
        evidence: Evidence,
        runbooks: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Rule-based classification fallback with baseline comparison + runbook mention."""
        metrics = evidence.metrics
        baseline = context.get("baseline_metrics", {})

        current_latency = metrics.get("latency_p99", 0)
        baseline_latency = baseline.get("latency_p99", 500)

        current_error = metrics.get("error_rate", 0)
        baseline_error = baseline.get("error_rate", 0.5)

        current_cpu = metrics.get("cpu_usage", 0)
        current_memory = metrics.get("memory_usage", 0)

        current_queue = metrics.get("queue_depth", 0)
        baseline_queue = baseline.get("queue_depth", 100)

        # Quick runbook reference for reasoning (not used for decision)
        rb_source = (runbooks or {}).get("source", "none")

        if current_latency > max(baseline_latency * 2, 1000):
            increase_pct = ((current_latency - baseline_latency) / baseline_latency * 100) if baseline_latency > 0 else 0
            return {
                "type": IncidentType.LATENCY_SPIKE,
                "confidence": 0.9,
                "reasoning": (
                    f"P99 latency elevated to {current_latency}ms (baseline: {baseline_latency}ms, +{increase_pct:.0f}%). "
                    f"Runbook source: {rb_source}."
                )
            }

        if current_error > max(baseline_error * 2, 5.0):
            increase_pct = ((current_error - baseline_error) / baseline_error * 100) if baseline_error > 0 else 0
            return {
                "type": IncidentType.ERROR_RATE,
                "confidence": 0.95,
                "reasoning": (
                    f"Error rate elevated to {current_error}% (baseline: {baseline_error}%, +{increase_pct:.0f}%). "
                    f"Runbook source: {rb_source}."
                )
            }

        if current_cpu > 85 or current_memory > 85:
            resource_type = "CPU" if current_cpu > current_memory else "Memory"
            usage = max(current_cpu, current_memory)
            return {
                "type": IncidentType.RESOURCE_SATURATION,
                "confidence": 0.85,
                "reasoning": (
                    f"{resource_type} utilization critically high at {usage}%. "
                    f"Runbook source: {rb_source}."
                )
            }

        if current_queue > max(baseline_queue * 2, 1000):
            increase_pct = ((current_queue - baseline_queue) / baseline_queue * 100) if baseline_queue > 0 else 0
            return {
                "type": IncidentType.QUEUE_DEPTH,
                "confidence": 0.8,
                "reasoning": (
                    f"Queue depth elevated to {current_queue} (baseline: {baseline_queue}, +{increase_pct:.0f}%). "
                    f"Runbook source: {rb_source}."
                )
            }

        return {
            "type": IncidentType.UNKNOWN,
            "confidence": 0.5,
            "reasoning": (
                "No clear pattern detected in metrics; manual investigation recommended. "
                f"Runbook source: {rb_source}."
            ),
        }