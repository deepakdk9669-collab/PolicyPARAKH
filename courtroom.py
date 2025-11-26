import streamlit as st
from google.genai import types
import tavily_search

def get_social_sentiment(client, company_name):
    """
    Checks Twitter/Reddit/News for recent scams or praise.
    """
    search_query = f"{company_name} insurance reviews complaints scandal twitter reddit 2024 2025"
    data = tavily_search.tavily_deep_search(search_query)
    
    prompt = f"Analyze this search data about '{company_name}'. What is the current Market Sentiment? Are people angry or happy? Give a 1-line verdict."
    res = client.models.generate_content(model='gemini-2.5-pro', contents=f"{prompt}\nData: {data}")
    return res.text

def check_local_presence(client, company_name, location):
    """
    Checks hospital network in a specific city (e.g., Gwalior).
    """
    search_query = f"{company_name} network hospitals list in {location} cashless coverage"
    data = tavily_search.tavily_deep_search(search_query)
    
    prompt = f"Based on this data, does '{company_name}' have a good presence in '{location}'? List 2-3 major hospitals if found."
    res = client.models.generate_content(model='gemini-2.5-pro', contents=f"{prompt}\nData: {data}")
    return res.text

def compare_policy(client, report):
    """Standard Comparison"""
    entity = report.get('entity_name', 'Provider')
    # ... (Keep previous logic or use Tavily) ...
    search_query = f"Better alternatives to {entity} health insurance India 2025 comparison"
    data = tavily_search.tavily_deep_search(search_query)
    
    res = client.models.generate_content(
        model='gemini-2.5-pro', 
        contents=f"User has {entity}. Suggest 2 better alternatives based on: {data}"
    )
    return res.text
