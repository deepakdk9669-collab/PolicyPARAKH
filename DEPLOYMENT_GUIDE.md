# ☁️ PolicyPARAKH Deployment Guide

Since you chose the "Hard Way" (Full Cloud Deployment), here is your step-by-step guide.

## Phase 1: Push to GitHub 🐙
1.  Go to [GitHub.com](https://github.com) and create a **New Repository** named `policy-parakh`.
2.  Open your `submission_package` folder on your computer.
3.  Drag and drop ALL the files from `submission_package` into the GitHub upload page.
4.  Click **Commit changes**.

---

## Phase 2: Deploy Backend (Render.com) 🧠
1.  Go to [Render.com](https://render.com) and Sign Up/Login with GitHub.
2.  Click **New +** -> **Web Service**.
3.  Connect your `policy-parakh` repository.
4.  **Fill in these settings EXACTLY:**
    *   **Name:** `policy-backend`
    *   **Root Directory:** `backend`
    *   **Runtime:** `Python 3`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
5.  **Environment Variables (Advanced -> Add Environment Variable):**
    *   Copy all the keys from your `backend/.env` file here (GOOGLE_API_KEY, GROQ_API_KEY, etc.).
6.  Click **Create Web Service**.
7.  **Wait.** It will take 2-3 minutes. Once it says "Live", copy the URL (e.g., `https://policy-backend.onrender.com`).

---

## Phase 3: Deploy Frontend (Vercel) 🎨
1.  Go to [Vercel.com](https://vercel.com) and Sign Up/Login with GitHub.
2.  Click **Add New...** -> **Project**.
3.  Import your `policy-parakh` repository.
4.  **Configure Project:**
    *   **Framework Preset:** Next.js (should be auto-detected).
    *   **Root Directory:** Click "Edit" and select `frontend`.
5.  **Environment Variables:**
    *   **Key:** `NEXT_PUBLIC_API_URL`
    *   **Value:** Paste the Render Backend URL you copied in Phase 2 (e.g., `https://policy-backend.onrender.com`).
    *   *(Make sure to remove any trailing slash `/` at the end of the URL)*
6.  Click **Deploy**.

---

## 🎉 You are Done!
Vercel will give you a link (e.g., `https://policy-parakh.vercel.app`).
Share that link with the judges!
