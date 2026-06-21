"""Tests for InsightGenerator and MotivationAssistant services.

Validates that weekly insights and motivational messages are
generated correctly for various score tiers and goal states.
"""

import pytest
from models.user import FootprintBreakdown, Goal, Recommendation
from services.insights import InsightGenerator, MotivationAssistant


def _make_footprint(total_co2: float, carbon_score: float) -> FootprintBreakdown:
    """Helper to create a FootprintBreakdown with specific totals."""
    return FootprintBreakdown(
        transport_co2=total_co2 * 0.3,
        electricity_co2=total_co2 * 0.3,
        food_co2=total_co2 * 0.2,
        shopping_co2=total_co2 * 0.1,
        waste_co2=total_co2 * 0.05,
        water_co2=total_co2 * 0.05,
        total_co2=total_co2,
        carbon_score=carbon_score,
    )


def _make_goal(completed: bool = False) -> Goal:
    """Helper to create a Goal."""
    return Goal(
        id="test-goal-1",
        description="Test Goal",
        target_value=10.0,
        current_value=10.0 if completed else 2.0,
        unit="items",
        completed=completed,
    )


class TestInsightGenerator:
    """Tests for InsightGenerator.generate_weekly_insight."""

    def test_excellent_score_insight(self):
        """High score should produce EXCELLENT feedback."""
        footprint = _make_footprint(10.0, 85.0)
        insight = InsightGenerator.generate_weekly_insight(footprint, [])
        assert "[EXCELLENT]" in insight
        assert "10.00 kg CO2" in insight

    def test_moderate_score_insight(self):
        """Moderate score should produce MODERATE feedback."""
        footprint = _make_footprint(20.0, 55.0)
        insight = InsightGenerator.generate_weekly_insight(footprint, [])
        assert "[MODERATE]" in insight

    def test_low_score_insight(self):
        """Low score should produce ATTENTION feedback."""
        footprint = _make_footprint(35.0, 10.0)
        insight = InsightGenerator.generate_weekly_insight(footprint, [])
        assert "[ATTENTION]" in insight

    def test_completed_goals_shown(self):
        """Completed goals should produce SUCCESS message."""
        footprint = _make_footprint(15.0, 60.0)
        goals = [_make_goal(completed=True)]
        insight = InsightGenerator.generate_weekly_insight(footprint, goals)
        assert "[SUCCESS]" in insight
        assert "1 goal(s)" in insight

    def test_no_completed_goals(self):
        """Insight should not contain SUCCESS when no goals are completed."""
        footprint = _make_footprint(15.0, 60.0)
        goals = [_make_goal(completed=False)]
        insight = InsightGenerator.generate_weekly_insight(footprint, goals)
        assert "[SUCCESS]" not in insight

    def test_focus_area_shown(self):
        """Insight should highlight the highest emission area."""
        footprint = _make_footprint(20.0, 50.0)
        insight = InsightGenerator.generate_weekly_insight(footprint, [])
        assert "[FOCUS]" in insight


class TestMotivationAssistant:
    """Tests for MotivationAssistant.get_motivation_message."""

    def test_with_recommendations(self):
        """Should produce a TIP based on the top recommendation."""
        recs = [
            Recommendation(
                category="Transport",
                action="Try cycling.",
                estimated_impact_kg_co2_mo=50.0,
                effort_level="Medium",
            )
        ]
        msg = MotivationAssistant.get_motivation_message(recs)
        assert "[TIP]" in msg
        assert "Try cycling." in msg
        assert "50.0" in msg

    def test_without_recommendations(self):
        """Should return a default positive message when no recs."""
        msg = MotivationAssistant.get_motivation_message([])
        assert "fantastic" in msg.lower()
