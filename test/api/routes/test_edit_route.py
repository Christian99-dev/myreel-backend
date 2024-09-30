import logging
from typing import List

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.services.database.occupied_slot import create as create_occupied_slot_database
from mock.database.data import data

import PIL

logger = logging.getLogger("test.unittest")


# Test for /edit POST (Create Edit)
def test_create_edit_blank_access(http_client: TestClient):
    # No Authorization header provided, should return 403
    response = http_client.post("/edit/")
    assert response.status_code == 403

def test_create_edit_success(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    song_id = data["songs"][0]["song_id"]  # Song 1
    group_id = data["groups"][0]["group_id"]  # Group 1
    user_id = data["users"][0]["user_id"]  # User 1 (Creator of Group 1)

    # Act
    response = http_client.post(
        "/edit/",
        headers=bearer_headers[0],
        json={
            "song_id": song_id,
            "groupid": group_id,
            "edit_name": "New Edit for Group 1"
        }
    )

    # Assert
    assert response.status_code == 200
    response_data = response.json()

    # Check if the new edit was created properly
    assert response_data["edit_id"] is not None
    assert response_data["name"] == "New Edit for Group 1"
    assert response_data["video_src"] == "memory://edits/10.mp4"
    assert response_data["group_id"] == group_id
    assert response_data["song_id"] == song_id
    assert response_data["created_by"] == user_id

def test_create_edit_invalid_name(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    song_id = data["songs"][0]["song_id"]  # Song 1
    group_id = data["groups"][0]["group_id"]  # Group 1

    # Act
    response = http_client.post(
        "/edit/",
        headers=bearer_headers[0],
        json={
            "song_id": song_id,
            "groupid": group_id,
            "edit_name": "New Edit for Group 1 TOOOOO LOOOOOOOONG"
        }
    )

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "String should have at most 20 characters"

# Test for /edit/{edit_id} GET (Get Edit Details)
def test_get_edit_details_blank_access(http_client: TestClient):
    # No Authorization header provided, should return 403
    response = http_client.get("/edit/1")
    assert response.status_code == 403

def test_get_edit_details_success(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    edit_id = data["edits"][0]["edit_id"]  # Edit 1
    expected_edit = data["edits"][0]  # Edit 1 of Group 1
    creator_id = data["users"][0]["user_id"]  # Creator of Group 1

    # Act
    response = http_client.get(f"/edit/{edit_id}", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 200
    response_data = response.json()
   
    # Check edit information
    assert response_data["edit"]["edit_id"] == expected_edit["edit_id"]
    assert response_data["edit"]["name"] == expected_edit["name"]
    assert response_data["edit"]["song_id"] == expected_edit["song_id"]
    assert response_data["edit"]["group_id"] == expected_edit["group_id"]
    assert response_data["edit"]["isLive"] == expected_edit["isLive"]
    assert response_data["edit"]["video_src"] == expected_edit["video_src"]

    # Check creator information
    assert response_data["created_by"]["user_id"] == creator_id
    assert response_data["created_by"]["name"] == "Creator of Group 1"

    # Check slot information
    assert len(response_data["slots"]) == 3  # There are 3 slots for Song 1
    assert response_data["slots"][0]["slot_id"] == 1
    assert response_data["slots"][0]["song_id"] == 1
    assert response_data["slots"][0]["start_time"] == 0
    assert response_data["slots"][0]["end_time"] == 0.5
    assert response_data["slots"][0]["occupied_by"]["user_id"] == 1
    assert response_data["slots"][0]["occupied_by"]["name"] == "Creator of Group 1"
    assert response_data["slots"][0]["video_src"] == "http://localhost:8000/files/occupied_slots/1.mp4"
    assert response_data["slots"][0]["occupied_start_time"] == 0
    assert response_data["slots"][0]["occupied_end_time"] == 0.5

    assert response_data["slots"][1]["slot_id"] == 2
    assert response_data["slots"][1]["song_id"] == 1
    assert response_data["slots"][1]["start_time"] == 0.5
    assert response_data["slots"][1]["end_time"] == 1
    assert response_data["slots"][1]["occupied_by"] is None
    assert response_data["slots"][1]["occupied_start_time"] is None
    assert response_data["slots"][1]["occupied_end_time"] is None

    # Assert the last slot has no user occupying
    assert response_data["slots"][2]["slot_id"] == 3
    assert response_data["slots"][2]["occupied_by"] is None

def test_get_edit_not_found(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    edit_id = -99  # Edit 1

    # Act
    response = http_client.get(f"/edit/{edit_id}", headers=bearer_headers[0])
    assert response.status_code == 403

# Test for /edit/{edit_id}/goLive POST (Go Live)
def test_go_live_blank_access(http_client: TestClient):
    # No Authorization header provided, should return 403
    response = http_client.post("/edit/1/goLive")
    assert response.status_code == 403

def test_go_live_success(http_client: TestClient, memory_database_session: Session, bearer_headers: List[dict[str, str]]):
    # Arrange: Set occupied slots for only Slot 2 and Slot 3
    edit_id = data["edits"][0]["edit_id"]  # We are using Edit 1 of Group 1
    user_id = data["users"][0]["user_id"]  # Creator of Group 1

    create_occupied_slot_database(user_id, 2, 1, "idk", database_session=memory_database_session, start_time=0, end_time=0.5)
    create_occupied_slot_database(user_id, 3, 1, "idk", database_session=memory_database_session, start_time=0, end_time=0.5)
    
    # Arrange
    edit_id = data["edits"][0]["edit_id"]

    # Act
    response = http_client.post(f"/edit/{edit_id}/goLive", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Auf instagram hochgeladen!"

def test_go_live_not_all_slots_are_occupied(http_client: TestClient, memory_database_session: Session, bearer_headers: List[dict[str, str]]):
    # Arrange: Set occupied slots for only Slot 2 and Slot 3
    edit_id = data["edits"][0]["edit_id"]  # We are using Edit 1 of Group 1

    # Act
    response = http_client.post(f"/edit/{edit_id}/goLive", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"] == "Edit not upload ready, occupie all slots"

def test_go_live_not_found(http_client: TestClient, memory_database_session: Session, bearer_headers: List[dict[str, str]]):

    # Act
    response = http_client.post(f"/edit/9999/goLive", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 403


# Test for /edit/{edit_id} DELETE (Delete Edit)
def test_delete_edit_blank_access(http_client: TestClient):
    # No Authorization header provided, should return 403
    response = http_client.delete("/edit/1")
    assert response.status_code == 403

def test_delete_edit_success(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    edit_id = data["edits"][0]["edit_id"]

    # Act
    response = http_client.delete(f"/edit/{edit_id}", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Deleted Successfully"

def test_delete_edit_not_found(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    edit_id = 9999

    # Act
    response = http_client.delete(f"/edit/{edit_id}", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 403
