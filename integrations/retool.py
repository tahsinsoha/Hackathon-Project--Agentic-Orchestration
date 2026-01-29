"""Retool integration for Incident Control Tower UI.

Retool provides the enterprise UI layer for:
- Incident alerts and real-time monitoring
- Approval workflows for mitigations
- Run history and audit logs
- Evidence visualization
- Real-time dashboard with statistics and timeline
"""
import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime


class RetoolClient:
    """Client for Retool API integration."""
    
    def __init__(self, api_key: str = None, workspace_url: str = None):
        self.api_key = api_key or os.getenv("RETOOL_API_KEY", "")
        self.workspace_url = workspace_url or os.getenv("RETOOL_WORKSPACE_URL", "https://mycompany.retool.com")
        self.webhook_url = os.getenv("RETOOL_WEBHOOK_URL", "")
        self.base_url = "https://api.retool.com/v1"
    
    def create_incident_dashboard(self, incident_data: Dict[str, Any]) -> str:
        """Create a Retool dashboard for an incident.
        
        Args:
            incident_data: Incident details to display
            
        Returns:
            URL to the Retool dashboard
        """
        # In production, use Retool API to create/update dashboards
        # For demo, return mock URL
        return f"https://mycompany.retool.com/apps/incident-{incident_data['id']}"
    
    def send_approval_request(self, incident_id: str, mitigation: Dict[str, Any]) -> bool:
        """Send approval request to Retool Workflow.
        
        Args:
            incident_id: ID of the incident
            mitigation: Mitigation details requiring approval
            
        Returns:
            True if approval request was sent successfully
        """
        # Prepare the payload
        payload = {
            "incident_id": incident_id,
            "mitigation_type": mitigation.get('type', 'unknown'),
            "description": mitigation.get('description', ''),
            "risk_level": mitigation.get('risk_level', 'unknown'),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Try webhook URL first (easiest setup)
        if self.webhook_url:
            print("\n" + "="*70)
            print("   ⚡ RETOOL WORKFLOW - Triggering via Webhook")
            print("="*70)
            print(f"   🎯 Incident ID: {incident_id}")
            print(f"   📋 Mitigation Type: {mitigation.get('type', 'unknown')}")
            print(f"   🔍 Risk Level: {mitigation.get('risk_level', 'unknown')}")
            print(f"   🌐 Webhook: {self.webhook_url[:50]}...")
            
            try:
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10
                )
                
                if response.status_code in [200, 201, 202]:
                    print(f"Workflow triggered successfully!")
                    print(f"Check Retool Workflows dashboard for the run")
                    print("="*70 + "\n")
                    return True
                else:
                    print(f"Webhook returned status {response.status_code}")
                    print("="*70 + "\n")
                    return False
                    
            except Exception as e:
                print(f"Webhook call failed: {e}")
                print("="*70 + "\n")
                return False
        
        # If no webhook, check for API key
        if not self.api_key:
            print("\n" + "="*70)
            print("   ⚡ RETOOL INTEGRATION - Approval Workflow (Demo Mode)")
            print("="*70)
            print(f"Incident ID: {incident_id}")
            print(f"Mitigation Type: {mitigation.get('type', 'unknown')}")
            print(f"Risk Level: {mitigation.get('risk_level', 'unknown')}")
            print(f"Mode: Demo (set RETOOL_WEBHOOK_URL or RETOOL_API_KEY)")
            print(f"Approval request simulated - would trigger Retool Workflow")
            print("="*70 + "\n")
            return True
        
        # Use API key method
        print("\n" + "="*70)
        print("   ⚡ RETOOL WORKFLOW - Triggering via API")
        print("="*70)
        print(f"Incident ID: {incident_id}")
        print(f"Mitigation Type: {mitigation.get('type', 'unknown')}")
        print(f"Risk Level: {mitigation.get('risk_level', 'unknown')}")
        print(f"Using API Key authentication")
        
        try:
            # Real Retool Workflows API call
            workflow_url = f"{self.base_url}/workflows/trigger"
            workflow_id = os.getenv("RETOOL_WORKFLOW_ID", "incident-approval")
            
            response = requests.post(
                workflow_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "workflowId": workflow_id,
                    "data": payload
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Workflow triggered successfully via API!")
                print(f"Check Retool Workflows dashboard for the run")
                print("="*70 + "\n")
                return True
            else:
                print(f"API returned status {response.status_code}")
                print("="*70 + "\n")
                return False
                
        except Exception as e:
            print(f"API call failed: {e}")
            print("="*70 + "\n")
            return False
    
    
    def get_approval_status(self, incident_id: str) -> str:
        return "approved"  # Auto-approve for demo
    
    def push_dashboard_data(self, data_type: str, data: Dict[str, Any]) -> bool:
        if not self.api_key:
            print(f"[RETOOL] Dashboard data ready: {data_type}")
            return True
        
        try:
            # Push to Retool resource/query
            resource_url = f"{self.base_url}/resources/data"
            
            response = requests.post(
                resource_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "resource": f"incident_autopilot_{data_type}",
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat()
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"[RETOOL] Pushed {data_type} to dashboard")
                return True
            else:
                print(f"[RETOOL] Failed to push {data_type}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[RETOOL] Error pushing {data_type}: {e}")
            return False
    
    def get_dashboard_url(self, incident_id: Optional[str] = None) -> str:
        if incident_id:
            return f"{self.workspace_url}/apps/incident-autopilot?incidentId={incident_id}"
        return f"{self.workspace_url}/apps/incident-autopilot"
    
    def create_dashboard_resources(self) -> Dict[str, str]:
        """Generate configuration for Retool dashboard resources.
        
        Returns:
            Dictionary mapping resource names to their configurations
        """
        return {
            "incident_api": {
                "type": "restapi",
                "name": "Incident Autopilot API",
                "base_url": "http://localhost:8000/api",
                "endpoints": {
                    "statistics": "/statistics",
                    "incidents": "/incidents",
                    "incident_detail": "/incidents/{{incidentId}}",
                    "simulate": "/incidents/simulate"
                }
            },
            "statistics_query": {
                "type": "query",
                "resource": "incident_api",
                "method": "GET",
                "path": "/statistics",
                "run_when_page_loads": True,
                "refresh_interval": 5000
            },
            "incidents_query": {
                "type": "query",
                "resource": "incident_api",
                "method": "GET",
                "path": "/incidents",
                "run_when_page_loads": True,
                "refresh_interval": 5000
            }
        }

