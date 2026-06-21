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
