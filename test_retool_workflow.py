#!/usr/bin/env python3
"""
Test Retool Workflow Integration

This script tests your Retool workflow configuration by sending a test approval request.
"""
import os
import sys
from dotenv import load_dotenv
from integrations.retool import RetoolClient

# Load environment variables
load_dotenv()

def test_retool_workflow():
    """Test Retool workflow integration."""
    
    print("\n" + "="*70)
    print("🧪 RETOOL WORKFLOW INTEGRATION TEST")
    print("="*70 + "\n")
    
    # Check configuration
    webhook_url = os.getenv("RETOOL_WEBHOOK_URL")
    api_key = os.getenv("RETOOL_API_KEY")
    
    if webhook_url:
        print(f"✅ Found RETOOL_WEBHOOK_URL")
        print(f"   {webhook_url[:50]}...\n")
    elif api_key:
        print(f"✅ Found RETOOL_API_KEY")
        print(f"   Using API key authentication\n")
    else:
        print("⚠️  No Retool configuration found!")
        print("\nTo configure Retool:")
        print("1. Create a workflow in Retool (see dashboard/RETOOL_WORKFLOW_SETUP.md)")
        print("2. Get the webhook URL or API key")
        print("3. Add to .env file:")
        print("   RETOOL_WEBHOOK_URL=https://api.retool.com/v1/workflows/...")
        print("\nRunning in demo mode (will simulate)...\n")
    
    # Create test data
    test_incident_id = "inc-test-" + str(os.urandom(4).hex())
    test_mitigation = {
        "type": "rollback",
        "description": "Test rollback mitigation from test script",
        "parameters": {
            "target_version": "v1.2.2",
            "current_version": "v1.2.3"
        },
        "risk_level": "medium"
    }
    
    print(f"📋 Test Data:")
    print(f"   Incident ID: {test_incident_id}")
    print(f"   Mitigation Type: {test_mitigation['type']}")
    print(f"   Risk Level: {test_mitigation['risk_level']}\n")
    
    # Test the integration
    client = RetoolClient()
    success = client.send_approval_request(test_incident_id, test_mitigation)
    
    # Report results
    print("\n" + "="*70)
    if success and (webhook_url or api_key):
        print("✅ TEST SUCCESSFUL!")
        print("="*70)
        print("\n🎉 Next Steps:")
        print("1. Open Retool → Workflows")
        print("2. Find your workflow")
        print("3. Click 'Runs' tab")
        print(f"4. You should see a run for incident: {test_incident_id}")
        print("\nYour Retool integration is working! 🚀\n")
    elif success:
        print("✅ TEST COMPLETED (Demo Mode)")
        print("="*70)
        print("\n💡 To test with real Retool:")
        print("1. Follow: dashboard/RETOOL_WORKFLOW_SETUP.md")
        print("2. Add RETOOL_WEBHOOK_URL to .env")
        print("3. Run this test again\n")
    else:
        print("❌ TEST FAILED")
        print("="*70)
        print("\n🔍 Troubleshooting:")
        print("1. Check your .env file has correct RETOOL_WEBHOOK_URL")
        print("2. Verify workflow is deployed in Retool")
        print("3. Check the error messages above")
        print("4. See: dashboard/RETOOL_WORKFLOW_SETUP.md\n")
    
    return success


if __name__ == "__main__":
    try:
        success = test_retool_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nSee dashboard/RETOOL_WORKFLOW_SETUP.md for help\n")
        sys.exit(1)

