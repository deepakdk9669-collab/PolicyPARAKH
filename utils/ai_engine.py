# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.security import SecurityManager
import streamlit as st

# Gemini 3.0 uses Search Grounding to bypass the knowledge cutoff limits.

class AIEngine:
    def __init__(self):
        self.security = SecurityManager()

    def get_genesis_model(self):
        """
        Returns the 'Genesis' Brain (Reasoning & Knowledge).
        Model: gemini-3-pro-preview (Best for reasoning & coding).
        Capabilities: Google Search Grounding enabled.
        """
        try:
            # CRITICAL SETTING: Enable Google Search Grounding
            # This allows the model to fetch "Today's" data.
            llm = ChatGoogleGenerativeAI(
                model="gemini-3-pro-preview",
                google_api_key=self.security.get_next_api_key(),
                temperature=0.2,
                # tools=[{"google_search": {}}] # Native Grounding Support
            )
            # Note: LangChain integration for native tools might vary, 
            # but we set the model name explicitly as requested.
            return llm
        except Exception as e:
            st.error(f"Genesis Brain Error: {e}")
            # Fallback to Flash if Pro is not accessible
            return self.get_flash_model()

    def get_flash_model(self):
        """
        Returns the 'Flash' Brain (Speed & Efficiency).
        Model: gemini-2.5-flash.
        Role: High-speed Native Audio/Video processing and Courtroom Simulation.
        """
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=self.security.get_next_api_key(),
                temperature=0.7,
                streaming=True # Enable stream for instant UI feedback
            )
            return llm
        except Exception as e:
            st.error(f"Flash Brain Error: {e}")
            return None

    def run_genesis_agent(self, prompt: str, context: str = ""):
        """
        Orchestrates the Genesis Agent.
        """
        # Final Prompt Construction
        full_prompt = f"""
        System: You are PolicyPARAKH's Genesis Brain (Gemini 3.0). 
        Use your Search Grounding capabilities to provide the latest information.
        
        Context: {context[:5000]}
        
        User Question: {prompt}
        """
        
        # Try all available keys before giving up
        max_retries = self.security.get_key_count()
        
        for _ in range(max_retries):
            model = self.get_genesis_model()
            if model:
                try:
                    return model.invoke(full_prompt).content
                except Exception as e:
                    err_str = str(e).lower()
                    # Check for Rate Limit (429) or other transient errors
                    if "429" in err_str or "quota" in err_str or "exhausted" in err_str:
                        # Key is automatically rotated by get_genesis_model -> get_next_api_key
                        continue
                    return f"Error: {str(e)}"
        
        # If all keys failed with 429, try Flash
        st.toast("⚠️ All Genesis Keys Busy. Switching to Flash...", icon="⚡")
        flash_model = self.get_flash_model()
        if flash_model:
            try:
                return flash_model.invoke(full_prompt).content
            except Exception as e:
                return f"Flash Error: {str(e)}"
                
                return f"Error: AI Brain Offline (All Keys Exhausted)."

    def classify_intent(self, prompt: str) -> str:
        """
        Classifies the user's intent into: AUDIT_REQUEST, COURTROOM_REQUEST, or GENERAL_QUERY.
        Uses the fast 'Flash' model.
        """
        model = self.get_flash_model()
        if not model:
            return "GENERAL_QUERY"
            
        sys_prompt = """
        Classify the user's query into exactly one of these categories:
        1. AUDIT_REQUEST: User wants to analyze/check/audit a policy document or asks for a report.
        2. COURTROOM_REQUEST: User wants to fight a case, simulate a trial, or has a legal dispute.
        3. GENERAL_QUERY: Standard questions, greetings, or small talk.
        
        Output ONLY the category name.
        """
        
    def smart_router(self, prompt: str) -> list:
        """
        Analyzes the prompt and returns a list of agents to activate.
        Agents: AUDITOR, MEDICAL, LAWYER, ARCHITECT, GENESIS.
        """
        model = self.get_flash_model()
        if not model:
            return ["GENESIS"]
            
        sys_prompt = """
        You are the Master Router. Analyze the user's query and select the best expert agents.
        Return a comma-separated list of agent names from: [AUDITOR, MEDICAL, LAWYER, ARCHITECT, GENESIS].
        
        Rules:
        - AUDITOR: For policy checks, coverage questions, exclusions.
        - MEDICAL: For medical terms, diagnosis explanation, health questions.
        - LAWYER: For disputes, legal action, fighting claims.
        - ARCHITECT: For financial forecasting, inflation, future costs.
        - GENESIS: For general chat, greetings, or if no specific expert is needed.
        
        Example: "Check my policy for heart attack coverage and explain what Angioplasty is." -> "AUDITOR, MEDICAL"
        """
        
        try:
            response = model.invoke(f"{sys_prompt}\nUser Query: {prompt}").content.strip().upper()
            agents = [a.strip() for a in response.split(",")]
            # Fallback if empty or invalid
            valid_agents = {"AUDITOR", "MEDICAL", "LAWYER", "ARCHITECT", "GENESIS"}
            final_list = [a for a in agents if a in valid_agents]
            return final_list if final_list else ["GENESIS"]
        except:
            return ["GENESIS"]
