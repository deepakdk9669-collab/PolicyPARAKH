from langchain_experimental.utilities import PythonREPL
from langchain.tools import Tool
from utils.security import SecurityManager
import streamlit as st

class GenesisTools:
    def __init__(self):
        self.repl = PythonREPL()
        self.security = SecurityManager()

    def safe_python_repl(self, code: str) -> str:
        """
        Executes Python code safely. 
        Triggers Permission Gate for high-risk keywords.
        """
        high_risk_keywords = ["os.system", "subprocess", "shutil", "delete", "remove", "drop table"]
        
        is_high_risk = any(keyword in code for keyword in high_risk_keywords)
        
        if is_high_risk:
            # In a real agent loop, we can't easily pause for UI input in the middle of a tool call 
            # without a complex callback system. 
            # For this demo, we will check if the Admin Key is ALREADY present in session state 
            # or return a message asking the user to authorize.
            
            if not self.security.check_permission_gate(f"Execute Code: {code[:50]}..."):
                return "⛔ ACTION BLOCKED: High Risk Code Detected. Admin Authorization Required."
        
        try:
            return self.repl.run(code)
        except Exception as e:
            return f"Execution Failed: {str(e)}"

    def get_tool(self):
        return Tool(
            name="Python_REPL",
            func=self.safe_python_repl,
            description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`."
        )
