"""Insight generation and motivational messaging for EcoDNA.

Produces human-readable weekly sustainability insights and
motivational messages based on the user's footprint analysis,
goal progress, and recommended actions.
"""

import logging
from typing import List

from models.user import Goal, FootprintBreakdown, Recommendation

logger = logging.getLogger(__name__)

# ── Score tier boundaries ────────────────────
_EXCELLENT_SCORE_THRESHOLD: float = 70.0
_MODERATE_SCORE_THRESHOLD: float = 40.0


class InsightGenerator:
    """Generates weekly sustainability insights from footprint data and goals."""

    @staticmethod
    def generate_weekly_insight(
        footprint: FootprintBreakdown, goals: List[Goal]
    ) -> str:
        """Generate a narrative weekly sustainability insight.

        Evaluates the user's carbon score and goal completion to
        produce a personalised summary with actionable messaging.

        Args:
            footprint: The user's computed carbon footprint.
            goals: List of active and completed goals.

        Returns:
            A formatted insight string with status indicators.
        """
        completed_goals = [g for g in goals if g.completed]

        insight = "[REPORT] **Weekly Sustainability Insight**\n\n"
        insight += (
            f"Your estimated daily carbon footprint is "
            f"{footprint.total_co2:.2f} kg CO2.\n"
        )

        # ── Score tier feedback ──────────────────
        if footprint.carbon_score > _EXCELLENT_SCORE_THRESHOLD:
            insight += (
                "[EXCELLENT] Great job! You are doing better than average "
                "in maintaining a low carbon footprint.\n"
            )
        elif footprint.carbon_score > _MODERATE_SCORE_THRESHOLD:
            insight += (
                "[MODERATE] You have a moderate footprint. There are "
                "good opportunities to reduce emissions.\n"
            )
        else:
            insight += (
                "[ATTENTION] Your footprint is on the higher side. "
                "Let's work on some high-impact areas!\n"
            )

        # ── Per-category highlights ──────────────
        categories = [
            ("Transport", footprint.transport_co2),
            ("Electricity", footprint.electricity_co2),
            ("Food", footprint.food_co2),
            ("Shopping", footprint.shopping_co2),
            ("Waste", footprint.waste_co2),
            ("Water", footprint.water_co2),
        ]

        if footprint.total_co2 > 0:
            highest = max(categories, key=lambda c: c[1])
            insight += (
                f"[FOCUS] Your highest emission area is {highest[0]} "
                f"at {highest[1]:.2f} kg CO2/day.\n"
            )

        # ── Goal progress ────────────────────────
        if completed_goals:
            insight += (
                f"[SUCCESS] Awesome work! You've completed "
                f"{len(completed_goals)} goal(s) this week.\n"
            )

        logger.info("Generated weekly insight (score=%.1f)", footprint.carbon_score)
        return insight


class MotivationAssistant:
    """Provides motivational messages to encourage sustainable habits."""

    @staticmethod
    def get_motivation_message(recommendations: List[Recommendation]) -> str:
        """Generate a motivational tip based on the top recommendation.

        Args:
            recommendations: Sorted list of recommendations (highest
                impact first).

        Returns:
            A motivational message string.
        """
        if not recommendations:
            return "You're doing fantastic! Keep up your sustainable habits."

        top_rec = recommendations[0]
        message = (
            f"[TIP] **Did you know?** {top_rec.action}\n"
            f"This could save approximately "
            f"{top_rec.estimated_impact_kg_co2_mo} kg CO2 every month!"
        )
        logger.debug("Motivation message generated for category: %s", top_rec.category)
        return message
