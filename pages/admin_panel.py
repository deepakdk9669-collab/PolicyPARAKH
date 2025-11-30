# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import os

# st.set_page_config is called in app.py, so we don't need it here if imported as a module.
# But if run standalone, it might be needed. For now, we assume it's a module.

def load_data():
    try:
        with open("market_intel.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def load_admin_requests():
    try:
        if os.path.exists("data/admin_requests.json"):
            with open("data/admin_requests.json", "r") as f:
                return json.load(f)
        return []
    except Exception:
        return []

def render_admin_dashboard():
    st.title("🔐 Consumer Oversight Dashboard")
    st.markdown("### Real-time Market Intelligence & System Control")
    
    data = load_data()
    requests = load_admin_requests()
    
    if not data:
        st.error("Market Intel Database not found.")
        return

    # Top Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Policies Analyzed", data["metrics"]["total_policies_analyzed"])
    c2.metric("Top Risk Zone", data["metrics"]["top_risk_zip"])
    c3.metric("Active Agents", "5 (Swarm Online)")
    c4.metric("Pending Actions", len(requests), delta_color="inverse")
    
    st.divider()
    
    # Section: Genesis Action Requests
    st.subheader("🛑 Genesis Action Requests")
    
    if requests:
        # Sort by timestamp desc
        requests.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        for i, req in enumerate(requests):
            # Render Card
            status_class = f"status-{req['status'].lower()}"
            
            # Card HTML
            st.markdown(f"""
            <div class="request-card">
                <div>
                    <div class="request-meta">{req['timestamp']} • {req['tool']}</div>
                    <div class="request-msg">{req['message']}</div>
                </div>
                <div class="status-badge {status_class}">{req['status']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action Buttons (Only for BLOCKED/PENDING)
            if req['status'] in ["BLOCKED", "PENDING"]:
                c1, c2 = st.columns([1, 4])
                with c1:
                    if st.button("✅ Approve", key=f"app_{i}"):
                        update_request_status(i, "APPROVED")
                        st.rerun()
                with c2:
                    if st.button("❌ Deny", key=f"deny_{i}"):
                        update_request_status(i, "DENIED")
                        st.rerun()
            
    else:
        st.info("No pending action requests from Genesis.")

def update_request_status(index, new_status):
    try:
        if os.path.exists("data/admin_requests.json"):
            with open("data/admin_requests.json", "r") as f:
                data = json.load(f)
            
            # Sort to match display order (descending timestamp)
            data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            if 0 <= index < len(data):
                data[index]["status"] = new_status
                
                # Write back (unsorted or sorted? usually append, but here we modify in place)
                # To be safe, we should probably rely on IDs, but index works for this demo if consistent.
                # Let's just write back the modified list.
                with open("data/admin_requests.json", "w") as f:
                    json.dump(data, f, indent=2)
                st.toast(f"Request {new_status}")
    except Exception as e:
        st.error(f"Failed to update status: {e}")

    st.divider()
    
    # Row 1: Company Risks & Issue Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚨 Most Flagged Companies")
        df_companies = pd.DataFrame(data["companies"])
        fig_companies = px.bar(
            df_companies, 
            x="name", 
            y="flags", 
            color="flags",
            color_continuous_scale="Reds",
            title="Consumer Complaints & Red Flags"
        )
        fig_companies.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig_companies, use_container_width=True)
        
    with col2:
        st.subheader("📉 Common Trap Clauses")
        df_issues = pd.DataFrame(list(data["issues_distribution"].items()), columns=["Issue", "Count"])
        fig_issues = px.pie(
            df_issues, 
            values="Count", 
            names="Issue", 
            title="Distribution of Hidden Clauses",
            hole=0.4
        )
        fig_issues.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig_issues, use_container_width=True)
        
    st.divider()
    
    # Row 2: Geographic Risk Heatmap
    st.subheader("🗺️ Geographic Risk Heatmap (Bengaluru)")
    df_geo = pd.DataFrame(data["geo_risk"])
    
    # Mock Lat/Lon for visualization
    lat_lon_map = {
        "Koramangala": {"lat": 12.9352, "lon": 77.6245},
        "HSR Layout": {"lat": 12.9121, "lon": 77.6446},
        "MG Road": {"lat": 12.9716, "lon": 77.5946},
        "Whitefield": {"lat": 12.9698, "lon": 77.7500},
        "JP Nagar": {"lat": 12.9063, "lon": 77.5857}
    }
    
    df_geo["lat"] = df_geo["area"].map(lambda x: lat_lon_map.get(x, {}).get("lat"))
    df_geo["lon"] = df_geo["area"].map(lambda x: lat_lon_map.get(x, {}).get("lon"))
    
    fig_map = px.scatter_mapbox(
        df_geo,
        lat="lat",
        lon="lon",
        color="risk_score",
        size="reports",
        color_continuous_scale="Bluered",
        size_max=30,
        zoom=10,
        hover_name="area",
        hover_data=["pincode", "risk_score"],
        mapbox_style="carto-darkmatter",
        title="Scam Hotspots by Location"
    )
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        margin={"r":0,"t":30,"l":0,"b":0}
    )
    st.plotly_chart(fig_map, use_container_width=True)

if __name__ == "__main__":
    render_admin_dashboard()
