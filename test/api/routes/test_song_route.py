from fastapi.testclient import TestClient
from test.utils.test_model import test_model

# create
def test_create(app_client_prod_routes: TestClient):
    # Act: Send a POST request to the create endpoint
    response = app_client_prod_routes.post("/song/create", json={
        "name": "Test Song",
        "author": "Test Author",
        "cover_src": "http://example.com/cover.jpg",
        "audio_src": "http://example.com/audio.mp3"
    })

    # Assert: Check the response status code and content
    assert response.status_code == 200
    data = response.json()
    assert data["name"]         == "Test Song"
    assert data["author"]       == "Test Author"
    assert data["cover_src"]    == "http://example.com/cover.jpg"
    assert data["audio_src"]    == "http://example.com/audio.mp3"
    assert data["times_used"]   == 0  
    
# list    
def test_list(app_client_prod_routes: TestClient):
    # Act: Send a GET request to the list endpoint
    response = app_client_prod_routes.get("/song/list")

    # Assert: Check the response status code and content
    assert response.status_code == 200
    data = response.json()
    
    songs = data.get("songs")
    
    # # Verify: Ensure the number of songs returned matches the test data
    assert len(songs) == len(test_model.songs)
    
    # # Verify: Ensure the content matches the test data
    for song in songs:
        assert any(
            song["song_id"] == test_song.song_id and
            song["name"] == test_song.name and
            song["author"] == test_song.author and
            song["cover_src"] == test_song.cover_src and
            song["audio_src"] == test_song.audio_src and
            song["times_used"] == test_song.times_used
            for test_song in test_model.songs
        )

# get
def test_get_song(app_client_prod_routes: TestClient):
    test_song = test_model.songs[0]
    response = app_client_prod_routes.get(f"/song/get/{test_song.song_id}")
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["song_id"] == test_song.song_id
    assert response_data["name"] == test_song.name
    assert response_data["author"] == test_song.author
    assert response_data["cover_src"] == test_song.cover_src
    assert response_data["audio_src"] == test_song.audio_src
    assert response_data["times_used"] == test_song.times_used

def test_get_song_not_found(app_client_prod_routes: TestClient):
    response = app_client_prod_routes.get("/song/get/999999")  
    assert response.status_code == 404
    assert response.json() == {"detail": "Song not found"}

def test_get_song_invalid_id(app_client_prod_routes: TestClient):
    response = app_client_prod_routes.get("/song/get/abc")  
    assert response.status_code == 422