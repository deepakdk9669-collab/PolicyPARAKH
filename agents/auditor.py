# Copyright (c) 2025 Deepak Kushwah. All rights reserved.

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from utils.security import SecurityManager
import json
from utils.knowledge_vault import KnowledgeVault

class AuditorAgent:
    def __init__(self):
        from utils.ai_engine import AIEngine
        engine = AIEngine()
        self.llm = engine.get_flash_model()

    def audit_policy(self, policy_text: str, doc_type: str = "Insurance") -> dict:
        """
        Scans the policy text based on document type.
        """
        
        prompts = {
            "Insurance": """
                You are the **Auditor Agent** (Insurance Specialist).
                Analyze the policy for:
                1. **Room Rent Capping**: Limit?
                2. **Co-Payment**: Mandatory?
                3. **Disease Sub-limits**: Specific limits?
                4. **Waiting Periods**: PED/Specific diseases?
                5. **Exclusions**: Top 3 critical ones.
                
                Risk Score (0-100): 0=Perfect, 100=Terrible.
                JSON Output: {{"room_rent": "...", "co_pay": "...", "sub_limits": "...", "waiting_periods": "...", "exclusions": [], "risk_score": 0, "risk_reason": "..."}}
            """,
            "Rent": """
                You are the **Tenant Guardian** (Real Estate Specialist).
                Analyze the Rental Agreement for:
                1. **Lock-in Period**: Is it reasonable?
                2. **Security Deposit**: Refund terms & deductions?
                3. **Maintenance Charges**: Who pays?
                4. **Notice Period**: Length?
                5. **Eviction Clauses**: Unfair grounds?
                
                Risk Score (0-100): 0=Fair, 100=Predatory.
                JSON Output: {{"room_rent": "Lock-in Period...", "co_pay": "Security Deposit...", "sub_limits": "Maintenance...", "waiting_periods": "Notice Period...", "exclusions": ["Eviction Clause 1", ...], "risk_score": 0, "risk_reason": "..."}}
            """,
            "Job": """
                You are the **Career Shield** (Employment Lawyer).
                Analyze the Offer Letter for:
                1. **Bond/Penalty**: Amount if quitting early?
                2. **Notice Period**: Length?
                3. **Non-Compete**: Duration & Scope?
                4. **IP Ownership**: Personal projects?
                5. **Variable Pay**: Is it guaranteed?
                
                Risk Score (0-100): 0=Fair, 100=Exploitative.
                JSON Output: {{"room_rent": "Bond/Penalty...", "co_pay": "Notice Period...", "sub_limits": "Non-Compete...", "waiting_periods": "IP Rights...", "exclusions": ["Variable Pay Clause", ...], "risk_score": 0, "risk_reason": "..."}}
            """
        }
        
        selected_prompt = prompts.get(doc_type, prompts["Insurance"])
        
        final_prompt = f"""
        {selected_prompt}
        
        Policy Text:
        {policy_text[:10000]}
        """
        
        prompt = PromptTemplate(
            input_variables=["policy_text"],
            template=final_prompt
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            response = chain.run(policy_text=policy_text)
            # 3. Community Scam Graph Check
            vault = KnowledgeVault()
            # Mock entity extraction - in prod use NER
            entity_flags = vault.check_entity("Star Health") 
            
            community_note = ""
            if entity_flags:
                community_note = f"⚠️ **Community Alert**: This entity has {entity_flags['flags']} flags. Issues: {', '.join(entity_flags['issues'])}."

            try:
                cleaned_response = response.replace("```json", "").replace("```", "").strip()
                report = json.loads(cleaned_response)
                if community_note:
                    report['risk_reason'] += f" {community_note}"
                return report
            except Exception as e:
                return {
                    "risk_score": 0,
                    "risk_reason": "Error parsing audit report.",
                    "exclusions": [],
                    "room_rent": "Unknown",
                    "co_pay": "Unknown",
                    "waiting_periods": "Unknown",
                    "sub_limits": "Unknown"
                }
            }

    def generate_full_report(self, policy_text: str) -> str:
        """
        Generates a comprehensive Markdown report using the Genesis Brain.
        """
        from utils.ai_engine import AIEngine
        engine = AIEngine()
        
        prompt = f"""
        You are the **Chief Policy Auditor**.
        Conduct a deep-dive forensic analysis of the following insurance policy document.
        
        Generate a **Comprehensive Markdown Report** with the following sections:
        
        # 🛡️ Policy Audit Report
        
        ## 1. Executive Summary
        - Brief overview of the policy type and key coverage.
        - **Overall Risk Rating**: (Low/Medium/High) with a short justification.
        
        ## 2. Critical Red Flags 🚩
        - List the top 3-5 most dangerous clauses that could lead to claim rejection.
        - Explain *why* they are dangerous in simple terms.
        
        ## 3. Financial Analysis 💰
        - **Room Rent Capping**: Detail any limits.
        - **Co-Payment**: Is there a mandatory co-pay?
        - **Sub-limits**: Check for disease-specific limits (Cataract, Knee Replacement, etc.).
        
        ## 4. Hidden Traps & Exclusions 🕸️
        - Identify obscure exclusions often missed by users.
        - Highlight "Reasonable and Customary" clauses if present.
        
        ## 5. Recommendations 💡
        - Actionable advice for the policyholder.
        - Questions to ask the insurer.
        
        ---
        **Policy Text**:
        {policy_text[:15000]}
        """
        
        # Use Genesis Agent (Robust with Retry)
        return engine.run_genesis_agent(prompt, context="")
