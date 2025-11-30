# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from tools.search_tools import get_search_tool
from utils.security import SecurityManager

class SentinelAgent:
    def __init__(self):
        from utils.ai_engine import AIEngine
        engine = AIEngine()
        self.llm = engine.get_flash_model()
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
            # 1. Try Live Search
            return agent.run(query)
        except Exception as e:
            # 2. Fallback to Internal Knowledge
            fallback_prompt = f"""
            The live search tool is currently unavailable (Error: {str(e)}).
            
            Based on your **Internal Knowledge** (up to your training cutoff), 
            what are known issues, scams, or reputation details for: {company_name}?
            
            Format:
            - ⚠️ **Note:** Live search failed. Using internal knowledge.
            - [Bullet Point 1]
            - [Bullet Point 2]
            - [Bullet Point 3]
            """
            return self.llm.invoke(fallback_prompt).content
