# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import streamlit as st

def render_member_card(member):
    """
    Renders a stylish card for a family member using HTML/CSS.
    """
    risk_color = "#00cc66" # Green
    if member.get('risk_level') == "High":
        risk_color = "#ff4b4b"
    elif member.get('risk_level') == "Medium":
        risk_color = "#ffa500"

    html = f"""
    <div class="member-card">
        <div class="member-role">{member.get('role', 'Member')}</div>
        <div class="member-name">{member.get('name', 'Unknown')}</div>
        <div class="member-stats">
            <span>Age: {member.get('age', 'N/A')}</span>
            <span style="color: {risk_color}">Risk: {member.get('risk_level', 'Low')}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_result_card(report):
    """
    Renders the analysis result as a comprehensive card in the chat stream.
    """
    score = report.get('risk_score', 0)
    score_class = "risk-score-low"
    if score > 70: score_class = "risk-score-high"
    elif score > 30: score_class = "risk-score-med"

    st.markdown(f"""
    <div class="result-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <h3 style="margin: 0;">Analysis Report</h3>
                <p style="color: #888; margin: 0;">AI Audit Complete</p>
            </div>
            <div style="text-align: right;">
                <h1 class="{score_class}" style="margin: 0; font-size: 3em;">{score}</h1>
                <span style="color: #888; font-size: 0.8em;">RISK SCORE</span>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 20px;">
            <div style="background: #1e1f20; padding: 10px; border-radius: 8px; text-align: center;">
                <div style="color: #888; font-size: 0.8em;">ROOM RENT</div>
                <div style="font-weight: 600;">{report.get('room_rent', 'N/A')}</div>
            </div>
            <div style="background: #1e1f20; padding: 10px; border-radius: 8px; text-align: center;">
                <div style="color: #888; font-size: 0.8em;">CO-PAY</div>
                <div style="font-weight: 600;">{report.get('co_pay', 'N/A')}</div>
            </div>
            <div style="background: #1e1f20; padding: 10px; border-radius: 8px; text-align: center;">
                <div style="color: #888; font-size: 0.8em;">WAITING</div>
                <div style="font-weight: 600;">{report.get('waiting_periods', 'N/A')}</div>
            </div>
        </div>

        <div style="background: rgba(255, 75, 75, 0.1); border-left: 4px solid #ff4b4b; padding: 12px; border-radius: 4px;">
            <strong>Critical Alert:</strong> {report.get('risk_reason', 'None detected.')}
        </div>
    </div>
    """, unsafe_allow_html=True)
