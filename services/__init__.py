"""EcoDNA Services module.

Core business logic services including carbon footprint calculation,
personalized recommendations, goal planning, and insight generation.
"""

from .calculator import CarbonCalculatorService
from .recommender import RecommendationEngine
from .goals import GoalPlanner
from .insights import InsightGenerator, MotivationAssistant

__all__ = [
    "CarbonCalculatorService",
    "RecommendationEngine",
    "GoalPlanner",
    "InsightGenerator",
    "MotivationAssistant",
]
