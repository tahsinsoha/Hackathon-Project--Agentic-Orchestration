# 🔄 Data Flow: Tonic → Multi-Agent → Retool

## Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         1. DATA GENERATION                          │
└─────────────────────────────────────────────────────────────────────┘

     🧪 Tonic AI
         │
         ├─→ Time-series metrics (latency, errors, CPU, etc.)
         ├─→ Log entries (realistic error messages)
         └─→ Incident metadata (service, region, severity)
         │
         ↓
    📊 Synthetic Incident Data
         │
         │  {
         │    "latency_p99": 5000ms,
         │    "error_rate": 15.8%,
         │    "cpu_usage": 92%,
         │    ...
         │  }
         │
         ↓

┌─────────────────────────────────────────────────────────────────────┐
│                    2. MULTI-AGENT PROCESSING                        │
└─────────────────────────────────────────────────────────────────────┘

    1️⃣  Scout Agent
         │
         ├─→ Detects: "Anomaly in latency_p99"
         ├─→ Severity: HIGH
         └─→ Evidence: Baseline 500ms → Current 5000ms
         │
         ↓

    2️⃣  Triage Agent  
         │
         ├─→ Classification: "Database Performance Issue"
         ├─→ Confidence: 0.92
         └─→ Impact: "Customer-facing latency"
         │
         ↓

    3️⃣  Hypothesis Agent
         │
         ├─→ Theory 1: "Recent deployment v1.2.3 introduced slow queries"
         ├─→ Theory 2: "Database connection pool exhausted"
         └─→ Theory 3: "Cache invalidation storm"
         │
         ↓

    4️⃣  Experiment Agent
         │
         ├─→ Validates: Theory 1 (deployment correlation)
         ├─→ Evidence: Timeline matches deployment
         └─→ Root Cause: "Code change in v1.2.3"
         │
         ↓

    5️⃣  Executor Agent  ⭐ TRIGGERS RETOOL HERE!
         │
         ├─→ Mitigation Plan: {
         │      "type": "rollback",
         │      "target_version": "v1.2.2",
         │      "risk_level": "medium"
         │   }
         │
         ├──────────────────────────────────────────┐
         │                                           │
         │                                           ↓
         │                               
         │                              ⚡ RETOOL WORKFLOW TRIGGER
         │                                           │
         │                              POST https://api.retool.com/...
         │                                           │
         │                              {
         │                                "incident_id": "inc-123",
         │                                "mitigation_type": "rollback",
         │                                "risk_level": "medium"
         │                              }
         │                                           │
         │                                           ↓
         │                              📋 Retool Workflow Executes
         │                                           │
         │                              • Sends approval request
         │                              • Notifies stakeholders
         │                              • Logs to audit trail
         │                              • Returns approval status
         │                                           │
         ├───────────────────────────────────────────┘
         │
         ├─→ Approval: Received
         └─→ Executes: Rollback to v1.2.2
         │
         ↓

    6️⃣  Postcheck Agent
         │
         ├─→ Verifies: Latency back to normal (498ms)
         ├─→ Confirms: Error rate reduced
         └─→ Status: ✅ Incident Resolved
         │
         ↓

┌─────────────────────────────────────────────────────────────────────┐
│                         3. RESULTS & STORAGE                        │
└─────────────────────────────────────────────────────────────────────┘

    📊 Incident Store
         │
         ├─→ Complete timeline
         ├─→ All agent actions
         ├─→ Metrics and evidence
         └─→ Resolution details
         │
         ↓

    🌐 Dashboard & API
         │
         ├─→ http://localhost:8000 (HTML Dashboard)
         ├─→ http://localhost:8000/api/incidents (REST API)
         └─→ Retool Dashboard (Enterprise UI)

```

---

## Timeline View

```
Time    Agent          Action                           Retool Activity
─────────────────────────────────────────────────────────────────────────
00:00   [START]        Incident detected
00:01   Scout          Analyzing metrics...
00:03   Scout          ✅ Anomaly confirmed
00:04   Triage         Classifying incident...
00:08   Triage         ✅ Type: Database Performance
00:09   Hypothesis     Forming theories...
00:15   Hypothesis     ✅ 3 theories generated
00:16   Experiment     Testing hypotheses...
00:25   Experiment     ✅ Root cause identified
00:26   Executor       Planning mitigation...
00:30   Executor       📤 Sending to Retool...        → Workflow triggered
00:31                                                  → Retool processing
00:32                                                  → Approval received ✅
00:33   Executor       ✅ Executing rollback
00:35   Postcheck      Verifying resolution...
00:40   Postcheck      ✅ Incident resolved
─────────────────────────────────────────────────────────────────────────
```

---

## Code Flow

### 1. Tonic Data Generation
```python
# integrations/tonic.py
tonic = TonicClient()
metrics_data = tonic.generate_metrics_dataset(
    scenario="latency_spike",
    duration_minutes=60
)
# Returns realistic time-series data
```

### 2. Incident Simulation
```python
# simulator/scenarios.py
simulator = IncidentSimulator()
incident, current_metrics, baseline_metrics = simulator.generate_incident(
    incident_type="latency_spike"
)
# Uses Tonic data under the hood
```

### 3. Pipeline Processing
```python
# core/pipeline.py
pipeline = IncidentPipeline()
result = await pipeline.run(
    incident,
    current_metrics,
    baseline_metrics,
    auto_approve=True
)
# Orchestrates all 6 agents
```

### 4. Retool Trigger (Inside Executor Agent)
```python
# agents/executor.py (line ~64)
success = self.retool.send_approval_request(
    incident.id,
    mitigation_plan
)
# ⚡ THIS IS WHERE RETOOL WORKFLOW GETS TRIGGERED!
```

### 5. Retool Integration
```python
# integrations/retool.py (line ~68)
response = requests.post(
    self.webhook_url,  # Retool webhook URL
    json={
        "incident_id": incident_id,
        "mitigation_type": mitigation.get('type'),
        "risk_level": mitigation.get('risk_level'),
        "timestamp": datetime.utcnow().isoformat()
    }
)
# Sends data to Retool Workflow
```

---

## File Structure

```
incident-autopilot/
│
├── integrations/
│   ├── tonic.py          ← 🧪 Tonic: Generates synthetic data
│   └── retool.py         ← ⚡ Retool: Triggers workflows
│
├── simulator/
│   └── scenarios.py      ← 📊 Uses Tonic to create incidents
│
├── agents/
│   ├── scout.py          ← 1️⃣  Detects anomalies
│   ├── triage.py         ← 2️⃣  Classifies incidents
│   ├── hypothesis.py     ← 3️⃣  Forms theories
│   ├── experiment.py     ← 4️⃣  Validates theories
│   ├── executor.py       ← 5️⃣  Executes mitigation + Triggers Retool
│   └── postcheck.py      ← 6️⃣  Verifies resolution
│
├── core/
│   └── pipeline.py       ← 🔄 Orchestrates all agents
│
├── main.py               ← 🚀 Main entry point
├── demo_tonic_to_retool.py  ← 🎬 Interactive demo script
│
└── .env                  ← ⚙️  Configuration
    ├── TONIC_API_KEY
    ├── RETOOL_WEBHOOK_URL
    └── OPENAI_API_KEY
```

---

## Configuration Flow

### Option 1: With Tonic API Key
```bash
# .env
TONIC_API_KEY=your_tonic_key
RETOOL_WEBHOOK_URL=https://api.retool.com/...
OPENAI_API_KEY=sk-...
```
**Result:**
- ✅ Real Tonic API calls for data
- ✅ Real Retool workflow triggers
- ✅ Complete integration demo

### Option 2: Without Tonic (Fallback)
```bash
# .env
# TONIC_API_KEY=not_set
RETOOL_WEBHOOK_URL=https://api.retool.com/...
OPENAI_API_KEY=sk-...
```
**Result:**
- ⚠️  Local synthetic data generation (still realistic!)
- ✅ Real Retool workflow triggers
- ✅ Still impressive demo

### Option 3: Demo Mode (Minimal)
```bash
# .env
OPENAI_API_KEY=sk-...
```
**Result:**
- ⚠️  Local synthetic data
- ⚠️  Retool workflow simulated
- ✅ All agents work, can show code

---

## Environment Variables Explained

```bash
# REQUIRED - Agents need this to work
OPENAI_API_KEY=sk-proj-...
# Get from: https://platform.openai.com/api-keys

# OPTIONAL - For real Tonic integration
TONIC_API_KEY=tonic_...
# Get from: https://tonic.ai
# Without it: Falls back to local generation

# OPTIONAL - For real Retool integration
RETOOL_WEBHOOK_URL=https://api.retool.com/v1/workflows/.../startTrigger?token=...
# Get from: Retool → Workflows → Create Workflow → Webhook Trigger
# Without it: Simulates workflow trigger

# ALTERNATIVE - For Retool API method
RETOOL_API_KEY=retool_...
RETOOL_WORKFLOW_ID=incident-approval
# Get from: Retool → Settings → API
```

---

## What Judges Will See

### 1. Console Output
```
   ✅ [TONIC] Successfully generated data via REAL Tonic API!
   
   [Scout Agent executing...]
   [Triage Agent executing...]
   ...
   
======================================================================
   ⚡ RETOOL WORKFLOW - Triggering via Webhook
======================================================================
   ✅ Workflow triggered successfully!
```

### 2. Retool Dashboard
- Open Retool Workflows
- Click "Runs" tab
- See the actual workflow run
- View incident data payload

### 3. Application Dashboard
- Real-time metrics
- Incident timeline
- Agent actions
- Resolution status

---

## Success Criteria

✅ **Tonic Integration Verified When:**
- Console shows Tonic API call
- OR shows fallback with realistic data
- Metrics look reasonable
- Timeline is coherent

✅ **Retool Integration Verified When:**
- Console shows webhook POST
- Retool Workflows shows new run
- Run contains incident data
- Timestamp matches execution

✅ **Complete System Verified When:**
- All 6 agents execute
- Mitigation is proposed
- Retool is triggered
- Incident is resolved
- Results are stored

---

## Common Questions

**Q: Do I need Tonic API key?**
A: No! It works perfectly with fallback. But having it shows real integration.

**Q: Do I need Retool webhook?**
A: No for basic demo. Yes to show real workflow execution in Retool dashboard.

**Q: What's the minimum config?**
A: Just `OPENAI_API_KEY` - everything else has fallbacks.

**Q: What's the full config?**
A: All three keys for complete real integrations.

**Q: How do I prove it's real?**
A: Show the Retool workflow run with incident data!

---

**This flow diagram shows EXACTLY how data moves through your system! 🎯**

