# EcoDNA

EcoDNA - An intelligent, context-aware sustainability assistant that analyzes lifestyle habits, tracks carbon footprint, and delivers personalized actions to help individuals reduce their environmental impact.

## Problem Statement

Helping individuals understand, track, and reduce their carbon footprint through simple actions and personalized insights.

## Chosen Vertical

Personal Sustainability Assistant

## Approach

Context-aware AI agent with:
- Carbon estimation
- Recommendation engine
- Goal tracking
- Progress analytics

## How It Works

1. Collect lifestyle data.
2. Calculate emissions.
3. Analyze high-impact areas.
4. Generate personalized suggestions.
5. Track improvements over time.

## Assumptions

- Estimates use standard emission factors.
- User-provided information is approximate.
- Results are educational and awareness-oriented.

## Project Structure

- `agents/`: Contains the main EcoDNA orchestrator agent.
- `tools/`: Extensible tools for the agent (planned).
- `models/`: Pydantic data models for validation and typing.
- `services/`: Core logic including the calculator, recommender, goals, and insights.
- `utils/`: Constants and emission factors.
- `tests/`: Comprehensive unit test suite.
