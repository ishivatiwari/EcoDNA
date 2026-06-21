"""Carbon footprint calculator service.

Computes daily carbon emissions from user lifestyle data across
transport, electricity, food, shopping, waste, and water categories.
Produces a sustainability score normalised to a 0-100 scale.
"""

import logging
from functools import lru_cache
from typing import Tuple

from models.user import UserHabits, FootprintBreakdown
from utils.emission_factors import (
    TRANSPORT_FACTORS,
    ELECTRICITY_FACTORS,
    HOME_TYPE_MULTIPLIERS,
    FOOD_FACTORS,
    SHOPPING_FACTORS,
    WASTE_PENALTY,
    RECYCLING_SAVINGS,
    COMPOSTING_SAVINGS,
    WATER_CO2_PER_LITRE,
    BASELINE_DAILY_CO2,
    SCORE_SCALING_FACTOR,
)

logger = logging.getLogger(__name__)


class CarbonCalculatorService:
    """Service that computes a user's daily carbon footprint.

    Applies published emission factors to user-reported habits
    and derives a normalised sustainability score.
    """

    @staticmethod
    def _compute_transport_co2(mode_value: str, distance_km: float) -> float:
        """Calculate transport-related CO2 emissions.

        Args:
            mode_value: String value of the transport mode enum.
            distance_km: Daily distance traveled in kilometres.

        Returns:
            Transport CO2 emissions in kg.
        """
        factor = TRANSPORT_FACTORS.get(mode_value, 0.0)
        return factor * distance_km

    @staticmethod
    def _compute_electricity_co2(
        hours_ac: float,
        hours_fan: float,
        hours_lights: float,
        hours_appliances: float,
        home_type_value: str,
    ) -> float:
        """Calculate electricity-related CO2 emissions.

        Applies a home-type multiplier to account for higher energy
        use in independent houses vs apartments.

        Args:
            hours_ac: Daily AC usage in hours.
            hours_fan: Daily fan usage in hours.
            hours_lights: Daily lights usage in hours.
            hours_appliances: Daily appliance usage in hours.
            home_type_value: String value of the home type enum.

        Returns:
            Electricity CO2 emissions in kg.
        """
        home_multiplier = HOME_TYPE_MULTIPLIERS.get(home_type_value, 1.0)
        base_co2 = (
            (hours_ac * ELECTRICITY_FACTORS["AC"])
            + (hours_fan * ELECTRICITY_FACTORS["Fan"])
            + (hours_lights * ELECTRICITY_FACTORS["Lights"])
            + (hours_appliances * ELECTRICITY_FACTORS["Appliances"])
        )
        return base_co2 * home_multiplier

    @staticmethod
    def _compute_waste_co2(recycles: bool, composts: bool) -> float:
        """Calculate waste-related CO2 emissions.

        Recycling and composting each reduce the base waste penalty.

        Args:
            recycles: Whether the user recycles.
            composts: Whether the user composts.

        Returns:
            Waste CO2 emissions in kg (non-negative).
        """
        waste_co2 = WASTE_PENALTY
        if recycles:
            waste_co2 -= RECYCLING_SAVINGS
        if composts:
            waste_co2 -= COMPOSTING_SAVINGS
        return max(0.0, waste_co2)

    @staticmethod
    def _compute_water_co2(water_liters: float) -> float:
        """Calculate water-related CO2 emissions.

        Accounts for energy used in water pumping, heating, and
        wastewater treatment.

        Args:
            water_liters: Daily water usage in litres.

        Returns:
            Water CO2 emissions in kg.
        """
        return water_liters * WATER_CO2_PER_LITRE

    @staticmethod
    def _compute_carbon_score(total_co2: float) -> float:
        """Compute sustainability score on a 0-100 scale.

        A score of 100 means zero emissions; 0 means emissions are
        at or above the scaled baseline.

        Args:
            total_co2: Total daily CO2 emissions in kg.

        Returns:
            Clamped sustainability score between 0.0 and 100.0.
        """
        score = 100 - ((total_co2 / (BASELINE_DAILY_CO2 * SCORE_SCALING_FACTOR)) * 100)
        return max(0.0, min(100.0, score))

    @staticmethod
    def calculate_daily_footprint(habits: UserHabits) -> FootprintBreakdown:
        """Calculate the complete daily carbon footprint for a user.

        Aggregates emissions from transport, electricity, food,
        shopping, waste, and water categories.

        Args:
            habits: Validated user lifestyle data.

        Returns:
            A FootprintBreakdown with per-category and total CO2
            values plus a sustainability score.
        """
        logger.info("Calculating daily footprint for user habits")

        transport_co2 = CarbonCalculatorService._compute_transport_co2(
            habits.transport.mode.value, habits.transport.distance_km_per_day
        )

        electricity_co2 = CarbonCalculatorService._compute_electricity_co2(
            habits.electricity.hours_ac,
            habits.electricity.hours_fan,
            habits.electricity.hours_lights,
            habits.electricity.hours_appliances,
            habits.home_type.value,
        )

        food_co2 = FOOD_FACTORS.get(
            habits.food_preference.value, FOOD_FACTORS["Mixed"]
        )

        shopping_co2 = SHOPPING_FACTORS.get(
            habits.shopping_level.value, SHOPPING_FACTORS["Medium"]
        )

        waste_co2 = CarbonCalculatorService._compute_waste_co2(
            habits.waste.recycles, habits.waste.composts
        )

        water_co2 = CarbonCalculatorService._compute_water_co2(
            habits.water_liters_per_day
        )

        total_co2 = (
            transport_co2
            + electricity_co2
            + food_co2
            + shopping_co2
            + waste_co2
            + water_co2
        )

        carbon_score = CarbonCalculatorService._compute_carbon_score(total_co2)

        logger.debug(
            "Footprint calculated: total=%.2f kg CO2, score=%.1f",
            total_co2,
            carbon_score,
        )

        return FootprintBreakdown(
            transport_co2=round(transport_co2, 2),
            electricity_co2=round(electricity_co2, 2),
            food_co2=round(food_co2, 2),
            shopping_co2=round(shopping_co2, 2),
            waste_co2=round(waste_co2, 2),
            water_co2=round(water_co2, 2),
            total_co2=round(total_co2, 2),
            carbon_score=round(carbon_score, 1),
        )
