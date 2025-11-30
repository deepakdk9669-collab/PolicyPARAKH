import sys
import os

from ..agents.auditor import AuditorAgent
from ..agents.medical_expert import MedicalExpertAgent
from ..agents.lawyer import CourtroomAgent
from ..agents.sentinel import SentinelAgent

def audit_policy_tool(policy_text: str) -> str:
    """
    Audits an insurance policy, rent agreement, or job offer.
    Returns a detailed risk report with red flags.
    """
    auditor = AuditorAgent()
    return auditor.generate_full_report(policy_text)

def medical_analysis_tool(query: str, policy_context: str = "") -> str:
    """
    Analyzes medical reports or explains medical terms.
    """
    expert = MedicalExpertAgent()
    return expert.analyze_medical_report(query, policy_context)

def courtroom_simulation_tool(scenario: str, policy_context: str) -> str:
    """
    Simulates a courtroom battle between a Company Lawyer and Consumer Advocate.
    Returns a script of the argument.
    """
    court = CourtroomAgent()
    # We use the static argument for the tool version for simplicity
    result = court.simulate_argument(policy_context, scenario)
    return str(result)

def check_reputation_tool(company_name: str) -> str:
    """
    Checks the reputation of a company for scams or issues.
    """
    sentinel = SentinelAgent()
    return sentinel.check_reputation(company_name)
