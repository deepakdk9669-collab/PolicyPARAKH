# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from utils.security import SecurityManager
import json

class CareerShieldAgent:
    def __init__(self):
        from utils.ai_engine import AIEngine
        engine = AIEngine()
        self.llm = engine.get_flash_model()

    def audit_offer_letter(self, policy_text: str) -> dict:
        """
        Analyzes Job Offer Letters for employment traps.
        """
        
        prompt_template = """
        You are the **Career Shield**, an employment law expert protecting employees.
        Analyze the following Offer Letter/Contract and extract critical details:

        1. **Bond/Penalty**: Is there a penalty for leaving early? (e.g., "Pay 2 lakhs if left within 2 years").
        2. **Notice Period**: How long is it? Is it buyable?
        3. **Non-Compete**: Are you banned from joining competitors? For how long?
        4. **IP Ownership**: Does the company own your side projects?
        5. **Variable Pay**: Is the bonus guaranteed or discretionary?
        
        Based on these, calculate a **Safety Score** (0-100).
        - 100 = Employee Friendly.
        - 0 = Exploitative (Bonded Labor).
        
        Output strictly in JSON format:
        {{
            "bond": "...",
            "notice_period": "...",
            "non_compete": "...",
            "ip_rights": "...",
            "variable_pay": "...",
            "risk_score": 0-100,
            "risk_reason": "Brief explanation of the score."
        }}
        
        Contract Text:
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
