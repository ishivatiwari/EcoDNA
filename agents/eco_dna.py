"""EcoDNA Agent — the main orchestrator.

The EcoDNAAgent coordinates all sub-services (calculator, recommender,
goal planner, insight generator, and motivation assistant) to provide
a unified interface for carbon footprint analysis, personalised
recommendations, and sustainability goal management.
"""

import logging

from models.user import UserHabits, FootprintBreakdown, Recommendation, Goal
from services.calculator import CarbonCalculatorService
from services.recommender import RecommendationEngine
from services.goals import GoalPlanner
from services.insights import InsightGenerator, MotivationAssistant

logger = logging.getLogger(__name__)


class EcoDNAAgent:
    """Context-aware AI sustainability assistant.

    Orchestrates the full analysis pipeline: footprint calculation,
    recommendation generation, goal tracking, and weekly reporting.
    Maintains an in-memory analysis history for comparison.

    All sub-service references are private (prefixed with ``_``) to
    enforce encapsulation and prevent external mutation.
    """

    def __init__(self) -> None:
        """Initialise the agent with all required sub-services."""
        self._calculator = CarbonCalculatorService()
        self._recommender = RecommendationEngine()
        self._goal_planner = GoalPlanner()
        self._insight_generator = InsightGenerator()
        self._motivation_assistant = MotivationAssistant()
        self._analysis_history: list[FootprintBreakdown] = []
        logger.info("EcoDNAAgent initialised")

    def analyze_user(self, habits: UserHabits) -> FootprintBreakdown:
        """Calculate the user's carbon footprint and store in history.

        Args:
            habits: Validated user lifestyle data.

        Returns:
            A FootprintBreakdown with per-category and total CO2 values.
        """
        footprint = self._calculator.calculate_daily_footprint(habits)
        self._analysis_history.append(footprint)
        logger.info(
            "Analysis complete: %.2f kg CO2, score=%.1f",
            footprint.total_co2,
            footprint.carbon_score,
        )
        return footprint

    def get_recommendations(
        self, habits: UserHabits, footprint: FootprintBreakdown
    ) -> list[Recommendation]:
        """Generate personalised recommendations based on habits and footprint.

        Args:
            habits: Validated user lifestyle data.
            footprint: Pre-computed carbon footprint breakdown.

        Returns:
            A sorted list of Recommendation objects.
        """
        return self._recommender.generate_recommendations(habits, footprint)

    def generate_weekly_report(
        self,
        habits: UserHabits,
        footprint: FootprintBreakdown | None = None,
    ) -> str:
        """Orchestrate a full weekly report.

        If a pre-computed footprint is provided it will be reused,
        avoiding redundant re-calculation.

        Args:
            habits: Validated user lifestyle data.
            footprint: Optional pre-computed footprint to avoid
                duplicate calculation.

        Returns:
            A formatted weekly report string combining insights
            and motivational messaging.
        """
        if footprint is None:
            footprint = self.analyze_user(habits)

        recommendations = self.get_recommendations(habits, footprint)
        goals = self._goal_planner.get_all_goals()

        insight_text = self._insight_generator.generate_weekly_insight(
            footprint, goals
        )
        motivation_text = self._motivation_assistant.get_motivation_message(
            recommendations
        )

        report = insight_text + "\n" + motivation_text
        logger.info("Weekly report generated")
        return report

    def add_goal(
        self,
        description: str,
        target_value: float,
        current_value: float,
        unit: str,
    ) -> Goal:
        """Add a new sustainability goal.

        Args:
            description: Human-readable goal description.
            target_value: The target value to achieve.
            current_value: The starting / current value.
            unit: Unit of measurement.

        Returns:
            The newly created Goal.
        """
        return self._goal_planner.add_goal(
            description, target_value, current_value, unit
        )

    def get_analysis_history(self) -> list[FootprintBreakdown]:
        """Retrieve all past footprint analyses.

        Returns:
            A list of previous FootprintBreakdown results (copy).
        """
        return list(self._analysis_history)
