# 🚨 Incident Autopilot with Guardrails

**Agentic Orchestration Hackathon 2026 Submission**

An intelligent multi-agent system that automatically detects, diagnoses, and mitigates incidents in microservices/K8s applications. This is a **shippable product**, not a demo.

## 🎯 What Makes This Unique

Most incident tools just **detect and page**. We close the entire loop:
**Detect → Diagnose → Mitigate → Verify → Summarize**

## 🤖 Multi-Agent Pipeline

```
📊 Anomaly Detected (metric threshold breach)
    ↓
🔍 Scout Agent (pulls evidence: metrics, logs, traces, deploys)
    ↓
🏥 Triage Agent (classifies: deploy regression vs infra vs dependency)
    ↓
💡 Hypothesis Agent (proposes 2-3 root causes + validation criteria)
    ↓
🧪 Experiment Agent (runs checks: canary comparison, correlation analysis)
    ↓
⚡ Executor Agent (applies guarded mitigation: rollback/scale/feature-flag)
    ↓
✅ Postcheck Agent (verifies recovery + generates incident report)
```

## 📊 What We Monitor

- **Latency spikes** (p95/p99)
- **Error rate increases**
- **CPU/Memory saturation**
- **Queue depth growth**

## 🛡️ Guardrails

- **Human approval** for critical actions
- **Reversible-only** mitigations
- **Impact limits** (max scale, canary %)
- **Circuit breakers** (auto-rollback if metrics worsen)
- **Audit trail** of all actions

## 🎨 Sponsor Tool Integration

| Tool | Purpose |
|------|---------|
| **Retool** | Incident Control Tower UI (alerts, approvals, history) |
| **TinyFish/Yutori** | Scout agent for pulling runbooks/docs from web |
| **Tonic** | Generate realistic incident datasets for reliable demos |
| **Freepik** | Generate incident card visuals & timeline graphics |
| **Cline** | Accelerate building simulator & agent orchestration |

## 📈 Metrics We Track

- **Detection Latency** (seconds from anomaly to alert)
- **Triage Accuracy** (% correct incident classification)
- **Time-to-Mitigation** (end-to-end resolution time)
- **Success Rate** (% of successful mitigations)
- **False Positive Rate** (incorrect alerts)

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Start backend server
python main.py

# Open dashboard
open http://localhost:8000

# Run simulation
python simulate_incident.py --type latency_spike
```

## 🏗️ Architecture

```
Backend (FastAPI + Multi-Agent System)
    ├── Incident Simulator (Tonic-powered)
    ├── Agent Orchestrator (LLM-based agents)
    ├── Guardrail Engine (safety policies)
    ├── Metrics Store (time-series data)
    └── Audit Log (full history)

Frontend (Retool + Web Dashboard)
    ├── Control Tower (alerts & approvals)
    ├── Evidence Viewer (metrics, logs, traces)
    ├── Timeline Visualizer (incident progression)
    └── Postmortem Generator (Freepik graphics)
```

## 🎮 Demo Scenarios

1. **Latency Spike**: p99 jumps from 200ms → 5s after deploy
2. **Error Rate Surge**: 0.1% → 15% errors from downstream dependency
3. **Memory Leak**: Gradual OOM leading to pod restarts
4. **Queue Backlog**: Message queue depth growing exponentially

## 📁 Project Structure

```
incident-autopilot/
├── agents/               # Individual agent implementations
│   ├── scout.py
│   ├── triage.py
│   ├── hypothesis.py
│   ├── experiment.py
│   ├── executor.py
│   └── postcheck.py
├── core/                 # Core orchestration
│   ├── pipeline.py
│   ├── guardrails.py
│   └── state.py
├── simulator/            # Incident generation
│   ├── metrics_generator.py
│   ├── log_generator.py
│   └── scenarios.py
├── integrations/         # Sponsor tool APIs
│   ├── retool.py
│   ├── tinyfish.py
│   ├── tonic.py
│   └── freepik.py
├── dashboard/            # Frontend
│   ├── index.html
│   ├── static/
│   └── retool_config.json
├── api.py               # FastAPI REST API
├── main.py              # Entry point
└── simulate_incident.py # CLI simulator
```

## 🏆 Hackathon Submission Highlights

- ✅ **3+ Sponsor Tools**: Retool, TinyFish, Tonic, Freepik
- ✅ **Full Autonomy**: End-to-end incident resolution with guardrails
- ✅ **Shippable Product**: Real API, UI, simulation, metrics
- ✅ **Multi-Agent**: Clear orchestration with specialized agents
- ✅ **Safety First**: Guardrails prevent dangerous actions

## 📺 Demo Video Script

1. Show dashboard with normal metrics
2. Trigger simulated incident (latency spike)
3. Watch agents work: Scout → Triage → Hypothesis → Experiment
4. Review proposed mitigation (rollback)
5. Approve action via Retool UI
6. See metrics recover in real-time
7. View generated incident report with timeline

## 🔮 Future Enhancements

- Integration with real K8s clusters (kubectl, ArgoCD)
- ML-based anomaly detection (not just thresholds)
- Multi-region incident coordination
- Slack/PagerDuty integration
- Custom runbook execution

