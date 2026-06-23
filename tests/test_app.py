import copy
import pytest
from fastapi.testclient import TestClient

import src.app as app_module
from src.app import app

client = TestClient(app, follow_redirects=False)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict to its original state after each test."""
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

def test_root_redirect():
    response = client.get("/")
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_200():
    response = client.get("/activities")
    assert response.status_code == 200


def test_get_activities_contains_known_keys():
    response = client.get("/activities")
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )
    assert response.status_code == 200
    assert "newstudent@mergington.edu" in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_invalid_activity_returns_404():
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "someone@mergington.edu"},
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success():
    # michael@mergington.edu is a pre-seeded participant of Chess Club
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )
    assert response.status_code == 200
    assert "michael@mergington.edu" not in app_module.activities["Chess Club"]["participants"]


def test_unregister_not_enrolled_returns_404():
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "noone@mergington.edu"},
    )
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"].lower()


def test_unregister_invalid_activity_returns_404():
    response = client.delete(
        "/activities/Nonexistent Club/signup",
        params={"email": "someone@mergington.edu"},
    )
    assert response.status_code == 404
