import os
from dotenv import load_dotenv

from models.user import (
    UserHabits, TransportHabits, TransportMode, 
    ElectricityHabits, WasteHabits, FoodPreference, 
    ConsumptionLevel, HomeType
)
from agents.eco_dna import EcoDNAAgent

def main():
    # Load environment variables (e.g., API keys if we were calling external services)
    load_dotenv()
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("Warning: API_KEY not found in environment variables. Running in local mode.")

    # Initialize the agent
    agent = EcoDNAAgent()

    # Collect mock user input (in a real app, this comes from a UI/API)
    print("--- Collecting User Lifestyle Data ---")
    mock_user_data = UserHabits(
        transport=TransportHabits(mode=TransportMode.CAR, distance_km_per_day=25.0),
        electricity=ElectricityHabits(hours_ac=5.0, hours_fan=12.0, hours_lights=6.0, hours_appliances=2.0),
        food_preference=FoodPreference.NON_VEGETARIAN,
        shopping_level=ConsumptionLevel.HIGH,
        waste=WasteHabits(recycles=False, composts=False),
        home_type=HomeType.INDEPENDENT_HOUSE
    )

    # Agent analyzes the footprint
    print("\n--- Analyzing Carbon Footprint ---")
    footprint = agent.analyze_user(mock_user_data)
    print(f"Total Daily CO2: {footprint.total_co2} kg")
    print(f"Carbon Score: {footprint.carbon_score}/100")

    # Agent sets some initial goals
    agent.add_goal("Start Recycling", target_value=1.0, current_value=0.0, unit="habit")
    agent.add_goal("Reduce AC Usage", target_value=3.0, current_value=5.0, unit="hours")

    # Agent generates recommendations and insights
    print("\n--- Generating Weekly Report ---")
    report = agent.generate_weekly_report(mock_user_data)
    print(report)

if __name__ == "__main__":
    main()
