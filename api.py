import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import time
import datetime
from fastapi import HTTPException
from core.models import Incident, AgentStage
from core.state import incident_store
from core.pipeline import IncidentPipeline
from simulator.scenarios import IncidentSimulator
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="Incident Autopilot API",
    description="Multi-agent incident response automation",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
pipeline = IncidentPipeline()
simulator = IncidentSimulator()


@app.get("/")
async def root():
    """Serve the dashboard."""
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard", "index.html")
    if os.path.exists(dashboard_path):
        with open(dashboard_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"message": "Incident Autopilot API", "docs": "/docs"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "incident-autopilot"}


@app.post("/api/incidents/simulate")
async def simulate_incident(
    incident_type: Optional[str] = None,
    auto_approve: bool = True,
    background_tasks: BackgroundTasks = None
):

    try:
        # Generate incident
        incident, current_metrics, baseline_metrics = simulator.generate_incident(incident_type)
        
        # Store incident
        incident_store.create_incident(incident)
        
        # Run pipeline in background
        background_tasks.add_task(
            pipeline.run,
            incident,
            current_metrics,
            baseline_metrics,
            auto_approve
        )
        
        return {
            "incident_id": incident.id,
            "service": incident.service_name,
            "status": "processing",
            "message": "Incident pipeline started"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/incidents")
async def list_incidents(limit: int = 50):
    """List recent incidents."""
    incidents = incident_store.list_incidents(limit)
    return {
        "incidents": [inc.dict() for inc in incidents],
        "count": len(incidents)
    }


@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get a specific incident."""
    incident = incident_store.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident.dict()


@app.get("/api/incidents/{incident_id}/summary")
async def get_incident_summary(incident_id: str):
    """Get incident summary/report."""
    incident = incident_store.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return {
        "incident_id": incident.id,
        "service": incident.service_name,
        "type": incident.incident_type.value,
        "stage": incident.stage.value,
        "summary": incident.incident_summary,
        "timeline": incident.timeline,
        "metrics": incident.metrics.dict()
    }

@app.post("/api/incidents/{incident_id}/approve")
async def approve_mitigation(incident_id: str):
    """Approve a proposed mitigation and APPLY it (real human-in-the-loop)."""
    incident = incident_store.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if not incident.proposed_mitigation:
        raise HTTPException(status_code=400, detail="No mitigation proposed")

    # If already applied, keep idempotent
    if incident.applied_mitigation:
        return {
            "incident_id": incident_id,
            "status": "already_applied",
            "mitigation": incident.applied_mitigation.dict(),
        }

    incident.mitigation_approved = True
    incident.add_timeline_event(
        "approval",
        "Human approved proposed mitigation",
        {"mitigation_type": incident.proposed_mitigation.type.value},
    )
    incident_store.update_incident(incident_id, incident)

    approved_at_ts = time.time()

    apply_result = await pipeline.executor.apply_mitigation(
        incident.proposed_mitigation,
        incident.service_name,
    )

    if not apply_result.get("success"):
        incident.stage = AgentStage.FAILED
        incident.add_timeline_event("executor", "Mitigation apply failed", apply_result)
        incident_store.update_incident(incident_id, incident)
        raise HTTPException(
            status_code=500,
            detail=apply_result.get("message", "Mitigation apply failed"),
        )

    # 3) Update incident state
    incident.applied_mitigation = incident.proposed_mitigation
    incident.stage = AgentStage.POSTCHECK

    start_ts = getattr(incident.metrics, "pipeline_start_ts", 0.0) or approved_at_ts
    if not incident.metrics.time_to_mitigation_seconds:
        incident.metrics.time_to_mitigation_seconds = max(0.0, time.time() - start_ts)

    incident.add_timeline_event(
        "executor",
        "Mitigation applied after human approval",
        {
            "mitigation_type": incident.applied_mitigation.type.value,
            "applied_at": apply_result.get("applied_at"),
            "time_to_mitigation": f"{incident.metrics.time_to_mitigation_seconds:.1f}s",
        },
    )
    incident_store.update_incident(incident_id, incident)

    context = {
        "incident": incident,
        "current_metrics": {},
        "baseline_metrics": {},
        "most_likely_cause": None,
    }

    incident = await pipeline._run_postcheck(incident, context)

    # Mark completion
    incident.stage = AgentStage.COMPLETED if incident.metrics_recovered else AgentStage.FAILED
    incident.end_time = datetime.datetime.utcnow()
    incident.metrics.mitigation_success = incident.metrics_recovered
    incident.add_timeline_event(
        "completed" if incident.metrics_recovered else "failed",
        "Incident completed after human approval"
        if incident.metrics_recovered
        else "Incident failed after human approval",
    )

    incident_store.update_incident(incident_id, incident)

    return {
        "incident_id": incident_id,
        "status": "applied" if incident.metrics_recovered else "applied_but_not_recovered",
        "approved": True,
        "applied_mitigation": incident.applied_mitigation.dict(),
        "metrics_recovered": incident.metrics_recovered,
    }



@app.get("/api/statistics")
async def get_statistics():
    """Get overall system statistics."""
    stats = incident_store.get_statistics()
    return stats


@app.get("/api/active")
async def get_active_incidents():
    """Get all active incidents."""
    incidents = incident_store.get_active_incidents()
    return {
        "incidents": [inc.dict() for inc in incidents],
        "count": len(incidents)
    }


@app.get("/api/dashboard/retool")
async def get_retool_info():
    """Get Retool dashboard integration information."""
    return {
        "dashboard_name": "Incident Autopilot Dashboard",
        "description": "Enterprise control tower built with Retool",
        "api_base_url": f"http://localhost:{os.getenv('INCIDENT_AUTOPILOT_PORT', 8000)}/api",
        "features": [
            "Real-time incident monitoring",
            "Statistics dashboard with key metrics",
            "Interactive incident timeline",
            "One-click incident simulation",
            "Approval workflows",
            "Auto-refresh every 5 seconds",
            "Sortable and searchable incident table",
            "Color-coded severity and status badges"
        ],
        "endpoints": {
            "statistics": "/api/statistics",
            "incidents": "/api/incidents",
            "incident_detail": "/api/incidents/{incident_id}",
            "simulate": "/api/incidents/simulate",
            "approve": "/api/incidents/{incident_id}/approve"
        },
        "setup_guide": "/dashboard/RETOOL_SETUP.md",
        "configuration_file": "/dashboard/retool_dashboard.json"
    }


@app.get("/api/retool/config")
async def get_retool_config():
    """Get Retool dashboard configuration JSON."""
    import json
    config_path = os.path.join(os.path.dirname(__file__), "dashboard", "retool_dashboard.json")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load config: {str(e)}")


@app.post("/api/retool/import")
async def import_to_retool():
    """Generate import instructions and URL for Retool dashboard."""
    from integrations.retool import RetoolClient
    import json
    
    # Load the dashboard config
    config_path = os.path.join(os.path.dirname(__file__), "dashboard", "retool_dashboard.json")
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Try to use Retool API if credentials available
    client = RetoolClient()
    
    # Build the response with instructions
    response = {
        "status": "ready_to_import",
        "dashboard_config": config,
        "instructions": {
            "step_1": "Go to your Retool workspace",
            "step_2": "Click 'Create new' → 'From JSON/YAML'",
            "step_3": "Upload the downloaded JSON file",
            "step_4": "Update API base URL to your server",
            "step_5": "Click 'Release' to publish"
        },
        "quick_links": {
            "retool_apps": "https://retool.com/apps",
            "retool_new_app": "https://retool.com/editor/new",
            "docs": "http://localhost:8000/dashboard/RETOOL_SETUP.md"
        },
        "api_base_url": f"http://localhost:{os.getenv('INCIDENT_AUTOPILOT_PORT', 8000)}/api"
    }
    
    return response


@app.post("/api/demo/tonic-retool")
async def demo_tonic_retool(incident_type: Optional[str] = None):
    """Run Tonic → Retool demo without OpenAI.
    
    Args:
        incident_type: Type of incident (latency_spike, error_rate, etc.)
    
    Returns:
        Demo results with Tonic data and Retool trigger status
    """
    from integrations.tonic import TonicClient
    from integrations.retool import RetoolClient
    from datetime import datetime
    
    try:
        # Initialize clients
        tonic = TonicClient()
        retool = RetoolClient()
        
        # Generate incident with Tonic data
        incident, current_metrics, baseline_metrics = simulator.generate_incident(incident_type)
        
        # Store the incident
        incident_store.create_incident(incident)
        
        # Generate time-series data from Tonic
        metrics_data = tonic.generate_metrics_dataset(
            incident_type or "latency_spike",
            duration_minutes=5
        )
        
        # Generate log samples
        logs = tonic.generate_log_entries(incident_type or "latency_spike", count=5)
        
        # Create mitigation plan
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
        
        mitigation = mitigation_plans.get(
            incident_type or "latency_spike",
            mitigation_plans["latency_spike"]
        )
        
        # Trigger Retool workflow
        retool_success = retool.send_approval_request(incident.id, mitigation)
        
        # Calculate metrics changes
        metrics_comparison = []
        for key in ['latency_p99', 'error_rate', 'cpu_usage', 'memory_usage']:
            current = current_metrics.get(key, 0)
            baseline = baseline_metrics.get(key, 0)
            if baseline > 0:
                change_pct = ((current - baseline) / baseline * 100)
                metrics_comparison.append({
                    "metric": key,
                    "current": round(current, 2),
                    "baseline": round(baseline, 2),
                    "change_percent": round(change_pct, 1),
                    "status": "critical" if abs(change_pct) > 50 else "warning" if abs(change_pct) > 20 else "normal"
                })
        
        # Return comprehensive results
        return {
            "success": True,
            "incident": {
                "id": incident.id,
                "service": incident.service_name,
                "severity": incident.severity.value,
                "timestamp": incident.start_time.isoformat()
            },
            "tonic": {
                "status": "success",
                "metrics_generated": len(metrics_data),
                "logs_generated": len(logs),
                "sample_logs": logs[:3],
                "latest_metrics": metrics_data[-1] if metrics_data else {}
            },
            "metrics_comparison": metrics_comparison,
            "mitigation": mitigation,
            "retool": {
                "triggered": retool_success,
                "status": "success" if retool_success else "demo_mode",
                "message": "Workflow triggered successfully" if retool_success else "Demo mode (configure RETOOL_WEBHOOK_URL)"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("INCIDENT_AUTOPILOT_PORT", 8000))
    print(f"\nStarting Incident Autopilot on http://localhost:{port}")
    print(f"Dashboard: http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

