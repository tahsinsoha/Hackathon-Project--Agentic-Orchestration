#!/usr/bin/env python3
"""CLI tool to simulate incidents for testing."""
import argparse
import asyncio
from core.pipeline import IncidentPipeline
from core.state import incident_store
from simulator.scenarios import IncidentSimulator


async def main():
    parser = argparse.ArgumentParser(description="Simulate an incident")
    parser.add_argument(
        "--type",
        choices=["latency_spike", "error_rate", "resource_saturation", "queue_depth"],
        help="Type of incident to simulate"
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        default=True,
        help="Auto-approve mitigations (default: True)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🚨 INCIDENT SIMULATOR")
    print("="*70 + "\n")
    
    simulator = IncidentSimulator()
    pipeline = IncidentPipeline()
    
    # Generate incident
    incident, current_metrics, baseline_metrics = simulator.generate_incident(args.type)
    
    print(f"Generated incident: {incident.id}")
    print(f"Service: {incident.service_name}")
    print(f"Type: {args.type or 'random'}\n")
    
    # Store and run
    incident_store.create_incident(incident)
    result = await pipeline.run(incident, current_metrics, baseline_metrics, args.auto_approve)
    
    print(f"\n✅ Incident {result.id} completed")
    print(f"Success: {result.metrics.mitigation_success}")
    print(f"Time to mitigation: {result.metrics.time_to_mitigation_seconds:.1f}s\n")


if __name__ == "__main__":
    asyncio.run(main())

