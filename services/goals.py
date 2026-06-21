"""Goal planning service for EcoDNA.

Manages user sustainability goals including creation, progress
tracking, completion detection, and identification of stagnant goals
that may need renewed attention.
"""

import logging
import uuid
from typing import Dict, List

from models.user import Goal
from utils.exceptions import GoalNotFoundError

logger = logging.getLogger(__name__)

# Threshold below which a goal is considered stagnant
_STAGNANT_PROGRESS_THRESHOLD: float = 20.0


class GoalPlanner:
    """Plans and tracks sustainability goals for a user.

    Goals are stored in memory with UUID-based identifiers.
    In a production system this would be backed by a database.
    """

    def __init__(self) -> None:
        """Initialise an empty goal planner."""
        self.goals: Dict[str, Goal] = {}

    def add_goal(
        self,
        description: str,
        target_value: float,
        current_value: float,
        unit: str,
    ) -> Goal:
        """Create and register a new sustainability goal.

        Args:
            description: Human-readable goal description.
            target_value: The target value to achieve.
            current_value: The starting / current value.
            unit: Unit of measurement (e.g. 'hours', 'days', '%').

        Returns:
            The newly created Goal.
        """
        goal_id = str(uuid.uuid4())
        goal = Goal(
            id=goal_id,
            description=description,
            target_value=target_value,
            current_value=current_value,
            unit=unit,
        )
        self.goals[goal_id] = goal
        logger.info("Added goal '%s' (id=%s)", description, goal_id)
        return goal

    def update_progress(self, goal_id: str, new_value: float) -> Goal:
        """Update a goal's current progress value.

        Automatically marks the goal as completed when
        ``current_value >= target_value``.

        Args:
            goal_id: Unique identifier of the goal.
            new_value: Updated progress value.

        Returns:
            The updated Goal.

        Raises:
            GoalNotFoundError: If no goal exists with the given ID.
        """
        if goal_id not in self.goals:
            logger.warning("Goal not found: %s", goal_id)
            raise GoalNotFoundError(goal_id)

        goal = self.goals[goal_id]
        goal.current_value = new_value

        if goal.current_value >= goal.target_value:
            goal.completed = True
            logger.info("Goal '%s' completed!", goal.description)

        return goal

    def get_all_goals(self) -> List[Goal]:
        """Retrieve all registered goals.

        Returns:
            A list of all Goal objects.
        """
        return list(self.goals.values())

    def get_stagnant_goals(self) -> List[Goal]:
        """Identify goals with little or no progress.

        A goal is considered stagnant if it is not completed and
        its progress is below the stagnant threshold.

        Returns:
            A list of stagnant Goal objects.
        """
        stagnant = [
            g
            for g in self.goals.values()
            if not g.completed and g.progress_percentage < _STAGNANT_PROGRESS_THRESHOLD
        ]
        if stagnant:
            logger.info("Found %d stagnant goals", len(stagnant))
        return stagnant
