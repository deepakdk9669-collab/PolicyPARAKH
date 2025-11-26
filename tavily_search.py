from tavily import TavilyClient
import streamlit as st

# Load API Key from Secrets or use the one you provided
# Security Note: Put "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" in Streamlit Secrets!
TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY", "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")

def tavily_deep_search(query):
    """
    Uses Tavily AI Search to get deep, factual context for the agents.
    Better than standard Google Search for AI agents.
    """
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        # 'advanced' search depth gives better results for legal/medical topics
        response = client.search(query, search_depth="advanced", max_results=3)
        
        context = []
        for result in response.get('results', []):
            context.append(f"Source: {result['title']}\nURL: {result['url']}\nContent: {result['content']}\n")
            
        return "\n\n".join(context)
    except Exception as e:
        return f"Tavily Search Error: {e}"
