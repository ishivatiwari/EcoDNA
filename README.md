<p align="center">
  <img src="assets/ecodna_banner.png" width="100%">
</p>

# 🌍 EcoDNA: Your Personal Sustainability Assistant

<p align="center">

[![Demo](https://img.shields.io/badge/🚀_DEMO-LIVE_NOW-orange?style=for-the-badge)](https://your-demo-url.com)
[![Project](https://img.shields.io/badge/GitHub-PROJECT-darkgrey?style=for-the-badge&logo=github)](https://github.com/username/EcoDNA)
[![Repository](https://img.shields.io/badge/SOURCE-CODE-green?style=for-the-badge)](https://github.com/username/EcoDNA)

</p>

<h3 align="center">
Empowering individuals with AI-driven, personalized, and actionable insights to understand, track, and reduce their carbon footprint.
</h3>

# 🌍 EcoDNA

**EcoDNA** is an intelligent, context-aware sustainability assistant that helps individuals understand, track, and reduce their carbon footprint through personalized insights and simple, high-impact actions. By transforming everyday lifestyle habits into measurable environmental impact, EcoDNA empowers users to make smarter and greener decisions.

---

## 🚀 Problem Statement

Modern lifestyles contribute significantly to carbon emissions, yet most individuals lack visibility into how their daily choices affect the environment.

**EcoDNA addresses this challenge by providing a smart assistant that:**

- Estimates carbon emissions from everyday activities.
- Identifies major sources of environmental impact.
- Delivers personalized, practical recommendations.
- Tracks progress over time.
- Encourages sustainable habits through actionable insights.

---

## 🎯 Chosen Vertical

### Personal Sustainability Assistant

EcoDNA is designed for individuals who want to adopt a more sustainable lifestyle without requiring technical knowledge or complex calculations.

---

## 🧠 Solution Approach

EcoDNA combines context-aware reasoning with rule-based decision making to provide meaningful and personalized sustainability guidance.

### Key Capabilities

- 🌱 **Carbon Footprint Estimation**
  - Analyze transportation, energy usage, food habits, and waste management.
  - Estimate daily and monthly CO₂ emissions.

- 💡 **Personalized Recommendation Engine**
  - Identify high-impact emission sources.
  - Suggest practical and achievable changes.

- 🎯 **Goal Tracking**
  - Set emission reduction goals.
  - Monitor progress and sustainability milestones.

- 📈 **Progress Analytics**
  - Visualize trends and improvements over time.

- 🤖 **Context-Aware Decision Making**
  - Prioritize recommendations based on user behavior and emission patterns.

---

## ⚙️ How It Works

### 1. Collect Lifestyle Information
EcoDNA gathers information about:

- Transportation habits
- Electricity usage
- Dietary preferences
- Shopping behavior
- Waste management practices
- Water consumption
- Home type

### 2. Calculate Carbon Emissions

Using standard emission factors, EcoDNA estimates:

- Transportation emissions
- Energy emissions
- Food-related emissions
- Waste emissions

### 3. Analyze High-Impact Areas

The agent identifies the categories contributing the most to the user's carbon footprint.

### 4. Generate Personalized Recommendations

Examples:

- Use public transportation more frequently.
- Reduce air conditioner usage.
- Switch to LED lighting.
- Introduce plant-based meals.
- Improve recycling habits.

### 5. Track Progress Over Time

Users can:

- Set reduction goals.
- Measure improvement.
- Receive periodic insights and motivation.

---

## 🏗 Architecture

```text
EcoDNA
│
├── Agent Layer
│      └── EcoDNA Orchestrator
│
├── Services Layer
│      ├── Carbon Calculator
│      ├── Recommendation Engine
│      ├── Goal Tracker
│      └── Insight Generator
│
├── Models Layer
│      └── Pydantic Data Models
│
├── Utility Layer
│      └── Emission Factors & Constants
│
└── Testing Layer
       └── Unit Tests
```

---

## 📂 Project Structure

```text
.
├── agents/
│   └── Main EcoDNA orchestrator agent
│
├── models/
│   └── Pydantic models and schemas
│
├── services/
│   ├── Carbon calculator
│   ├── Recommendation engine
│   ├── Goal tracker
│   └── Insight generator
│
├── tools/
│   └── Reusable tools and integrations
│
├── utils/
│   └── Emission factors and constants
│
└── tests/
    └── Unit tests and validation cases
```

---

## 🔍 Decision Logic

EcoDNA prioritizes recommendations using contextual reasoning.

### Transportation Emissions High
➡ Recommend:

- Public transport
- Carpooling
- Cycling
- Walking

### Electricity Consumption High
➡ Recommend:

- LED bulbs
- Reduced AC runtime
- Energy-efficient appliances

### Food Emissions High
➡ Recommend:

- More plant-based meals
- Reduced meat consumption

### Waste Management Poor
➡ Recommend:

- Recycling
- Composting
- Waste segregation

Recommendations are always optimized for:

1. **Maximum impact**
2. **Minimum effort**
3. **Long-term sustainability**

---

## 🔐 Security

EcoDNA follows secure development practices:

- Input validation using Pydantic.
- No hardcoded secrets.
- Safe exception handling.
- Modular and maintainable architecture.
- Responsible and explainable recommendations.

---

## 🧪 Testing

Comprehensive unit tests validate:

- Carbon footprint calculations.
- Recommendation engine behavior.
- Goal tracking functionality.
- Edge cases and invalid inputs.

---

## ♿ Accessibility

EcoDNA is designed to be inclusive and user-friendly:

- Clear and simple language.
- Human-readable outputs.
- Lightweight and efficient interactions.
- Beginner-friendly experience.

---

## 📌 Assumptions

- Carbon estimates are based on standard emission factors.
- User-provided information is approximate.
- Results are intended for awareness and educational purposes.
- Recommendations prioritize practicality over perfection.

---

## 🌎 Vision

**EcoDNA aims to make sustainability accessible to everyone by turning daily habits into measurable environmental insights and empowering people to create a greener future—one small action at a time.**

---

### *Measure Smarter • Live Greener • Reduce Your Footprint*
