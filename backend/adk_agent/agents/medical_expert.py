# Copyright (c) 2025 Deepak Kushwah. All rights reserved.

from utils.ai_engine import AIEngine

class MedicalExpertAgent:
    def __init__(self):
        self.engine = AIEngine()

    def analyze_medical_report(self, report_text: str, policy_context: str = "") -> str:
        """
        Analyzes a medical report to explain the diagnosis and check against policy exclusions.
        """
        prompt = f"""
        You are Dr. Gemini, a **Medical Expert** and Insurance Claims Specialist.
        
        Analyze the following medical report/notes:
        
        "{report_text}"
        
        Context (Policy Exclusions/Terms):
        "{policy_context}"
        
        Provide a response in Markdown:
        1. **Diagnosis Explanation**: Explain the condition in simple, non-medical terms.
        2. **Treatment Analysis**: Is the prescribed treatment standard? (e.g., Is hospitalization necessary?)
        3. **Policy Check**: Based on the provided policy context (if any), are there potential coverage issues? (e.g., cosmetic, experimental, pre-existing?)
        4. **Next Steps**: What should the patient ask their doctor?
        """
        
        return self.engine.run_genesis_agent(prompt)

    def explain_term(self, term: str) -> str:
        """
        Explains a specific medical term.
        """
        prompt = f"""
        Explain the medical term "**{term}**" to a 10-year-old. 
        Also, mention if this is typically covered in standard health insurance policies in India.
        """
        return self.engine.run_genesis_agent(prompt)
