"""EcoDNA FastAPI application.

Provides the REST API for carbon footprint analysis, serving the
frontend, and health checks.  Includes security middleware, CORS
configuration, rate limiting, and structured logging.
"""

import logging
import os
import time
from typing import List

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from models.user import UserHabits, FootprintBreakdown, Recommendation
from agents.eco_dna import EcoDNAAgent

# ── Logging configuration ────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Application setup ────────────────────────
app = FastAPI(
    title="EcoDNA API",
    description=(
        "Context-aware AI agent API for personal sustainability "
        "and lifestyle carbon footprint analysis."
    ),
    version="1.0.0",
)

# ── CORS — allow the frontend origin only ────
_ALLOWED_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
    "https://ecodna-api-hdgnoiba3q-uc.a.run.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept"],
)


# ── Security headers middleware ──────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    """Attach security headers to every response."""
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# ── Simple in-memory rate limiter ────────────
_rate_limit_store: dict[str, list[float]] = {}
_RATE_LIMIT_WINDOW: int = 60  # seconds
_RATE_LIMIT_MAX_REQUESTS: int = 30  # per window


@app.middleware("http")
async def rate_limiter(request: Request, call_next) -> Response:
    """Basic IP-based rate limiting middleware."""
    client_ip: str = request.client.host if request.client else "unknown"
    now = time.time()

    # Clean old entries
    if client_ip in _rate_limit_store:
        _rate_limit_store[client_ip] = [
            t for t in _rate_limit_store[client_ip] if now - t < _RATE_LIMIT_WINDOW
        ]
    else:
        _rate_limit_store[client_ip] = []

    if len(_rate_limit_store[client_ip]) >= _RATE_LIMIT_MAX_REQUESTS:
        logger.warning("Rate limit exceeded for %s", client_ip)
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."},
        )

    _rate_limit_store[client_ip].append(now)
    return await call_next(request)


# ── Agent instance ───────────────────────────
agent = EcoDNAAgent()


# ── Response models ──────────────────────────
class AnalysisResponse(BaseModel):
    """Response model for the analysis endpoint."""

    footprint: FootprintBreakdown
    recommendations: List[Recommendation]
    weekly_report: str


# ── API endpoints ────────────────────────────
@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """Health check endpoint for container orchestrators."""
    return {"status": "healthy", "service": "ecodna-api"}


@app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_habits(habits: UserHabits) -> AnalysisResponse:
    """Analyse user habits and return footprint, recommendations, and report.

    Accepts validated user lifestyle data and returns a comprehensive
    analysis including carbon footprint breakdown, personalised
    recommendations, and a weekly narrative report.

    Args:
        habits: Validated user lifestyle data (JSON body).

    Returns:
        AnalysisResponse with footprint, recommendations, and report.
    """
    logger.info("Received analysis request")
    footprint = agent.analyze_user(habits)
    recommendations = agent.get_recommendations(habits, footprint)
    weekly_report = agent.generate_weekly_report(habits, footprint=footprint)

    return AnalysisResponse(
        footprint=footprint,
        recommendations=recommendations,
        weekly_report=weekly_report,
    )


# ── Frontend static file serving ─────────────
_frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")


@app.get("/", tags=["Frontend"])
async def serve_frontend() -> Response:
    """Serve the frontend SPA entry point."""
    index_path = os.path.join(_frontend_dist, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        content={"message": "Welcome to EcoDNA API. Frontend not built yet."}
    )


if os.path.exists(_frontend_dist):
    app.mount(
        "/assets",
        StaticFiles(directory=_frontend_dist),
        name="static",
    )
