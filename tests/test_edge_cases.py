import pytest
from pydantic import ValidationError
from models.user import UserHabits, TransportHabits, TransportMode, ElectricityHabits, WasteHabits, FoodPreference, ConsumptionLevel, HomeType

def test_invalid_transport_mode():
    with pytest.raises(ValidationError):
        TransportHabits(mode="Spaceship", distance_km_per_day=10.0)

def test_invalid_distance():
    # Pydantic usually coerces strings to floats if possible, but let's test a dict to object validation
    try:
        TransportHabits(mode=TransportMode.CAR, distance_km_per_day="not a number")
    except ValidationError:
        pass # Expected
    else:
        pytest.fail("Should have raised ValidationError")

def test_missing_required_fields():
    with pytest.raises(ValidationError):
        # Missing mode
        TransportHabits(distance_km_per_day=10.0)
