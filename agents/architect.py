# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
from tools.chart_tools import generate_inflation_chart

class ArchitectAgent:
    def __init__(self):
        pass

    def forecast_financials(self, current_cover: int):
        """
        Returns a Plotly figure for financial forecasting.
        """
        return generate_inflation_chart(current_cover)
