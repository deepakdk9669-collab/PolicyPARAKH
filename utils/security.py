# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import os
import streamlit as st
import random
from typing import List, Optional

class SecurityManager:
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.admin_key = st.secrets.get("ADMIN_KEY", "admin123") # Default for dev, change in prod

    def _load_api_keys(self) -> List[str]:
        """Loads Gemini API keys from Streamlit secrets."""
        keys = []
        # Support for multiple keys: GEMINI_KEY_1, GEMINI_KEY_2, etc.
        # Or a single list in GEMINI_KEYS
        if "GEMINI_KEYS" in st.secrets:
            keys = st.secrets["GEMINI_KEYS"]
        else:
            # Fallback to checking individual keys
            i = 1
            while True:
                key_name = f"GEMINI_KEY_{i}"
                if key_name in st.secrets:
                    keys.append(st.secrets[key_name])
                    i += 1
                else:
                    break
        
        if not keys and "GEMINI_API_KEY" in st.secrets:
             keys.append(st.secrets["GEMINI_API_KEY"])

        if not keys:
            st.error("No Gemini API Keys found in secrets.toml!")
            return []
        
        return keys

    def get_next_api_key(self) -> str:
        """Round-robin or random selection of API key."""
        if not self.api_keys:
            raise ValueError("No API keys available.")
        return random.choice(self.api_keys)

    def get_secret(self, key_name: str) -> Optional[str]:
        """
        Retrieves a secret from Streamlit secrets or Session State (BYOK).
        """
        # 1. Check Session State (User provided key)
        if key_name in st.session_state:
            return st.session_state[key_name]
            
        # 2. Check Secrets.toml
        if key_name in st.secrets:
            return st.secrets[key_name]
            
        return None

    def generate_admin_token(self, action_details: str) -> str:
        """
        Generates a unique token for a blocked action to request Admin approval.
        """
        import uuid
        token = f"REQ-{str(uuid.uuid4())[:8].upper()}"
        # In a real app, log this token to a database
        print(f"Generated Admin Token: {token} for action: {action_details}")
        return token

    def check_permission_gate(self, action_description: str) -> tuple[bool, Optional[str]]:
        """
        The 'Genesis' Safety Gate.
        Returns (True, None) if allowed.
        Returns (False, Token) if blocked.
        """
        # In a real app, this would trigger a UI modal for approval.
        # For now, we simulate it by checking if the Admin Key is provided.
        
        st.warning(f"⚠️ **SECURITY ALERT**: An agent is attempting a High-Risk Action: `{action_description}`")
        
        admin_key = self.get_secret("ADMIN_KEY")
        
        # Unique key for this specific check to avoid UI conflicts
        user_key = st.sidebar.text_input("Enter Admin Key to Authorize Action:", type="password", key=f"auth_{hash(action_description)}")
        
        if user_key == admin_key:
            st.success("Action Authorized.")
            return True, None
        elif user_key:
            st.error("Invalid Admin Key.")
            return False, self.generate_admin_token(action_description)
        
        # Default block
        return False, self.generate_admin_token(action_description)
