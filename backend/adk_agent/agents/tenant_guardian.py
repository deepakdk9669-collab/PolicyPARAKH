# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from utils.security import SecurityManager
import json

class TenantGuardianAgent:
    def __init__(self):
        from utils.ai_engine import AIEngine
        engine = AIEngine()
        self.llm = engine.get_flash_model()

    def audit_rent_agreement(self, policy_text: str) -> dict:
        """
        Analyzes Rental Agreements for tenant traps.
        """
        
        prompt_template = """
        You are the **Tenant Guardian**, a real estate legal expert protecting tenants.
        Analyze the following Rental Agreement text and extract critical details:

        1. **Lock-in Period**: Is there a minimum stay? (e.g., "Cannot vacate for 6 months").
        2. **Security Deposit**: Amount and Refund terms? (e.g., "Deduction for painting").
        3. **Maintenance Charges**: Who pays for major repairs vs. minor repairs?
        4. **Notice Period**: How many months notice is required?
        5. **Eviction Clauses**: Are there unfair grounds for immediate eviction?
        
        Based on these, calculate a **Fairness Score** (0-100).
        - 100 = Tenant Friendly.
        - 0 = Landlord Trap (Predatory).
        
        Output strictly in JSON format:
        {{
            "lock_in": "...",
            "security_deposit": "...",
            "maintenance": "...",
            "notice_period": "...",
            "eviction_terms": "...",
            "risk_score": 0-100,
            "risk_reason": "Brief explanation of the score."
        }}
        
        Agreement Text:
        {policy_text}
        """
        
        prompt = PromptTemplate(
            input_variables=["policy_text"],
            template=prompt_template
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            response = chain.run(policy_text=policy_text)
            cleaned_response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_response)
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "risk_score": 0
            }
