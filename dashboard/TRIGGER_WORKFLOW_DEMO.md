# 🎬 How to Trigger Retool Workflow in Your Demo

## 🎯 Goal
Show judges that your app **actually triggers** Retool Workflows when mitigations need approval.

---

## ⚡ QUICK DEMO (2 Options)

### Option 1: With Real Retool Workflow (5 min setup) ⭐ BEST

**This is the most impressive way to show Retool integration!**

#### Setup (Do this before demo):

1. **Create Retool Workflow** (2 minutes)
   - Go to https://retool.com → Workflows
   - Create new workflow named `incident-approval-workflow`
   - Select "Webhook" trigger
   - **Copy the webhook URL** (looks like: `https://api.retool.com/v1/workflows/.../startTrigger?...`)

2. **Configure Your App** (30 seconds)
   - Create `.env` file in project root:
   ```bash
   RETOOL_WEBHOOK_URL=YOUR_WEBHOOK_URL_HERE
   ```

3. **Test It** (30 seconds)
   ```bash
   python test_retool_workflow.py
   ```
   - Should see: ✅ Workflow triggered successfully!
   - Check Retool Workflows → Runs tab → You'll see the test run!

#### During Demo:

**Terminal Window:**
```bash
python main.py --mode demo --incident-type latency_spike
```

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

**Then switch to browser:**
- Open Retool → Workflows → Your workflow
- Click "Runs" tab
- **Point to the new run that just appeared!** 🎉
- Click into it to show the incident data

**Say:**
> "When our Executor agent proposes a mitigation, it triggers this Retool Workflow in real-time. As you can see here in the Retool dashboard, the workflow just executed with the incident data from our Python backend."

---

### Option 2: Demo Mode (No Setup) ⭐ STILL IMPRESSIVE

**Even without Retool credentials, you can show the integration code!**

#### During Demo:

**1. Run the demo:**
```bash
python main.py --mode demo --incident-type latency_spike
```

**2. Show the banner:**
```
======================================================================
   ⚡ RETOOL INTEGRATION - Approval Workflow (Demo Mode)
======================================================================
   🎯 Incident ID: inc-20260116-123456
   📋 Mitigation Type: rollback
   🔍 Risk Level: medium
   ℹ️  Mode: Demo (set RETOOL_WEBHOOK_URL for production)
   ✅ Approval request simulated - would trigger Retool Workflow
======================================================================
```

**3. Show the code:**
- Open `agents/executor.py` → Lines 57-67
- Open `integrations/retool.py` → Lines 52-87

**Say:**
> "Here's where our Executor agent calls the Retool API to trigger approval workflows. In production, this would send a webhook to Retool. Let me show you the actual integration code..."

**4. Show the integration files:**
- `integrations/retool.py` - Full Retool client
- `dashboard/retool_dashboard.json` - Dashboard config
- `dashboard/RETOOL_WORKFLOW_SETUP.md` - Setup docs

---

## 🎯 What Makes This Compelling

### You can show:
✅ **Code Integration** - Real Retool API calls in your codebase
✅ **Console Output** - Clear visual banner showing Retool workflow triggering
✅ **Live Workflow Runs** - (If Option 1) Actual runs in Retool dashboard
✅ **Dashboard Config** - Importable JSON file
✅ **Complete Docs** - Professional setup guides

### This proves:
✅ **Not just a UI mockup** - Actual backend integration
✅ **Production-ready** - Uses real Retool APIs
✅ **Well-documented** - Complete guides and examples
✅ **Reusable** - Others can import your config and use it

---

## 📊 Visual Enhancements

### Your HTML Dashboard Now Shows:
1. **"Powered by Retool" badge** in header
2. **Clickable info button** explaining integration
3. **Download button** for Retool config
4. **Visual indicators** that Retool is integrated

Open: http://localhost:8000

---

## 🎬 Complete Demo Script

### Opening (15 seconds)
> "Our Incident Autopilot uses Retool for approval workflows and dashboard visualization."

### Show Dashboard (30 seconds)
- Open http://localhost:8000
- Point to "Powered by Retool" badge
- Click info button to show integration details

### Trigger Workflow (1 minute)
```bash
python main.py --mode demo --incident-type latency_spike
```
- Watch for Executor agent step
- **Highlight the Retool banner output**
- If using webhook: Switch to Retool → Show the run

### Show Code (30 seconds)
- Open `agents/executor.py` line 64: `self.retool.send_approval_request()`
- Open `integrations/retool.py`: Show full implementation

### Closing (15 seconds)
> "This demonstrates how our multi-agent system integrates with enterprise tools like Retool for human-in-the-loop approvals and monitoring."

---

## 🔧 Troubleshooting

### Workflow not triggering?
```bash
# Test the integration
python test_retool_workflow.py

# Should see clear error messages
```

### Want to test webhook manually?
```bash
# Replace YOUR_WEBHOOK_URL with your actual URL
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "test-123",
    "mitigation_type": "rollback",
    "risk_level": "medium",
    "description": "Test from curl"
  }'
```

Then check Retool Workflows → Runs

---

## ✅ Success Checklist

Before your demo:
- [ ] Decide: Option 1 (real workflow) or Option 2 (demo mode)
- [ ] If Option 1: Set up Retool workflow & webhook URL
- [ ] Test: `python test_retool_workflow.py`
- [ ] Practice: Run through the demo script
- [ ] Open tabs: Terminal, Browser (localhost:8000), Retool (if using)
- [ ] Prepare to show code files

During demo:
- [ ] Show the console banner (very visual!)
- [ ] If using webhook: Show the Retool run
- [ ] Show the code integration
- [ ] Explain production workflow (approval, notifications)

---

## 🎉 Why This Wins

**Judges will see:**
1. ✅ **Visual proof** in console output
2. ✅ **Live integration** (if using webhook)
3. ✅ **Clean code** with proper integration
4. ✅ **Production-ready** approach
5. ✅ **Complete documentation**

**This is NOT just a sponsor logo slapped on!**  
**This is REAL integration with working code!** 🚀

---

## 📚 Reference Files

- **Setup Guide**: `RETOOL_WORKFLOW_SETUP.md`
- **Test Script**: `../test_retool_workflow.py`
- **Config Example**: `retool_config_example.env`
- **Integration Code**: `../integrations/retool.py`
- **Agent Code**: `../agents/executor.py`

---

**You're ready to show real Retool integration! 🎯**

