"""EcoDNA — main entry point for local demonstration.

Runs the EcoDNA agent in standalone mode with mock user data
to demonstrate carbon footprint analysis, goal tracking, and
weekly report generation.
"""

import logging
import os

from dotenv import load_dotenv

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
from agents.eco_dna import EcoDNAAgent

# ── Logging configuration ────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the EcoDNA agent with sample data.

    Demonstrates the full pipeline: environment loading, footprint
    analysis, goal creation, and weekly report generation.
    """
    # Load environment variables (e.g., API keys if we were calling external services)
    load_dotenv()
    api_key = os.getenv("API_KEY")
    if not api_key:
        logger.warning(
            "API_KEY not found in environment variables. Running in local mode."
        )

    # Initialize the agent
    agent = EcoDNAAgent()

    # Collect mock user input (in a real app, this comes from a UI/API)
    logger.info("Collecting user lifestyle data")
    mock_user_data = UserHabits(
        transport=TransportHabits(
            mode=TransportMode.CAR, distance_km_per_day=25.0
        ),
        electricity=ElectricityHabits(
            hours_ac=5.0,
            hours_fan=12.0,
            hours_lights=6.0,
            hours_appliances=2.0,
        ),
        food_preference=FoodPreference.NON_VEGETARIAN,
        shopping_level=ConsumptionLevel.HIGH,
        waste=WasteHabits(recycles=False, composts=False),
        home_type=HomeType.INDEPENDENT_HOUSE,
    )

    # Agent analyzes the footprint
    logger.info("Analysing carbon footprint")
    footprint = agent.analyze_user(mock_user_data)
    logger.info("Total Daily CO2: %.2f kg", footprint.total_co2)
    logger.info("Carbon Score: %.1f/100", footprint.carbon_score)

    # Agent sets some initial goals
    agent.add_goal(
        "Start Recycling", target_value=1.0, current_value=0.0, unit="habit"
    )
    agent.add_goal(
        "Reduce AC Usage", target_value=3.0, current_value=5.0, unit="hours"
    )

    # Agent generates recommendations and insights
    logger.info("Generating weekly report")
    report = agent.generate_weekly_report(mock_user_data, footprint=footprint)
    logger.info("Weekly Report:\n%s", report)


if __name__ == "__main__":
    main()
