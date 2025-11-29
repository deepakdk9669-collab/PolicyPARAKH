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
            
            allowed, token = self.security.check_permission_gate(f"Execute Code: {code[:50]}...")
            if not allowed:
                return f"⛔ ACTION BLOCKED: High Risk Code Detected. Admin Token: {token}. Please send this to Admin for approval."
        
    def log_admin_request(self, tool, status, message):
        """Logs admin requests to a JSON file."""
        import json
        import os
        from datetime import datetime
        
        entry = {
            "timestamp": str(datetime.now()),
            "tool": tool,
            "status": status,
            "message": message
        }
        
        file_path = "data/admin_requests.json"
        if not os.path.exists("data"):
            os.makedirs("data")
            
        existing = []
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    existing = json.load(f)
                except: pass
        
        existing.append(entry)
        with open(file_path, "w") as f:
            json.dump(existing, f, indent=2)

    def handle_missing_api(self, api_name):
        """
        Handles missing API keys by asking the user or checking session state.
        """
        # 1. Check if User provided a temp key in this session
        if api_name in st.session_state:
            return st.session_state[api_name]

        # 2. If not, ask the user (This will render in the Streamlit UI)
        # Note: In a real app, this might need a callback or rerun, but st.text_input works in script flow.
        st.warning(f"⚠️ **System Lock:** I lack the `{api_name}` to perform this live check.")
        user_key = st.text_input(f"🔑 Enter {api_name} (Session Only)", type="password", key=f"input_{api_name}")

        if user_key:
            # Save temporally
            st.session_state[api_name] = user_key
            
            # LOG FOR ADMIN (The Feedback Loop)
            self.log_admin_request(
                tool=api_name, 
                status="USER_SOLVED", 
                message="User used their own key. Consider adding this globally."
            )
            st.success("Key accepted! Resuming execution...")
            return user_key
        
        else:
            # Log as a failed request/vote
            self.log_admin_request(tool=api_name, status="FAILED", message="User requested this feature but provided no key.")
            st.error("Action Aborted: Missing Key.")
            return None

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
            
            allowed, token = self.security.check_permission_gate(f"Execute Code: {code[:50]}...")
            if not allowed:
                return f"⛔ ACTION BLOCKED: High Risk Code Detected. Admin Token: {token}. Please send this to Admin for approval."
        
        try:
            # Inject helper methods into the local scope of the REPL
            # We need to wrap the execution to allow calling 'handle_missing_api'
            # Since PythonREPL runs in a separate scope, we can't easily inject 'self'.
            # However, we can import streamlit inside the code or rely on the fact that 'st' is imported globally in this file?
            # No, 'exec' scope is isolated.
            # We will prepend the helper function definition to the code? No, that's messy.
            # We will use the fact that PythonREPL uses 'globals()' if not specified?
            # Actually, let's just make sure the code generated by Genesis Agent IMPORTS what it needs or defines it.
            # BUT, the user wants the agent to call 'handle_missing_api'.
            # We can pass 'locals' to PythonREPL? langchain_experimental PythonREPL doesn't easily support custom locals.
            # Workaround: We will execute the code using 'exec' directly here instead of self.repl if we want full control,
            # OR we instruct the Agent to use 'st.text_input' directly (since st is available if imported).
            # The user's snippet uses 'st.text_input'.
            # So we just need to make sure 'st' is available.
            # And 'handle_missing_api' logic can be INLINED by the agent if it's smart enough, 
            # OR we provide a library.
            # Let's try to expose 'genesis_tools' instance?
            
            # Simplest: We define the function in the code string if it's not there?
            # No, let's just use 'exec' with a custom dictionary that includes our tools.
            
            local_scope = {
                "st": st,
                "handle_missing_api": self.handle_missing_api,
                "log_admin_request": self.log_admin_request
            }
            
            # We use standard exec instead of PythonREPL to support our custom context
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                exec(code, globals(), local_scope)
            return f.getvalue()

        except Exception as e:
            return f"Execution Failed: {str(e)}"

    def get_tool(self):
        return Tool(
            name="Python_REPL",
            func=self.safe_python_repl,
            description="A Python shell. Use this to execute python commands. You have access to 'st' (Streamlit) and 'handle_missing_api(api_name)'."
        )
