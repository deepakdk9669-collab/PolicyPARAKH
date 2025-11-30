import plotly.graph_objects as go
import pandas as pd

def generate_inflation_chart(current_cover: int, years=10, inflation_rate=0.07):
    """
    Generates a Plotly figure showing the depreciation of coverage value over time.
    """
    years_list = list(range(2025, 2025 + years + 1))
    real_value = [current_cover / ((1 + inflation_rate) ** i) for i in range(len(years_list))]
    medical_cost = [current_cover * ((1 + 0.10) ** i) for i in range(len(years_list))] # Medical inflation is higher (10%)

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years_list, y=real_value,
        mode='lines+markers',
        name='Real Coverage Value (7% Inflation)',
        line=dict(color='red', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=years_list, y=medical_cost,
        mode='lines+markers',
        name='Projected Medical Cost (10% Inflation)',
        line=dict(color='orange', width=3, dash='dash')
    ))

    fig.update_layout(
        title="The Inflation Trap: Coverage vs. Cost",
        xaxis_title="Year",
        yaxis_title="Amount (INR)",
        template="plotly_dark",
        hovermode="x unified"
    )
    
    return fig
