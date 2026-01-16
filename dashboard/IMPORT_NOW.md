# ⚡ Import Retool Dashboard NOW (2 Minutes)

## 🎯 Visual Demo - Show Retool is Being Used

### Step 1: Sign Up (30 seconds)
1. Go to: **https://retool.com**
2. Click "Start building for free"
3. Sign up with Google/email

### Step 2: Import Dashboard (30 seconds)
1. In Retool, click **"Create new"** (blue button top right)
2. Select **"From JSON/YAML"**
3. Upload: `dashboard/retool_dashboard.json`
4. Name it: "Incident Autopilot"
5. Click "Create app"

### Step 3: Configure (30 seconds)
1. Go to **Resources** (left sidebar)
2. Click on "Incident Autopilot API"
3. Change Base URL to: `https://YOUR_NGROK_URL/api`
   
   **Get ngrok URL:**
   ```bash
   # In a new terminal:
   ngrok http 8000
   # Copy the https URL (like https://abc123.ngrok.io)
   ```

4. Click "Save"

### Step 4: Test (30 seconds)
1. Click each query at the bottom (getStatistics, getIncidents)
2. Click "Run" button
3. See data appear!
4. Click "Release" (top right) to publish

### Step 5: Demo! 🎉
1. Open your Retool app URL
2. Click "🚀 Simulate Incident"
3. Watch real-time updates
4. Show timeline panel

**SAY:** "This is our incident dashboard built with Retool, connecting to our Python API in real-time. Watch as our agents work through the incident."

---

## 🚀 Fastest Way (Use ngrok):

```bash
# Terminal 1: Start API
cd incident-autopilot
python main.py --mode server

# Terminal 2: Expose with ngrok
ngrok http 8000

# Copy the https URL and use it in Retool!
```

---

## 📸 Take Screenshots of:
1. Retool editor with your dashboard
2. The live dashboard with data
3. Timeline showing agent actions

**This proves you're using Retool!** ✅

