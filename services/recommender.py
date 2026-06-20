from typing import List
from models.user import UserHabits, FootprintBreakdown, Recommendation, TransportMode, FoodPreference

class RecommendationEngine:
    @staticmethod
    def generate_recommendations(habits: UserHabits, footprint: FootprintBreakdown) -> List[Recommendation]:
        recommendations = []
        total = footprint.total_co2

        if total == 0:
            return recommendations

        # Transportation rules
        transport_pct = (footprint.transport_co2 / total) * 100
        if transport_pct > 30 or habits.transport.mode == TransportMode.CAR:
            recommendations.append(Recommendation(
                category="Transportation",
                action="Try carpooling, public transport, or cycling for your daily commute to significantly reduce emissions.",
                estimated_impact_kg_co2_mo=footprint.transport_co2 * 30 * 0.4, # Assume 40% reduction
                effort_level="Medium"
            ))

        # Electricity rules
        electricity_pct = (footprint.electricity_co2 / total) * 100
        if electricity_pct > 30 or habits.electricity.hours_ac > 4:
            recommendations.append(Recommendation(
                category="Energy",
                action="Reduce AC runtime by 1-2 hours and switch to LED bulbs if you haven't already.",
                estimated_impact_kg_co2_mo=30.0, # Approximate saving
                effort_level="Low"
            ))

        # Food rules
        if habits.food_preference in [FoodPreference.NON_VEGETARIAN, FoodPreference.MIXED]:
            if (footprint.food_co2 / total) * 100 > 25:
                recommendations.append(Recommendation(
                    category="Food",
                    action="Swap one or two meat-based meals per week for plant-based alternatives.",
                    estimated_impact_kg_co2_mo=15.0,
                    effort_level="Low"
                ))

        # Waste rules
        if not habits.waste.recycles:
            recommendations.append(Recommendation(
                category="Waste",
                action="Start segregating waste and recycling paper, plastic, and glass.",
                estimated_impact_kg_co2_mo=15.0,
                effort_level="Medium"
            ))

        # Sort recommendations by highest impact first
        recommendations.sort(key=lambda x: x.estimated_impact_kg_co2_mo, reverse=True)
        return recommendations
