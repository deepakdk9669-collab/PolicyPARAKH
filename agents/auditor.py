# Copyright (c) 2025 Deepak Kushwah. All rights reserved.

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from utils.security import SecurityManager
import json
from utils.knowledge_vault import KnowledgeVault

class AuditorAgent:
    def __init__(self):
        self.security = SecurityManager()
        # Get a key (in a real app, we might want to rotate per request)
        api_key = self.security.get_next_api_key()
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp", # Using Flash for speed as requested
            google_api_key=api_key,
            temperature=0.1 # Low temp for factual extraction
        )

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
        except Exception as e:
            return {
                "error": f"Audit failed: {str(e)}",
                "risk_score": 0
            }
