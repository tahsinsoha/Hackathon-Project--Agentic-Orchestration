"""Main entry point for Incident Autopilot."""
import asyncio
import argparse
from core.pipeline import IncidentPipeline
from core.state import incident_store
from simulator.scenarios import IncidentSimulator


async def run_demo(incident_type: str = None):
    """Run a demo incident simulation."""
    print("\n" + "="*70)
    print("🚨 INCIDENT AUTOPILOT WITH GUARDRAILS - Demo Mode")
    print("="*70)
    print("\nThis demo simulates a realistic incident and runs the full")
    print("multi-agent pipeline: Scout → Triage → Hypothesis → Experiment → Execute → Postcheck\n")
    
    # Initialize
    simulator = IncidentSimulator()
    pipeline = IncidentPipeline()
    
    # Generate incident
    print(f"Generating incident{f' of type: {incident_type}' if incident_type else ''}...")
    incident, current_metrics, baseline_metrics = simulator.generate_incident(incident_type)
    
    print(f"\n📋 Incident Details:")
    print(f"   ID: {incident.id}")
    print(f"   Service: {incident.service_name}")
    print(f"   Severity: {incident.severity.value}")
    
    print(f"\n📊 Current Metrics:")
    for key, value in current_metrics.items():
        baseline = baseline_metrics.get(key, 0)
        if isinstance(value, float):
            change = ((value - baseline) / baseline * 100) if baseline > 0 else 0
            symbol = "📈" if change > 20 else "📊"
            print(f"   {symbol} {key}: {value:.1f} (baseline: {baseline:.1f}, change: {change:+.1f}%)")
    
    # Store incident
    incident_store.create_incident(incident)
    
    # Run pipeline
    result = await pipeline.run(
        incident,
        current_metrics,
        baseline_metrics,
        auto_approve=True  # Auto-approve for demo
    )
    
    # Display results
    print("\n" + "="*70)
    print("📈 FINAL METRICS")
    print("="*70)
    print(f"Detection Latency: {result.metrics.detection_latency_seconds:.1f}s")
    print(f"Time to Mitigation: {result.metrics.time_to_mitigation_seconds:.1f}s")
    print(f"Triage Accuracy: {result.metrics.triage_accuracy*100:.1f}%")
    print(f"Mitigation Success: {'✅ Yes' if result.metrics.mitigation_success else '❌ No'}")
    
    print("\n" + "="*70)
    print("📝 INCIDENT SUMMARY")
    print("="*70)
    if result.incident_summary:
        print(result.incident_summary)
    
    print("\n" + "="*70)
    print(f"✅ Demo completed! Incident ID: {result.id}")
    print("="*70 + "\n")
    
    return result


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Incident Autopilot with Guardrails")
    parser.add_argument(
        "--mode",
        choices=["demo", "server"],
        default="demo",
        help="Run mode: demo (single incident) or server (API server)"
    )
    parser.add_argument(
        "--incident-type",
        choices=["latency_spike", "error_rate", "resource_saturation", "queue_depth"],
        help="Type of incident to simulate (demo mode only)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for API server (server mode only)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "demo":
        # Run single demo
        asyncio.run(run_demo(args.incident_type))
    else:
        # Start API server
        import uvicorn
        from api import app
        
        print(f"\n🚀 Starting Incident Autopilot API Server")
        print(f"📊 Dashboard: http://localhost:{args.port}")
        print(f"📚 API Docs: http://localhost:{args.port}/docs\n")
        
        uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()

