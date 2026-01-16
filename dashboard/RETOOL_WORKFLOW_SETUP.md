# ⚡ Retool Workflow Setup - Trigger Real Workflows

## 🎯 Goal
Make your Incident Autopilot **actually trigger** Retool Workflows when mitigations need approval.

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Create Retool Workflow (2 minutes)

1. **Sign in to Retool**: https://retool.com
2. **Go to Workflows**: Click "Workflows" in the left sidebar
3. **Create New Workflow**: Click "Create new" → "Workflow"
4. **Name it**: `incident-approval-workflow`

### Step 2: Configure Workflow Trigger

1. **Select trigger type**: "Webhook"
2. You'll get a webhook URL like: `https://api.retool.com/v1/workflows/abc123/startTrigger?workflowApiToken=xyz`
3. **Save this URL!**

### Step 3: Add Workflow Steps

Add these blocks (drag from left panel):

**Block 1: Parse Incident Data**
- Type: JavaScript Code
- Name: `parseIncident`
- Code:
```javascript
return {
  incident_id: trigger.data.incident_id,
  mitigation_type: trigger.data.mitigation_type,
  description: trigger.data.description,
  risk_level: trigger.data.risk_level,
  timestamp: trigger.data.timestamp
};
```

**Block 2: Send Slack Notification** (Optional)
- Type: Slack - Send Message
- Channel: `#incidents`
- Message:
```
🚨 *Incident Approval Required*

*Incident ID:* {{parseIncident.value.incident_id}}
*Mitigation:* {{parseIncident.value.mitigation_type}}
*Risk Level:* {{parseIncident.value.risk_level}}
*Description:* {{parseIncident.value.description}}

Please review in the Incident Autopilot dashboard.
```

**Block 3: Log to Database** (Optional)
- Type: Query Resource (if you have a DB)
- Or use Retool Database

**Block 4: Return Response**
- Type: Return
- Value:
```javascript
{
  status: "success",
  message: "Approval workflow triggered",
  incident_id: parseIncident.value.incident_id
}
```

### Step 4: Test the Workflow

1. Click **"Test"** in top right
2. Use this test data:
```json
{
  "incident_id": "inc-test-123",
  "mitigation_type": "rollback",
  "description": "Rollback to previous version",
  "risk_level": "medium",
  "timestamp": "2026-01-16T12:00:00Z"
}
```
3. Click **"Run"** - verify it works!
4. **Deploy** the workflow

---

## 🔑 Step 5: Configure Your App

### Option A: Use Webhook URL (Easiest)

1. Copy your workflow webhook URL
2. Create `.env` file in your project:

```bash
# .env file
RETOOL_WEBHOOK_URL=https://api.retool.com/v1/workflows/YOUR_WORKFLOW_ID/startTrigger?workflowApiToken=YOUR_TOKEN
```

### Option B: Use API Key (Production)

1. In Retool, go to **Settings** → **API Keys**
2. Generate new API key
3. Add to `.env`:

```bash
# .env file
RETOOL_API_KEY=retool_pk_your_api_key_here
RETOOL_WORKFLOW_ID=your_workflow_id
```

---

## 🎬 Step 6: Test It Live!

### Terminal Demo:

```bash
# Start your server
python main.py --mode demo --incident-type latency_spike
```

**Watch for this output:**
```
======================================================================
   ⚡ RETOOL INTEGRATION - Approval Workflow Triggered
======================================================================
   🎯 Incident ID: inc-20260116-123456
   📋 Mitigation Type: rollback
   🔍 Risk Level: medium
   ✅ Workflow triggered successfully!
======================================================================
```

### Dashboard Demo:

```bash
# Start server
python main.py --mode server

# Open browser
open http://localhost:8000
```

1. Click "🚀 Simulate Incident"
2. Watch the console logs
3. **Check your Retool Workflow runs** - you'll see it triggered!

---

## 📊 Verify It's Working

### In Retool:
1. Go to **Workflows**
2. Click your `incident-approval-workflow`
3. Click **"Runs"** tab
4. You'll see the triggered runs with incident data! ✅

### In Your Terminal:
Look for the banner:
```
⚡ RETOOL INTEGRATION - Approval Workflow Triggered
```

### In Your Code:
The integration happens in:
- `agents/executor.py` (line 57-67)
- `integrations/retool.py` (line 37-87)

---

## 🎯 Demo Script for Judges

### What to Say:
> "When our Executor agent proposes a mitigation that requires approval, it triggers a Retool Workflow. Let me show you..."

### What to Do:
1. **Show the code**: Open `agents/executor.py` line 64
2. **Run a demo**: `python main.py --mode demo --incident-type latency_spike`
3. **Point to output**: The Retool banner in the console
4. **Show Retool**: Open Retool Workflows → Show the run that just happened
5. **Explain**: "In production, this would send Slack notifications, log to database, and wait for human approval"

### What to Show:
✅ Code that calls Retool API
✅ Console output showing Retool integration
✅ Retool Workflow dashboard with actual runs
✅ The workflow configuration you created

---

## 💡 Pro Tips

### Make It More Visual:
1. Add a Slack block to your workflow
2. When you trigger an incident, show the Slack message appear
3. Or add an email notification

### For Demo Without API Key:
The current code works WITHOUT an API key too! It simulates the call and shows:
```
ℹ️  Mode: Demo (set RETOOL_API_KEY for production)
✅ Approval request simulated - would trigger Retool Workflow
```

### To Use Real API:
Just add the webhook URL or API key to `.env` - no code changes needed!

---

## 🔧 Troubleshooting

**Workflow not triggering?**
- Check `.env` file has correct webhook URL
- Verify workflow is deployed in Retool
- Check console for error messages

**Want to test without running full demo?**
```bash
# Test just the Retool integration
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "test-123",
    "mitigation_type": "rollback",
    "risk_level": "medium"
  }'
```

---

## 🎉 Success Criteria

You'll know it's working when:
- ✅ Console shows Retool banner
- ✅ Retool Workflow runs tab shows new runs
- ✅ You can click into a run and see the incident data
- ✅ Slack/email notifications arrive (if configured)

**This is REAL Retool integration!** 🚀

