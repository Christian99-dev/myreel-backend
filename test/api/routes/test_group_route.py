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

    # Assert members
    assert "members" in response_data
    members = response_data["members"]
    assert len(members) == len([user for user in data["users"] if user["group_id"] == group_id])
    for member in members:
        member_data = next((user for user in data["users"] if user["user_id"] == member["user_id"]), None)
        assert member_data is not None
        assert member["name"] == member_data["name"]
        assert member["role"] == member_data["role"]

    # Assert edits
    assert "edits" in response_data
    edits = response_data["edits"]
    assert len(edits) == len([edit for edit in data["edits"] if edit["group_id"] == group_id])
    for edit in edits:
        edit_data = next((e for e in data["edits"] if e["edit_id"] == edit["edit_id"]), None)
        assert edit_data is not None
        assert edit["created_by"] == edit_data["created_by"]
        assert edit["name"] == edit_data["name"]
        assert edit["isLive"] == edit_data["isLive"]

    # Assert group data
    assert response_data["group_id"] == group_id
    assert response_data["group_name"] == data["groups"][0]["name"]

def test_get_group_details_not_exists(http_client: TestClient):
    response = http_client.get("/group/11111111-1111-1111-1111-111111111112")
    assert response.status_code == 403
