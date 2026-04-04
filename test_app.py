"""
test_app.py - Comprehensive Pytest Test Suite for ACEest Fitness & Gym
======================================================================
Covers:
  - Health-check endpoint
  - Client CRUD operations
  - BMI calculation (logic + endpoint)
  - Calorie estimation
  - AI program generation
  - Workout logging & retrieval
  - Membership status checking
  - Program listing endpoint
  - Edge cases and error handling
"""

import pytest
import os
import sys

# Ensure the app module is importable
sys.path.insert(0, os.path.dirname(__file__))

from app import (
    app,
    init_db,
    calculate_bmi,
    bmi_category,
    estimate_calories,
    generate_ai_program,
    DB_NAME,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    """Use a temporary database for every test to avoid side-effects."""
    test_db = str(tmp_path / "test.db")
    monkeypatch.setattr("app.DB_NAME", test_db)
    init_db()
    yield
    if os.path.exists(test_db):
        os.remove(test_db)


@pytest.fixture
def client():
    """Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# 1. Health-check
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_json_structure(self, client):
        data = client.get("/health").get_json()
        assert data["status"] == "healthy"
        assert "app" in data


# ---------------------------------------------------------------------------
# 2. Home page
# ---------------------------------------------------------------------------

class TestHomePage:
    def test_home_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_home_contains_title(self, client):
        resp = client.get("/")
        assert b"ACEest" in resp.data


# ---------------------------------------------------------------------------
# 3. BMI logic
# ---------------------------------------------------------------------------

class TestBMICalculation:
    def test_normal_bmi(self):
        bmi = calculate_bmi(70, 175)
        assert 22 <= bmi <= 24

    def test_underweight(self):
        assert bmi_category(17.0) == "Underweight"

    def test_normal_weight(self):
        assert bmi_category(22.0) == "Normal weight"

    def test_overweight(self):
        assert bmi_category(27.5) == "Overweight"

    def test_obese(self):
        assert bmi_category(35.0) == "Obese"

    def test_zero_height_raises(self):
        with pytest.raises(ValueError):
            calculate_bmi(70, 0)

    def test_negative_weight_raises(self):
        with pytest.raises(ValueError):
            calculate_bmi(-5, 170)


# ---------------------------------------------------------------------------
# 4. BMI endpoint
# ---------------------------------------------------------------------------

class TestBMIEndpoint:
    def test_bmi_endpoint_success(self, client):
        resp = client.post("/api/bmi", json={"weight": 70, "height": 175})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "bmi" in data
        assert "category" in data

    def test_bmi_endpoint_invalid(self, client):
        resp = client.post("/api/bmi", json={"weight": 0, "height": 175})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# 5. Calorie estimation
# ---------------------------------------------------------------------------

class TestCalorieEstimation:
    def test_fat_loss_calories(self):
        cal = estimate_calories(80, "Fat Loss (FL) - 3 day")
        assert cal == 80 * 22

    def test_muscle_gain_calories(self):
        cal = estimate_calories(80, "Muscle Gain (MG) - PPL")
        assert cal == 80 * 35

    def test_unknown_program_raises(self):
        with pytest.raises(ValueError):
            estimate_calories(70, "NonExistent Program")

    def test_zero_weight_raises(self):
        with pytest.raises(ValueError):
            estimate_calories(0, "Beginner (BG)")


# ---------------------------------------------------------------------------
# 6. AI program generation
# ---------------------------------------------------------------------------

class TestAIProgramGeneration:
    def test_beginner_program(self):
        plan = generate_ai_program("Beginner (BG)", "beginner")
        assert len(plan) > 0
        assert all("day" in item and "exercise" in item for item in plan)

    def test_advanced_has_more_days(self):
        beginner = generate_ai_program("Beginner (BG)", "beginner")
        advanced = generate_ai_program("Beginner (BG)", "advanced")
        beginner_days = set(item["day"] for item in beginner)
        advanced_days = set(item["day"] for item in advanced)
        assert len(advanced_days) > len(beginner_days)

    def test_invalid_experience_raises(self):
        with pytest.raises(ValueError):
            generate_ai_program("Beginner (BG)", "elite")

    def test_program_endpoint_success(self, client):
        resp = client.post("/api/generate-program", json={
            "program": "Fat Loss (FL) - 3 day",
            "experience": "intermediate",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "program" in data
        assert len(data["program"]) > 0


# ---------------------------------------------------------------------------
# 7. Client CRUD
# ---------------------------------------------------------------------------

class TestClientCRUD:
    def test_create_client(self, client):
        resp = client.post("/api/clients", json={
            "name": "TestUser",
            "age": 25,
            "height": 180,
            "weight": 80,
            "program": "Beginner (BG)",
        })
        assert resp.status_code == 201

    def test_get_clients_empty(self, client):
        resp = client.get("/api/clients")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_get_clients_after_create(self, client):
        client.post("/api/clients", json={"name": "Alice", "age": 30})
        resp = client.get("/api/clients")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Alice"

    def test_get_single_client(self, client):
        client.post("/api/clients", json={"name": "Bob", "age": 22})
        resp = client.get("/api/clients/Bob")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Bob"

    def test_get_nonexistent_client(self, client):
        resp = client.get("/api/clients/Nobody")
        assert resp.status_code == 404

    def test_delete_client(self, client):
        client.post("/api/clients", json={"name": "Charlie"})
        resp = client.delete("/api/clients/Charlie")
        assert resp.status_code == 200
        resp2 = client.get("/api/clients/Charlie")
        assert resp2.status_code == 404

    def test_create_client_no_name(self, client):
        resp = client.post("/api/clients", json={"age": 20})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# 8. Workouts
# ---------------------------------------------------------------------------

class TestWorkouts:
    def test_log_workout(self, client):
        resp = client.post("/api/workouts", json={
            "client_name": "Dave",
            "workout_type": "Strength",
            "duration_min": 45,
            "notes": "Good session",
        })
        assert resp.status_code == 201

    def test_get_workouts(self, client):
        client.post("/api/workouts", json={
            "client_name": "Eve",
            "workout_type": "Cardio",
        })
        resp = client.get("/api/workouts/Eve")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 1

    def test_log_workout_no_client(self, client):
        resp = client.post("/api/workouts", json={"workout_type": "Cardio"})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# 9. Membership
# ---------------------------------------------------------------------------

class TestMembership:
    def test_active_membership(self, client):
        client.post("/api/clients", json={
            "name": "Frank",
            "membership_expiry": "2099-12-31",
        })
        resp = client.get("/api/membership/Frank")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["is_active"] is True

    def test_expired_membership(self, client):
        client.post("/api/clients", json={
            "name": "Grace",
            "membership_expiry": "2020-01-01",
        })
        resp = client.get("/api/membership/Grace")
        data = resp.get_json()
        assert data["is_active"] is False

    def test_membership_not_found(self, client):
        resp = client.get("/api/membership/Unknown")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 10. Programs listing
# ---------------------------------------------------------------------------

class TestProgramsEndpoint:
    def test_list_programs(self, client):
        resp = client.get("/api/programs")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "Beginner (BG)" in data
        assert "Fat Loss (FL) - 3 day" in data
