from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.models.database.model import Song
from api.sessions.files import BaseFileSessionManager
from mock.database.data import data


# Test for creating a song
def test_create_blank_access(http_client: TestClient):
    response = http_client.post("/song/")
    assert response.status_code == 403

def test_create_song_success(http_client: TestClient, memory_file_session: BaseFileSessionManager, admintoken: str):
    
    # Arrange
    cover_file_bytes = memory_file_session.get("1", "covers")
    song_file_bytes = memory_file_session.get("1", "songs")

    assert type(cover_file_bytes) is bytes 
    assert type(song_file_bytes) is bytes 

    # Act
    response = http_client.post(
        "/song/", 
        headers={"admintoken": admintoken},
        files={
            "cover_file": ("test_cover.png", cover_file_bytes, "image/png"),
            "song_file": ("test_song.wav", song_file_bytes, "audio/wav"),
        },
        data={
            "name": "Test Song",
            "author": "Test Artist",
            "breakpoints": [0.0, 1.0, 2.5],
        }
    )

    # Assert
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "Test Song"
    assert response_json["author"] == "Test Artist"
    assert response_json["audio_src"] is not None
    assert response_json["cover_src"] is not None

def test_create_song_invalid_file_format(http_client: TestClient, memory_file_session: BaseFileSessionManager, admintoken: str):
    # Arrange: Retrieve a video file (which is an invalid format for the song upload)
    invalid_file_bytes = memory_file_session.get("demo", "demo_slot")  # Assuming you have videos in the file session

    assert type(invalid_file_bytes) is bytes 

    # Act: Try to upload the video as a song file
    response = http_client.post(
        "/song/", 
        headers={"admintoken": admintoken},
        files={
            "cover_file": ("test_cover.png", invalid_file_bytes, "image/png"),
            "song_file": ("test_video.mp4", invalid_file_bytes, "video/mp4"),  # Invalid file type for song
        },
        data={
            "name": "Test Song with Invalid Format",
            "author": "Test Artist",
            "breakpoints": [0.0, 1.0, 2.5],
        }
    )

    # Assert: Expect a 400 error due to invalid file format
    assert response.status_code == 400
    assert "Dateityp video/mp4 nicht erlaubt für audio" in response.json()["detail"]

def test_create_song_invalid_breakpoints(http_client: TestClient, memory_file_session: BaseFileSessionManager, admintoken: str):
    # Arrange: Retrieve valid cover and song files
    cover_file_bytes = memory_file_session.get("1", "covers")
    song_file_bytes = memory_file_session.get("1", "songs")

    assert type(cover_file_bytes) is bytes 
    assert type(song_file_bytes) is bytes 

    # Act: Try to create a song with invalid breakpoints
    response = http_client.post(
        "/song/", 
        headers={"admintoken": admintoken},
        files={
            "cover_file": ("test_cover.png", cover_file_bytes, "image/png"),
            "song_file": ("test_song.wav", song_file_bytes, "audio/wav"),
        },
        data={
            "name": "Test Song with Invalid Breakpoints",
            "author": "Test Artist",
            # Invalid breakpoints (end time > song duration)
            "breakpoints": [0.0, 10000.0],  
        }
    )

    # Assert: Expect a 400 error due to invalid breakpoints
    assert response.status_code == 400
    assert "Breakpoints exceed song duration" in response.json()["detail"]

# Test for deleting a song
def test_delete_blank_access(http_client: TestClient):
    response = http_client.delete("/song/1")
    assert response.status_code == 403

def test_delete_song_success(http_client: TestClient, admintoken: str):
    # Arrange
    song_id = data["songs"][0]["song_id"]

    # Act
    response = http_client.delete(f"/song/{song_id}", headers={"admintoken": admintoken},)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Song and associated media deleted successfully"

def test_delete_song_not_foungs(http_client: TestClient, admintoken: str):
    # Arrange
    song_id = 99

    # Act
    response = http_client.delete(f"/song/{song_id}", headers={"admintoken": admintoken})

    # Assert
    assert response.status_code == 500
    assert response.json()["detail"] == "File '99' not found in memory under 'songs'"

# Test for listing songs
def test_list_blank_access(http_client: TestClient):
    response = http_client.get("/song/list")
    assert response.status_code == 200

def test_list_songs_success(http_client: TestClient):
    # Act
    response = http_client.get("/song/list")

    # Assert
    assert response.status_code == 200
    songs = response.json()["songs"]
    assert len(songs) > 0  # Should return more than one song
    assert songs[0]["name"] == data["songs"][0]["name"]

def test_list_songs_no_songs(http_client: TestClient, memory_database_session: Session):
    # Arrange: Lösche alle Songs aus der Datenbank
    memory_database_session.query(Song).delete()
    memory_database_session.commit()

    # Act: Rufe die Liste der Songs ab
    response = http_client.get("/song/list")

    # Assert: Überprüfe, dass keine Songs vorhanden sind
    assert response.status_code == 404
    assert "No songs found in the database." in response.json()["detail"]


# Test for getting a song by ID
def test_get_blank_access(http_client: TestClient):
    response = http_client.get("/song/1")
    assert response.status_code == 200

def test_get_song_success(http_client: TestClient):
    # Arrange
    song_id = data["songs"][0]["song_id"]

    # Act
    response = http_client.get(f"/song/{song_id}")

    # Assert
    assert response.status_code == 200
    song = response.json()
    assert song["name"] == data["songs"][0]["name"]
    assert song["author"] == data["songs"][0]["author"]

def test_get_song_not_found(http_client: TestClient):
    # Arrange
    song_id = 99

    # Act
    response = http_client.get(f"/song/{song_id}")

    # Assert
    assert response.status_code == 404
    assert "Song with ID 99 not found." in response.json()["detail"]
