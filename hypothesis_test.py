"""Test the Hypothesis Agent."""
import asyncio
import sys
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime, timedelta

from agents.hypothesis import HypothesisAgent
from core.models import (
    Evidence,
    Incident,
    IncidentType,
    IncidentSeverity,
)


async def test_hypothesis_agent():
    print("\n" + "=" * 70)
    print("TESTING HYPOTHESIS AGENT")
    print("=" * 70)

    # Fake incident (already triaged)
    incident = Incident(
        id="test-hypothesis-001",
        service_name="api-service",
        incident_type=IncidentType.LATENCY_SPIKE,
        severity=IncidentSeverity.HIGH,
        detected_at=datetime.utcnow(),
    )

    # Evidence (normally produced by Scout)
    evidence = Evidence(
        metrics={
            "latency_p50": 500,
            "latency_p95": 1500,
            "latency_p99": 3000,
            "error_rate": 1.5,
            "cpu_usage": 70,
            "memory_usage": 65,
            "request_rate": 1200,
            "queue_depth": 180,
        },
        logs=[
            "[ERROR] api-service: Connection timeout to database",
            "[WARN] api-service: Slow query detected",
            "[INFO] api-service: Request processing took 4.2s",
        ],
        recent_deploys=[
            {
                "service": "api-service",
                "version": "v2.3.1",
                "deployed_at": (datetime.utcnow() - timedelta(minutes=20)).isoformat(),
                "deployed_by": "deploy-bot",
                "commit": "abc123f",
            }
        ],
        traces=[],
        dependencies=["database", "redis-cache", "auth-service"],
    )

    # Context (what pipeline normally provides)
    context = {
        "incident": incident,
        "incident_type": IncidentType.LATENCY_SPIKE,
        "evidence": evidence,
        "baseline_metrics": {
            "latency_p99": 500,
            "error_rate": 0.5,
            "cpu_usage": 40,
            "queue_depth": 100,
        },
        # This MUST be present after your pipeline fix
        "reasoning": (
            "P99 latency increased to 3000ms (6x baseline). "
            "Database timeouts observed in logs. "
            "Recent deployment occurred shortly before incident."
        ),
        # Optional: runbooks if you later extend hypothesis to use them
        "runbooks": {
            "latency_spike": "Check DB performance, recent deploys, downstream services",
            "source": "Demo Runbooks",
        },
    }

    agent = HypothesisAgent()

    print("\n💡 Running Hypothesis Agent...\n")
    result = await agent.execute(context)

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    hypotheses = result["hypotheses"]
    print(f"\n✅ Generated {len(hypotheses)} hypotheses\n")

    for i, h in enumerate(hypotheses, 1):
        print(f"{i}. {h.description}")
        print(f"   Confidence: {h.confidence:.0%}")
        print(f"   Evidence needed: {h.evidence_needed}")
        print(f"   Validation: {h.validation_criteria}\n")

    print("=" * 70)
    print("✅ HYPOTHESIS TEST COMPLETED SUCCESSFULLY")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(test_hypothesis_agent())
