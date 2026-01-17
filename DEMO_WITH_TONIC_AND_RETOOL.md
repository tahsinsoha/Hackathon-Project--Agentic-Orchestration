# 🎬 Complete Demo: Tonic Synthetic Data → Retool Workflow

This guide shows you how to run a complete demo where:
1. **Tonic** generates realistic incident data (synthetic data)
2. **Multi-agent pipeline** processes the incident
3. **Retool Workflow** gets triggered for approval
4. You see everything in action!

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Set Up Retool Workflow (2 minutes)

**Create the workflow:**

1. Go to https://retool.com → Sign up (free)
2. Click **Workflows** in left sidebar
3. Click **Create New** → **Blank Workflow**
4. Name it: `incident-approval-workflow`
5. Click **Start with trigger** → Select **Webhook**
6. **Copy the webhook URL** (it looks like):
   ```
   https://api.retool.com/v1/workflows/wf_xxxxx/startTrigger?token=xxxxx
   ```

**Add a simple action (optional but impressive):**

7. Click the **+** button to add a block
8. Choose **JavaScript Code**
9. Add this code:
   ```javascript
   console.log("Incident approval request received!");
   console.log("Incident ID:", {{ trigger.data.incident_id }});
   console.log("Mitigation Type:", {{ trigger.data.mitigation_type }});
   console.log("Risk Level:", {{ trigger.data.risk_level }});
   
   return {
     status: "received",
     incident_id: {{ trigger.data.incident_id }},
     timestamp: new Date().toISOString()
   };
   ```
10. Click **Deploy** (top right)

---

### Step 2: Configure Your App (30 seconds)

Create or edit `.env` file in your project root:

```bash
# Retool Workflow Configuration
RETOOL_WEBHOOK_URL=YOUR_WEBHOOK_URL_HERE

# Tonic (Optional - works without it using local generation)
TONIC_API_KEY=your_tonic_api_key_here

# OpenAI (Required for agents)
OPENAI_API_KEY=your_openai_api_key_here
```

**Replace** `YOUR_WEBHOOK_URL_HERE` with the webhook URL you copied from Retool.

---

### Step 3: Test the Setup (30 seconds)

```bash
# Test that Retool workflow is reachable
python test_retool_workflow.py
```

You should see:
```
✅ Workflow triggered successfully!
🎉 Check Retool Workflows dashboard for the run
```

Open Retool → Workflows → Your workflow → **Runs tab** → You'll see the test run! 🎉

---

### Step 4: Run the Full Demo (2 minutes)

**Terminal 1 - Run the incident simulation:**

```bash
python main.py --mode demo --incident-type latency_spike
```

**What happens:**
1. ✅ **Tonic** generates realistic metrics (or uses local fallback)
2. ✅ **Scout agent** detects the anomaly
3. ✅ **Triage agent** classifies the incident
4. ✅ **Hypothesis agent** forms theories
5. ✅ **Experiment agent** validates the hypothesis
6. ✅ **Executor agent** proposes mitigation → **Triggers Retool Workflow!** 🚀
7. ✅ **Postcheck agent** verifies the fix

**Watch for this output:**

```
======================================================================
   ⚡ RETOOL WORKFLOW - Triggering via Webhook
======================================================================
   🎯 Incident ID: inc-20260116-123456
   📋 Mitigation Type: rollback
   🔍 Risk Level: medium
   🌐 Webhook: https://api.retool.com/v1/workflows/...
   ✅ Workflow triggered successfully!
   🎉 Check Retool Workflows dashboard for the run
======================================================================
```

**Terminal 2 - Verify in Retool:**

Go back to Retool:
- Workflows → Your workflow → **Runs** tab
- You'll see a new run with the incident data!
- Click on it to see all the details

---

## 🎯 Different Incident Types

Try different scenarios to see various mitigations:

```bash
# Latency spike (triggers rollback)
python main.py --mode demo --incident-type latency_spike

# Error rate spike (triggers scaling)
python main.py --mode demo --incident-type error_rate

# Resource saturation (triggers resource scaling)
python main.py --mode demo --incident-type resource_saturation

# Queue depth explosion (triggers consumer scaling)
python main.py --mode demo --incident-type queue_depth
```

Each will trigger the Retool workflow with different parameters!

---

## 📊 View the Dashboard While Running

**Option 1: HTML Dashboard (Built-in)**

Terminal 1:
```bash
python main.py --mode server
```

Browser:
```
http://localhost:8000
```

Terminal 2:
```bash
# Trigger incidents from another terminal
python simulate_incident.py --type latency_spike
python simulate_incident.py --type error_rate
```

**Option 2: Retool Dashboard**

See `dashboard/RETOOL_SETUP.md` for importing the full dashboard.

---

## 🔍 What's Happening Behind the Scenes

### Tonic Integration

When the incident simulator runs:

```python
# simulator/scenarios.py
self.tonic = TonicClient()

# Generates realistic metrics
tonic_data = self.tonic.generate_metrics_dataset("latency_spike", duration_minutes=60)
```

**With Tonic API Key:**
- Calls real Tonic API for synthetic data
- Gets realistic time-series metrics
- Professional-grade test data

**Without Tonic API Key (Fallback):**
- Uses local generation
- Still realistic enough for demos
- No external dependencies

Output:
```
   ℹ️ [TONIC] No API key, using local synthetic data generation
```

or

```
   ✅ [TONIC] Successfully generated data via REAL Tonic API!
```

### Retool Workflow Trigger

When Executor agent proposes mitigation:

```python
# agents/executor.py
success = self.retool.send_approval_request(
    incident.id,
    mitigation_plan
)
```

This sends an HTTP POST to your Retool webhook:

```json
{
  "incident_id": "inc-20260116-123456",
  "mitigation_type": "rollback",
  "description": "Roll back to previous stable version v1.2.2",
  "risk_level": "medium",
  "timestamp": "2026-01-16T12:34:56Z"
}
```

---

## 🎬 Complete Demo Script for Presentation

**Setup (before demo):**
```bash
# Terminal 1: Start the server
python main.py --mode server

# Browser: Open dashboard
open http://localhost:8000

# Browser 2: Open Retool Workflows
# Go to your workflow's Runs page
```

**During Demo (2 minutes):**

**Say:** "Let me show you our AI-powered incident response system with enterprise integrations."

**Terminal 2:**
```bash
python main.py --mode demo --incident-type latency_spike
```

**Point out as it runs:**

1. **Tonic Data Generation** (5 seconds)
   - "We use Tonic AI to generate realistic incident scenarios"
   - Show the metrics being generated

2. **Multi-Agent Pipeline** (30-60 seconds)
   - "Six AI agents work together: Scout, Triage, Hypothesis, Experiment, Executor, Postcheck"
   - Watch the agents execute in sequence

3. **Retool Workflow Trigger** (instant)
   - **Highlight the banner!**
   - "When the Executor proposes a mitigation, it triggers our Retool approval workflow"
   - **Switch to Retool browser tab**
   - **Show the new run that just appeared!**
   - "Here's the workflow run with all the incident data"

4. **Dashboard View** (10 seconds)
   - Switch to http://localhost:8000
   - "We can monitor all incidents in our real-time dashboard"
   - Show the statistics and timeline

**Closing:**
"This demonstrates how AI agents can integrate with enterprise tools like Retool and use synthetic data from Tonic to ensure reliability."

---

## 🔧 Troubleshooting

### Retool Workflow Not Triggering

**Check 1: Webhook URL**
```bash
# Test manually with curl
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "test-123",
    "mitigation_type": "rollback",
    "risk_level": "medium"
  }'
```

Check Retool → Workflows → Runs. Should see a new run.

**Check 2: .env file**
```bash
cat .env | grep RETOOL_WEBHOOK_URL
```

Should show your URL. If not, add it.

**Check 3: Test script**
```bash
python test_retool_workflow.py
```

This will show you exactly what's wrong.

### Tonic Not Working

Don't worry! The system works perfectly without Tonic API access:

- Falls back to local synthetic data generation
- Still produces realistic metrics
- No degradation in demo quality

To use real Tonic API:
1. Sign up at https://tonic.ai
2. Get your API key
3. Add to `.env`: `TONIC_API_KEY=your_key_here`

### No Incident Output

**Check OpenAI API Key:**
```bash
cat .env | grep OPENAI_API_KEY
```

The agents need this to work.

**Activate virtual environment:**
```bash
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate  # On Windows
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

---

## 📚 Advanced Usage

### Auto-Approve vs Manual Approval

**Auto-approve (Demo mode - default):**
```bash
python main.py --mode demo --incident-type latency_spike
# Automatically approves mitigations after triggering Retool
```

**Manual approval (Production simulation):**
```python
# In main.py, change auto_approve=False
result = await pipeline.run(
    incident,
    current_metrics,
    baseline_metrics,
    auto_approve=False  # Wait for human approval
)
```

### View All Past Incidents

**Via API:**
```bash
# Start server
python main.py --mode server

# In another terminal
curl http://localhost:8000/api/incidents
```

**Via Dashboard:**
```
http://localhost:8000
```

### Custom Incident Scenarios

Create your own in `simulator/scenarios.py`:

```python
def _generate_custom_scenario(self):
    """Generate your custom incident."""
    incident = Incident(
        id=f"inc-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        service_name="your-service",
        severity=IncidentSeverity.HIGH,
    )
    
    # Your custom metrics
    current_metrics = {
        "latency_p99": 8000,
        "error_rate": 25.0,
        # ... more metrics
    }
    
    baseline_metrics = {
        "latency_p99": 400,
        "error_rate": 0.5,
        # ... baseline values
    }
    
    return incident, current_metrics, baseline_metrics
```

---

## ✅ Success Checklist

Before your demo:
- [ ] Retool workflow created and deployed
- [ ] Webhook URL copied to `.env` file
- [ ] Test script passed: `python test_retool_workflow.py`
- [ ] Can see test run in Retool Workflows
- [ ] Full demo runs successfully
- [ ] Practiced the demo script
- [ ] Have both dashboard and Retool tabs open

During demo:
- [ ] Show the console output with Retool banner
- [ ] Switch to Retool to show the workflow run
- [ ] Explain the Tonic integration (even if using fallback)
- [ ] Show the agent pipeline working
- [ ] Demonstrate the dashboard

---

## 🎉 Why This Demo Wins

**Judges will see:**
1. ✅ **Real Tonic integration** - Synthetic data generation (or intelligent fallback)
2. ✅ **Real Retool integration** - Live workflow triggering
3. ✅ **Complete pipeline** - Six AI agents working together
4. ✅ **Production-ready** - Guardrails, validation, approval flows
5. ✅ **Visual proof** - Console output + Retool dashboard + Web UI

**This is NOT just logos slapped on!**  
**These are REAL, WORKING integrations!** 🚀

---

## 📞 Quick Reference

### Key Commands

```bash
# Test Retool
python test_retool_workflow.py

# Run demo
python main.py --mode demo --incident-type latency_spike

# Start server
python main.py --mode server

# Simulate from CLI
python simulate_incident.py --type error_rate
```

### Key Files

- **Retool Integration:** `integrations/retool.py`
- **Tonic Integration:** `integrations/tonic.py`
- **Scenario Generator:** `simulator/scenarios.py`
- **Main Pipeline:** `core/pipeline.py`
- **Config:** `.env`

### Key URLs

- Dashboard: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Retool: https://retool.com

---

**You're ready to show a complete demo with real integrations! 🎯**

Run it, show it, and impress! 💪

