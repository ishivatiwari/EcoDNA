"""Recommendation engine for EcoDNA.

Analyses a user's carbon footprint breakdown and lifestyle habits to
generate personalised, prioritised recommendations for reducing
environmental impact.  Recommendations are sorted by estimated
monthly CO2 savings so the highest-impact actions appear first.
"""

import logging
from typing import List

from models.user import (
    UserHabits,
    FootprintBreakdown,
    Recommendation,
    TransportMode,
    FoodPreference,
)
from utils.emission_factors import (
    HIGH_CATEGORY_THRESHOLD_PCT,
    MODERATE_CATEGORY_THRESHOLD_PCT,
    HIGH_AC_HOURS_THRESHOLD,
    TRANSPORT_REDUCTION_FACTOR,
    DAYS_PER_MONTH,
    ENERGY_SAVINGS_KG_CO2_MO,
    FOOD_SWAP_SAVINGS_KG_CO2_MO,
    WASTE_MGMT_SAVINGS_KG_CO2_MO,
    WATER_SAVINGS_KG_CO2_MO,
)

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generates context-aware sustainability recommendations.

    Examines per-category emission shares and absolute usage values
    to produce actionable suggestions with effort ratings and
    estimated monthly impact.
    """

    @staticmethod
    def generate_recommendations(
        habits: UserHabits, footprint: FootprintBreakdown
    ) -> List[Recommendation]:
        """Generate personalised recommendations based on habits and footprint.

        Rules are evaluated independently for each category:
        transportation, energy, food, waste, and water.  Each rule
        considers both relative contribution (percentage of total)
        and absolute values.

        Args:
            habits: Validated user lifestyle data.
            footprint: Computed carbon footprint breakdown.

        Returns:
            A list of Recommendation objects sorted by descending
            estimated monthly impact.
        """
        recommendations: List[Recommendation] = []
        total = footprint.total_co2

        if total == 0:
            logger.info("Zero total emissions — no recommendations needed")
            return recommendations

        # ── Transportation ───────────────────────────
        transport_pct = (footprint.transport_co2 / total) * 100
        if transport_pct > HIGH_CATEGORY_THRESHOLD_PCT or habits.transport.mode == TransportMode.CAR:
            estimated_saving = footprint.transport_co2 * DAYS_PER_MONTH * TRANSPORT_REDUCTION_FACTOR
            recommendations.append(
                Recommendation(
                    category="Transportation",
                    action=(
                        "Try carpooling, public transport, or cycling for your "
                        "daily commute to significantly reduce emissions."
                    ),
                    estimated_impact_kg_co2_mo=round(estimated_saving, 1),
                    effort_level="Medium",
                )
            )

        # ── Electricity / Energy ─────────────────────
        electricity_pct = (footprint.electricity_co2 / total) * 100
        if electricity_pct > HIGH_CATEGORY_THRESHOLD_PCT or habits.electricity.hours_ac > HIGH_AC_HOURS_THRESHOLD:
            recommendations.append(
                Recommendation(
                    category="Energy",
                    action=(
                        "Reduce AC runtime by 1-2 hours and switch to LED "
                        "bulbs if you haven't already."
                    ),
                    estimated_impact_kg_co2_mo=ENERGY_SAVINGS_KG_CO2_MO,
                    effort_level="Low",
                )
            )

        # ── Food ─────────────────────────────────────
        if habits.food_preference in (FoodPreference.NON_VEGETARIAN, FoodPreference.MIXED):
            food_pct = (footprint.food_co2 / total) * 100
            if food_pct > MODERATE_CATEGORY_THRESHOLD_PCT:
                recommendations.append(
                    Recommendation(
                        category="Food",
                        action=(
                            "Swap one or two meat-based meals per week for "
                            "plant-based alternatives."
                        ),
                        estimated_impact_kg_co2_mo=FOOD_SWAP_SAVINGS_KG_CO2_MO,
                        effort_level="Low",
                    )
                )

        # ── Waste ────────────────────────────────────
        if not habits.waste.recycles:
            recommendations.append(
                Recommendation(
                    category="Waste",
                    action=(
                        "Start segregating waste and recycling paper, "
                        "plastic, and glass."
                    ),
                    estimated_impact_kg_co2_mo=WASTE_MGMT_SAVINGS_KG_CO2_MO,
                    effort_level="Medium",
                )
            )

        if not habits.waste.composts:
            recommendations.append(
                Recommendation(
                    category="Waste",
                    action=(
                        "Start composting kitchen and garden organic waste "
                        "to reduce landfill methane emissions."
                    ),
                    estimated_impact_kg_co2_mo=WASTE_MGMT_SAVINGS_KG_CO2_MO * 0.6,
                    effort_level="Low",
                )
            )

        # ── Water ────────────────────────────────────
        if habits.water_liters_per_day > 200.0:
            recommendations.append(
                Recommendation(
                    category="Water",
                    action=(
                        "Reduce daily water usage by fixing leaks, taking "
                        "shorter showers, and using water-efficient fixtures."
                    ),
                    estimated_impact_kg_co2_mo=WATER_SAVINGS_KG_CO2_MO,
                    effort_level="Low",
                )
            )

        # Sort by highest impact first
        recommendations.sort(
            key=lambda r: r.estimated_impact_kg_co2_mo, reverse=True
        )

        logger.info("Generated %d recommendations", len(recommendations))
        return recommendations
