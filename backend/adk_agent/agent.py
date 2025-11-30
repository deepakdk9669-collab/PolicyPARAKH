from google.adk.agents.llm_agent import Agent
import vertexai
import os
from .tools import (
    audit_policy_tool, 
    medical_analysis_tool, 
    courtroom_simulation_tool, 
    check_reputation_tool
)

# Initialize Vertex AI
# Note: In production, these env vars are set by the runtime.
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

if project_id:
    vertexai.init(project=project_id, location=location)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='policy_parakh_agent',
    description="An AI Swarm that fights for consumer rights in insurance, rent, and employment contracts.",
    instruction="""
    You are PolicyPARAKH, an autonomous agent system designed to protect consumers.
    
    Your goal is to help users understand contracts, find hidden risks, and simulate legal battles.
    
    You have access to the following tools:
    1. `audit_policy_tool`: Use this when the user uploads a document text or asks to check a policy/agreement/offer letter.
    2. `medical_analysis_tool`: Use this for medical queries, diagnosis explanations, or checking disease coverage.
    3. `courtroom_simulation_tool`: Use this if the user wants to fight a claim rejection or simulate a legal argument.
    4. `check_reputation_tool`: Use this to check if a company is a scam or has bad reviews.
    
    If the user greets you, respond politely as PolicyPARAKH.
    Always prioritize the user's financial safety.
    """,
    tools=[
        audit_policy_tool, 
        medical_analysis_tool, 
        courtroom_simulation_tool, 
        check_reputation_tool
    ],
)
