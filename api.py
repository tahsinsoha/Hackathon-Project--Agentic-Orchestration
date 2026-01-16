"""FastAPI REST API for Incident Autopilot."""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os

from core.models import Incident, AgentStage
from core.state import incident_store
from core.pipeline import IncidentPipeline
from simulator.scenarios import IncidentSimulator

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
        with open(dashboard_path, "r") as f:
            return HTMLResponse(content=f.read())
    return {"message": "Incident Autopilot API", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "incident-autopilot"}


@app.post("/api/incidents/simulate")
async def simulate_incident(
    incident_type: Optional[str] = None,
    auto_approve: bool = True,
    background_tasks: BackgroundTasks = None
):
    """Simulate and process an incident.
    
    Args:
        incident_type: Type of incident to simulate (latency_spike, error_rate, etc.)
        auto_approve: Whether to auto-approve mitigations
    """
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
    """Approve a proposed mitigation."""
    incident = incident_store.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if not incident.proposed_mitigation:
        raise HTTPException(status_code=400, detail="No mitigation proposed")
    
    incident.mitigation_approved = True
    incident_store.update_incident(incident_id, incident)
    
    return {
        "incident_id": incident_id,
        "status": "approved",
        "mitigation": incident.proposed_mitigation.dict()
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


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("INCIDENT_AUTOPILOT_PORT", 8000))
    print(f"\n🚀 Starting Incident Autopilot on http://localhost:{port}")
    print(f"📊 Dashboard: http://localhost:{port}")
    print(f"📚 API Docs: http://localhost:{port}/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=port)

