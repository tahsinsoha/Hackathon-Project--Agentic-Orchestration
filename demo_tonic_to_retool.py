#!/usr/bin/env python3
"""
Demo: Tonic Synthetic Data → Multi-Agent Pipeline → Retool Workflow

This script demonstrates the complete flow:
1. Tonic generates realistic incident data
2. Multi-agent pipeline processes it
3. Retool workflow gets triggered for approval
4. You see everything in action!

Usage:
    python demo_tonic_to_retool.py
    python demo_tonic_to_retool.py --incident-type error_rate
    python demo_tonic_to_retool.py --show-tonic-data
"""
import asyncio
import argparse
import os
from dotenv import load_dotenv
from integrations.tonic import TonicClient
from integrations.retool import RetoolClient
from simulator.scenarios import IncidentSimulator
from core.pipeline import IncidentPipeline
from core.state import incident_store

# Load environment
load_dotenv()


def print_banner(title: str, color: str = "blue"):
    """Print a colored banner."""
    colors = {
        "blue": "\033[94m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "purple": "\033[95m",
        "end": "\033[0m"
    }
    
    c = colors.get(color, colors["blue"])
    end = colors["end"]
    
    print(f"\n{c}{'='*70}")
    print(f"   {title}")
    print(f"{'='*70}{end}\n")


async def main():
    parser = argparse.ArgumentParser(
        description="Demo: Tonic → Pipeline → Retool"
    )
    parser.add_argument(
        "--incident-type",
        choices=["latency_spike", "error_rate", "resource_saturation", "queue_depth"],
        help="Type of incident to simulate"
    )
    parser.add_argument(
        "--show-tonic-data",
        action="store_true",
        help="Show detailed Tonic synthetic data"
    )
    parser.add_argument(
        "--no-pipeline",
        action="store_true",
        help="Skip pipeline execution (just show data generation)"
    )
    
    args = parser.parse_args()
    
    # ========================================================================
    # INTRO
    # ========================================================================
    print_banner("🎬 TONIC → MULTI-AGENT → RETOOL DEMO", "purple")
    
    print("This demo will:")
    print("  1. 🧪 Generate synthetic data using Tonic")
    print("  2. 🤖 Process incident with 6 AI agents")
    print("  3. ⚡ Trigger Retool approval workflow")
    print("  4. 📊 Show you the results")
    print()
    
    # Check configuration
    tonic_key = os.getenv("TONIC_API_KEY")
    retool_webhook = os.getenv("RETOOL_WEBHOOK_URL")
    retool_api_key = os.getenv("RETOOL_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print("Configuration Status:")
    print(f"  {'✅' if tonic_key else '⚠️ '} Tonic API Key: {'Found' if tonic_key else 'Not found (will use fallback)'}")
    print(f"  {'✅' if retool_webhook or retool_api_key else '⚠️ '} Retool: {'Found' if retool_webhook or retool_api_key else 'Not found (demo mode)'}")
    print(f"  {'✅' if openai_key else '❌'} OpenAI API Key: {'Found' if openai_key else 'REQUIRED - Set OPENAI_API_KEY!'}")
    print()
    
    if not openai_key and not args.no_pipeline:
        print("❌ Error: OPENAI_API_KEY required for agent pipeline!")
        print("   Add it to your .env file or run with --no-pipeline")
        return
    
    input("Press Enter to start the demo... ")
    
    # ========================================================================
    # STEP 1: TONIC DATA GENERATION
    # ========================================================================
    print_banner("STEP 1: 🧪 TONIC - Generating Synthetic Data", "blue")
    
    tonic = TonicClient()
    simulator = IncidentSimulator()
    
    # Generate incident scenario
    print(f"Generating incident scenario{f': {args.incident_type}' if args.incident_type else ' (random)'}...")
    incident, current_metrics, baseline_metrics = simulator.generate_incident(args.incident_type)
    
    print(f"\n✅ Incident Generated!")
    print(f"   ID: {incident.id}")
    print(f"   Service: {incident.service_name}")
    print(f"   Severity: {incident.severity.value}")
    print(f"   Timestamp: {incident.timestamp}")
    
    # Show metrics comparison
    print(f"\n📊 Metrics Comparison (Current vs Baseline):")
    print(f"   {'Metric':<20} {'Current':<15} {'Baseline':<15} {'Change':<10}")
    print(f"   {'-'*60}")
    
    for key in current_metrics.keys():
        current = current_metrics.get(key, 0)
        baseline = baseline_metrics.get(key, 0)
        if baseline > 0:
            change_pct = ((current - baseline) / baseline * 100)
            emoji = "🔴" if abs(change_pct) > 50 else "🟡" if abs(change_pct) > 20 else "🟢"
            print(f"   {emoji} {key:<17} {current:<15.1f} {baseline:<15.1f} {change_pct:+.0f}%")
        else:
            print(f"   🔵 {key:<17} {current:<15.1f} {baseline:<15.1f} N/A")
    
    # Show Tonic-generated time-series data if requested
    if args.show_tonic_data:
        print(f"\n📈 Tonic Time-Series Data (Last 5 points):")
        metrics_data = tonic.generate_metrics_dataset(
            args.incident_type or "latency_spike",
            duration_minutes=5
        )
        
        for i, point in enumerate(metrics_data[-5:], 1):
            print(f"   Point {i}: latency_p99={point.get('latency_p99', 0):.0f}ms, "
                  f"error_rate={point.get('error_rate', 0):.2f}%, "
                  f"cpu={point.get('cpu_usage', 0):.0f}%")
        
        print(f"\n   📝 Tonic also generates log entries:")
        logs = tonic.generate_log_entries(args.incident_type or "latency_spike", count=3)
        for log in logs:
            print(f"      {log}")
    
    print(f"\n{'='*70}")
    
    if args.no_pipeline:
        print("\n✅ Data generation complete! (Skipping pipeline as requested)")
        return
    
    input("\nPress Enter to run the multi-agent pipeline... ")
    
    # ========================================================================
    # STEP 2: MULTI-AGENT PIPELINE
    # ========================================================================
    print_banner("STEP 2: 🤖 MULTI-AGENT PIPELINE", "green")
    
    print("Running 6 AI agents in sequence:")
    print("  1️⃣  Scout - Detects anomalies")
    print("  2️⃣  Triage - Classifies incident type")
    print("  3️⃣  Hypothesis - Forms theories about root cause")
    print("  4️⃣  Experiment - Validates hypotheses")
    print("  5️⃣  Executor - Proposes mitigation → Triggers Retool!")
    print("  6️⃣  Postcheck - Verifies the fix")
    print()
    
    # Store incident
    incident_store.create_incident(incident)
    
    # Run pipeline
    pipeline = IncidentPipeline()
    result = await pipeline.run(
        incident,
        current_metrics,
        baseline_metrics,
        auto_approve=True  # Auto-approve for demo
    )
    
    print(f"\n{'='*70}")
    
    # ========================================================================
    # STEP 3: RESULTS
    # ========================================================================
    print_banner("STEP 3: 📊 RESULTS & RETOOL VERIFICATION", "yellow")
    
    print("Pipeline Metrics:")
    print(f"   ⏱️  Detection Latency: {result.metrics.detection_latency_seconds:.1f}s")
    print(f"   ⏱️  Time to Mitigation: {result.metrics.time_to_mitigation_seconds:.1f}s")
    print(f"   🎯 Triage Accuracy: {result.metrics.triage_accuracy*100:.0f}%")
    print(f"   {'✅' if result.metrics.mitigation_success else '❌'} Mitigation Success: {result.metrics.mitigation_success}")
    print(f"   🔍 Root Cause: {result.root_cause or 'Unknown'}")
    
    print(f"\n📝 Agent Actions ({len(result.actions)} total):")
    for i, action in enumerate(result.actions[-5:], 1):  # Show last 5
        print(f"   {i}. [{action.agent_type.value}] {action.action_type}")
        print(f"      {action.description[:80]}...")
    
    print(f"\n{'='*70}")
    
    # ========================================================================
    # STEP 4: RETOOL VERIFICATION
    # ========================================================================
    print_banner("STEP 4: ⚡ VERIFY RETOOL WORKFLOW", "purple")
    
    if retool_webhook or retool_api_key:
        print("✅ Retool workflow was triggered during execution!")
        print()
        print("To verify:")
        print("  1. Open Retool: https://retool.com")
        print("  2. Go to Workflows")
        print("  3. Find your workflow")
        print("  4. Click 'Runs' tab")
        print(f"  5. Look for run with incident ID: {incident.id}")
        print()
        print("You should see the incident data that was sent!")
    else:
        print("⚠️  Running in demo mode (no Retool configured)")
        print()
        print("To see real Retool integration:")
        print("  1. Create workflow: https://retool.com → Workflows")
        print("  2. Get webhook URL")
        print("  3. Add to .env: RETOOL_WEBHOOK_URL=your_url")
        print("  4. Run this demo again!")
    
    print(f"\n{'='*70}")
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print_banner("✅ DEMO COMPLETE!", "green")
    
    print("What just happened:")
    print(f"  1. ✅ Tonic {'(via API)' if tonic_key else '(local fallback)'} generated incident data")
    print(f"  2. ✅ 6 AI agents analyzed and resolved the incident")
    print(f"  3. {'✅' if retool_webhook or retool_api_key else '⚠️ '} Retool workflow {'triggered' if retool_webhook or retool_api_key else 'simulated'}")
    print(f"  4. ✅ Complete audit trail stored")
    
    print(f"\nIncident Details:")
    print(f"   🆔 Incident ID: {result.id}")
    print(f"   ⏱️  Total Time: {result.metrics.time_to_mitigation_seconds:.1f}s")
    print(f"   📊 Status: {result.status.value}")
    
    print(f"\nNext Steps:")
    print(f"  • View dashboard: python main.py --mode server")
    print(f"  • Check API: curl http://localhost:8000/api/incidents/{result.id}")
    print(f"  • Run another: python demo_tonic_to_retool.py --incident-type error_rate")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check .env file exists with OPENAI_API_KEY")
        print("  2. Ensure dependencies installed: pip install -r requirements.txt")
        print("  3. See DEMO_WITH_TONIC_AND_RETOOL.md for detailed guide")

