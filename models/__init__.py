"""EcoDNA Data Models module.

Pydantic data models for user habits, carbon footprint breakdowns,
goals, and recommendations used throughout the application.
"""

from .user import (
    TransportMode,
    FoodPreference,
    ConsumptionLevel,
    HomeType,
    TransportHabits,
    ElectricityHabits,
    WasteHabits,
    UserHabits,
    FootprintBreakdown,
    Goal,
    Recommendation,
)

__all__ = [
    "TransportMode",
    "FoodPreference",
    "ConsumptionLevel",
    "HomeType",
    "TransportHabits",
    "ElectricityHabits",
    "WasteHabits",
    "UserHabits",
    "FootprintBreakdown",
    "Goal",
    "Recommendation",
]
