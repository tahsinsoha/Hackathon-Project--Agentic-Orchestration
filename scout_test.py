"""Test the refactored Scout Agent with Jina AI."""
import asyncio
import sys
sys.path.insert(0, '.')  # Ensure imports work

from agents.scout import ScoutAgent
from core.models import Incident, IncidentType, IncidentSeverity
from datetime import datetime


async def test_scout_basic():
    """Test Scout agent with basic functionality."""
    print("\n" + "="*70)
    print("TESTING SCOUT AGENT - BASIC FUNCTIONALITY")
    print("="*70)
    
    # Create test incident
    incident = Incident(
        id="test-001",
        service_name="api-service",
        incident_type=IncidentType.LATENCY_SPIKE,
        severity=IncidentSeverity.HIGH,
        detected_at=datetime.utcnow()
    )
    
    # Create test context
    context = {
        "incident": incident,
        "current_metrics": {
            "latency_p50": 500,
            "latency_p95": 1500,
            "latency_p99": 3000,
            "error_rate": 2.5,
            "cpu_usage": 75,
            "memory_usage": 68,
            "request_rate": 1000,
            "queue_depth": 150
        }
    }
    
    # Run Scout agent
    scout = ScoutAgent()
    print("\n🔍 Running Scout Agent...\n")
    
    result = await scout.execute(context)
    
    # Display results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"\n✅ {result['summary']}")
    
    print(f"\n📊 Evidence Collected:")
    print(f"   - Metrics: {len(result['evidence'].metrics)} items")
    print(f"   - Logs: {len(result['evidence'].logs)} entries")
    print(f"   - Recent deploys: {len(result['evidence'].recent_deploys)}")
    print(f"   - Dependencies: {len(result['evidence'].dependencies)}")
    
    print(f"\n📚 Runbooks:")
    runbooks = result.get('runbooks', {})
    for key, value in runbooks.items():
        if key != "full_content":  # Skip full content for brevity
            print(f"\n   [{key}]:")
            content = str(value)
            if len(content) > 200:
                print(f"   {content[:200]}...")
            else:
                print(f"   {content}")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETED SUCCESSFULLY")
    print("="*70 + "\n")
    
    return result


async def test_scout_all_incident_types():
    """Test Scout with different incident types."""
    print("\n" + "="*70)
    print("TESTING SCOUT AGENT - ALL INCIDENT TYPES")
    print("="*70)
    
    incident_types = [
        IncidentType.LATENCY_SPIKE,
        IncidentType.ERROR_RATE,
        IncidentType.RESOURCE_SATURATION,
        IncidentType.QUEUE_DEPTH
    ]
    
    scout = ScoutAgent()
    
    for inc_type in incident_types:
        print(f"\n{'─'*70}")
        print(f"Testing: {inc_type.value}")
        print(f"{'─'*70}")
        
        incident = Incident(
            id=f"test-{inc_type.value}",
            service_name="test-service",
            incident_type=inc_type,
            severity=IncidentSeverity.MEDIUM,
            detected_at=datetime.utcnow()
        )
        
        context = {
            "incident": incident,
            "current_metrics": {
                "latency_p50": 200,
                "latency_p95": 500,
                "latency_p99": 1000,
                "error_rate": 1.5,
                "cpu_usage": 60,
                "memory_usage": 55,
                "request_rate": 800,
                "queue_depth": 100
            }
        }
        
        result = await scout.execute(context)
        
        runbooks = result.get('runbooks', {})
        print(f"   Source: {runbooks.get('source', 'Unknown')}")
        print(f"   Runbook type: {inc_type.value}")
        
        if inc_type.value in runbooks:
            content = str(runbooks[inc_type.value])
            print(f"   Content: {content[:100]}...")
    
    print("\n" + "="*70)
    print("✅ ALL INCIDENT TYPES TESTED")
    print("="*70 + "\n")


async def main():
    """Run all tests."""
    # Test 1: Basic functionality
    await test_scout_basic()
    
    # Small delay
    await asyncio.sleep(2)
    
    # Test 2: All incident types
    await test_scout_all_incident_types()


if __name__ == "__main__":
    asyncio.run(main())