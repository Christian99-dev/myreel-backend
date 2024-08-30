from fastapi.testclient import TestClient

from api.auth import jwt
from api.mock.database.model import mock_model_local_links

# test edit go live
def test_edit_go_live_success(http_client: TestClient):
    response = http_client.post("/edit/3/goLive", headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Auf instagram hochgeladen!"
      
def test_edit_go_live_not_ready(http_client: TestClient):
    response = http_client.post("/edit/2/goLive", headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"})
    
    assert response.status_code == 422

def test_edit_go_live_not_auth(http_client: TestClient):
    response = http_client.post("/edit/3/goLive", headers={"Authorization": f"Bearer {jwt.create_jwt(3, 10)}"})
    
    assert response.status_code == 403
    
# delete
def test_edit_success(http_client: TestClient):
    response = http_client.delete("/edit/1", headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Deleted Successfully"

def test_edit_wrong_edit(http_client: TestClient):
    response = http_client.delete("/edit/5", headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"})
    
    assert response.status_code == 403

def test_edit_not_auth(http_client: TestClient):
    response = http_client.delete("/edit/5", headers={"Authorization": f"Bearer {jwt.create_jwt(99, 10)}"})
    
    assert response.status_code == 403

# create edit 
def notest_create_edit(http_client: TestClient):
    response = http_client.post(
        "/edit", 
        json={
            "groupid":mock_model_local_links.groups[0].group_id,
            "song_id":1,
            "edit_name":"joooo"
        }, 
        headers={"Authorization": f"Bearer {jwt.create_jwt(2, 10)}"})
    
    assert response.status_code == 200
    
def test_create_edit_no_song(http_client: TestClient):
    response = http_client.post(
        "/edit", 
        json={
            "groupid":mock_model_local_links.groups[0].group_id,
            "song_id":5,
            "edit_name":"joooo"
        }, 
        headers={"Authorization": f"Bearer {jwt.create_jwt(2, 10)}"})
    
    assert response.status_code == 422
    
def test_create_edit_auth(http_client: TestClient):
    response = http_client.post(
        "/edit", 
        json={
            "groupid":"s",
            "song_id":5,
            "edit_name":"joooo"
        }, 
        headers={"Authorization": f"Bearer {jwt.create_jwt(2, 10)}"})
    
    assert response.status_code == 403
    
def test_create_edit_auth_again(http_client: TestClient):
    response = http_client.post(
        "/edit", 
        json={
            "groupid":mock_model_local_links.groups[0].group_id,
            "song_id":5,
            "edit_name":"joooo"
        }, 
        headers={"Authorization": f"Bearer {jwt.create_jwt(5, 10)}"})
    
    assert response.status_code == 403
    
# list edits per grou
def test_create_edit(http_client: TestClient):
    response = http_client.get(
        f"/edit/group/{mock_model_local_links.groups[0].group_id}/list", headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"}
    )
    
    assert response.status_code == 200
    edits = response.json()["edits"]
    assert len(edits) == 3

def test_create_edit_auth(http_client: TestClient):
    response = http_client.get(
        f"/edit/group/{mock_model_local_links.groups[0].group_id}/list", headers={"Authorization": f"Bearer {jwt.create_jwt(4, 10)}"}
    )
    
    assert response.status_code == 403
    
def test_create_edit_auth_secound(http_client: TestClient):
    response = http_client.get(
        f"/edit/group/asd/list", headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"}
    )
    
    assert response.status_code == 403

# test get edit 
def test_get_edit(http_client: TestClient):
    # Definieren Sie die Gruppen-IDs
    group_id_1 = mock_model_local_links.groups[0].group_id

    # Senden Sie die GET-Anfrage an die API
    response = http_client.get(
        f"/edit/group/{group_id_1}/1", headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"}
    )

    # Assertions
    assert response.status_code == 200  # Überprüfen Sie, ob die Antwort den Status 200 hat

    # Überprüfen Sie die Struktur und den Inhalt der Antwort
    data = response.json()
    assert "edit_id" in data
    assert "song_id" in data
    assert "created_by" in data
    assert "group_id" in data
    assert "name" in data
    assert "isLive" in data
    assert "video_src" in data
    assert "slots" in data

    # Überprüfen Sie die Werte in der Antwort
    assert data["edit_id"] == 1
    assert data["song_id"] == 1
    assert data["created_by"]["user_id"] == 1
    assert data["created_by"]["name"] == "Creator of Group 1"
    assert data["group_id"] == group_id_1
    assert data["name"] == "Edit 1 of Group 1"
    assert data["isLive"] is False
    assert data["video_src"] == "http://localhost:8000/static/edits/1.mp4"

    # Überprüfen Sie die Slots
    assert isinstance(data["slots"], list)
    assert len(data["slots"]) > 0  # Überprüfen Sie, dass Slots zurückgegeben werden

    # Hier können Sie spezifische Überprüfungen für die Slots durchführen
    for slot in data["slots"]:
        assert "slot_id" in slot
        assert "song_id" in slot
        assert "start_time" in slot
        assert "end_time" in slot
        assert "occupied_by" in slot  # Überprüfen Sie, ob occupied_by existiert

def test_get_edit(http_client: TestClient):
    # Definieren Sie die Gruppen-IDs
    group_id_1 = mock_model_local_links.groups[2].group_id

    # Senden Sie die GET-Anfrage an die API
    response = http_client.get(
        f"/edit/group/{group_id_1}/1", headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"}
    )
    
    assert response.status_code == 403