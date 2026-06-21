# EcoDNA 🌱

**EcoDNA** — An intelligent, context-aware AI sustainability assistant that analyzes lifestyle habits, tracks carbon footprint, and delivers personalized actions to help individuals reduce their environmental impact.

## Problem Statement

Helping individuals understand, track, and reduce their carbon footprint through simple actions, personalized insights, and goal-based progress tracking.

## Chosen Vertical

Personal Sustainability Assistant

## Key Features

- **Carbon Footprint Calculator** — Estimates daily CO₂ emissions across transport, electricity, food, shopping, waste, and water usage categories.
- **Context-Aware AI Agent** — Orchestrates analysis, recommendations, and reporting through a unified agent interface with analysis history.
- **Personalised Recommendations** — Rule-based engine that identifies high-impact emission areas and suggests actionable improvements.
- **Goal Tracking** — Set, monitor, and complete sustainability goals with progress percentage tracking and stagnant-goal detection.
- **Weekly Insights & Motivation** — Narrative reports with score-tiered feedback and motivational messaging.
- **Interactive Web Dashboard** — Glassmorphic UI with real-time analysis, animated agent chat, and goal management.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                 Frontend (Vite)                  │
│   HTML / CSS / JS  →  REST API  →  Dashboard    │
└────────────────────────┬────────────────────────┘
                         │  POST /analyze
┌────────────────────────▼────────────────────────┐
│              FastAPI Backend (api.py)            │
│  Security Headers │ Rate Limiting │ CORS        │
└────────────────────────┬────────────────────────┘
                         │
┌────────────────────────▼────────────────────────┐
│           EcoDNA Agent (agents/eco_dna.py)       │
│  Orchestrates: Calculator, Recommender, Goals,  │
│  Insights, Motivation — with analysis history   │
└────────────────────────┬────────────────────────┘
                         │
┌────────────────────────▼────────────────────────┐
│               Services Layer                     │
│  calculator.py │ recommender.py │ goals.py │    │
│  insights.py                                     │
└────────────────────────┬────────────────────────┘
                         │
┌────────────────────────▼────────────────────────┐
│          Utils & Models                          │
│  emission_factors.py │ exceptions.py │ user.py  │
└─────────────────────────────────────────────────┘
```

## How It Works

1. **Collect** lifestyle data via the web form (transport, food, energy, waste, water, home type).
2. **Calculate** emissions using published emission factors with home-type multipliers.
3. **Analyse** high-impact areas and compute a sustainability score (0-100).
4. **Recommend** personalised, prioritised actions sorted by estimated monthly CO₂ savings.
5. **Track** goals with progress bars and stagnant-goal detection.
6. **Report** weekly insights with narrative feedback and motivational messaging.

## Project Structure

```
EcoDNA/
├── agents/          # Main EcoDNA orchestrator agent
├── models/          # Pydantic data models with validation
├── services/        # Core logic: calculator, recommender, goals, insights
├── utils/           # Constants, emission factors, custom exceptions
├── tests/           # Comprehensive test suite (40+ tests)
├── frontend/        # Vite-based web dashboard
├── api.py           # FastAPI REST API with security middleware
├── main.py          # CLI demonstration entry point
├── Dockerfile       # Production container image
├── requirements.txt # Python dependencies
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ (for the frontend)

### Backend Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Run tests
python -m pytest tests/ -v

# Start the API server
uvicorn api:app --reload --port 8080
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev       # Development server at http://localhost:5173
npm run build     # Production build to dist/
```

## Assumptions

- Emission factors are approximate values for educational and awareness purposes.
- User-provided information is approximate and self-reported.
- Results are intended for personal sustainability awareness, not regulatory compliance.
- Water CO₂ accounts for pumping, heating, and treatment energy costs.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, Pydantic v2 |
| Frontend | HTML5, CSS3 (Glassmorphism), Vanilla JS |
| Build | Vite, Docker |
| Testing | pytest, FastAPI TestClient |

## License

MIT
