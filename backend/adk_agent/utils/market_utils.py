# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import json
import os
import streamlit as st
import random

def log_market_intel(data: dict, consent_given: bool = True):
    """
    Safely logs anonymous data only if consent_given is True.
    Appends to a local JSON file (market_intel.json).
    """
    if not consent_given:
        return

    file_path = "market_intel.json"
    
    # Ensure file exists
    if not os.path.exists(file_path):
        # Create with default structure if missing
        default_data = {
            "companies": [],
            "issues_distribution": {},
            "metrics": {"total_policies_analyzed": 0, "top_risk_zip": "N/A"},
            "geo_risk": []
        }
        with open(file_path, "w") as f:
            json.dump(default_data, f)

    try:
        with open(file_path, "r") as f:
            current_data = json.load(f)
        
        # Update Metrics
        current_data["metrics"]["total_policies_analyzed"] += 1
        
        # Update Company Flags (Simple Logic)
        company_name = data.get("company_name", "Unknown")
        found = False
        for comp in current_data["companies"]:
            if comp["name"] == company_name:
                comp["flags"] += 1
                found = True
                break
        if not found and company_name != "Unknown":
            current_data["companies"].append({"name": company_name, "flags": 1, "issues": "New Detected"})
            
        # Save back
        with open(file_path, "w") as f:
            json.dump(current_data, f)
            
    except Exception as e:
        print(f"Logging failed: {e}")

def show_funny_error(error_msg: str):
    """
    Displays a humorous error message in Streamlit.
    """
    funny_messages = [
        "Oops! The hamsters running the server tripped.",
        "Computer says NO.",
        "Looks like the AI is on a coffee break.",
        "Error 404: Logic not found.",
        "Have you tried turning it off and on again?",
        "Our monkeys are working on this. Please hold."
    ]
    
    msg = random.choice(funny_messages)
    st.error(f"**{msg}**")
    st.caption(f"Technical Details: {error_msg}")
