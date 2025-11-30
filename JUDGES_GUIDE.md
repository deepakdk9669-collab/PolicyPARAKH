# 🏛️ PolicyPARAKH - Capstone Project Guide

**Team:** PolicyPARAKH  
**Competition:** Agents Intensive - Capstone Project  
**Stack:** Python FastAPI (Backend) + Next.js (Frontend) + Google Gemini (AI)

---

## 🚀 Quick Start (One-Click)

We have provided a simple script to launch the entire application:

1.  **Double-click** `run_app.bat` in the root directory.
2.  The app will open automatically at `http://localhost:3000`.

*(Note: Requires Node.js and Python to be installed)*

---

## 🌟 Key Features (What to Test)

### 1. The Genesis Chat (Home Page)
*   **URL:** `http://localhost:3000/`
*   **What it is:** A Gemini-powered insurance assistant.
*   **Try this:** Ask "Explain my policy coverage" or "What is the claim process?".

### 2. The Courtroom Simulator (Capstone Feature)
*   **URL:** `http://localhost:3000/courtroom`
*   **What it is:** An AI-simulated debate between a Policyholder and an Insurer, presided over by an AI Judge.
*   **Try this:** Enter a dispute like "Claim rejected for pre-existing diabetes" and click **Start Session**. Watch the agents debate in real-time!

### 3. God Mode Dashboard (Hidden Admin Panel)
*   **URL:** `http://localhost:3000/admin`
*   **Passkey:** `admin123`
*   **What it is:** A control center to view live stats and manually trigger agents.
*   **Try this:** Unlock the dashboard and use the **"Force Audit Policy"** button to trigger a background agent task.

---

## 🛠️ Manual Setup (If needed)

If the batch script doesn't work, you can run the components manually:

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
