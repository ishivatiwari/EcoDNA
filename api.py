"""EcoDNA FastAPI application.

Provides the REST API for carbon footprint analysis, serving the
frontend, and health checks.  Includes security middleware (CSP, HSTS,
CORP, COOP), CORS configuration, thread-safe rate limiting, global
exception handlers, and structured logging.
"""

import asyncio
import logging
import os
import time

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
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
    docs_url="/docs",
    redoc_url="/redoc",
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
    """Attach comprehensive security headers to every response.

    Headers applied:
    - Content-Security-Policy: Restricts resource loading to trusted origins.
    - Strict-Transport-Security: Enforces HTTPS connections (HSTS).
    - X-Content-Type-Options: Prevents MIME-sniffing attacks.
    - X-Frame-Options: Prevents clickjacking via iframes.
    - Referrer-Policy: Limits referrer information leakage.
    - Permissions-Policy: Disables sensitive browser APIs.
    - X-XSS-Protection: Legacy XSS filter for older browsers.
    - Cross-Origin-Opener-Policy: Isolates browsing context.
    - Cross-Origin-Resource-Policy: Restricts cross-origin resource reads.
    """
    response: Response = await call_next(request)

    # Prevents loading scripts/styles from untrusted origins
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    # Enforce HTTPS for 1 year, including subdomains
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-site"
    return response


# ── Thread-safe in-memory rate limiter ───────
_rate_limit_store: dict[str, list[float]] = {}
_rate_limit_lock = asyncio.Lock()
_RATE_LIMIT_WINDOW: int = 60       # seconds
_RATE_LIMIT_MAX_REQUESTS: int = 30  # per window
_MAX_REQUEST_BODY_BYTES: int = 64 * 1024  # 64 KB


@app.middleware("http")
async def rate_limiter(request: Request, call_next) -> Response:
    """Thread-safe IP-based rate limiting middleware.

    Uses an asyncio.Lock to prevent race conditions when multiple
    concurrent requests modify the rate limit store.  Returns 429
    if a client exceeds the configured request limit.
    """
    client_ip: str = request.client.host if request.client else "unknown"
    now = time.time()

    async with _rate_limit_lock:
        # Evict timestamps outside the current window
        _rate_limit_store[client_ip] = [
            t
            for t in _rate_limit_store.get(client_ip, [])
            if now - t < _RATE_LIMIT_WINDOW
        ]

        if len(_rate_limit_store[client_ip]) >= _RATE_LIMIT_MAX_REQUESTS:
            logger.warning("Rate limit exceeded for %s", client_ip)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
                headers={"Retry-After": str(_RATE_LIMIT_WINDOW)},
            )

        _rate_limit_store[client_ip].append(now)

    return await call_next(request)


# ── Global exception handlers ─────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return a clean 422 response for invalid request payloads.

    Provides structured error details without exposing internal tracebacks.
    """
    errors = [
        {"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]}
        for e in exc.errors()
    ]
    logger.warning("Validation error on %s: %s", request.url.path, errors)
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request data.", "errors": errors},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Return a generic 500 response without leaking internal details.

    Logs the full exception server-side for debugging while returning
    only a safe message to the client.
    """
    logger.exception(
        "Unhandled exception on %s %s", request.method, request.url.path
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )


# ── Agent instance ───────────────────────────
agent = EcoDNAAgent()


# ── Response models ──────────────────────────
class AnalysisResponse(BaseModel):
    """Response model for the analysis endpoint."""

    footprint: FootprintBreakdown
    recommendations: list[Recommendation]
    weekly_report: str


# ── API endpoints ────────────────────────────
@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """Health check endpoint for container orchestrators."""
    return {"status": "healthy", "service": "ecodna-api"}


@app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_habits(habits: UserHabits, request: Request) -> AnalysisResponse:
    """Analyse user habits and return footprint, recommendations, and report.

    Accepts validated user lifestyle data and returns a comprehensive
    analysis including carbon footprint breakdown, personalised
    recommendations, and a weekly narrative report.

    Args:
        habits: Validated user lifestyle data (JSON body).
        request: The incoming HTTP request (used for audit logging).

    Returns:
        AnalysisResponse with footprint, recommendations, and report.
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info("Analysis request from %s", client_ip)

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
_frontend_assets = os.path.join(_frontend_dist, "assets")


@app.get("/", tags=["Frontend"])
async def serve_frontend() -> Response:
    """Serve the frontend SPA entry point."""
    index_path = os.path.join(_frontend_dist, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        content={"message": "Welcome to EcoDNA API. Frontend not built yet."}
    )


@app.get("/{file_path:path}", tags=["Frontend"])
async def serve_static(file_path: str) -> Response:
    """Serve any remaining static file from the dist root (e.g. vite.svg).

    Falls back to index.html for unknown paths so client-side routing works.
    """
    full_path = os.path.join(_frontend_dist, file_path)
    if os.path.isfile(full_path):
        return FileResponse(full_path)
    # Fall back to index.html for SPA client-side routes
    index_path = os.path.join(_frontend_dist, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"detail": "Not found"})


# Mount dist/assets/ directory at /assets so Vite-built CSS/JS loads correctly.
# Vite outputs: dist/assets/index-*.css and dist/assets/index-*.js
# The HTML references them as /assets/..., so the directory must be dist/assets/.
if os.path.exists(_frontend_assets):
    app.mount(
        "/assets",
        StaticFiles(directory=_frontend_assets),
        name="static",
    )

