# 🚀 Quick Demo Reference Card

## ⚡ Super Quick Start (2 Minutes)

### 1. Set Up Retool Workflow
```
1. Go to retool.com → Workflows → Create New
2. Name: incident-approval-workflow
3. Trigger: Webhook
4. Copy webhook URL
5. Deploy
```

### 2. Configure .env
```bash
RETOOL_WEBHOOK_URL=https://api.retool.com/v1/workflows/...
OPENAI_API_KEY=your_openai_key
# TONIC_API_KEY=optional
```

### 3. Test
```bash
python test_retool_workflow.py
```

### 4. Run Demo
```bash
python demo_tonic_to_retool.py
```

---

## 📋 Demo Commands

### Interactive Demo (Recommended)
```bash
# Step-by-step with explanations
python demo_tonic_to_retool.py

# Specific incident type
python demo_tonic_to_retool.py --incident-type latency_spike
python demo_tonic_to_retool.py --incident-type error_rate
python demo_tonic_to_retool.py --incident-type resource_saturation
```

### Standard Demo
```bash
# Auto-running demo
python main.py --mode demo --incident-type latency_spike
```

### Server Mode + Dashboard
```bash
# Terminal 1: Start server
python main.py --mode server

# Browser: Open dashboard
http://localhost:8000

# Terminal 2: Trigger incidents
python simulate_incident.py --type error_rate
```

---

## 🔍 What to Watch For

### Console Output - Tonic
```
   ℹ️ [TONIC] No API key, using local synthetic data generation
```
or
```
   ✅ [TONIC] Successfully generated data via REAL Tonic API!
```

### Console Output - Retool (THE MONEY SHOT!)
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

### Retool Dashboard
```
1. Open retool.com
2. Go to Workflows
3. Click your workflow
4. Click "Runs" tab
5. See the new run with your incident data! 🎉
```

---

## 🎬 Presentation Script (2 Minutes)

**Before Demo:**
- Terminal ready with command
- Retool Workflows page open (Runs tab)
- Dashboard open: http://localhost:8000

**Say & Do:**

**Intro (15 sec):**
> "Our system uses Tonic for synthetic data and Retool for enterprise workflows. Let me show you."

**Run (10 sec):**
```bash
python demo_tonic_to_retool.py --incident-type latency_spike
```

**Point Out (1 min):**
1. Tonic generates realistic incident data (show console)
2. Six AI agents process it in sequence (watch them execute)
3. **Highlight Retool banner** when Executor runs
4. **Switch to Retool** → Show the new run that just appeared!
5. Click into run → Show incident data

**Wrap (15 sec):**
> "This is a complete integration: Tonic generates data, AI agents analyze it, and Retool manages the approval workflow. Everything is production-ready."

---

## 🔧 Troubleshooting

### Workflow Not Triggered
```bash
# Test manually
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Check Retool → Workflows → Runs
# Should see a new run
```

### Missing OpenAI Key
```bash
# Add to .env
echo "OPENAI_API_KEY=sk-..." >> .env
```

### Just Want to Test Data Generation
```bash
# Skip pipeline, just show Tonic data
python demo_tonic_to_retool.py --show-tonic-data --no-pipeline
```

---

## 📊 Different Incident Types

| Command | Mitigation | Impact |
|---------|-----------|--------|
| `latency_spike` | Rollback to v1.2.2 | High latency → Normal |
| `error_rate` | Scale up replicas | 15% errors → 0.1% |
| `resource_saturation` | Increase CPU/Memory | 92% CPU → 45% |
| `queue_depth` | Scale consumers | 15k queue → 200 |

---

## ✅ Pre-Demo Checklist

- [ ] Retool workflow created and deployed
- [ ] Webhook URL in .env file
- [ ] Test passed: `python test_retool_workflow.py`
- [ ] OpenAI API key configured
- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Practiced demo script
- [ ] Browser tabs ready (Retool Workflows)

---

## 🎯 Key Points to Emphasize

1. **Tonic Integration**
   - "We use Tonic AI to generate realistic synthetic data"
   - "Ensures reliable demos and testing"
   - Works with or without API key (fallback)

2. **Multi-Agent AI**
   - "Six specialized agents work together"
   - "Each has a specific role in incident response"
   - "Complete with guardrails and validation"

3. **Retool Integration** ⭐ HIGHLIGHT THIS
   - "When mitigation is proposed, Retool workflow triggers"
   - "Enterprise-ready approval process"
   - "Real-time workflow execution"
   - **SHOW THE RETOOL RUN!**

4. **Production Ready**
   - "Complete API and dashboard"
   - "Audit trails and metrics"
   - "Importable Retool configuration"

---

## 📞 Quick Links

- **Detailed Guide:** `DEMO_WITH_TONIC_AND_RETOOL.md`
- **Retool Setup:** `dashboard/RETOOL_WORKFLOW_SETUP.md`
- **Dashboard:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Test Script:** `test_retool_workflow.py`

---

**You got this! 🚀**

