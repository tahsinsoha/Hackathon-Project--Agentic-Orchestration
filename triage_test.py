"""Test Triage Agent with Google Gemini."""
import asyncio
from dotenv import load_dotenv
from agents.triage import TriageAgent
from core.models import Incident, Evidence, IncidentType, IncidentSeverity
from datetime import datetime, timedelta

load_dotenv()


async def test_gemini_connection():
    """Test if Gemini API is working."""
    print("\n" + "="*70)
    print("TEST 0: GEMINI API CONNECTION")
    print("="*70)
    
    try:
        from integrations.gemini import GeminiClient
        import os
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ No GOOGLE_API_KEY found in .env file")
            return False
        
        print(f"✅ API key loaded: {api_key[:15]}...")
        
        client = GeminiClient(api_key)
        
        print("🔄 Testing simple API call...")
        response = client.generate_content("Say 'Hello from Gemini!' if you can read this.")
        
        if response:
            print(f"✅ Gemini responded: {response}")
            return True
        else:
            print("❌ Gemini returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_triage_latency_spike():
    """Test triage with latency spike scenario."""
    print("\n" + "="*70)
    print("TEST 1: LATENCY SPIKE CLASSIFICATION")
    print("="*70)
    
    evidence = Evidence(
        metrics={
            "latency_p50": 500,
            "latency_p95": 1500,
            "latency_p99": 3000,  # Spike!
            "error_rate": 1.5,
            "cpu_usage": 65,
            "memory_usage": 60,
            "request_rate": 1000,
            "queue_depth": 150
        },
        logs=[
            "[ERROR] api-service: Database connection timeout after 5000ms",
            "[WARN] api-service: Request processing took 4.5s",
            "[ERROR] api-service: Failed to acquire database connection from pool"
        ],
        recent_deploys=[
            {
                "service": "api-service",
                "version": "v2.3.1",
                "deployed_at": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                "deployed_by": "deploy-bot"
            }
        ],
        dependencies=["database", "redis-cache"],
        traces=[]
    )
    
    context = {
        "evidence": evidence,
        "incident": Incident(
            id="test-latency",
            service_name="api-service",
            severity=IncidentSeverity.HIGH,
            detected_at=datetime.utcnow()
        ),
        "baseline_metrics": {
            "latency_p99": 500,
            "error_rate": 0.5,
            "cpu_usage": 45
        }
    }
    
    triage = TriageAgent()
    result = await triage.execute(context)
    
    print(f"\n📊 Results:")
    print(f"   Type: {result['incident_type'].value}")
    print(f"   Confidence: {result['confidence']*100:.1f}%")
    print(f"   Reasoning: {result['reasoning']}")
    print("\n" + "="*70)


async def main():
    """Run all tests."""
    # Test Gemini connection first
    connected = await test_gemini_connection()
    
    if not connected:
        print("\n⚠️ Gemini API not working. Triage will use rule-based fallback.")
        print("Please check:")
        print("1. GOOGLE_API_KEY is in .env file")
        print("2. API key is valid")
        print("3. google-generativeai is installed: pip install google-generativeai")
        print("\nContinuing with tests anyway...\n")
    
    # Test triage
    await asyncio.sleep(2)
    await test_triage_latency_spike()


if __name__ == "__main__":
    asyncio.run(main())