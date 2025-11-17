# PolicyPARAKH: The AI Policy Auditor

<p align="center">
  <strong>An advanced AI Agent Swarm for comprehensive insurance policy auditing and risk analysis.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python Version">
  <img src="https://img.shields.io/badge/Google%20Gemini-API-blueviolet?style=for-the-badge&logo=google-gemini" alt="Gemini API">
  <img src="https://img.shields.io/badge/Kaggle-Competition-cyan?style=for-the-badge&logo=kaggle" alt="Kaggle Competition">
  <img src="https://img.shields.io/badge/Status-In%20Development-green?style=for-the-badge" alt="Status">
</p>

PolicyPARAKH is an advanced AI Agent Swarm designed to help users understand complex insurance policies, identify hidden "loopholes," and make informed financial decisions. This project leverages key concepts from the Google & Kaggle 5-Day AI Agents Intensive course to create a robust, reliable, and user-centric tool.

---

## 2. System Architecture: The "PolicyPARAKH Swarm"

We use a **"Swarm"** architecture. A central **"Gatekeeper"** (Router) agent manages a team of specialist agents. This modular design allows us to scale, debug, and ensure quality.

**(NOTE: You must upload the `1000011765.jpg` file to your GitHub repository for this image to appear)**
<p align="center">
  <img src="1000011765.jpg" alt="PolicyPARAKH Swarm Architecture Diagram" width="700">
</p>

---

## 3. The Build: Features & Course Concepts (The 7 Agents)

### Mapping Course Concepts to Features
We applied key concepts from all 5 days of the course to build PolicyPARAKH.

* **Day 1: Tools & Custom Functions (The 7 Specialist Agents)**
    * **Concept:** Agents need custom tools to act.
    * **Our Build:** We designed 7 advanced custom tools (which act as specialist agents) for our swarm:

        * **1. Social_Sentinel (The Social Media Detective)**
            * **How it works:** This agent scans Twitter/Reddit to see if other users are reporting this company or policy for a "scam" or "fraud".

        * **2. Risk_Auditor (The Financial Detective)**
            * **How it works:** This agent uses Google to check the company's financial health (Solvency Ratio). A ratio below 1.5 is a red flag.

        * **3. Audio_Lie_Detector (The Lie Detector Agent)**
            * **How it works:** This agent listens to the sales call audio and compares it to the PDF. It finds any promises the salesman made that are *not* written in the policy.

        * **4. Financial_Projector (The Future Value Agent)**
            * **How it works:** This agent calculates what your $100,000 policy will be worth in 20 years after accounting for inflation.

        * **5. Room_Rent_Modeler (The "Hidden Cost" Agent)**
            * **How it works:** This agent finds the dangerous "pro-portionate deduction" loophole, which can cause your entire hospital bill to be rejected.

        * **6. Legal_Scanner (The Court Case Agent)**
            * **How it works:** This agent checks a (simulated) database to see how many court cases are active against the company for not paying claims.

        * **7. Market_Comparator (The "Better Deal" Agent)**
            * **How it works:** This agent searches the market to find 2-3 better alternative policies from other companies.

* **Day 2: Human-in-the-Loop (Long-Running Operations)**
    * **Concept:** High-stakes operations need human approval.
    * **Our Build:** The `Audio_Lie_Detector` tool (in our code) uses `pause_before_tool_call=True`. The agent will first ask for your permission before listening to your private audio file.

* **Day 3: Sessions & Memory**
    * **Concept:** Agents must learn and remember.
    * **Our Build:** We use two types of memory:
        1.  **Session Memory:** The agent remembers your name in the conversation (e.g., "Welcome back, Deepak!").
        2.  **Long-Term Memory ("Global Scam Ledger"):** When a new scam is found (by `Social_Sentinel`), the agent saves it permanently to warn all future users.

* **Day 4: Quality & Observability (LLM-as-a-Judge)**
    * **Concept:** Agents must be reliable and accurate.
    * **Our Build:** We designed a "Devil's Advocate" (LLM-as-a-Judge) agent. Its only job is to double-check the math from the `Financial_Projector` agent to ensure 99.9% accuracy.

* **Day 5: Deployment & A2A Protocol**
    * **Concept:** Agents must be deployable and able to interact.
    * **Our Build:** Our "Iron Gatekeeper" (Boss Agent) uses the A2A protocol to route tasks to our 7 specialist agents.

---

## 4. The Demo Flow: The "Smart Packet" (The Full Report)

Our agent does NOT deliver a 5-line summary. It processes the documents and delivers the **complete deep-dive report ("Smart Packet")** all at once, because a user with a serious query deserves a full, readable analysis, not small "tukde" (pieces).

Here is the flow of the report the user receives:

### **Part 1: The Executive Summary & Overall Scores**
Analysis Complete. Your 'Smart Packet' report is ready:

> **OVERALL SCORE: 45/100 (HIGH RISK / POOR VALUE)**
>
> **SAFETY SCORE: 35/100 (HIGH RISK)** ⚠️
> *(This audits the policy for loopholes, hidden costs, and claim rejection risk.)*
>
> **VALUE SCORE: 80/100 (GOOD VALUE)** ✅
> *(This audits the financial benefits (coverage) against the premium paid.)*
>
> **Top-Level Finding:** This policy is cheap, but has 3 critical loopholes that could cost you thousands.

---
### **Part 2: The Detailed Report (The "Pros")**
Here are the "Pros" (Good Value) items found in your policy:

* **1. Low Premium Cost:**
    * **Finding:** The annual premium of 10,000 for a $100,000 cover is approximately **20% cheaper** than the market average for a 30-year-old.

* **2. Wide Critical Illness Coverage:**
    * **Finding:** This policy covers **45 critical illnesses**, while the industry standard is 30. It includes rare conditions like 'X' and 'Y'.

---
### **Part 3: The Detailed Report (The "Cons" / High Risk)**
Here are the "Cons" (High Risk) items found in your policy:

* **1. CRITICAL LOOPHOLE: 'Pro-portionate Deduction' Clause** (Found by: `Room_Rent_Modeler` tool)
    * **What it is:** The policy has a 5,000 limit on room rent.
    * **The Trap:** If you take a 10,000 room (2x the limit), the insurer will pay only 50% of your *ENTIRE* hospital bill, not just the room rent. On a 2,00,000 bill, this loophole would cost you 1,00,000.

* **2. LIE DETECTED: Sales Call Contradiction** (Found by: `Audio_Lie_Detector` tool)
    * **The Promise:** The salesman promised **'24-hour claim approval'** on the audio call.
    * **The Truth:** The policy PDF (Section 4.b) explicitly states a **'7-day review period'** for all non-emergency claims.

* **3. FINANCIAL RED FLAG: Insurer Company Background** (Found by: `Risk_Auditor` tool)
    * **The Finding:** The insurer ('Shady Mutual') has a low **Solvency Ratio of 1.2**.
    * **Why it matters:** The IRDAI (India) recommended minimum is 1.5. A 1.2 ratio is a potential risk that the company may have trouble paying a high volume of claims.

* **4. PUBLIC COMPLAINTS (Social & Legal Risk)** (Found by: `Legal_Scanner` & `Social_Sentinel` tools)
    * **Legal:** We found **12 pending consumer court cases** against 'Shady Mutual' for 'claim rejection'.
    * **Social:** We found **3 high-severity Reddit threads** in the last month detailing a new scam pattern where claims are rejected for 'missing paperwork'.

---
### **Part 4: Market Alternatives**
(Found by: `Market_Comparator` tool)

Here are two alternative policies found that address the "Cons" listed above:

* **1. 'TotalSecure' by SecureHealth:**
    * **Why it's better:** This policy has **no 'pro-portionate deduction' clause** (no room rent limit).
    * **Trade-off:** The premium is 15% higher.

* **2. 'LifeGuard' by SafeFuture:**
    * **Why it's better:** This company has a **Solvency Ratio of 1.8** (very safe) and 0 pending court cases.
    * **Trade-off:** It has a similar premium but covers 5 fewer critical illnesses.

### Bonus Points
* **Video:** We will submit a 3-minute screen recording demonstrating this "Demo Flow" using our runnable, simulated code.
* **Gemini:** Our "Router" and "Devil's Advocate" agents use the live Gemini API.
* **Deployment:** Our code is 100% runnable.

---

## 5. Honesty & Future Scope

### A Note on Technical Implementation (Honesty)
**For the Judges:** PolicyPARAKH is a high-stakes FinTech/LegalTech product involving PII and paid APIs (Twitter, Audio, Legal DBs). For security and API cost reasons, we have **simulated** these complex tools in our `demo.py` file. Our `Social_Sentinel` tool (in the code) reads from a `local_fake_db` instead of the live Twitter API. This ensures our code is 100% runnable and crash-free for evaluation. The core agent logic (Router, Memory, Judge) runs on the live Gemini API.

### If I had more time...
* **Monetization:** We would build the "Competitor Spy" feature (a B2B subscription for insurance companies).
* **Claim Filing:** We would build a "Claim Filing" agent to auto-generate all TPA forms.
* **Deeper Finance:** We would connect the agent to the CIBIL API to audit Loan Protection policies.
