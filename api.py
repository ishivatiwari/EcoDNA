from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os

from models.user import UserHabits, FootprintBreakdown, Recommendation
from agents.eco_dna import EcoDNAAgent

app = FastAPI(
    title="EcoDNA API",
    description="Context-aware AI agent API for personal sustainability and lifestyle assistance.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, you'd restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize a global agent for simplicity
agent = EcoDNAAgent()

class AnalysisResponse(BaseModel):
    footprint: FootprintBreakdown
    recommendations: List[Recommendation]
    weekly_report: str

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_habits(habits: UserHabits):
    footprint = agent.analyze_user(habits)
    recommendations = agent.get_recommendations(habits, footprint)
    weekly_report = agent.generate_weekly_report(habits)
    
    return AnalysisResponse(
        footprint=footprint,
        recommendations=recommendations,
        weekly_report=weekly_report
    )

# Serve the Vite frontend
frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")

@app.get("/")
def serve_frontend():
    if os.path.exists(os.path.join(frontend_dist, "index.html")):
        return FileResponse(os.path.join(frontend_dist, "index.html"))
    return {"message": "Welcome to EcoDNA API. Frontend not built yet."}

if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist), name="static")
