"""Tests for the EcoDNAAgent orchestrator.

Verifies that the agent correctly coordinates its sub-services
and maintains analysis history.
"""

import pytest
from agents.eco_dna import EcoDNAAgent
from models.user import FootprintBreakdown, Recommendation, Goal


def test_agent_analyze_user(agent, moderate_habits):
    """Agent should return a valid FootprintBreakdown."""
    footprint = agent.analyze_user(moderate_habits)
    assert isinstance(footprint, FootprintBreakdown)
    assert footprint.total_co2 > 0
    assert 0.0 <= footprint.carbon_score <= 100.0


def test_agent_get_recommendations(agent, high_emission_habits):
    """Agent should return recommendations for high-emission habits."""
    footprint = agent.analyze_user(high_emission_habits)
    recommendations = agent.get_recommendations(high_emission_habits, footprint)
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    assert all(isinstance(r, Recommendation) for r in recommendations)


def test_agent_weekly_report_with_precomputed(agent, moderate_habits):
    """Weekly report should reuse pre-computed footprint (no double-calc)."""
    footprint = agent.analyze_user(moderate_habits)
    history_before = len(agent.get_analysis_history())

    report = agent.generate_weekly_report(moderate_habits, footprint=footprint)

    # Should NOT have added a new history entry since footprint was passed
    assert len(agent.get_analysis_history()) == history_before
    assert isinstance(report, str)
    assert len(report) > 0


def test_agent_weekly_report_without_precomputed(agent, moderate_habits):
    """Weekly report should compute footprint when none is provided."""
    report = agent.generate_weekly_report(moderate_habits)
    assert isinstance(report, str)
    assert len(report) > 0
    # Should have stored the analysis
    assert len(agent.get_analysis_history()) >= 1


def test_agent_add_goal(agent):
    """Agent should delegate goal creation to goal planner."""
    goal = agent.add_goal("Test Goal", 10.0, 0.0, "items")
    assert isinstance(goal, Goal)
    assert goal.description == "Test Goal"
    assert not goal.completed


def test_agent_analysis_history(agent, eco_friendly_habits, high_emission_habits):
    """Agent should maintain ordered analysis history."""
    agent.analyze_user(eco_friendly_habits)
    agent.analyze_user(high_emission_habits)

    history = agent.get_analysis_history()
    assert len(history) == 2
    # Eco-friendly should have lower CO2 than high-emission
    assert history[0].total_co2 < history[1].total_co2
