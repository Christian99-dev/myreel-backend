from typing import List
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session
from api.exceptions.sessions.files import FileNotFoundInSessionError
from api.models.database.model import Edit, OccupiedSlot, Slot
from api.sessions.files import BaseFileSessionManager
from mock.database.data import data

# Test for deleting a slot
def test_delete_slot_blank_access(http_client: TestClient):
    response = http_client.delete("/edit/1/slot/1")
    assert response.status_code == 403

def test_delete_slot_success(http_client: TestClient, memory_database_session: Session, memory_file_session: BaseFileSessionManager,bearer_headers: List[dict[str, str]]):
    # Arrange
    occupied_slot_id = data["occupied_slots"][0]["occupied_slot_id"]
    
    # Act
    response = http_client.delete(f"/edit/1/slot/{occupied_slot_id}", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Successfull delete"
    
    # Check if slot is deleted from the database
    occupied_slot = memory_database_session.query(OccupiedSlot).filter_by(occupied_slot_id=occupied_slot_id).first()
    assert occupied_slot is None

    with pytest.raises(FileNotFoundInSessionError):
        memory_file_session.get("1", "occupied_slots")

def test_delete_slot_wrong_edit(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    occupied_slot_id = data["occupied_slots"][0]["occupied_slot_id"]
    
    # Act
    response = http_client.delete(f"/edit/2/slot/{occupied_slot_id}", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 403
    assert response.json()["detail"] == "Edit has not occupied slot with id 2"

def test_delete_slot_unauthorized_edit(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    occupied_slot_id = data["occupied_slots"][0]["occupied_slot_id"]
    
    # Act
    response = http_client.delete(f"/edit/5/slot/{occupied_slot_id}", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 403

def test_delete_slot_wrong_slot(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    occupied_slot_id = 99
    
    # Act
    response = http_client.delete(f"/edit/1/slot/{occupied_slot_id}", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Occupied slot with ID 99 not found."

def test_delete_slot_not_yours(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    occupied_slot_id = 2
    
    # Act
    response = http_client.delete(f"/edit/1/slot/{occupied_slot_id}", headers=bearer_headers[0])

    # Assert
    assert response.status_code == 403
    assert response.json()["detail"] == "Slot not yours"


# Test for posting a slot
def test_post_slot_blank_access(http_client: TestClient):
    response = http_client.post("/edit/1/slot/1")
    assert response.status_code == 403

def test_post_slot_success(http_client: TestClient, memory_database_session: Session, memory_file_session: BaseFileSessionManager,bearer_headers: List[dict[str, str]]):
    # Arrange
    slot_id = data["slots"][1]["slot_id"]
    video_file_bytes = memory_file_session.get("1", "occupied_slots")
    
    
    # Act
    response = http_client.post(
        f"/edit/1/slot/{slot_id}", 
        headers=bearer_headers[0],
        files={
            "video_file": ("test_video.mp4", video_file_bytes, "video/mp4")
        },
        data={
            "start_time": 0.0,
            "end_time": 0.5
        }
    )
    
    # Assert
    assert response.json()["message"] == "Successfull post"
    
    # Check if slot is added to the database
    occupied_slot = memory_database_session.query(OccupiedSlot).filter_by(slot_id=slot_id).first()
    assert occupied_slot is not None

    # datei ist da
    new_occupied_slot_video = memory_file_session.get(occupied_slot.occupied_slot_id, "occupied_slots")
    assert new_occupied_slot_video is not None

def test_post_taken_slot(http_client: TestClient, memory_file_session: BaseFileSessionManager, bearer_headers: List[dict[str, str]]):
    # Arrange
    slot_id = data["slots"][1]["slot_id"]
    video_file_bytes = memory_file_session.get("1", "occupied_slots")

    
    # Act
    response = http_client.post(
        f"/edit/2/slot/{slot_id}", 
        headers=bearer_headers[0],
        files={
            "video_file": ("test_video.mp4", video_file_bytes, "video/mp4")
        },
        data={
            "start_time": 0.0,
            "end_time": 0.5
        }
    )

    # Assert
    assert response.status_code == 403
    assert response.json()["detail"] == "Slot ist schon belegt"
    
def test_post_slot_to_long(http_client: TestClient, memory_file_session: BaseFileSessionManager, bearer_headers: List[dict[str, str]]):
    # Arrange
    slot_id = data["slots"][1]["slot_id"]
    video_file_bytes = memory_file_session.get("1", "occupied_slots")

    
    # Act
    response = http_client.post(
        f"/edit/1/slot/{slot_id}", 
        headers=bearer_headers[0],
        files={
            "video_file": ("test_video.mp4", video_file_bytes, "video/mp4")
        },
        data={
            "start_time": 0.0,
            "end_time": 0.6
        }
    )

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"] == "Slot länge muss die gleiche sein"

def test_post_slot_not_found(http_client: TestClient, memory_file_session: BaseFileSessionManager, bearer_headers: List[dict[str, str]]):
    # Arrange
    slot_id = 99
    video_file_bytes = memory_file_session.get("1", "occupied_slots")

    
    # Act
    response = http_client.post(
        f"/edit/2/slot/{slot_id}", 
        headers=bearer_headers[0],
        files={
            "video_file": ("test_video.mp4", video_file_bytes, "video/mp4")
        },
        data={
            "start_time": 0.0,
            "end_time": 0.5
        }
    )

    # Assert
    assert response.status_code == 404


# Test for updating a slot
def test_put_slot_blank_access(http_client: TestClient):
    response = http_client.put("/edit/1/slot/1")
    assert response.status_code == 403
    
def test_put_slot_success(http_client: TestClient, memory_file_session: BaseFileSessionManager, bearer_headers: List[dict[str, str]], memory_database_session: Session):
    # Arrange
    occupied_slot_id = data["occupied_slots"][0]["occupied_slot_id"]
    video_file_bytes = memory_file_session.get("1", "occupied_slots")

    # Act
    response = http_client.put(
        f"/edit/1/slot/{occupied_slot_id}", 
        headers=bearer_headers[0],
        files={
            "video_file": ("updated_test_video.mp4", video_file_bytes, "video/mp4")
        },
        data={
            "start_time": 0.0,
            "end_time": 0.5
        }
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Successfull swap"
    
    # Check if slot is updated in the database
    updated_slot = memory_database_session.query(OccupiedSlot).filter_by(occupied_slot_id=occupied_slot_id).first()
    assert updated_slot is not None
    
def test_put_new_slot_too_long(http_client: TestClient, memory_file_session: BaseFileSessionManager, bearer_headers: List[dict[str, str]], memory_database_session: Session):
    # Arrange
    occupied_slot_id = data["occupied_slots"][0]["occupied_slot_id"]
    video_file_bytes = memory_file_session.get("1", "occupied_slots")
    old_location = data["occupied_slots"][0]["video_src"]

    # Act
    response = http_client.put(
        f"/edit/1/slot/{occupied_slot_id}", 
        headers=bearer_headers[0],
        files={
            "video_file": ("updated_test_video.mp4", video_file_bytes, "video/mp4")
        },
        data={
            "start_time": 0.0,
            "end_time": 0.6
        }
    )
    
    # Assert
    assert response.status_code == 422
    assert response.json()["detail"] == "Slot länge muss die gleiche sein"
    
def test_put_slot_wrong_edit(http_client: TestClient, memory_file_session: BaseFileSessionManager, bearer_headers: List[dict[str, str]], memory_database_session: Session):
    # Arrange
    occupied_slot_id = data["occupied_slots"][0]["occupied_slot_id"]
    video_file_bytes = memory_file_session.get("1", "occupied_slots")

    # Act
    response = http_client.put(
        f"/edit/2/slot/{occupied_slot_id}", 
        headers=bearer_headers[0],
        files={
            "video_file": ("updated_test_video.mp4", video_file_bytes, "video/mp4")
        },
        data={
            "start_time": 0.0,
            "end_time": 0.5
        }
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Edit has not occupied slot with id 2"

def test_put_slot_unauthorized(http_client: TestClient, memory_file_session: BaseFileSessionManager, bearer_headers: List[dict[str, str]], memory_database_session: Session):
    # Arrange
    occupied_slot_id = data["occupied_slots"][0]["occupied_slot_id"]
    video_file_bytes = memory_file_session.get("1", "occupied_slots")

    # Act
    response = http_client.put(
        f"/edit/5/slot/{occupied_slot_id}", 
        headers=bearer_headers[0],
        files={
            "video_file": ("updated_test_video.mp4", video_file_bytes, "video/mp4")
        },
        data={
            "start_time": 0.0,
            "end_time": 0.5
        }
    )
    
    assert response.status_code == 403

def test_put_slot_not_yours(http_client: TestClient, memory_file_session: BaseFileSessionManager, bearer_headers: List[dict[str, str]], memory_database_session: Session):
    # Arrange
    occupied_slot_id = data["occupied_slots"][1]["occupied_slot_id"]
    video_file_bytes = memory_file_session.get("1", "occupied_slots")

    # Act
    response = http_client.put(
        f"/edit/1/slot/{occupied_slot_id}", 
        headers=bearer_headers[0],
        files={
            "video_file": ("updated_test_video.mp4", video_file_bytes, "video/mp4")
        },
        data={
            "start_time": 0.0,
            "end_time": 0.5
        }
    )
    
    assert response.status_code == 403

def test_put_slot_not_found(http_client: TestClient, memory_file_session: BaseFileSessionManager, bearer_headers: List[dict[str, str]], memory_database_session: Session):
    # Arrange
    occupied_slot_id = 9
    video_file_bytes = memory_file_session.get("1", "occupied_slots")

    # Act
    response = http_client.put(
        f"/edit/1/slot/{occupied_slot_id}", 
        headers=bearer_headers[0],
        files={
            "video_file": ("updated_test_video.mp4", video_file_bytes, "video/mp4")
        },
        data={
            "start_time": 0.0,
            "end_time": 0.5
        }
    )
    
    assert response.status_code == 404
