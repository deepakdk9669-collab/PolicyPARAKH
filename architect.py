import pandas as pd
import re
import streamlit as st

def get_real_time_inflation(client):
    """
    Internal helper: Asks Gemini to find the CURRENT medical inflation rate in India.
    """
    try:
        # We ask specifically for a number to use in our math
        prompt = (
            "Search for the current annual 'medical inflation rate' in India for the year 2024-2025. "
            "Return ONLY the percentage number as an integer (e.g., if it is 14%, return 14). "
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                "tools": [{"google_search": {}}],
                "temperature": 0.0 # Deterministic
            }
        )
        
        # Extract the number from the text (fallback to 10% if search fails)
        text = response.text
        match = re.search(r"(\d+)", text)
        if match:
            return int(match.group(1))
        return 10 # Fallback default
        
    except Exception:
        return 10 # Safe fallback

def architect_agent_forecast(client, policy_details) -> pd.DataFrame:
    """
    Architect Agent Task:
    1. Fetches REAL-TIME Medical Inflation Rate.
    2. Generates Financial Forecast Graph.
    """
    # Step 1: Get the LIVE inflation rate
    with st.spinner("📈 Architect Agent searching for live inflation data..."):
        inflation_rate = get_real_time_inflation(client)
    
    inflation_multiplier = 1 + (inflation_rate / 100)
    
    # Step 2: Calculate Impact
    current_coverage = 500000  # Default 5 Lakh base
    years = list(range(1, 11)) # Next 10 years
    
    # Formula: Value = Coverage / (1 + Inflation)^Year
    coverage_value = [int(current_coverage / (inflation_multiplier ** year)) for year in years]
    
    # Step 3: Create Dataframe for the Graph
    df = pd.DataFrame({
        'Year': years,
        'Actual_Coverage_Value': [current_coverage] * 10,
        'Real_Purchasing_Power': coverage_value
    })
    
    # Add metadata so the UI can show which rate was used
    df.attrs['inflation_rate_used'] = inflation_rate
    
    return df
