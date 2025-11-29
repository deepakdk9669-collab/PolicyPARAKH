# Copyright (c) 2025 Deepak Kushwah. All rights reserved.
import json
import os

class KnowledgeVault:
    def __init__(self, db_path="data/scam_graph.json"):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists(self.db_path):
            # Seed data with some common scams
            seed_data = {
                "companies": {
                    "Star Health": {"flags": 15, "issues": ["Room Rent Capping", "Co-Pay Hidden"]},
                    "NestAway": {"flags": 8, "issues": ["Security Deposit Refund Delay"]},
                    "TCS": {"flags": 5, "issues": ["Bond Period Enforceability"]}
                },
                "clauses": {
                    "room_rent_capping": {"risk": "High", "count": 120},
                    "non_compete_2_years": {"risk": "Medium", "count": 45}
                }
            }
            with open(self.db_path, "w") as f:
                json.dump(seed_data, f)

    def check_entity(self, entity_name: str) -> dict:
        """Checks if a company/entity has been flagged by the community."""
        with open(self.db_path, "r") as f:
            data = json.load(f)
        
        # Simple fuzzy match simulation
        for company, info in data["companies"].items():
            if entity_name.lower() in company.lower():
                return info
        return None

    def flag_entity(self, entity_name: str, issue: str):
        """Adds a new flag to the community graph."""
        with open(self.db_path, "r") as f:
            data = json.load(f)
        
        if entity_name not in data["companies"]:
            data["companies"][entity_name] = {"flags": 0, "issues": []}
        
        data["companies"][entity_name]["flags"] += 1
        if issue not in data["companies"][entity_name]["issues"]:
            data["companies"][entity_name]["issues"].append(issue)
            
        with open(self.db_path, "w") as f:
            json.dump(data, f)
