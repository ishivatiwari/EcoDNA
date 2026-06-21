"""Custom exception classes for the EcoDNA application.

Provides domain-specific exceptions for clearer error handling
and more informative error messages throughout the system.
"""


class EcoDNAError(Exception):
    """Base exception for all EcoDNA-related errors."""


class GoalNotFoundError(EcoDNAError):
    """Raised when a goal with the specified ID cannot be found."""

    def __init__(self, goal_id: str) -> None:
        self.goal_id = goal_id
        super().__init__(f"Goal with id '{goal_id}' not found.")


class InvalidHabitDataError(EcoDNAError):
    """Raised when user habit data fails domain-specific validation."""

    def __init__(self, field: str, reason: str) -> None:
        self.field = field
        self.reason = reason
        super().__init__(f"Invalid data for '{field}': {reason}")
