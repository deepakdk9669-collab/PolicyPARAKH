# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import streamlit as st
import json

class FamilyMemory:
    def __init__(self):
        if 'family_profile' not in st.session_state:
            st.session_state['family_profile'] = []
        
        # Auto-Load from Drive
        self.load_memory()

    def add_member(self, name: str, age: int, conditions: str):
        """Adds a family member to the session state and syncs to Drive."""
        member = {
            "name": name,
            "age": age,
            "conditions": conditions
        }
        st.session_state['family_profile'].append(member)
        self.save_memory()

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
        # TODO: Persist case history too if needed

    def get_case_history(self):
        """Retrieves past cases."""
        return st.session_state.get('case_history', [])

    # --- Persistent Memory (Supabase) ---
    def save_memory(self):
        """Saves family profile to Supabase."""
        try:
            from utils.supabase_client import SupabaseManager
            manager = SupabaseManager()
            
            # CIRCUIT BREAKER: If DB down, skip save (Session State still holds data)
            if not manager.is_connected():
                print("⚠️ Supabase Disconnected. Using local memory only.")
                return

            sb = manager.get_client()
            if not sb: return

            # For this demo, we assume a single user or 'default_user'
            user_id = "default_user"
            
            # Upsert logic (Delete old for user, insert new)
            # In a real app, we'd update specific rows. Here we sync the whole list.
            # 1. Delete existing
            sb.table("family_profiles").delete().eq("user_id", user_id).execute()
            
            # 2. Insert new
            if st.session_state['family_profile']:
                data = []
                for m in st.session_state['family_profile']:
                    data.append({
                        "user_id": user_id,
                        "name": m["name"],
                        "age": m["age"],
                        "conditions": m["conditions"]
                    })
                sb.table("family_profiles").insert(data).execute()
                
        except Exception as e:
            print(f"Memory Save Failed: {e}")

    def load_memory(self):
        """Loads family profile from Supabase."""
        try:
            # Only load if session is empty
            if st.session_state['family_profile']:
                return

            from utils.supabase_client import SupabaseManager
            manager = SupabaseManager()
            
            # CIRCUIT BREAKER
            if not manager.is_connected():
                print("⚠️ Supabase Disconnected. Starting with empty memory.")
                return

            sb = manager.get_client()
            if not sb: return
            
            user_id = "default_user"
            response = sb.table("family_profiles").select("*").eq("user_id", user_id).execute()
            
            if response.data:
                st.session_state['family_profile'] = response.data
                st.toast("🧠 Memory Restored from Supabase", icon="⚡")
        except Exception as e:
            print(f"Memory Load Failed: {e}")
