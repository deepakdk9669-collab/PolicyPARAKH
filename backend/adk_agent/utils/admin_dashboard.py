# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

def load_data():
    """Loads market intelligence data from JSON."""
    file_path = "market_intel.json"
    if not os.path.exists(file_path):
        st.error(f"Data file not found: {file_path}")
        return None
    
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

def render_admin_dashboard():
    st.title("🛡️ Consumer Oversight Dashboard")
    
    st.markdown("### Market Intelligence & Risk Monitoring")
    if st.button("Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()
        
    st.divider()

    data = load_data()
    if not data:
        return

    # --- Metrics Row ---
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Policies Analyzed", data["metrics"]["total_policies_analyzed"], "+12% vs last week")
    with m2:
        st.metric("Top Risk Zip Code", data["metrics"]["top_risk_zip"], "High Fraud Detected")
    with m3:
        st.metric("Active Agents", "5 (Swarm)", "Operational")

    st.divider()

    # --- Charts Row ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🚨 Top 5 Bad Actors")
        df_companies = pd.DataFrame(data["companies"])
        fig_bar = px.bar(
            df_companies, 
            x="name", 
            y="flags", 
            color="flags",
            color_continuous_scale="Reds",
            title="Companies with Most Flags",
            labels={"name": "Company", "flags": "Issues Detected"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("🧩 Pain Points Distribution")
        df_issues = pd.DataFrame(list(data["issues_distribution"].items()), columns=["Issue", "Percentage"])
        fig_pie = px.pie(
            df_issues, 
            values="Percentage", 
            names="Issue", 
            title="Detected Issues Breakdown",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- Geographic Risk ---
    st.divider()
    st.subheader("🗺️ Geographic Risk Heatmap")
    
    if "geo_risk" in data:
        df_geo = pd.DataFrame(data["geo_risk"])
        
        # Using a Bar Chart for Pincodes (Simpler than Mapbox for demo without lat/lon)
        fig_geo = px.bar(
            df_geo,
            x="pincode",
            y="risk_score",
            color="reports",
            hover_data=["area"],
            title="Risk Score by Pincode (Color = Report Volume)",
            labels={"risk_score": "Avg Risk Score", "pincode": "Zip Code"},
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_geo, use_container_width=True)
    else:
        st.info("No Geographic Data Available yet.")

    # --- Data Export ---
    st.divider()
    st.subheader("📂 Export Data")
    
    # Convert full data to CSV for download
    # Flattening the structure for CSV
    export_data = []
    for comp in data["companies"]:
        export_data.append({
            "Company": comp["name"],
            "Flags": comp["flags"],
            "Primary Issue": comp["issues"],
            "Zip Code": data["metrics"]["top_risk_zip"] # Dummy mapping for demo
        })
    
    df_export = pd.DataFrame(export_data)
    csv = df_export.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Export Data for Regulatory Review (CSV)",
        data=csv,
        file_name='market_intel_report.csv',
        mime='text/csv',
    )
