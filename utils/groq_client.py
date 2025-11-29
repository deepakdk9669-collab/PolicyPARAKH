# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import os
from langchain_groq import ChatGroq
from utils.security import SecurityManager
import streamlit as st

class GroqClient:
    def __init__(self):
        self.security = SecurityManager()
        # Try to get Groq key from secrets or session state (BYOK)
        self.api_key = self.security.get_secret("GROQ_API_KEY")
        
    def get_llm(self, temperature=0.7):
        if not self.api_key:
            return None
            
        return ChatGroq(
            temperature=temperature, 
            model_name="llama3-70b-8192", 
            groq_api_key=self.api_key
        )
