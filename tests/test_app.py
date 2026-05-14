import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

INITIAL_ACTIVITIES = copy.deepcopy(activities)
client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activity database before each test."""
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_root_redirects_to_static_index():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_list():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities
    assert "Chess Club" in response.json()


def test_signup_for_activity_success():
    # Arrange
    activity_name = "Chess Club"
    email = "new_student@mergington.edu"
    request_params = {"email": email}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=request_params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_missing_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    request_params = {"email": "student@mergington.edu"}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=request_params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_duplicate_student_returns_400():
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = activities[activity_name]["participants"][0]
    request_params = {"email": duplicate_email}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=request_params)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"
