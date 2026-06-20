# Constants and emission factors for EcoDNA
# Values are approximate representations in kg CO2e for educational purposes.

# Transportation (kg CO2 per km)
TRANSPORT_FACTORS = {
    "Car": 0.192,
    "Bike": 0.03,  # Assuming motorcycle. If bicycle, it's 0.
    "Public Transport": 0.041,
    "Walking": 0.0
}

# Electricity (kg CO2 per hour of typical usage)
# Assumes average wattage and standard grid emission factor
ELECTRICITY_FACTORS = {
    "AC": 1.5,         # ~1500W
    "Fan": 0.075,      # ~75W
    "Lights": 0.05,    # ~50W (multiple bulbs)
    "Appliances": 0.5  # Mixed
}

# Food (kg CO2 per day)
FOOD_FACTORS = {
    "Vegan": 2.9,
    "Vegetarian": 3.8,
    "Mixed": 5.6,
    "Non-Vegetarian": 7.2
}

# Shopping (kg CO2 per day, estimated average footprint)
SHOPPING_FACTORS = {
    "Low": 2.0,
    "Medium": 5.0,
    "High": 10.0
}

# Waste (kg CO2 per day penalty for not managing)
WASTE_PENALTY = 1.5
RECYCLING_SAVINGS = 0.5
COMPOSTING_SAVINGS = 0.3

# Average Total CO2 per day for Carbon Score calculation
# Assuming average is around 20-30 kg CO2/day per person
BASELINE_DAILY_CO2 = 25.0
