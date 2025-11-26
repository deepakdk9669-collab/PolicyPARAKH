import streamlit as st
from tavily import TavilyClient
from duckduckgo_search import DDGS
from googleapiclient.discovery import build

# Secrets Load
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY", "")
GOOGLE_CSE_ID = st.secrets.get("GOOGLE_CSE_ID", "")
GOOGLE_SEARCH_KEY = st.secrets.get("GOOGLE_SEARCH_KEY", "")

def search_web(query, focus="general"):
    """
    Rotates between Tavily -> Google -> DuckDuckGo.
    focus: 'general', 'social' (reviews), 'maps' (locations)
    """
    search_query = query
    if focus == "social": search_query += " site:reddit.com OR site:twitter.com OR site:quora.com review complaint"
    elif focus == "maps": search_query += " hospital network address contact"

    results = []

    # 1. Tavily (Primary)
    if TAVILY_KEY:
        try:
            client = TavilyClient(api_key=TAVILY_KEY)
            res = client.search(search_query, max_results=3)
            return "\n".join([f"- {r['content']} ({r['url']})" for r in res.get('results', [])])
        except: pass

    # 2. Google (Secondary)
    if GOOGLE_SEARCH_KEY:
        try:
            service = build("customsearch", "v1", developerKey=GOOGLE_SEARCH_KEY)
            res = service.cse().list(q=search_query, cx=GOOGLE_CSE_ID, num=3).execute()
            return "\n".join([f"- {i['snippet']}" for i in res.get('items', [])])
        except: pass

    # 3. DuckDuckGo (Fallback)
    try:
        with DDGS() as ddgs:
            res = list(ddgs.text(search_query, max_results=3))
            return "\n".join([f"- {r['body']}" for r in res])
    except:
        return "No internet access available."
