import streamlit as st
from langchain_community.tools import DuckDuckGoSearchRun

def immortal_search(query):
    """
    The Immortal Search: Tries DuckDuckGo first.
    """
    try:
        ddg = DuckDuckGoSearchRun()
        return ddg.invoke(query)
    except:
        return "⚠️ Search unavailable. Relying on internal logic."
      
