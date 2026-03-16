"""Tests for the FastAPI High School Management System API.

Uses AAA (Arrange/Act/Assert) test structure for clarity.
"""

import copy
import pytest

from fastapi.testclient import TestClient
from src.app import app, activities


# Snapshot the initial in-memory activities so tests can reset state.
INITIAL_ACTIVITIES = copy.deepcopy(activities)


def reset_activities_state():
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture(autouse=True)
def auto_reset_state():
    """Reset the in-memory activities dict before each test."""
    reset_activities_state()
    yield
    reset_activities_state()


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_expected_structure(self, client):
        # Arrange
        expected_keys = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        payload = response.json()
        assert "Chess Club" in payload
        for activity_data in payload.values():
            assert expected_keys.issubset(activity_data.keys())
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    def test_signup_adds_participant(self, client):
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity]["participants"])

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert email in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count + 1

    def test_signup_duplicate_is_rejected(self, client):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # already registered in initial state
        initial_count = len(activities[activity]["participants"])

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
        assert len(activities[activity]["participants"]) == initial_count

    def test_signup_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipant:
    def test_remove_participant_removes_it(self, client):
        # Arrange
        activity = "Programming Class"
        email = "emma@mergington.edu"
        assert email in activities[activity]["participants"]
        initial_count = len(activities[activity]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity}/participants", params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count - 1

    def test_remove_nonexistent_participant_returns_404(self, client):
        # Arrange
        activity = "Gym Class"
        email = "notfound@mergington.edu"
        initial_count = len(activities[activity]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity}/participants", params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
        assert len(activities[activity]["participants"]) == initial_count

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity}/participants", params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
