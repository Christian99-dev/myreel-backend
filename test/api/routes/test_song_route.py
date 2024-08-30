from fastapi.testclient import TestClient
from api.config.media_access import BaseMediaAccess
from api.services.media.cover import get as get_cover
from api.services.media.song import get as get_song
from api.services.database.song import remove as remove_song_service
from sqlalchemy.orm import Session

# create
def test_create(http_client: TestClient, media_access_memory: BaseMediaAccess, admintoken: int): 
    cover_file_bytes = get_cover(1, media_access_memory)  # Mock cover file
    song_file_bytes = get_song(1, media_access_memory)    # Mock song file

    valid_breakpoints = [0.0, 30.0, 60.0]  # Example valid breakpoints

    response = http_client.post(
        "/song/",  # Your endpoint here
        headers={"admintoken": admintoken},
        files={
            "cover_file": ("test_cover.jpg", cover_file_bytes, "image/jpeg"),
            "song_file": ("test_song.wav", song_file_bytes, "audio/wav"),
        },
        data={
            "name": "Test Song",
            "author": "Test Artist",
            "breakpoints": valid_breakpoints,
        }
    )

    assert response.status_code == 200  # Expecting a successful creation
    response_data = response.json()

    # Validate response structure and data
    assert "song_id" in response_data
    assert response_data["name"] == "Test Song"
    assert response_data["author"] == "Test Artist"
    assert isinstance(response_data["times_used"], int)
    assert isinstance(response_data["cover_src"], str)
    assert isinstance(response_data["audio_src"], str)
    
def test_create_not_good_breakpoints(http_client: TestClient, media_access_memory: BaseMediaAccess, admintoken: int): 
    cover_file_bytes = get_cover(1, media_access_memory)  # Mock cover file
    song_file_bytes = get_song(1, media_access_memory)    # Mock song file

    valid_breakpoints = [0.0, 30.0, 1000.0]  # Example valid breakpoints

    response = http_client.post(
        "/song/",  # Your endpoint here
        headers={"admintoken": admintoken},
        files={
            "cover_file": ("test_cover.jpg", cover_file_bytes, "image/jpeg"),
            "song_file": ("test_song.wav", song_file_bytes, "audio/wav"),
        },
        data={
            "name": "Test Song",
            "author": "Test Artist",
            "breakpoints": valid_breakpoints,
        }
    )

    assert response.status_code == 400  # Expecting a successful creation

def test_create_status(http_client: TestClient): 
    assert http_client.post("/song/").status_code == 403

# remove
def test_delete_song(http_client: TestClient, admintoken: int):
    # Step 1: Now, try to delete the created song
    delete_response = http_client.delete(f"/song/2", headers={"admintoken": admintoken})

    # Step 2: Validate the response from the DELETE request
    assert delete_response.status_code == 200  # Expecting a successful deletion

def test_delete_non_existent_song(http_client: TestClient, admintoken: int):
    non_existent_song_id = 9999  # A song ID that doesn't exist

    delete_response = http_client.delete(f"/song/{non_existent_song_id}", headers={"admintoken": admintoken})
    
    # Expect a 404 response as the song does not exist
    assert delete_response.status_code == 404

def test_delete_status(http_client: TestClient):
    assert http_client.delete("/song/1").status_code == 403

# list
def test_list_songs(http_client: TestClient):
    response = http_client.get("/song/list")  # Adjust the endpoint as necessary
    assert response.status_code == 200  # Expecting a successful response
    response_data = response.json()
    
    # Validate the response structure
    assert "songs" in response_data
    assert isinstance(response_data["songs"], list)
    
    # Validate that the returned list matches the mock data
    assert len(response_data["songs"]) == 3  # Assuming you have 3 songs in mock data
    assert response_data["songs"][0]["name"] == "Song 1"
    assert response_data["songs"][1]["name"] == "Song 2"
    assert response_data["songs"][2]["name"] == "Song 3"

def test_list_status(http_client: TestClient):
    assert http_client.get("/song/list").status_code == 200


# get
def test_get_song(http_client: TestClient):
    response = http_client.get("/song/1")  # Get song with ID 1
    assert response.status_code == 200  # Expecting a successful response
    response_data = response.json()
    
    # Validate the response structure
    assert response_data["song_id"] == 1
    assert response_data["name"] == "Song 1"
    assert response_data["author"] == "Author 1"

def test_get_non_existent_song(http_client: TestClient):
    response = http_client.get("/song/999")  # Attempting to get a non-existent song
    assert response.status_code == 404  # Expecting a not found response
    
def test_get_status(http_client: TestClient):
    assert http_client.get("/song/1").status_code == 200


