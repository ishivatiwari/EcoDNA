"""Tests for the FastAPI endpoints.

Uses the FastAPI TestClient for synchronous, in-process testing
of the /analyze and /health endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from api import app


@pytest.fixture
def client() -> TestClient:
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_check(self, client):
        """Health endpoint should return 200 and healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ecodna-api"


class TestAnalyzeEndpoint:
    """Tests for POST /analyze."""

    def test_analyze_valid_input(self, client):
        """Valid input should return 200 with footprint, recs, and report."""
        payload = {
            "transport": {"mode": "Car", "distance_km_per_day": 20.0},
            "electricity": {
                "hours_ac": 3.0,
                "hours_fan": 8.0,
                "hours_lights": 4.0,
                "hours_appliances": 2.0,
            },
            "food_preference": "Mixed",
            "shopping_level": "Medium",
            "waste": {"recycles": True, "composts": False},
            "water_liters_per_day": 150.0,
            "home_type": "Apartment",
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "footprint" in data
        assert "recommendations" in data
        assert "weekly_report" in data
        assert data["footprint"]["total_co2"] > 0
        assert 0.0 <= data["footprint"]["carbon_score"] <= 100.0

    def test_analyze_eco_friendly(self, client):
        """Eco-friendly input should produce a high carbon score."""
        payload = {
            "transport": {"mode": "Walking", "distance_km_per_day": 5.0},
            "electricity": {
                "hours_ac": 0.0,
                "hours_fan": 0.0,
                "hours_lights": 0.0,
                "hours_appliances": 0.0,
            },
            "food_preference": "Vegan",
            "shopping_level": "Low",
            "waste": {"recycles": True, "composts": True},
            "water_liters_per_day": 80.0,
            "home_type": "Apartment",
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["footprint"]["carbon_score"] > 80.0

    def test_analyze_invalid_transport_mode(self, client):
        """Invalid transport mode should return 422."""
        payload = {
            "transport": {"mode": "Spaceship", "distance_km_per_day": 10.0},
            "electricity": {},
            "food_preference": "Vegan",
            "shopping_level": "Low",
            "waste": {"recycles": True, "composts": True},
            "water_liters_per_day": 150.0,
            "home_type": "Apartment",
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 422

    def test_analyze_negative_distance(self, client):
        """Negative distance should be rejected by validators."""
        payload = {
            "transport": {"mode": "Car", "distance_km_per_day": -10.0},
            "electricity": {},
            "food_preference": "Vegan",
            "shopping_level": "Low",
            "waste": {"recycles": True, "composts": True},
            "water_liters_per_day": 150.0,
            "home_type": "Apartment",
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 422

    def test_analyze_missing_required_fields(self, client):
        """Missing required fields should return 422."""
        response = client.post("/analyze", json={})
        assert response.status_code == 422

    def test_analyze_response_has_water_co2(self, client):
        """Response should include water_co2 in footprint."""
        payload = {
            "transport": {"mode": "Walking", "distance_km_per_day": 0.0},
            "electricity": {},
            "food_preference": "Vegan",
            "shopping_level": "Low",
            "waste": {"recycles": True, "composts": True},
            "water_liters_per_day": 200.0,
            "home_type": "Apartment",
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "water_co2" in data["footprint"]
        assert data["footprint"]["water_co2"] >= 0


class TestSecurityHeaders:
    """Tests for security HTTP response headers."""

    def test_x_content_type_options(self, client):
        """Response should include X-Content-Type-Options: nosniff."""
        response = client.get("/health")
        assert response.headers.get("x-content-type-options") == "nosniff"

    def test_x_frame_options(self, client):
        """Response should include X-Frame-Options: DENY."""
        assert client.get("/health").headers.get("x-frame-options") == "DENY"

    def test_referrer_policy(self, client):
        """Response should include strict Referrer-Policy."""
        assert (
            client.get("/health").headers.get("referrer-policy")
            == "strict-origin-when-cross-origin"
        )

    def test_content_security_policy_present(self, client):
        """Response should include a Content-Security-Policy header."""
        response = client.get("/health")
        assert "content-security-policy" in response.headers
        assert "default-src" in response.headers["content-security-policy"]

    def test_strict_transport_security_present(self, client):
        """Response should include HSTS header."""
        response = client.get("/health")
        assert "strict-transport-security" in response.headers
        assert "max-age=31536000" in response.headers["strict-transport-security"]

    def test_cross_origin_opener_policy(self, client):
        """Response should include Cross-Origin-Opener-Policy."""
        response = client.get("/health")
        assert response.headers.get("cross-origin-opener-policy") == "same-origin"

    def test_cross_origin_resource_policy(self, client):
        """Response should include Cross-Origin-Resource-Policy."""
        response = client.get("/health")
        assert response.headers.get("cross-origin-resource-policy") == "same-site"

    def test_permissions_policy(self, client):
        """Response should disable sensitive browser APIs."""
        response = client.get("/health")
        perms = response.headers.get("permissions-policy", "")
        assert "camera=()" in perms
        assert "microphone=()" in perms

    def test_validation_error_format(self, client):
        """Custom validation error handler should return structured errors."""
        response = client.post("/analyze", json={"transport": {"mode": "InvalidMode"}})
        assert response.status_code == 422
        data = response.json()
        assert "errors" in data or "detail" in data

