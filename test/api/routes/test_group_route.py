import logging
from typing import List

from fastapi.testclient import TestClient

from mock.database.data import data

logger = logging.getLogger("test.unittest")

# Test for /group POST (Create Group)
def test_create_group_blank_access(http_client: TestClient):
    response = http_client.post("/group/")
    assert response.status_code == 422

def test_create_group_success(http_client: TestClient):
    # Arrange
    groupname = "Test Group"
    username = "Test User"
    email = "test@example.com"

    # Act
    response = http_client.post(
        "/group/",
        json={
            "groupname": groupname,
            "username": username,
            "email": email
        }
    )

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert "jwt" in response_data
    assert response_data["group_id"] is not None

def test_create_group_invalid_email(http_client: TestClient):
    # Arrange
    groupname = "Test Group"
    username = "Test User"
    email = "invalid-email"  # Invalid email format

    # Act
    response = http_client.post(
        "/group/",
        json={
            "groupname": groupname,
            "username": username,
            "email": email
        }
    )

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "value is not a valid email address: An email address must have an @-sign."

def test_create_group_short_groupname(http_client: TestClient):
    # Arrange
    groupname = "TG"  # Too short group name
    username = "Test User"
    email = "test@example.com"

    # Act
    response = http_client.post(
        "/group/",
        json={
            "groupname": groupname,
            "username": username,
            "email": email
        }
    )

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "String should have at least 3 characters"

def test_create_group_short_username(http_client: TestClient):
    # Arrange
    groupname = "Test Group"
    username = "TU"  # Too short username
    email = "test@example.com"

    # Act
    response = http_client.post(
        "/group/",
        json={
            "groupname": groupname,
            "username": username,
            "email": email
        }
    )

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "String should have at least 3 characters"

def test_create_group_missing_fields(http_client: TestClient):
    # Arrange: Missing username field
    groupname = "Test Group"
    email = "test@example.com"

    # Act
    response = http_client.post(
        "/group/",
        json={
            "groupname": groupname,
            "email": email
        }
    )

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"

# Test for /group DELETE (Delete Group)
def test_delete_group_blank_access(http_client: TestClient):
    response = http_client.delete("/group/1")
    assert response.status_code == 403

def test_delete_group_success(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    group_id = data["groups"][0]["group_id"]

    # Act
    response = http_client.delete(f"/group/{group_id}", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Group successfully deleted"

def test_delete_group_not_found(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    group_id = "not existing group"

    # Act
    response = http_client.delete(f"/group/{group_id}", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 403

# Test for /group/{group_id}/name GET (Get Group Name)
def test_get_group_name_blank_access(http_client: TestClient):
    response = http_client.get("/group/11111111-1111-1111-1111-111111111111/name")
    assert response.status_code == 200

def test_get_group_name_success(http_client: TestClient):
    # Arrange
    group_id = data["groups"][0]["group_id"]

    # Act
    response = http_client.get(f"/group/{group_id}/name")

    # Assert
    assert response.status_code == 200
    assert response.json()["name"] == data["groups"][0]["name"]

def test_get_group_name_not_exists(http_client: TestClient):
    # Arrange
    group_id = "not existing group"

    # Act
    response = http_client.get(f"/group/{group_id}/name")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Group with ID not existing group not found"

# Test for /group/{group_id} GET (Get Group Details)
def test_get_group_details_blank_access(http_client: TestClient):
    response = http_client.get("/group/11111111-1111-1111-1111-111111111111")
    assert response.status_code == 403

def test_get_group_details_success(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    group_id = data["groups"][0]["group_id"]

    # Act
    response = http_client.get(f"/group/{group_id}", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 200
    response_data = response.json()

    # Assert user data
    assert "user" in response_data
    assert response_data["user"]["id"] == data["users"][0]["user_id"]
    assert response_data["user"]["name"] == data["users"][0]["name"]
    assert response_data["user"]["role"] == data["users"][0]["role"]
    assert response_data["user"]["email"] == data["users"][0]["email"]

    # Assert group data
    assert response_data["group_id"] == group_id
    assert response_data["group_name"] == data["groups"][0]["name"]
    assert response_data["created_by"] == data["users"][0]["name"]

def test_get_group_details_not_exists(http_client: TestClient):
    response = http_client.get("/group/11111111-1111-1111-1111-111111111112")
    assert response.status_code == 403

# Test for /group/{group_id}/members GET (Get Group Members)

def test_get_group_members_blank_access(http_client: TestClient):
    response = http_client.get("/group/11111111-1111-1111-1111-111111111111/members")
    assert response.status_code == 403

def test_get_group_members_success(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    group_id = data["groups"][0]["group_id"]

    # Act
    response = http_client.get(f"/group/{group_id}/members", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 200
    response_data = response.json()

    # Assert members data
    assert isinstance(response_data["members"], list)
    assert len(response_data["members"]) > 0  # Ensure there's at least one member
    for member in response_data["members"]:
        assert "user_id" in member
        assert "role" in member
        assert "name" in member

    # Specific checks for the first member
    assert response_data["members"][0]["user_id"] == data["users"][0]["user_id"]
    assert response_data["members"][0]["name"] == data["users"][0]["name"]
    assert response_data["members"][0]["role"] == data["users"][0]["role"]

def test_get_group_members_not_exists(http_client: TestClient):
    response = http_client.get("/group/11111111-1111-1111-1111-111111111112/members")
    assert response.status_code == 403

# Test for /group/{group_id}/edits GET (Get Group Members)

def test_get_group_edits_blank_access(http_client: TestClient):
    response = http_client.get("/group/11111111-1111-1111-1111-111111111111/edits")
    assert response.status_code == 403

def test_get_group_edits_success(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    group_id = data["groups"][0]["group_id"]

    # Act
    response = http_client.get(f"/group/{group_id}/edits", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 200
    response_data = response.json()

    # Assert edits data
    assert isinstance(response_data["edits"], list)
    assert len(response_data["edits"]) > 0  # Ensure there's at least one edit
    for edit in response_data["edits"]:
        assert "edit_id" in edit
        assert "created_by" in edit
        assert "name" in edit
        assert "isLive" in edit

    # Specific checks for the first edit
    assert response_data["edits"][0]["edit_id"] == data["edits"][0]["edit_id"]
    assert response_data["edits"][0]["name"] == data["edits"][0]["name"]
    assert response_data["edits"][0]["created_by"] == data["edits"][0]["created_by"]

def test_get_group_edits_not_exists(http_client: TestClient):
    response = http_client.get("/group/11111111-1111-1111-1111-111111111112/edits")
    assert response.status_code == 403
    
""" Integration """

def test_create_and_get_group_details(http_client: TestClient):
    # Arrange - Erstellen der Gruppendaten
    groupname = "Integration Test Group"
    username = "Integration Test User"
    email = "integration_test@example.com"

    # Act - Erstellen der Gruppe
    response_create = http_client.post(
        "/group/",
        json={
            "groupname": groupname,
            "username": username,
            "email": email
        }
    )

    # Assert - Überprüfen der Antwort nach Erstellung
    assert response_create.status_code == 200
    response_data = response_create.json()
    assert "jwt" in response_data
    assert response_data["group_id"] is not None

    jwt_token = response_data["jwt"]
    group_id = response_data["group_id"]

    # Headers mit JWT-Token vorbereiten
    headers = {"Authorization": f"Bearer {jwt_token}"}

    # Act - Abrufen der Gruppendetails mit dem JWT-Token
    response_get = http_client.get(f"/group/{group_id}", headers=headers)

    # Assert - Überprüfen der Antwort nach Abruf der Details
    assert response_get.status_code == 200
    response_get_data = response_get.json()

    # Überprüfen der Benutzerdaten
    assert "user" in response_get_data
    assert response_get_data["user"]["name"] == username
    assert response_get_data["user"]["email"] == email

    # Überprüfen der Gruppendaten
    assert response_get_data["group_id"] == group_id
    assert response_get_data["group_name"] == groupname
    assert response_get_data["created_by"] == username