# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from tools.search_tools import get_search_tool
from utils.security import SecurityManager

class SentinelAgent:
    def __init__(self):
        self.security = SecurityManager()
        api_key = self.security.get_next_api_key()
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.2
        )
        self.search_tool = get_search_tool()

    def check_reputation(self, company_name: str) -> str:
        """
        Searches for recent news, scams, or regulatory actions against the company.
        """
        
        tools = [self.search_tool]
        
        agent = initialize_agent(
            tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )
        
        query = f"""
        Search for recent "scams", "regulatory fines", "claim rejection ratio", and "consumer complaints" 
        for the insurance company: {company_name} in India.
        Summarize the reputation in 3 bullet points.
        """
        
        try:
            return agent.run(query)
        except Exception as e:
            return f"Sentinel failed to patrol: {str(e)}"
