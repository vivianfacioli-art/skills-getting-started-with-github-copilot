from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_all_activities():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "Programming Class" in payload


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Basketball Team"
    email = "lexi@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_returns_404_for_unknown_activity():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "alex@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_returns_400_for_duplicate_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_removes_existing_student():
    # Arrange
    activity_name = "Chess Club"
    email = "daniel@mergington.edu"
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_returns_404_for_missing_student():
    # Arrange
    activity_name = "Chess Club"
    email = "nonexistent@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
