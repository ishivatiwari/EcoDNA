"""Emission factors and constants for EcoDNA carbon footprint calculations.

All values are approximate representations in kg CO2e for educational
purposes, sourced from publicly available environmental data and
research papers. These factors enable standardised estimation of
individual daily carbon emissions across multiple lifestyle categories.

References:
    - EPA Greenhouse Gas Equivalencies Calculator
    - DEFRA emission conversion factors
    - IPCC AR6 guidelines for national GHG inventories
"""

from typing import Final

# ──────────────────────────────────────────────
# Transportation (kg CO2 per km)
# ──────────────────────────────────────────────
TRANSPORT_FACTORS: Final[dict[str, float]] = {
    "Car": 0.192,
    "Bike": 0.03,             # Assuming motorcycle; bicycle is 0.0
    "Public Transport": 0.041,
    "Walking": 0.0,
}

# ──────────────────────────────────────────────
# Electricity (kg CO2 per hour of typical usage)
# Assumes average wattage and India standard grid emission factor
# ──────────────────────────────────────────────
ELECTRICITY_FACTORS: Final[dict[str, float]] = {
    "AC": 1.5,           # ~1500W
    "Fan": 0.075,        # ~75W
    "Lights": 0.05,      # ~50W (multiple bulbs)
    "Appliances": 0.5,   # Mixed average
}

# ──────────────────────────────────────────────
# Home type multiplier for electricity usage
# Independent houses typically use more energy
# ──────────────────────────────────────────────
HOME_TYPE_MULTIPLIERS: Final[dict[str, float]] = {
    "Apartment": 1.0,
    "Independent House": 1.3,
}

# ──────────────────────────────────────────────
# Food (kg CO2 per day based on dietary preference)
# ──────────────────────────────────────────────
FOOD_FACTORS: Final[dict[str, float]] = {
    "Vegan": 2.9,
    "Vegetarian": 3.8,
    "Mixed": 5.6,
    "Non-Vegetarian": 7.2,
}

# ──────────────────────────────────────────────
# Shopping / consumption (kg CO2 per day, estimated)
# ──────────────────────────────────────────────
SHOPPING_FACTORS: Final[dict[str, float]] = {
    "Low": 2.0,
    "Medium": 5.0,
    "High": 10.0,
}

# ──────────────────────────────────────────────
# Waste management (kg CO2 per day)
# ──────────────────────────────────────────────
WASTE_PENALTY: Final[float] = 1.5
RECYCLING_SAVINGS: Final[float] = 0.5
COMPOSTING_SAVINGS: Final[float] = 0.3

# ──────────────────────────────────────────────
# Water usage (kg CO2 per litre per day)
# Covers energy for heating, pumping, and treatment
# ──────────────────────────────────────────────
WATER_CO2_PER_LITRE: Final[float] = 0.001

# ──────────────────────────────────────────────
# Recommendation engine thresholds
# ──────────────────────────────────────────────
HIGH_CATEGORY_THRESHOLD_PCT: Final[float] = 30.0
MODERATE_CATEGORY_THRESHOLD_PCT: Final[float] = 25.0
HIGH_AC_HOURS_THRESHOLD: Final[float] = 4.0
TRANSPORT_REDUCTION_FACTOR: Final[float] = 0.4
DAYS_PER_MONTH: Final[int] = 30
ENERGY_SAVINGS_KG_CO2_MO: Final[float] = 30.0
FOOD_SWAP_SAVINGS_KG_CO2_MO: Final[float] = 15.0
WASTE_MGMT_SAVINGS_KG_CO2_MO: Final[float] = 15.0
WATER_SAVINGS_KG_CO2_MO: Final[float] = 5.0

# ──────────────────────────────────────────────
# Scoring baseline
# Average total CO2 per day for carbon score calculation
# Assumes ~20-30 kg CO2/day per person in India
# ──────────────────────────────────────────────
BASELINE_DAILY_CO2: Final[float] = 25.0
SCORE_SCALING_FACTOR: Final[float] = 1.5
