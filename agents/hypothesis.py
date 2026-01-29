import json
from typing import Dict, Any, List
from .base import BaseAgent
from core.models import Hypothesis, IncidentType, Evidence


class HypothesisAgent(BaseAgent):
    """Generates AI-powered root cause hypotheses using evidence analysis."""
    
    def __init__(self):
        super().__init__("Hypothesis", model="gemini-2.0-flash")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate root cause hypotheses based on incident type and evidence."""
        incident_type = context.get("incident_type")
        evidence: Evidence = context.get("evidence")
        triage_reasoning = context.get("reasoning", "")
        
        # Try AI generation first
        if self.ai_client:
            print(f"[HYPOTHESIS] Using Gemini AI to generate hypotheses")
            try:
                hypotheses = await self._generate_with_ai(
                    incident_type, evidence, triage_reasoning
                )
                if hypotheses:
                    print(f"[HYPOTHESIS] Generated {len(hypotheses)} AI-powered hypotheses")
                    return {
                        "hypotheses": hypotheses,
                        "summary": f"Generated {len(hypotheses)} AI-powered hypotheses"
                    }
            except Exception as e:
                print(f"[HYPOTHESIS] AI generation failed: {e}, using rule-based fallback")
        
        # Fallback to rule-based
        print(f"[HYPOTHESIS] Using rule-based hypothesis generation")
        hypotheses = self._generate_with_rules(incident_type, evidence)
        
        return {
            "hypotheses": hypotheses,
            "summary": f"Generated {len(hypotheses)} hypotheses"
        }
    
    async def _generate_with_ai(self, incident_type: IncidentType,
                                evidence: Evidence,
                                triage_reasoning: str) -> List[Hypothesis]:
        """Generate hypotheses using Gemini AI."""
        
        metrics = evidence.metrics
        
        prompt = f"""You are an expert Site Reliability Engineer investigating a production incident.

INCIDENT TYPE: {incident_type.value}

TRIAGE ANALYSIS:
{triage_reasoning}

CURRENT METRICS:
- Latency p95: {metrics.get('latency_p95')}ms
- Latency p99: {metrics.get('latency_p99')}ms
- Error rate: {metrics.get('error_rate')}%
- CPU usage: {metrics.get('cpu_usage')}%
- Memory usage: {metrics.get('memory_usage')}%
- Queue depth: {metrics.get('queue_depth')}

RECENT ERROR LOGS:
{chr(10).join(evidence.logs[:5])}

RECENT DEPLOYMENTS:
{json.dumps(evidence.recent_deploys, indent=2)}

SERVICE DEPENDENCIES:
{', '.join(evidence.dependencies) if evidence.dependencies else 'None listed'}

YOUR TASK:
Generate 2-3 plausible root cause hypotheses for this {incident_type.value} incident.
For EACH hypothesis provide:
1. A specific, actionable description of the root cause
2. Confidence level (0.0-1.0) based on available evidence
3. What additional evidence would confirm this hypothesis
4. How to validate/test this hypothesis

IMPORTANT GUIDELINES:
- Base confidence on actual evidence (logs, metrics, deployments)
- Higher confidence if logs directly support the hypothesis
- Lower confidence for speculation without evidence
- Consider deployment timing correlation
- Look for patterns in error messages
- Be specific (not "database issues" but "connection pool exhaustion")

RESPONSE FORMAT:
Respond ONLY with valid JSON (no markdown, no code blocks):

{{
  "hypotheses": [
    {{
      "description": "Specific root cause description",
      "confidence": 0.85,
      "evidence_needed": ["specific evidence item 1", "specific evidence item 2"],
      "validation_criteria": "Specific test or check to validate this hypothesis"
    }},
    {{
      "description": "Another specific root cause",
      "confidence": 0.65,
      "evidence_needed": ["evidence needed"],
      "validation_criteria": "How to validate"
    }}
  ]
}}"""

        # Call Gemini API
        result = self.ai_client.generate_json(
            prompt=prompt,
            temperature=0.4,  # Moderate creativity
            max_tokens=1500
        )
        
        if not result or "hypotheses" not in result:
            return None
        
        # Convert to Hypothesis objects
        hypotheses = []
        for h in result["hypotheses"]:
            try:
                hypotheses.append(Hypothesis(
                    description=h.get("description", "Unknown"),
                    confidence=float(h.get("confidence", 0.5)),
                    evidence_needed=h.get("evidence_needed", []),
                    validation_criteria=h.get("validation_criteria", "Manual validation")
                ))
            except Exception as e:
                print(f"   ⚠️  [HYPOTHESIS] Skipping malformed hypothesis: {e}")
                continue
        
        return hypotheses if hypotheses else None
    
    def _generate_with_rules(self, incident_type: IncidentType,
                            evidence: Evidence) -> List[Hypothesis]:
        """Rule-based hypothesis generation fallback."""
        
        # Analyze evidence
        has_recent_deploy = len(evidence.recent_deploys) > 0
        has_db_errors = any("database" in log.lower() for log in evidence.logs)
        has_cache_errors = any("cache" in log.lower() or "redis" in log.lower() 
                              for log in evidence.logs)
        
        if incident_type == IncidentType.LATENCY_SPIKE:
            hypotheses = []
            
            if has_recent_deploy:
                deploy = evidence.recent_deploys[0]
                hypotheses.append(Hypothesis(
                    description=f"Deployment {deploy.get('version')} introduced performance regression",
                    confidence=0.80,
                    evidence_needed=["query times", "deployment correlation"],
                    validation_criteria=f"Compare performance before/after {deploy.get('deployed_at')}"
                ))
            
            if has_db_errors:
                hypotheses.append(Hypothesis(
                    description="Database connection pool exhaustion",
                    confidence=0.75,
                    evidence_needed=["connection pool metrics"],
                    validation_criteria="Check pool utilization and wait times"
                ))
            
            hypotheses.append(Hypothesis(
                description="Downstream service degradation",
                confidence=0.60,
                evidence_needed=["dependency health"],
                validation_criteria="Check dependent service health"
            ))
            
            return hypotheses[:3]
        
        # Similar logic for other incident types...
        # (Use the improved rule-based version from Option A)
        
        return [
            Hypothesis(
                description=f"Generic {incident_type.value} root cause",
                confidence=0.50,
                evidence_needed=["additional investigation"],
                validation_criteria="Manual investigation required"
            )
        ]