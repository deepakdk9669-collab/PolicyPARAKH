import streamlit as st
from tavily import TavilyClient
from duckduckgo_search import DDGS
from googleapiclient.discovery import build

# --- CONFIGURATION ---
# Tavily Key
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY", "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")

# Google CSE Config
GOOGLE_CSE_ID = st.secrets.get("GOOGLE_CSE_ID", "11902b0ebe4d84784")
# We need a Google API Key specifically for Search (different from Gemini)
# Assuming it's in the pool or secrets, otherwise fallback to DDG
GOOGLE_SEARCH_KEY = st.secrets.get("GOOGLE_SEARCH_KEY", "") 

def search_web(query):
    """
    The Master Search Function.
    Rotates: Tavily -> Google CSE -> DuckDuckGo (Backup).
    """
    results = ""
    
    # 1. TRY TAVILY (Best for Deep Context)
    try:
        print("Attempting Tavily Search...")
        client = TavilyClient(api_key=TAVILY_KEY)
        response = client.search(query, search_depth="basic", max_results=3)
        results = "\n".join([f"- {r['content']} (Source: {r['url']})" for r in response.get('results', [])])
        return f"[Source: Tavily]\n{results}"
    except Exception as e:
        print(f"Tavily Failed: {e}")

    # 2. TRY GOOGLE CSE (Best for News)
    if GOOGLE_SEARCH_KEY:
        try:
            print("Attempting Google CSE...")
            service = build("customsearch", "v1", developerKey=GOOGLE_SEARCH_KEY)
            res = service.cse().list(q=query, cx=GOOGLE_CSE_ID, num=3).execute()
            results = "\n".join([f"- {item['snippet']} (Source: {item['link']})" for item in res.get('items', [])])
            return f"[Source: Google]\n{results}"
        except Exception as e:
            print(f"Google CSE Failed: {e}")

    # 3. TRY DUCKDUCKGO (Unlimited Free Backup)
    try:
        print("Attempting DuckDuckGo (Backup)...")
        with DDGS() as ddgs:
            # ddgs.text() returns a generator, so we list() it
            ddg_results = list(ddgs.text(query, max_results=3))
            results = "\n".join([f"- {r['body']} (Source: {r['href']})" for r in ddg_results])
            return f"[Source: DuckDuckGo]\n{results}"
    except Exception as e:
        return f"All Search Engines Failed. Error: {e}"
