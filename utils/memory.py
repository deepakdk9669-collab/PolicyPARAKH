# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import streamlit as st
import json

class FamilyMemory:
    def __init__(self):
        if 'family_profile' not in st.session_state:
            st.session_state['family_profile'] = []

    def add_member(self, name: str, age: int, conditions: str):
        """Adds a family member to the session state."""
        member = {
            "name": name,
            "age": age,
            "conditions": conditions
        }
        st.session_state['family_profile'].append(member)

    def get_profile_string(self) -> str:
        """Returns the family profile as a string for the LLM."""
        if not st.session_state['family_profile']:
            return "No family profile found."
        
        profile_str = "Family Profile:\n"
        for m in st.session_state['family_profile']:
            profile_str += f"- {m['name']} (Age: {m['age']}): {m['conditions']}\n"
        return profile_str

    def add_case_history(self, case_data: dict):
        """Stores a verified case/report for future reference."""
        if 'case_history' not in st.session_state:
            st.session_state['case_history'] = []
        st.session_state['case_history'].append(case_data)

    def get_case_history(self):
        """Retrieves past cases."""
        return st.session_state.get('case_history', [])

    def clear_memory(self):
        st.session_state['family_profile'] = []
        st.session_state['case_history'] = []
