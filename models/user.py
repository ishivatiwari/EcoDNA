from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class TransportMode(str, Enum):
    CAR = "Car"
    BIKE = "Bike"
    PUBLIC_TRANSPORT = "Public Transport"
    WALKING = "Walking"

class FoodPreference(str, Enum):
    VEGAN = "Vegan"
    VEGETARIAN = "Vegetarian"
    MIXED = "Mixed"
    NON_VEGETARIAN = "Non-Vegetarian"

class ConsumptionLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class HomeType(str, Enum):
    APARTMENT = "Apartment"
    INDEPENDENT_HOUSE = "Independent House"

class TransportHabits(BaseModel):
    mode: TransportMode = Field(..., description="Primary mode of transportation")
    distance_km_per_day: float = Field(default=0.0, description="Daily distance traveled in km")

class ElectricityHabits(BaseModel):
    hours_ac: float = Field(default=0.0, description="Daily AC usage in hours")
    hours_fan: float = Field(default=0.0, description="Daily fan usage in hours")
    hours_lights: float = Field(default=0.0, description="Daily lights usage in hours")
    hours_appliances: float = Field(default=0.0, description="Daily appliances usage in hours")

class WasteHabits(BaseModel):
    recycles: bool = Field(default=False, description="Does the user recycle?")
    composts: bool = Field(default=False, description="Does the user compost?")

class UserHabits(BaseModel):
    transport: TransportHabits
    electricity: ElectricityHabits
    food_preference: FoodPreference
    shopping_level: ConsumptionLevel
    waste: WasteHabits
    water_liters_per_day: float = Field(default=150.0, description="Daily water consumption in liters")
    home_type: HomeType

class FootprintBreakdown(BaseModel):
    transport_co2: float
    electricity_co2: float
    food_co2: float
    shopping_co2: float
    waste_co2: float
    total_co2: float
    carbon_score: float = Field(default=0.0, description="Score from 0 to 100, where 100 is excellent sustainability")

class Goal(BaseModel):
    id: str
    description: str
    target_value: float
    current_value: float
    unit: str
    completed: bool = False

    @property
    def progress_percentage(self) -> float:
        if self.target_value == 0:
            return 100.0 if self.current_value == 0 else 0.0
        # If we are reducing, current_value going down means progress.
        # But this depends on context. Let's assume progress is towards the target from an initial value.
        # For simplicity, we just calculate a generic progress percentage if it's an additive goal.
        # If it's a reduction goal, this logic might need refinement in the goals service.
        pct = (self.current_value / self.target_value) * 100
        return min(max(pct, 0.0), 100.0)

class Recommendation(BaseModel):
    category: str
    action: str
    estimated_impact_kg_co2_mo: float
    effort_level: str
