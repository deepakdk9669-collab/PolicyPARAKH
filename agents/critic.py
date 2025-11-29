# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from utils.security import SecurityManager

class CriticAgent:
    def __init__(self):
        self.security = SecurityManager()
        api_key = self.security.get_next_api_key()
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.3
        )

    def review_audit(self, policy_text: str, audit_report: dict) -> dict:
        """
        Reviews the Auditor's findings against the raw text to check for hallucinations.
        """
        
        prompt_template = """
        You are the **Critic Agent**, a senior supervisor.
        Your job is to verify the work of a junior Auditor.
        
        Here is the raw Policy Text:
        {policy_text}
        
        Here is the Auditor's Report:
        {audit_report}
        
        Task:
        1. Verify if the "Risk Score" and "Risk Reason" make sense based on the text.
        2. Check if the "Exclusions" listed actually exist in the text.
        3. Identify any critical missing clauses that the Auditor missed.
        
        Output your review in JSON format:
        {{
            "is_accurate": true/false,
            "corrections": "None" or "Correction details...",
            "missing_clauses": ["...", "..."],
            "final_verdict": "Safe to buy" or "Avoid" or "Negotiate"
        }}
        """
        
        prompt = PromptTemplate(
            input_variables=["policy_text", "audit_report"],
            template=prompt_template
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            # Convert dict to string for the prompt
            import json
            report_str = json.dumps(audit_report)
            
            response = chain.run(policy_text=policy_text[:10000], audit_report=report_str) # Truncate text if too long
            response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(response)
        except Exception as e:
            return {
                "error": f"Critic review failed: {str(e)}",
                "is_accurate": False
            }
