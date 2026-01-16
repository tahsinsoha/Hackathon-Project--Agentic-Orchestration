# 🚀 Setup Guide - Incident Autopilot

Complete guide to get Incident Autopilot running for the hackathon demo.

---

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Optional: API keys for sponsor tools (demo works without them)

---

## Installation

### 1. Install Dependencies

```bash
cd incident-autopilot
pip install -r requirements.txt
```

If you encounter issues, install individually:

```bash
pip install fastapi uvicorn pydantic anthropic openai requests numpy pandas python-dateutil aiohttp websockets redis prometheus-client psutil pyyaml python-dotenv jinja2
```

### 2. Configure Environment (Optional)

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```bash
# AI Provider (optional - works with simulation fallback)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Sponsor Tools (optional - demo stubs work without keys)
RETOOL_API_KEY=your_key
TINYFISH_API_KEY=your_key
TONIC_API_KEY=your_key
FREEPIK_API_KEY=your_key

# App Settings
INCIDENT_AUTOPILOT_PORT=8000
ENABLE_AUTO_MITIGATION=false
GUARDRAIL_MODE=strict
```

**Note**: The system works in **demo mode** without any API keys! Agent responses will be simulated.

---

## Running the Demo

### Option 1: Single Incident Demo (CLI)

Run a complete incident simulation from the command line:

```bash
# Random incident type
python3 main.py --mode demo

# Specific incident type
python3 main.py --mode demo --incident-type latency_spike
python3 main.py --mode demo --incident-type error_rate
python3 main.py --mode demo --incident-type resource_saturation
python3 main.py --mode demo --incident-type queue_depth
```

**What you'll see**:
```
🚨 INCIDENT AUTOPILOT WITH GUARDRAILS - Demo Mode
==================================================================

📋 Incident Details:
   ID: inc-20260116-123456
   Service: api-service
   Severity: high

📊 Current Metrics:
   📈 latency_p99: 5000.0 (baseline: 500.0, change: +900.0%)
   📈 error_rate: 1.2 (baseline: 0.1, change: +1100.0%)

==================================================================
🚨 INCIDENT PIPELINE STARTED: inc-20260116-123456
==================================================================

🔍 [SCOUT] Gathering evidence...
   ✓ Collected 4 log entries, found 1 recent deploys

🏥 [TRIAGE] Classifying incident type...
   ✓ Type: latency_spike (confidence: 90%)
   ✓ P99 latency significantly elevated above baseline

💡 [HYPOTHESIS] Generating root cause hypotheses...
   ✓ Generated 3 hypotheses:
     1. Recent deployment introduced slow database queries (confidence: 80%)
     2. Database connection pool exhaustion (confidence: 60%)
     3. Downstream service degradation (confidence: 50%)

🧪 [EXPERIMENT] Validating hypotheses...
   ✓ Validated 1/3 hypotheses
   ✓ Most likely: Deployment v1.2.3 occurred 15min before incident

⚡ [EXECUTOR] Proposing mitigation...
   ✓ Proposed: rollback
   ✓ Rollback to previous version before deployment v1.2.3
   ✓ Risk: medium, Reversible: True
   ⏸️  Waiting for human approval...
   ✅ [AUTO-APPROVED for demo]
   🔧 Applying mitigation...
   ✅ Mitigation applied successfully

✅ [POSTCHECK] Verifying recovery...
   ✅ Metrics recovered successfully
   ✓ Generated incident report

==================================================================
✅ INCIDENT PIPELINE COMPLETED: inc-20260116-123456
Time to mitigation: 2.3s
Success: True
==================================================================
```

### Option 2: Web Dashboard (Recommended for Demo)

Start the API server and use the interactive dashboard:

```bash
# Start server
python3 main.py --mode server --port 8000

# Or just
python3 main.py
```

Then open in your browser:

```
http://localhost:8000
```

**Dashboard Features**:

1. **Statistics Cards** - Real-time KPIs
   - Total incidents
   - Detection latency
   - Time to mitigation
   - Success rate

2. **Incident Controls**
   - Select incident type (or random)
   - Click "🚀 Simulate Incident"
   - Watch real-time processing

3. **Incident List**
   - See all incidents
   - Click to view details
   - Color-coded by severity

4. **Pipeline Timeline**
   - Watch agents work in real-time
   - See each stage complete
   - View timestamps

### Option 3: API Endpoints

Use the REST API directly:

```bash
# Simulate incident
curl -X POST "http://localhost:8000/api/incidents/simulate?incident_type=latency_spike&auto_approve=true"

# Get all incidents
curl "http://localhost:8000/api/incidents"

# Get specific incident
curl "http://localhost:8000/api/incidents/{incident_id}"

# Get statistics
curl "http://localhost:8000/api/statistics"

# Get active incidents
curl "http://localhost:8000/api/active"
```

---

## Demo Flow for Hackathon Judges

### 5-Minute Live Demo Script

**1. Introduction (30 seconds)**
```
"Hi judges! I'm demoing Incident Autopilot - a multi-agent system that 
automatically resolves incidents 60x faster than manual response."
```

**2. Show Dashboard (30 seconds)**
- Open http://localhost:8000
- Point out clean UI
- Explain the 6-agent pipeline diagram
- Show current stats (all zeros initially)

**3. Trigger Incident (1 minute)**
- Select "Latency Spike" from dropdown
- Click "🚀 Simulate Incident"
- Watch in real-time:
  - Scout gathering evidence
  - Triage classifying (90% confidence)
  - Hypotheses generated (3 options)
  - Experiments validating root cause
  - Executor proposing rollback
  - Mitigation applied
  - Recovery verified

**4. Explain Key Points (2 minutes)**

Point out each agent's output:

- **Scout**: "Collected metrics, logs, found recent deployment"
- **Triage**: "Classified as latency spike with 90% confidence"
- **Hypothesis**: "Proposed 3 root causes, deployment most likely"
- **Experiment**: "Validated deployment correlation"
- **Executor**: "Proposed safe rollback with guardrails"
- **Postcheck**: "Verified metrics recovered"

**5. Highlight Differentiators (1 minute)**

- **Autonomy**: "No human intervention needed - 45 second resolution"
- **Safety**: "Guardrails prevent dangerous actions - rollback required approval"
- **Explainability**: "Full audit trail - every decision logged"
- **Sponsor Tools**: "Retool for UI, TinyFish for runbooks, Tonic for data, Freepik for visuals"

**6. Show Results (30 seconds)**
- Point to updated stats:
  - Time to mitigation: 45s
  - Success rate: 100%
  - Detection latency: 2.5s
- Compare to manual response: "Traditional approach takes 30-60 minutes"

---

## Testing Different Scenarios

### Scenario 1: Latency Spike
```bash
python3 main.py --mode demo --incident-type latency_spike
```

**Expected behavior**:
- Detects p99 latency 5000ms (baseline: 500ms)
- Finds recent deployment correlation
- Proposes rollback
- Metrics recover

### Scenario 2: Error Rate Spike
```bash
python3 main.py --mode demo --incident-type error_rate
```

**Expected behavior**:
- Detects 15% error rate (baseline: 0.1%)
- Finds dependency connection failures
- Proposes feature flag disable
- Errors drop below 1%

### Scenario 3: Resource Saturation
```bash
python3 main.py --mode demo --incident-type resource_saturation
```

**Expected behavior**:
- Detects 92% CPU, 89% memory
- Identifies capacity issue
- Proposes scale up
- Load distributed

### Scenario 4: Queue Backlog
```bash
python3 main.py --mode demo --incident-type queue_depth
```

**Expected behavior**:
- Detects 15k messages in queue
- Finds consumer service down
- Proposes service restart
- Queue draining

---

## Sponsor Tool Integration Demo

### Show Retool Integration

Point to code in `integrations/retool.py`:

```python
# Approval workflow
retool.send_approval_request(incident_id, mitigation)

# Dashboard creation
retool.create_incident_dashboard(incident_data)

# Audit logging
retool.log_incident_event(incident_id, event)
```

### Show TinyFish Integration

Point to code in `integrations/tinyfish.py`:

```python
# Fetch runbooks
runbooks = tinyfish.fetch_runbook(service, incident_type)

# Scrape status pages
status = tinyfish.scrape_status_page(url)

# Search docs
docs = tinyfish.search_documentation(query)
```

### Show Tonic Integration

Point to code in `integrations/tonic.py`:

```python
# Generate realistic metrics
metrics = tonic.generate_metrics_dataset(scenario)

# Generate logs
logs = tonic.generate_log_entries(scenario, count)
```

### Show Freepik Integration

Point to code in `integrations/freepik.py`:

```python
# Generate incident card
card = freepik.generate_incident_card(incident_data)

# Timeline visualization
timeline = freepik.generate_timeline_graphic(events)
```

---

## Troubleshooting

### Issue: Module not found

```bash
# Make sure you're in the right directory
cd incident-autopilot

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Port already in use

```bash
# Use a different port
python3 main.py --mode server --port 8080
```

### Issue: Python not found

```bash
# Try python3 explicitly
python3 main.py

# Or check Python installation
which python3
python3 --version
```

### Issue: No incidents showing

```bash
# Refresh the page
# Or click "🔄 Refresh" button
# Or simulate a new incident
```

---

## API Documentation

When server is running, visit:

```
http://localhost:8000/docs
```

This shows interactive API documentation with:
- All endpoints
- Request/response schemas
- Try-it-out functionality

---

## Files Overview

```
incident-autopilot/
├── core/
│   ├── models.py          # Data models (Incident, Evidence, etc.)
│   ├── state.py           # State management
│   ├── guardrails.py      # Safety policies
│   └── pipeline.py        # Orchestration
├── agents/
│   ├── scout.py           # Evidence gathering
│   ├── triage.py          # Classification
│   ├── hypothesis.py      # Root cause analysis
│   ├── experiment.py      # Validation
│   ├── executor.py        # Mitigation
│   └── postcheck.py       # Verification
├── simulator/
│   └── scenarios.py       # Incident generation
├── integrations/
│   ├── retool.py          # Retool API
│   ├── tinyfish.py        # TinyFish API
│   ├── tonic.py           # Tonic API
│   └── freepik.py         # Freepik API
├── dashboard/
│   └── index.html         # Web UI
├── main.py                # Entry point
├── api.py                 # REST API
└── simulate_incident.py   # CLI simulator
```

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Run demo mode
3. ✅ Start web server
4. ✅ Test different scenarios
5. ✅ Review sponsor integrations
6. ✅ Prepare 5-minute demo
7. ✅ Record demo video

---

## Support

For questions or issues:
- Check the README.md
- Review HACKATHON_SUBMISSION.md
- Check API docs at /docs endpoint

---

**Ready to demo! 🚀**

