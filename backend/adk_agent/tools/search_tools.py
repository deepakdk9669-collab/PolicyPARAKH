from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

def get_search_tool():
    """
    Returns a configured DuckDuckGo search tool.
    """
    wrapper = DuckDuckGoSearchAPIWrapper(region="in-en", time="y", max_results=5)
    search = DuckDuckGoSearchRun(api_wrapper=wrapper)
    return search
