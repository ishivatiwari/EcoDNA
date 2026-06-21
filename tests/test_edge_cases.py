"""Edge-case and validation tests for EcoDNA models.

Ensures Pydantic validation correctly rejects invalid data including
wrong enum values, non-numeric inputs, missing required fields,
and out-of-range values.
"""

import pytest
from pydantic import ValidationError
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


def test_invalid_transport_mode():
    """Should reject an unknown transport mode."""
    with pytest.raises(ValidationError):
        TransportHabits(mode="Spaceship", distance_km_per_day=10.0)


def test_invalid_distance_type():
    """Should reject non-numeric distance values."""
    with pytest.raises(ValidationError):
        TransportHabits(mode=TransportMode.CAR, distance_km_per_day="not a number")


def test_missing_required_fields():
    """Should reject when required 'mode' field is missing."""
    with pytest.raises(ValidationError):
        TransportHabits(distance_km_per_day=10.0)


def test_negative_distance_rejected():
    """Should reject negative distance values (ge=0 constraint)."""
    with pytest.raises(ValidationError):
        TransportHabits(mode=TransportMode.CAR, distance_km_per_day=-5.0)


def test_excessive_distance_rejected():
    """Should reject distances exceeding 500 km (le=500 constraint)."""
    with pytest.raises(ValidationError):
        TransportHabits(mode=TransportMode.CAR, distance_km_per_day=600.0)


def test_negative_ac_hours_rejected():
    """Should reject negative AC hours."""
    with pytest.raises(ValidationError):
        ElectricityHabits(hours_ac=-1.0)


def test_excessive_ac_hours_rejected():
    """Should reject AC hours exceeding 24."""
    with pytest.raises(ValidationError):
        ElectricityHabits(hours_ac=25.0)


def test_negative_water_rejected():
    """Should reject negative water usage."""
    with pytest.raises(ValidationError):
        UserHabits(
            transport=TransportHabits(mode=TransportMode.CAR, distance_km_per_day=10.0),
            electricity=ElectricityHabits(),
            food_preference=FoodPreference.VEGAN,
            shopping_level=ConsumptionLevel.LOW,
            waste=WasteHabits(),
            water_liters_per_day=-50.0,
            home_type=HomeType.APARTMENT,
        )


def test_excessive_water_rejected():
    """Should reject water usage exceeding 2000 litres."""
    with pytest.raises(ValidationError):
        UserHabits(
            transport=TransportHabits(mode=TransportMode.CAR, distance_km_per_day=10.0),
            electricity=ElectricityHabits(),
            food_preference=FoodPreference.VEGAN,
            shopping_level=ConsumptionLevel.LOW,
            waste=WasteHabits(),
            water_liters_per_day=3000.0,
            home_type=HomeType.APARTMENT,
        )


def test_invalid_food_preference():
    """Should reject an unknown food preference."""
    with pytest.raises(ValidationError):
        UserHabits(
            transport=TransportHabits(mode=TransportMode.CAR, distance_km_per_day=10.0),
            electricity=ElectricityHabits(),
            food_preference="Pescatarian",
            shopping_level=ConsumptionLevel.LOW,
            waste=WasteHabits(),
            home_type=HomeType.APARTMENT,
        )


def test_zero_distance_allowed():
    """Zero distance should be accepted."""
    habits = TransportHabits(mode=TransportMode.CAR, distance_km_per_day=0.0)
    assert habits.distance_km_per_day == 0.0
