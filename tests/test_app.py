import copy

from fastapi.testclient import TestClient

from src.app import activities, app

INITIAL_ACTIVITIES = copy.deepcopy(activities)


def reset_activities() -> None:
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_root_redirects_to_static_index_html() -> None:
    # Arrange
    reset_activities()
    with TestClient(app) as client:
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code in (302, 307)
        assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list() -> None:
    # Arrange
    reset_activities()
    with TestClient(app) as client:
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert response.json() == INITIAL_ACTIVITIES


def test_signup_for_activity_succeeds() -> None:
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        assert email in activities[activity_name]["participants"]


def test_signup_for_same_student_is_rejected() -> None:
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_missing_activity_returns_404() -> None:
    # Arrange
    reset_activities()
    activity_name = "Robotics Club"
    email = "futurestudent@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_succeeds() -> None:
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Removed {email} from {activity_name}"
        }
        assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404() -> None:
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    missing_email = "unknown@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": missing_email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found in activity"


def test_unregister_from_missing_activity_returns_404() -> None:
    # Arrange
    reset_activities()
    activity_name = "Robotics Club"
    email = "student@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
