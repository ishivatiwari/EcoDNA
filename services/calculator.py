import math
from models.user import UserHabits, FootprintBreakdown
from utils.emission_factors import (
    TRANSPORT_FACTORS,
    ELECTRICITY_FACTORS,
    FOOD_FACTORS,
    SHOPPING_FACTORS,
    WASTE_PENALTY,
    RECYCLING_SAVINGS,
    COMPOSTING_SAVINGS,
    BASELINE_DAILY_CO2
)

class CarbonCalculatorService:
    @staticmethod
    def calculate_daily_footprint(habits: UserHabits) -> FootprintBreakdown:
        # 1. Transport CO2
        transport_factor = TRANSPORT_FACTORS.get(habits.transport.mode.value, 0.0)
        transport_co2 = transport_factor * habits.transport.distance_km_per_day

        # 2. Electricity CO2
        electricity_co2 = (
            (habits.electricity.hours_ac * ELECTRICITY_FACTORS["AC"]) +
            (habits.electricity.hours_fan * ELECTRICITY_FACTORS["Fan"]) +
            (habits.electricity.hours_lights * ELECTRICITY_FACTORS["Lights"]) +
            (habits.electricity.hours_appliances * ELECTRICITY_FACTORS["Appliances"])
        )

        # 3. Food CO2
        food_co2 = FOOD_FACTORS.get(habits.food_preference.value, FOOD_FACTORS["Mixed"])

        # 4. Shopping CO2
        shopping_co2 = SHOPPING_FACTORS.get(habits.shopping_level.value, SHOPPING_FACTORS["Medium"])

        # 5. Waste CO2
        waste_co2 = WASTE_PENALTY
        if habits.waste.recycles:
            waste_co2 -= RECYCLING_SAVINGS
        if habits.waste.composts:
            waste_co2 -= COMPOSTING_SAVINGS
        
        # Ensure waste_co2 doesn't go below 0
        waste_co2 = max(0.0, waste_co2)

        # Total
        total_co2 = transport_co2 + electricity_co2 + food_co2 + shopping_co2 + waste_co2

        # Calculate score (0 to 100). Higher is better.
        # If total_co2 >= 2 * BASELINE, score is 0. If total_co2 == 0, score is 100.
        score = 100 - ((total_co2 / (BASELINE_DAILY_CO2 * 1.5)) * 100)
        carbon_score = max(0.0, min(100.0, score))

        return FootprintBreakdown(
            transport_co2=round(transport_co2, 2),
            electricity_co2=round(electricity_co2, 2),
            food_co2=round(food_co2, 2),
            shopping_co2=round(shopping_co2, 2),
            waste_co2=round(waste_co2, 2),
            total_co2=round(total_co2, 2),
            carbon_score=round(carbon_score, 1)
        )
