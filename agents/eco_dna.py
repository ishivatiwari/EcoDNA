from typing import List
from models.user import UserHabits, FootprintBreakdown, Recommendation, Goal
from services.calculator import CarbonCalculatorService
from services.recommender import RecommendationEngine
from services.goals import GoalPlanner
from services.insights import InsightGenerator, MotivationAssistant

class EcoDNAAgent:
    def __init__(self):
        self.calculator = CarbonCalculatorService()
        self.recommender = RecommendationEngine()
        self.goal_planner = GoalPlanner()
        self.insight_generator = InsightGenerator()
        self.motivation_assistant = MotivationAssistant()

    def analyze_user(self, habits: UserHabits) -> FootprintBreakdown:
        """Calculate the user's carbon footprint."""
        return self.calculator.calculate_daily_footprint(habits)

    def get_recommendations(self, habits: UserHabits, footprint: FootprintBreakdown) -> List[Recommendation]:
        """Generate personalized recommendations based on habits and footprint."""
        return self.recommender.generate_recommendations(habits, footprint)

    def generate_weekly_report(self, habits: UserHabits) -> str:
        """Orchestrate a full weekly report including footprint, recommendations, and insights."""
        footprint = self.analyze_user(habits)
        recommendations = self.get_recommendations(habits, footprint)
        goals = self.goal_planner.get_all_goals()
        
        insight_text = self.insight_generator.generate_weekly_insight(footprint, goals)
        motivation_text = self.motivation_assistant.get_motivation_message(recommendations)
        
        report = insight_text + "\n" + motivation_text
        return report

    def add_goal(self, description: str, target_value: float, current_value: float, unit: str) -> Goal:
        return self.goal_planner.add_goal(description, target_value, current_value, unit)
