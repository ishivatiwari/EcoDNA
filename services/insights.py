from typing import List
from models.user import Goal, FootprintBreakdown, Recommendation

class InsightGenerator:
    @staticmethod
    def generate_weekly_insight(footprint: FootprintBreakdown, goals: List[Goal]) -> str:
        completed_goals = [g for g in goals if g.completed]
        
        insight = "[REPORT] **Weekly Sustainability Insight**\n\n"
        insight += f"Your estimated daily carbon footprint is {footprint.total_co2:.2f} kg CO2.\n"
        
        if footprint.carbon_score > 70:
            insight += "[EXCELLENT] Great job! You are doing better than average in maintaining a low carbon footprint.\n"
        elif footprint.carbon_score > 40:
            insight += "[MODERATE] You have a moderate footprint. There are good opportunities to reduce emissions.\n"
        else:
            insight += "[ATTENTION] Your footprint is on the higher side. Let's work on some high-impact areas!\n"

        if completed_goals:
            insight += f"[SUCCESS] Awesome work! You've completed {len(completed_goals)} goals this week.\n"
        
        return insight

class MotivationAssistant:
    @staticmethod
    def get_motivation_message(recommendations: List[Recommendation]) -> str:
        if not recommendations:
            return "You're doing fantastic! Keep up your sustainable habits."
        
        top_rec = recommendations[0]
        return f"[TIP] **Did you know?** {top_rec.action}\nThis could save approximately {top_rec.estimated_impact_kg_co2_mo} kg CO2 every month!"
