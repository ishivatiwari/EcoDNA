"""Tests for the RecommendationEngine.

Validates that the engine produces correct recommendations based
on different user profiles and emission patterns.
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
from services.recommender import RecommendationEngine


def test_recommender_high_transport():
    """Should recommend transport improvements for car users."""
    habits = UserHabits(
        transport=TransportHabits(mode=TransportMode.CAR, distance_km_per_day=50.0),
        electricity=ElectricityHabits(),
        food_preference=FoodPreference.VEGAN,
        shopping_level=ConsumptionLevel.LOW,
        waste=WasteHabits(recycles=True, composts=True),
        home_type=HomeType.APARTMENT,
    )

    footprint = CarbonCalculatorService.calculate_daily_footprint(habits)
    recommendations = RecommendationEngine.generate_recommendations(habits, footprint)

    assert any(rec.category == "Transportation" for rec in recommendations)


def test_recommender_no_waste_management():
    """Should recommend waste segregation for non-recyclers."""
    habits = UserHabits(
        transport=TransportHabits(
            mode=TransportMode.PUBLIC_TRANSPORT, distance_km_per_day=5.0
        ),
        electricity=ElectricityHabits(),
        food_preference=FoodPreference.VEGAN,
        shopping_level=ConsumptionLevel.LOW,
        waste=WasteHabits(recycles=False, composts=False),
        home_type=HomeType.APARTMENT,
    )

    footprint = CarbonCalculatorService.calculate_daily_footprint(habits)
    recommendations = RecommendationEngine.generate_recommendations(habits, footprint)

    assert any(rec.category == "Waste" for rec in recommendations)


def test_recommender_high_ac_usage():
    """Should recommend energy savings for high AC users."""
    habits = UserHabits(
        transport=TransportHabits(mode=TransportMode.WALKING, distance_km_per_day=2.0),
        electricity=ElectricityHabits(hours_ac=8.0, hours_fan=12.0),
        food_preference=FoodPreference.VEGAN,
        shopping_level=ConsumptionLevel.LOW,
        waste=WasteHabits(recycles=True, composts=True),
        home_type=HomeType.APARTMENT,
    )

    footprint = CarbonCalculatorService.calculate_daily_footprint(habits)
    recommendations = RecommendationEngine.generate_recommendations(habits, footprint)

    assert any(rec.category == "Energy" for rec in recommendations)


def test_recommender_high_water_usage():
    """Should recommend water reduction for high water users."""
    habits = UserHabits(
        transport=TransportHabits(mode=TransportMode.WALKING, distance_km_per_day=2.0),
        electricity=ElectricityHabits(),
        food_preference=FoodPreference.VEGAN,
        shopping_level=ConsumptionLevel.LOW,
        waste=WasteHabits(recycles=True, composts=True),
        water_liters_per_day=300.0,
        home_type=HomeType.APARTMENT,
    )

    footprint = CarbonCalculatorService.calculate_daily_footprint(habits)
    recommendations = RecommendationEngine.generate_recommendations(habits, footprint)

    assert any(rec.category == "Water" for rec in recommendations)


def test_recommender_eco_user_few_recs(eco_friendly_habits):
    """Eco-friendly users should get fewer recommendations."""
    footprint = CarbonCalculatorService.calculate_daily_footprint(eco_friendly_habits)
    recs = RecommendationEngine.generate_recommendations(eco_friendly_habits, footprint)

    # Should have minimal recommendations
    assert len(recs) <= 2


def test_recommender_sorted_by_impact(high_emission_habits):
    """Recommendations should be sorted by descending impact."""
    footprint = CarbonCalculatorService.calculate_daily_footprint(high_emission_habits)
    recs = RecommendationEngine.generate_recommendations(
        high_emission_habits, footprint
    )

    if len(recs) >= 2:
        impacts = [r.estimated_impact_kg_co2_mo for r in recs]
        assert impacts == sorted(impacts, reverse=True)


def test_recommender_zero_emissions():
    """Zero total emissions should produce no recommendations.

    Constructs a FootprintBreakdown directly with all-zero values
    to guarantee the zero-emissions code path is exercised.
    """
    from models.user import FootprintBreakdown

    habits = UserHabits(
        transport=TransportHabits(mode=TransportMode.WALKING, distance_km_per_day=0.0),
        electricity=ElectricityHabits(),
        food_preference=FoodPreference.VEGAN,
        shopping_level=ConsumptionLevel.LOW,
        waste=WasteHabits(recycles=True, composts=True),
        water_liters_per_day=0.0,
        home_type=HomeType.APARTMENT,
    )

    # Force a truly zero footprint to test the branch
    zero_footprint = FootprintBreakdown(
        transport_co2=0.0,
        electricity_co2=0.0,
        food_co2=0.0,
        shopping_co2=0.0,
        waste_co2=0.0,
        water_co2=0.0,
        total_co2=0.0,
        carbon_score=100.0,
    )

    recs = RecommendationEngine.generate_recommendations(habits, zero_footprint)
    assert recs == []

