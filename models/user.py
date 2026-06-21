"""Data models for EcoDNA user habits and carbon footprint analysis.

Defines Pydantic models for validated input (user lifestyle data),
computed output (footprint breakdowns), goals, and recommendations.
All numeric inputs are constrained to sensible ranges to prevent
erroneous or malicious data from propagating through the system.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, computed_field

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


class TransportMode(str, Enum):
    """Primary mode of daily transportation."""

    CAR = "Car"
    BIKE = "Bike"
    PUBLIC_TRANSPORT = "Public Transport"
    WALKING = "Walking"


class FoodPreference(str, Enum):
    """Dietary preference affecting food-related carbon emissions."""

    VEGAN = "Vegan"
    VEGETARIAN = "Vegetarian"
    MIXED = "Mixed"
    NON_VEGETARIAN = "Non-Vegetarian"


class ConsumptionLevel(str, Enum):
    """Shopping and consumption frequency level."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class HomeType(str, Enum):
    """Type of dwelling, which affects energy consumption patterns."""

    APARTMENT = "Apartment"
    INDEPENDENT_HOUSE = "Independent House"


class TransportHabits(BaseModel):
    """Transport-related lifestyle data with validated inputs."""

    mode: TransportMode = Field(..., description="Primary mode of transportation")
    distance_km_per_day: float = Field(
        default=0.0,
        ge=0.0,
        le=500.0,
        description="Daily distance traveled in km (0-500)",
    )


class ElectricityHabits(BaseModel):
    """Daily electricity usage habits with validated hour ranges."""

    hours_ac: float = Field(
        default=0.0, ge=0.0, le=24.0, description="Daily AC usage in hours"
    )
    hours_fan: float = Field(
        default=0.0, ge=0.0, le=24.0, description="Daily fan usage in hours"
    )
    hours_lights: float = Field(
        default=0.0, ge=0.0, le=24.0, description="Daily lights usage in hours"
    )
    hours_appliances: float = Field(
        default=0.0, ge=0.0, le=24.0, description="Daily appliances usage in hours"
    )


class WasteHabits(BaseModel):
    """Waste management practices."""

    recycles: bool = Field(default=False, description="Does the user recycle?")
    composts: bool = Field(default=False, description="Does the user compost?")


class UserHabits(BaseModel):
    """Complete user lifestyle data for carbon footprint calculation.

    Aggregates all habit categories into a single validated input
    model that is consumed by the calculator service.
    """

    transport: TransportHabits
    electricity: ElectricityHabits
    food_preference: FoodPreference
    shopping_level: ConsumptionLevel
    waste: WasteHabits
    water_liters_per_day: float = Field(
        default=150.0,
        ge=0.0,
        le=2000.0,
        description="Daily water consumption in liters",
    )
    home_type: HomeType


class FootprintBreakdown(BaseModel):
    """Detailed breakdown of daily carbon emissions by category.

    Provides per-category CO2 values and an overall sustainability
    score where 100 indicates excellent (low emissions) and 0
    indicates poor (high emissions).
    """

    transport_co2: float = Field(
        ..., ge=0.0, description="Transport emissions in kg CO2"
    )
    electricity_co2: float = Field(
        ..., ge=0.0, description="Electricity emissions in kg CO2"
    )
    food_co2: float = Field(..., ge=0.0, description="Food emissions in kg CO2")
    shopping_co2: float = Field(
        ..., ge=0.0, description="Shopping emissions in kg CO2"
    )
    waste_co2: float = Field(..., ge=0.0, description="Waste emissions in kg CO2")
    water_co2: float = Field(
        default=0.0, ge=0.0, description="Water usage emissions in kg CO2"
    )
    total_co2: float = Field(..., ge=0.0, description="Total daily CO2 emissions")
    carbon_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Sustainability score from 0 to 100, where 100 is excellent",
    )


class Goal(BaseModel):
    """A sustainability goal with progress tracking.

    Supports both additive goals (building new habits) and reduction
    goals (reducing consumption). Progress is computed as a percentage
    from 0 to 100.
    """

    id: str
    description: str
    target_value: float = Field(..., description="Target value to reach")
    current_value: float = Field(..., description="Current progress value")
    unit: str
    completed: bool = False

    @computed_field  # type: ignore[misc]
    @property
    def progress_percentage(self) -> float:
        """Calculate goal progress as a percentage (0-100).

        For additive goals the percentage rises as current_value
        approaches target_value.  The result is clamped to [0, 100].
        """
        if self.target_value == 0:
            return 100.0 if self.current_value == 0 else 0.0
        pct = (self.current_value / self.target_value) * 100
        return min(max(pct, 0.0), 100.0)


class Recommendation(BaseModel):
    """A personalised sustainability recommendation.

    Contains an actionable suggestion, its estimated monthly CO2
    impact, and an effort rating to help users prioritise changes.
    """

    category: str = Field(..., description="Category of the recommendation")
    action: str = Field(..., description="Actionable suggestion text")
    estimated_impact_kg_co2_mo: float = Field(
        ..., ge=0.0, description="Estimated monthly CO2 savings in kg"
    )
    effort_level: str = Field(
        ..., description="Effort required: Low, Medium, or High"
    )
