from typing import List, Dict
import uuid
from models.user import Goal

class GoalPlanner:
    def __init__(self):
        self.goals: Dict[str, Goal] = {}

    def add_goal(self, description: str, target_value: float, current_value: float, unit: str) -> Goal:
        goal_id = str(uuid.uuid4())
        goal = Goal(
            id=goal_id,
            description=description,
            target_value=target_value,
            current_value=current_value,
            unit=unit
        )
        self.goals[goal_id] = goal
        return goal

    def update_progress(self, goal_id: str, new_value: float) -> Goal:
        if goal_id in self.goals:
            goal = self.goals[goal_id]
            goal.current_value = new_value
            # For simplicity, assuming if we reach target, it's completed
            # Note: For reductions, logic might be `new_value <= target_value`
            if goal.current_value >= goal.target_value:
                goal.completed = True
            return goal
        raise ValueError(f"Goal with id {goal_id} not found.")

    def get_all_goals(self) -> List[Goal]:
        return list(self.goals.values())

    def get_stagnant_goals(self) -> List[Goal]:
        # Simplistic logic: if it's not complete and progress is low
        return [g for g in self.goals.values() if not g.completed and g.progress_percentage < 20.0]
