import pytest
from models.user import UserHabits, TransportHabits, TransportMode, ElectricityHabits, WasteHabits, FoodPreference, ConsumptionLevel, HomeType
from services.calculator import CarbonCalculatorService
from utils.emission_factors import TRANSPORT_FACTORS

def test_calculator_basic():
    habits = UserHabits(
        transport=TransportHabits(mode=TransportMode.CAR, distance_km_per_day=10.0),
        electricity=ElectricityHabits(hours_ac=2.0, hours_fan=10.0, hours_lights=5.0, hours_appliances=2.0),
        food_preference=FoodPreference.MIXED,
        shopping_level=ConsumptionLevel.MEDIUM,
        waste=WasteHabits(recycles=True, composts=False),
        home_type=HomeType.APARTMENT
    )
    
    footprint = CarbonCalculatorService.calculate_daily_footprint(habits)
    
    # Check transport
    expected_transport = TRANSPORT_FACTORS["Car"] * 10.0
    assert abs(footprint.transport_co2 - expected_transport) < 0.01

    # Check that score is between 0 and 100
    assert 0.0 <= footprint.carbon_score <= 100.0
    
    # Check total is positive
    assert footprint.total_co2 > 0

def test_calculator_zero_emissions():
    habits = UserHabits(
        transport=TransportHabits(mode=TransportMode.WALKING, distance_km_per_day=5.0),
        electricity=ElectricityHabits(hours_ac=0, hours_fan=0, hours_lights=0, hours_appliances=0),
        food_preference=FoodPreference.VEGAN,
        shopping_level=ConsumptionLevel.LOW,
        waste=WasteHabits(recycles=True, composts=True),
        home_type=HomeType.APARTMENT
    )
    
    footprint = CarbonCalculatorService.calculate_daily_footprint(habits)
    assert footprint.transport_co2 == 0.0
    assert footprint.electricity_co2 == 0.0
    # Should have a high score
    assert footprint.carbon_score > 80.0
