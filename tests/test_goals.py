import pytest
from services.goals import GoalPlanner

def test_add_and_update_goal():
    planner = GoalPlanner()
    goal = planner.add_goal(
        description="Reduce meat consumption",
        target_value=2.0, # Target 2 days a week
        current_value=0.0,
        unit="days"
    )
    
    assert not goal.completed
    assert goal.id in planner.goals
    
    # Update progress
    updated_goal = planner.update_progress(goal.id, 2.0)
    assert updated_goal.completed
    assert updated_goal.progress_percentage == 100.0

def test_stagnant_goals():
    planner = GoalPlanner()
    planner.add_goal("Hard goal", 100.0, 10.0, "%")
    planner.add_goal("Completed goal", 100.0, 100.0, "%")
    
    stagnant = planner.get_stagnant_goals()
    assert len(stagnant) == 1
    assert stagnant[0].description == "Hard goal"
