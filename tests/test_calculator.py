"""Tests for the CarbonCalculatorService.

Covers basic calculation, zero-emission profiles, high-emission
profiles, water footprint, and home type multiplier effects.
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
from services.calculator import CarbonCalculatorService
from utils.emission_factors import TRANSPORT_FACTORS


def test_calculator_basic():
    """Standard profile should produce valid, positive emissions and score."""
    habits = UserHabits(
        transport=TransportHabits(mode=TransportMode.CAR, distance_km_per_day=10.0),
        electricity=ElectricityHabits(
            hours_ac=2.0, hours_fan=10.0, hours_lights=5.0, hours_appliances=2.0
        ),
        food_preference=FoodPreference.MIXED,
        shopping_level=ConsumptionLevel.MEDIUM,
        waste=WasteHabits(recycles=True, composts=False),
        home_type=HomeType.APARTMENT,
    )

    footprint = CarbonCalculatorService.calculate_daily_footprint(habits)

    # Check transport
    expected_transport = TRANSPORT_FACTORS["Car"] * 10.0
    assert abs(footprint.transport_co2 - expected_transport) < 0.01

    # Check that score is between 0 and 100
    assert 0.0 <= footprint.carbon_score <= 100.0

    # Check total is positive
    assert footprint.total_co2 > 0


def test_calculator_zero_emissions(eco_friendly_habits):
    """Eco-friendly profile should have zero transport/electricity and high score."""
    footprint = CarbonCalculatorService.calculate_daily_footprint(eco_friendly_habits)
    assert footprint.transport_co2 == 0.0
    assert footprint.electricity_co2 == 0.0
    assert footprint.carbon_score > 80.0


def test_calculator_high_emissions(high_emission_habits):
    """High-emission profile should produce low score."""
    footprint = CarbonCalculatorService.calculate_daily_footprint(high_emission_habits)
    assert footprint.total_co2 > 30.0
    assert footprint.carbon_score < 50.0


def test_calculator_water_included():
    """Water CO2 should be included in total when water usage is set."""
    habits = UserHabits(
        transport=TransportHabits(mode=TransportMode.WALKING, distance_km_per_day=0.0),
        electricity=ElectricityHabits(),
        food_preference=FoodPreference.VEGAN,
        shopping_level=ConsumptionLevel.LOW,
        waste=WasteHabits(recycles=True, composts=True),
        water_liters_per_day=500.0,
        home_type=HomeType.APARTMENT,
    )
    footprint = CarbonCalculatorService.calculate_daily_footprint(habits)
    assert footprint.water_co2 > 0
    assert footprint.water_co2 == round(500.0 * 0.001, 2)


def test_calculator_home_type_multiplier():
    """Independent house should produce higher electricity CO2 than apartment."""
    base_habits = dict(
        transport=TransportHabits(mode=TransportMode.WALKING, distance_km_per_day=0.0),
        electricity=ElectricityHabits(
            hours_ac=5.0, hours_fan=8.0, hours_lights=6.0, hours_appliances=3.0
        ),
        food_preference=FoodPreference.VEGETARIAN,
        shopping_level=ConsumptionLevel.MEDIUM,
        waste=WasteHabits(recycles=True, composts=True),
        water_liters_per_day=150.0,
    )

    apartment = UserHabits(**base_habits, home_type=HomeType.APARTMENT)
    house = UserHabits(**base_habits, home_type=HomeType.INDEPENDENT_HOUSE)

    fp_apartment = CarbonCalculatorService.calculate_daily_footprint(apartment)
    fp_house = CarbonCalculatorService.calculate_daily_footprint(house)

    assert fp_house.electricity_co2 > fp_apartment.electricity_co2


def test_calculator_total_is_sum_of_parts():
    """Total CO2 should equal the sum of all category CO2 values."""
    habits = UserHabits(
        transport=TransportHabits(mode=TransportMode.CAR, distance_km_per_day=20.0),
        electricity=ElectricityHabits(hours_ac=4.0, hours_fan=6.0),
        food_preference=FoodPreference.MIXED,
        shopping_level=ConsumptionLevel.HIGH,
        waste=WasteHabits(recycles=False, composts=False),
        water_liters_per_day=200.0,
        home_type=HomeType.APARTMENT,
    )
    fp = CarbonCalculatorService.calculate_daily_footprint(habits)
    expected_total = (
        fp.transport_co2
        + fp.electricity_co2
        + fp.food_co2
        + fp.shopping_co2
        + fp.waste_co2
        + fp.water_co2
    )
    assert abs(fp.total_co2 - expected_total) < 0.02
