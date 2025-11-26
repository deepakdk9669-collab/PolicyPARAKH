import streamlit as st
from google.genai import types
import search_engine

def get_social_sentiment(client, company_name):
    data = search_engine.search_web(f"{company_name} insurance reviews", focus="social")
    try:
        res = client.models.generate_content(
            model='gemini-2.5-pro', 
            contents=f"Analyze sentiment for {company_name} based on: {data}. Return Verdict."
        )
        return res.text
    except: return "Error analyzing sentiment."

def check_local_presence(client, company_name, location):
    data = search_engine.search_web(f"{company_name} hospitals in {location}", focus="maps")
    try:
        res = client.models.generate_content(
            model='gemini-2.5-pro', 
            contents=f"List hospitals for {company_name} in {location} based on: {data}"
        )
        return res.text
    except: return "Error checking location."

def compare_policy(client, report):
    entity = report.get('entity_name', 'Provider')
    data = search_engine.search_web(f"Better alternatives to {entity} health insurance India 2025")
    try:
        res = client.models.generate_content(
            model='gemini-2.5-pro', 
            contents=f"Compare {entity} with alternatives based on: {data}"
        )
        return res.text
    except: return "Comparison failed."
