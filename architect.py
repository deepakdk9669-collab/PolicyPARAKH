import pandas as pd
import re
import streamlit as st
from google.genai import types

def get_real_time_inflation(client):
    try:
        prompt = "Current annual medical inflation rate in India 2024-2025? Return ONLY the integer number."
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.0
            )
        )
        match = re.search(r"(\d+)", response.text)
        return int(match.group(1)) if match else 10
    except:
        return 10

def architect_agent_forecast(client, policy_details) -> pd.DataFrame:
    with st.spinner("📈 Architect Agent महंगाई का डेटा ला रहा है..."):
        rate = get_real_time_inflation(client)
    
    multiplier = 1 + (rate / 100)
    current_val = 500000 
    years = list(range(1, 11))
    real_val = [int(current_val / (multiplier ** year)) for year in years]
    
    df = pd.DataFrame({
        'Year': years,
        'Actual_Coverage_Value': [current_val] * 10,
        'Real_Purchasing_Power': real_val
    })
    df.attrs['inflation_rate_used'] = rate
    return df
