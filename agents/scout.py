# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.security import SecurityManager

class ScoutAgent:
    def __init__(self):
        self.security = SecurityManager()
        api_key = self.security.get_next_api_key()
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.2
        )

    def compare_policies(self, current_policy_name: str, user_profile: str) -> str:
        """
        Suggests better alternatives based on the user profile.
        """
        prompt = f"""
        You are the **Market Scout**, an expert insurance broker.
        
        The user has a policy from: {current_policy_name}
        User Profile: {user_profile}
        
        Task:
        1. Identify 2 better alternatives in the Indian market that suit this profile better.
        2. Focus on features like "No Claim Bonus", "Restoration Benefit", and "PED Waiting Period".
        3. Create a small comparison table (Markdown).
        
        Output:
        A concise recommendation with the comparison table.
        """
        
        try:
            return self.llm.invoke(prompt).content
        except Exception as e:
            return f"Scout failed to find alternatives: {str(e)}"
