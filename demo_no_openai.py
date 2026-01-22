#!/usr/bin/env python3
"""
Demo: Tonic → Retool (No OpenAI Required!)

This demo shows:
1. Tonic generating synthetic incident data
2. Directly triggering Retool workflow
3. No AI agents needed!

Usage:
    python demo_no_openai.py
    python demo_no_openai.py --incident-type error_rate
"""
import argparse
import os
from dotenv import load_dotenv
from integrations.tonic import TonicClient
from integrations.retool import RetoolClient
from simulator.scenarios import IncidentSimulator

load_dotenv()


def print_banner(title: str):
    print(f"\n{'='*70}")
    print(f"   {title}")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Demo: Tonic → Retool (No OpenAI needed)"
    )
    parser.add_argument(
        "--incident-type",
        choices=["latency_spike", "error_rate", "resource_saturation", "queue_depth"],
        help="Type of incident to simulate"
    )
    
    args = parser.parse_args()
    
    print_banner("🎬 TONIC → RETOOL DEMO (No AI Agents)")
    
    print("This demo will:")
    print("  1. 🧪 Generate synthetic data using Tonic")
    print("  2. ⚡ Trigger Retool approval workflow")
    print("  3. ✅ Show you the results")
    print("\n✨ No OpenAI API key needed!")
    print()
    
    # Check configuration
    tonic_key = os.getenv("TONIC_API_KEY")
    retool_webhook = os.getenv("RETOOL_WEBHOOK_URL")
    
    print("Configuration Status:")
    print(f"  {'✅' if tonic_key else '⚠️ '} Tonic API Key: {'Found' if tonic_key else 'Not found (will use fallback)'}")
    print(f"  {'✅' if retool_webhook else '⚠️ '} Retool: {'Found' if retool_webhook else 'Not found (demo mode)'}")
    print()
    
    input("Press Enter to start... ")
    
    # ========================================================================
    # STEP 1: TONIC DATA GENERATION
    # ========================================================================
    print_banner("STEP 1: 🧪 TONIC - Generating Synthetic Data")
    
    tonic = TonicClient()
    simulator = IncidentSimulator()
    
    print(f"Generating incident scenario{f': {args.incident_type}' if args.incident_type else ' (random)'}...")
    incident, current_metrics, baseline_metrics = simulator.generate_incident(args.incident_type)
    
    print(f"\n✅ Incident Generated!")
    print(f"   ID: {incident.id}")
    print(f"   Service: {incident.service_name}")
    print(f"   Severity: {incident.severity.value}")
    
    print(f"\n📊 Metrics Comparison:")
    print(f"   {'Metric':<20} {'Current':<15} {'Baseline':<15} {'Change':<10}")
    print(f"   {'-'*60}")
    
    for key in ['latency_p99', 'error_rate', 'cpu_usage', 'memory_usage']:
        current = current_metrics.get(key, 0)
        baseline = baseline_metrics.get(key, 0)
        if baseline > 0:
            change_pct = ((current - baseline) / baseline * 100)
            emoji = "🔴" if abs(change_pct) > 50 else "🟡" if abs(change_pct) > 20 else "🟢"
            print(f"   {emoji} {key:<17} {current:<15.1f} {baseline:<15.1f} {change_pct:+.0f}%")
    
    # Show Tonic time-series data
    print(f"\n📈 Tonic Time-Series Data (Last 5 points):")
    metrics_data = tonic.generate_metrics_dataset(
        args.incident_type or "latency_spike",
        duration_minutes=5
    )
    
    for i, point in enumerate(metrics_data[-5:], 1):
        print(f"   Point {i}: latency_p99={point.get('latency_p99', 0):.0f}ms, "
              f"error_rate={point.get('error_rate', 0):.2f}%, "
              f"cpu={point.get('cpu_usage', 0):.0f}%")
    
    print(f"\n📝 Tonic Log Samples:")
    logs = tonic.generate_log_entries(args.incident_type or "latency_spike", count=3)
    for log in logs:
        print(f"   {log}")
    
    input("\nPress Enter to trigger Retool workflow... ")
    
    # ========================================================================
    # STEP 2: TRIGGER RETOOL WORKFLOW
    # ========================================================================
    print_banner("STEP 2: ⚡ TRIGGER RETOOL WORKFLOW")
    
    # Create a mitigation plan based on incident type
    mitigation_plans = {
        "latency_spike": {
            "type": "rollback",
            "description": "Roll back to previous stable version v1.2.2",
            "risk_level": "medium",
            "parameters": {"target_version": "v1.2.2"}
        },
        "error_rate": {
            "type": "scale_up",
            "description": "Scale up service replicas from 3 to 6",
            "risk_level": "low",
            "parameters": {"current_replicas": 3, "target_replicas": 6}
        },
        "resource_saturation": {
            "type": "increase_resources",
            "description": "Increase CPU limit from 2 cores to 4 cores",
            "risk_level": "low",
            "parameters": {"resource": "cpu", "from": "2", "to": "4"}
        },
        "queue_depth": {
            "type": "scale_consumers",
            "description": "Scale up queue consumers from 2 to 8",
            "risk_level": "medium",
            "parameters": {"current": 2, "target": 8}
        }
    }
    
    incident_type = args.incident_type or "latency_spike"
    mitigation = mitigation_plans.get(incident_type, mitigation_plans["latency_spike"])
    
    print(f"Mitigation Plan:")
    print(f"   Type: {mitigation['type']}")
    print(f"   Description: {mitigation['description']}")
    print(f"   Risk Level: {mitigation['risk_level']}")
    print()
    
    # Trigger Retool
    retool = RetoolClient()
    success = retool.send_approval_request(incident.id, mitigation)
    
    # ========================================================================
    # STEP 3: RESULTS
    # ========================================================================
    print_banner("STEP 3: ✅ RESULTS")
    
    if success and (retool_webhook):
        print("✅ SUCCESS! Retool workflow was triggered!")
        print()
        print("To verify:")
        print("  1. Open Retool: https://retool.com")
        print("  2. Go to Workflows")
        print("  3. Click 'Runs' tab")
        print(f"  4. Look for incident ID: {incident.id}")
        print()
        print("You should see the incident data and mitigation plan!")
    elif success:
        print("Success")

    
    print(f"\n{'='*70}")
    print("\n🎉 What You Just Saw:")
    print(f"  ✅ Tonic generated realistic incident data")
    print(f"  ✅ Created mitigation plan")
    print(f"  {'✅' if retool_webhook else '⚠️ '} Retool workflow {'triggered' if retool_webhook else 'simulated'}")
    print(f"  ✅ No AI agents or OpenAI needed!")
    
    print(f"\nNext Steps:")
    print(f"  • Try different types: python demo_no_openai.py --incident-type error_rate")
    print(f"  • View dashboard: http://localhost:8000 (if server running)")
    print(f"  • Configure Retool for real workflow triggers")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

