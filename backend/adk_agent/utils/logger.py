# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import datetime
import json
import streamlit as st
from typing import Optional
from utils.drive_storage import DriveManager

class AgentLogger:
    def __init__(self):
        if 'agent_logs' not in st.session_state:
            st.session_state['agent_logs'] = []
        # Supabase client is stateless, so we just init when needed or keep a ref
        # self.drive = DriveManager() # Removed

    def log_step(self, agent_name: str, input_data: str, output_data: str, metadata: Optional[dict] = None):
        """Logs a single step in the agent's execution."""
        try:
            from utils.supabase_client import SupabaseManager
            sb = SupabaseManager().get_client()
            
            entry = {
                "agent_name": agent_name,
                "input": input_data[:1000], # Limit size
                "output": output_data[:1000],
                "metadata": metadata or {}
            }
            
            # Async insert (fire and forget ideally, but here sync)
            if sb:
                sb.table("agent_logs").insert(entry).execute()
                
        except Exception as e:
            print(f"Log Insert Failed: {e}")

    def save_logs(self):
        """Uploads the current session logs to Google Drive."""
        # Deprecated: Supabase logs are real-time.
        pass

    def get_logs(self):
        # Fetch from Supabase if needed, or just return empty
        return []
