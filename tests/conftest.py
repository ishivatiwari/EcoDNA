"""Shared test fixtures for EcoDNA test suite.

Provides reusable fixtures for common test data and service
instances, reducing duplication across test modules.
"""

import pytest

from models.user import (
    UserHabits,
    TransportHabits,
    TransportMode,
    ElectricityHabits,
    WasteHabits,
    FoodPreference,
    ConsumptionLevel,
    HomeType,
)
from agents.eco_dna import EcoDNAAgent
from services.goals import GoalPlanner


@pytest.fixture
def eco_friendly_habits() -> UserHabits:
    """A very eco-friendly user profile (walking, vegan, low consumption)."""
    return UserHabits(
        transport=TransportHabits(
            mode=TransportMode.WALKING, distance_km_per_day=5.0
        ),
        electricity=ElectricityHabits(
            hours_ac=0.0, hours_fan=0.0, hours_lights=0.0, hours_appliances=0.0
        ),
        food_preference=FoodPreference.VEGAN,
        shopping_level=ConsumptionLevel.LOW,
        waste=WasteHabits(recycles=True, composts=True),
        water_liters_per_day=80.0,
        home_type=HomeType.APARTMENT,
    )


@pytest.fixture
def high_emission_habits() -> UserHabits:
    """A high-emission user profile (car, non-veg, high consumption)."""
    return UserHabits(
        transport=TransportHabits(
            mode=TransportMode.CAR, distance_km_per_day=50.0
        ),
        electricity=ElectricityHabits(
            hours_ac=8.0, hours_fan=12.0, hours_lights=6.0, hours_appliances=4.0
        ),
        food_preference=FoodPreference.NON_VEGETARIAN,
        shopping_level=ConsumptionLevel.HIGH,
        waste=WasteHabits(recycles=False, composts=False),
        water_liters_per_day=300.0,
        home_type=HomeType.INDEPENDENT_HOUSE,
    )


@pytest.fixture
def moderate_habits() -> UserHabits:
    """A moderate user profile."""
    return UserHabits(
        transport=TransportHabits(
            mode=TransportMode.PUBLIC_TRANSPORT, distance_km_per_day=15.0
        ),
        electricity=ElectricityHabits(
            hours_ac=3.0, hours_fan=8.0, hours_lights=4.0, hours_appliances=2.0
        ),
        food_preference=FoodPreference.MIXED,
        shopping_level=ConsumptionLevel.MEDIUM,
        waste=WasteHabits(recycles=True, composts=False),
        water_liters_per_day=150.0,
        home_type=HomeType.APARTMENT,
    )


@pytest.fixture
def agent() -> EcoDNAAgent:
    """A fresh EcoDNAAgent instance."""
    return EcoDNAAgent()


@pytest.fixture
def goal_planner() -> GoalPlanner:
    """A fresh GoalPlanner instance."""
    return GoalPlanner()
