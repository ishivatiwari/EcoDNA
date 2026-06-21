"""Tests for the GoalPlanner service.

Covers goal creation, progress updates, completion detection,
stagnant goal identification, and error handling.
"""

import pytest
from services.goals import GoalPlanner
from utils.exceptions import GoalNotFoundError


def test_add_and_update_goal(goal_planner):
    """Should create a goal and mark it complete on progress update."""
    goal = goal_planner.add_goal(
        description="Reduce meat consumption",
        target_value=2.0,
        current_value=0.0,
        unit="days",
    )

    assert not goal.completed
    assert goal.id in goal_planner.goals

    # Update progress to meet target
    updated_goal = goal_planner.update_progress(goal.id, 2.0)
    assert updated_goal.completed
    assert updated_goal.progress_percentage == 100.0


def test_stagnant_goals(goal_planner):
    """Should identify goals with low progress as stagnant."""
    goal_planner.add_goal("Hard goal", 100.0, 10.0, "%")
    goal_planner.add_goal("Completed goal", 100.0, 100.0, "%")

    stagnant = goal_planner.get_stagnant_goals()
    assert len(stagnant) == 1
    assert stagnant[0].description == "Hard goal"


def test_update_nonexistent_goal(goal_planner):
    """Should raise GoalNotFoundError for unknown goal IDs."""
    with pytest.raises(GoalNotFoundError):
        goal_planner.update_progress("nonexistent-id", 5.0)


def test_get_all_goals_empty(goal_planner):
    """Empty planner should return empty list."""
    assert goal_planner.get_all_goals() == []


def test_get_all_goals_multiple(goal_planner):
    """Should return all added goals."""
    goal_planner.add_goal("Goal A", 10.0, 0.0, "items")
    goal_planner.add_goal("Goal B", 20.0, 5.0, "km")

    all_goals = goal_planner.get_all_goals()
    assert len(all_goals) == 2
    descriptions = {g.description for g in all_goals}
    assert descriptions == {"Goal A", "Goal B"}


def test_goal_progress_percentage_zero_target():
    """Goal with zero target should show 100% if current is also 0."""
    from models.user import Goal

    goal = Goal(id="z", description="Zero", target_value=0.0, current_value=0.0, unit="x")
    assert goal.progress_percentage == 100.0

    goal2 = Goal(id="z2", description="Zero2", target_value=0.0, current_value=5.0, unit="x")
    assert goal2.progress_percentage == 0.0
