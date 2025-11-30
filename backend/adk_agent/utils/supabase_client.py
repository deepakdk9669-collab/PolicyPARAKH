# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import streamlit as st
from supabase import create_client, Client
from typing import Optional

class SupabaseManager:
    _instance = None
    client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseManager, cls).__new__(cls)
            cls._instance.client = cls._init_client()
        return cls._instance

    @staticmethod
    def _init_client() -> Optional[Client]:
        try:
            # Try loading from secrets
            if "supabase" not in st.secrets:
                return None
                
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            return create_client(url, key)
        except Exception as e:
            # Log internally but don't crash the app
            print(f"Supabase Connection Failed: {e}")
            return None

    def get_client(self) -> Optional[Client]:
        return self.client

    def is_connected(self) -> bool:
        """Returns True if Supabase client is successfully initialized."""
        return self.client is not None
