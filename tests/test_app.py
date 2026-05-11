from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def reset_activities(original_activities):
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_get_activities_returns_available_activities():
    # Arrange
    original_activities = deepcopy(activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert "Chess Club" in body
    assert "Programming Class" in body
    assert body["Chess Club"]["description"] == original_activities["Chess Club"]["description"]

    reset_activities(original_activities)


def test_signup_for_activity_adds_participant():
    # Arrange
    original_activities = deepcopy(activities)
    activity_name = "Chess Club"
    new_email = "peter@mergington.edu"
    assert new_email not in activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={new_email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]

    reset_activities(original_activities)


def test_signup_for_activity_rejects_duplicate_registration():
    # Arrange
    original_activities = deepcopy(activities)
    activity_name = "Programming Class"
    existing_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={existing_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"].count(existing_email) == 1

    reset_activities(original_activities)


def test_unregister_from_activity_removes_participant():
    # Arrange
    original_activities = deepcopy(activities)
    activity_name = "Gym Class"
    existing_email = activities[activity_name]["participants"][0]
    assert existing_email in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={existing_email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {existing_email} from {activity_name}"}
    assert existing_email not in activities[activity_name]["participants"]

    reset_activities(original_activities)
