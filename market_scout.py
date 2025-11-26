import streamlit as st
from google.genai import types
import search_engine

def get_social_sentiment(client, company_name):
    """
    Analyzes Social Media (Reddit/Twitter) for Real User Reviews.
    """
    # Step 1: Get Raw Data from Social Media
    raw_data = search_engine.search_web(f"{company_name} insurance reviews claims", focus="social")
    
    # Step 2: Analyze with Gemini
    prompt = f"""
    Analyze these raw social media comments about '{company_name}'.
    Data: {raw_data}
    
    Output a JSON-like summary:
    1. **Overall Sentiment:** (Positive/Negative/Mixed)
    2. **Major Complaints:** (e.g., "Claim rejection", "Slow customer service")
    3. **Trust Score:** (1-10 based on user anger)
    """
    try:
        res = client.models.generate_content(model='gemini-2.5-pro', contents=prompt)
        return res.text
    except:
        return "Could not analyze sentiment."

def check_local_presence(client, company_name, location):
    """
    Checks Network Hospitals in a specific city.
    """
    # Step 1: Get Data with Maps Focus
    raw_data = search_engine.search_web(f"{company_name} network hospitals list in {location}", focus="maps")
    
    # Step 2: Summarize
    prompt = f"""
    User is in '{location}'. Does '{company_name}' have good network hospitals there?
    Data: {raw_data}
    
    List the top 3 hospitals found in the data.
    """
    try:
        res = client.models.generate_content(model='gemini-2.5-pro', contents=prompt)
        return res.text
    except:
        return "Could not check local network."

def compare_policy(client, report):
    """Standard Market Comparison"""
    entity = report.get('entity_name', 'Provider')
    doc_type = report.get('doc_category', 'Insurance')
    
    # General Search for Comparison
    data = search_engine.search_web(f"Best alternatives to {entity} {doc_type} India 2025 reviews", focus="general")
    
    try:
        res = client.models.generate_content(
            model='gemini-2.5-pro', 
            contents=f"User has {entity} ({doc_type}). Suggest 2 better alternatives based on this market data: {data}"
        )
        return res.text
    except:
        return "Comparison failed."
