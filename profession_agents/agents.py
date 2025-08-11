#!/usr/bin/env python3
"""
Profession Agents - simple auto-bidder per profession (no external deps)
"""
from typing import Dict

PROFESSION_FACTORS = {
    'Software Developer': 0.85,
    'Designer': 0.8,
    'Engineer': 0.9,
    'Marketer': 0.75,
    'Data Scientist': 0.88,
    'Translator': 0.7,
    'Writer': 0.68,
    'Consultant': 0.92,
}

class AutoBidder:
    @staticmethod
    def generate_bid(profession: str, tender: Dict) -> Dict:
        factor = PROFESSION_FACTORS.get(profession, 0.8)
        base = float(tender.get('budget') or 1000.0)
        amount = max(100.0, round(base * factor, 2))
        return {
            'bidder_name': f"{profession} Agent",
            'bid_amount': amount,
            'message': f"Professional {profession} agent proposes {amount} based on scope and deadline {tender.get('deadline', '')}.",
        }