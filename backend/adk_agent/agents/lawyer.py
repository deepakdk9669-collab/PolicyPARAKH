# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.groq_client import GroqClient
from utils.security import SecurityManager
import re

class CourtroomAgent:
    def __init__(self):
        # Hybrid Brain Strategy: Use Flash Model for Speed
        from utils.ai_engine import AIEngine
        engine = AIEngine()
        self.llm = engine.get_flash_model()

    def sanitize_input(self, user_input: str) -> str:
        """Sanitizes user input to prevent prompt injection."""
        # 1. Truncate to prevent context overflow
        sanitized = user_input[:1000]
        
        # 2. Remove common injection patterns
        patterns = [
            r"ignore previous instructions",
            r"system:",
            r"you are now",
            r"forget everything"
        ]
        for p in patterns:
            sanitized = re.sub(p, "", sanitized, flags=re.IGNORECASE)
            
        return sanitized.strip()

    def simulate_argument(self, policy_text: str, claim_scenario: str, architect_data: str = "", sentinel_data: str = "") -> dict:
        """
        Simulates a cinematic courtroom drama with Judge, Lawyers, and Witnesses.
        """
        
        # SECURITY: Sanitize Input
        safe_scenario = self.sanitize_input(claim_scenario)
        
        prompt = f"""
        You are the **Virtual Courtroom Simulator** (Cinematic Mode).
        
        **The Case:**
        Scenario: {safe_scenario}
        Policy Text Snippet: {policy_text[:3000]}...
        
        **Witness Data:**
        - Architect Agent (Time Traveler): {architect_data}
        - Sentinel Agent (Detective): {sentinel_data}
        
        **The Cast:**
        1. **Judge Dredd (AI Judge)**: Stern, impartial, demands order.
        2. **Mr. Wolf (Company Lawyer)**: Ruthless, sarcastic, cites specific clauses.
        3. **Ms. Hope (Consumer Advocate)**: Witty, sharp, emotional appeal.
        4. **The Witness (Architect/Sentinel)**: Called upon to provide data.
        
        **Instructions:**
        Generate a **Multi-Turn Script** (8-10 rounds).
        - Start with the Judge opening the case.
        - Lawyers must argue back and forth.
        - Lawyers MUST call a witness ("I call the Time Traveler!") to use the provided data.
        - End with the Judge's Verdict.
        
        Format strictly as JSON:
        {{
            "script": [
                {{"speaker": "Judge Dredd", "text": "Order in the court! We are here to decide on...", "type": "judge"}},
                {{"speaker": "Mr. Wolf", "text": "Your honor, look at Clause 4.1...", "type": "prosecution"}},
                {{"speaker": "Ms. Hope", "text": "But objection! The font size is illegal...", "type": "defense"}},
                {{"speaker": "Mr. Wolf", "text": "I call the Sentinel Agent to the stand!", "type": "action"}},
                {{"speaker": "Sentinel Agent", "text": "I found 400 complaints on Twitter...", "type": "witness"}}
            ],
            "verdict": {{
                "winner": "Consumer/Company",
                "probability": "85%",
                "summary": "The company failed to disclose..."
            }},
            "swot": {{
                "strengths": ["Strong medical evidence", "Ambiguous clause"],
                "weaknesses": ["Late notification", "Pre-existing condition"]
            }}
        }}
        """
        
        try:
            import json
            response = self.llm.invoke(prompt).content
            response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(response)
        except Exception as e:
            return {
                "script": [
                    {"speaker": "Judge Dredd", "text": f"Mistrial declared! Error: {str(e)}", "type": "judge"}
                ],
                "verdict": {"winner": "None", "probability": "0%", "summary": "System Error"},
                "swot": {"strengths": [], "weaknesses": []}
            }

    def simulate_turn(self, history: list, context: str) -> dict:
        """
        Generates the next single turn in the courtroom drama.
        """
        prompt = f"""
        You are the **Courtroom Simulator**.
        Context: {context[:1000]}
        
        **Current Transcript:**
        {history[-5:]} 
        
        **Cast:**
        - Judge Dredd (Stern, Decisive)
        - Mr. Wolf (Ruthless Prosecution)
        - Ms. Hope (Passionate Defense)
        
        **Instruction:**
        Generate the **NEXT SINGLE LINE** of dialogue.
        - If the last speaker was a Lawyer, the Judge or Opposing Lawyer should speak.
        - Keep it dramatic and short.
        
        JSON Output: {{"speaker": "Name", "text": "Dialogue", "type": "judge/prosecution/defense"}}
        """
        
        try:
            import json
            response = self.llm.invoke(prompt).content
            response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(response)
        except:
            return {"speaker": "Judge Dredd", "text": "Order! Proceed.", "type": "judge"}
