import pytest
from models.user import UserHabits, TransportHabits, TransportMode, ElectricityHabits, WasteHabits, FoodPreference, ConsumptionLevel, HomeType
from services.calculator import CarbonCalculatorService
from services.recommender import RecommendationEngine

def test_recommender_high_transport():
    habits = UserHabits(
        transport=TransportHabits(mode=TransportMode.CAR, distance_km_per_day=50.0),
        electricity=ElectricityHabits(),
        food_preference=FoodPreference.VEGAN,
        shopping_level=ConsumptionLevel.LOW,
        waste=WasteHabits(recycles=True, composts=True),
        home_type=HomeType.APARTMENT
    )
    
    footprint = CarbonCalculatorService.calculate_daily_footprint(habits)
    recommendations = RecommendationEngine.generate_recommendations(habits, footprint)
    
    # Should recommend transport improvements
    assert any(rec.category == "Transportation" for rec in recommendations)

def test_recommender_no_waste_management():
    habits = UserHabits(
        transport=TransportHabits(mode=TransportMode.PUBLIC_TRANSPORT, distance_km_per_day=5.0),
        electricity=ElectricityHabits(),
        food_preference=FoodPreference.VEGAN,
        shopping_level=ConsumptionLevel.LOW,
        waste=WasteHabits(recycles=False, composts=False),
        home_type=HomeType.APARTMENT
    )
    
    footprint = CarbonCalculatorService.calculate_daily_footprint(habits)
    recommendations = RecommendationEngine.generate_recommendations(habits, footprint)
    
    # Should recommend waste segregation
    assert any(rec.category == "Waste" for rec in recommendations)
