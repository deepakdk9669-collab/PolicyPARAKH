# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from tools.genesis_tools import GenesisTools
from utils.security import SecurityManager

class GenesisAgent:
    def __init__(self):
        self.security = SecurityManager()
        api_key = self.security.get_next_api_key()
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp", # Using Pro for better coding capability if available, else Flash
            google_api_key=api_key,
            temperature=0.4
        )
        self.genesis_tools = GenesisTools()

    def solve_problem(self, problem_statement: str) -> str:
        """
        Attempts to solve a novel problem by writing and executing code.
        """
        
        tools = [self.genesis_tools.get_tool()]
        
        agent = initialize_agent(
            tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )
        
        prompt = f"""
        You are the **Genesis Agent**, an intelligent engineer.
        Your goal is to solve the user's problem by creating and executing Python code.
        
        Problem: {problem_statement}
        
        Rules:
        1. Use the Python_REPL tool to calculate, process data, or simulate scenarios.
        2. If the tool returns "ACTION BLOCKED", the output MUST be: "🚫 Action Blocked. Please send Token [TOKEN] to Admin."
        3. Be concise in your final answer.
        """
        
        try:
            return agent.run(prompt)
        except Exception as e:
            return f"Genesis crashed: {str(e)}"
