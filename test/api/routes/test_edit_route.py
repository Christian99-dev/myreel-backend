from fastapi.testclient import TestClient

from api.utils.jwt import jwt

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
def test_create_edit(http_client: TestClient):
    response = http_client.post(
        "/edit", 
        json={
            "groupid":"11111111-1111-1111-1111-111111111111",
            "song_id":1,
            "edit_name":"joooo"
        }, 
        headers={"Authorization": f"Bearer {jwt.create_jwt(2, 10)}"})
    
    assert response.status_code == 200
    
def test_create_edit_no_song(http_client: TestClient):
    response = http_client.post(
        "/edit", 
        json={
            "groupid":"11111111-1111-1111-1111-111111111111",
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
            "groupid":"11111111-1111-1111-1111-111111111111",
            "song_id":5,
            "edit_name":"joooo"
        }, 
        headers={"Authorization": f"Bearer {jwt.create_jwt(5, 10)}"})
    
    assert response.status_code == 403
    
# list edits per grou
def test_create_edit(http_client: TestClient):
    response = http_client.get(
        f"/edit/group/11111111-1111-1111-1111-111111111111/list", headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"}
    )
    
    assert response.status_code == 200
    edits = response.json()["edits"]
    assert len(edits) == 3

def test_create_edit_auth(http_client: TestClient):
    response = http_client.get(
        f"/edit/group/11111111-1111-1111-1111-111111111111/list", headers={"Authorization": f"Bearer {jwt.create_jwt(4, 10)}"}
    )
    
    assert response.status_code == 403
    
def test_create_edit_auth_secound(http_client: TestClient):
    response = http_client.get(
        f"/edit/group/asd/list", headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"}
    )
    
    assert response.status_code == 403

# test get edit 
def test_get_edit(http_client: TestClient):

    # Senden Sie die GET-Anfrage an die API
    response = http_client.get(
        f"/edit/group/11111111-1111-1111-1111-111111111111/1", headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"}
    )

    # Assertions
    assert response.status_code == 200  # Überprüfen Sie, ob die Antwort den Status 200 hat

    # Überprüfen Sie die Struktur und den Inhalt der Antwort
    data = response.json()
    assert "edit" in data  # Überprüfen, ob das edit-Objekt existiert
    assert "slots" in data  # Überprüfen, ob die Slots existieren

    # Überprüfen Sie die Struktur des edit-Objekts
    edit = data["edit"]
    assert "edit_id" in edit
    assert "song_id" in edit
    assert "created_by" in edit
    assert "group_id" in edit
    assert "name" in edit
    assert "isLive" in edit
    assert "video_src" in edit

    # Überprüfen Sie die Werte im edit-Objekt
    assert edit["edit_id"] == 1
    assert edit["song_id"] == 1
    assert edit["created_by"]["user_id"] == 1
    assert edit["created_by"]["name"] == "Creator of Group 1"
    assert edit["group_id"] == "11111111-1111-1111-1111-111111111111"
    assert edit["name"] == "Edit 1 of Group 1"
    assert edit["isLive"] is False
    assert edit["video_src"] == "http://localhost:8000/files/edits/1.mp4"

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
        assert "occupied_id" in slot  # Überprüfen, ob occupied_id existiert

        # Überprüfen Sie den occupied_by-Wert
        if slot["occupied_by"] is not None:
            assert "user_id" in slot["occupied_by"]
            assert "name" in slot["occupied_by"]
        else:
            assert slot["occupied_id"] is None  # Bei nicht belegten Slots sollte occupied_id None sein
            
def test_get_edit_not_working(http_client: TestClient):
    # Senden Sie die GET-Anfrage an die API
    response = http_client.get(
        f"/edit/group/33333333-3333-3333-3333-333333333333/1", headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"}
    )
    
    assert response.status_code == 403
 
# test delete slot
def test_delete_slot_success(http_client: TestClient):  
    
    response = http_client.delete(
        f"/edit/group/11111111-1111-1111-1111-111111111111/1/slot/1", 
        headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"},
    )
    
    assert response.status_code == 200
    
def notest_delete_slot_not_yours(http_client: TestClient):  
    
    response = http_client.delete(
        f"/edit/group/11111111-1111-1111-1111-111111111111/1/slot/2", 
        headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"},
    )
    
    assert response.status_code == 403
    
def notest_delete_slot_not_found(http_client: TestClient):  
    
    response = http_client.delete(
        f"/edit/group/11111111-1111-1111-1111-111111111111/1/slot/44", 
        headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"},
    )
    
    assert response.status_code == 404
        
# test posts slot
def notest_post_slot_success(http_client: TestClient, file_session_memory):  
    
    video_file_slot = file_session_memory.get("demo.mp4","demo_slot")
      
    response = http_client.post(
        f"/edit/group/11111111-1111-1111-1111-111111111111/2/slot/1",
        headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"},
        files={
            "video_file": ("4.mp4", video_file_slot, "video/mp4"),
        },
        data={
            "start_time": 1,
            "end_time": 2
        }
    )
    
    assert response.status_code == 200
    
def notest_post_slot_slot_is_not_empty(http_client: TestClient, file_session_memory):  
    
    video_file_slot = file_session_memory.get("demo.mp4","demo_slot")
      
    response = http_client.post(
        f"/edit/group/11111111-1111-1111-1111-111111111111/1/slot/1",
        headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"},
        files={
            "video_file": ("4.mp4", video_file_slot, "video/mp4"),
        },
        data={
            "start_time": 1,
            "end_time": 2
        }
    )
    
    assert response.status_code == 403
    
# test swap slot
def notest_post_swap_slot_is_empty(http_client: TestClient, file_session_memory):  
    
    video_file_slot = file_session_memory.get("demo.mp4","demo_slot")
      
    response = http_client.put(
        f"/edit/group/11111111-1111-1111-1111-111111111111/2/slot/99",
        headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"},
        files={
            "video_file": ("4.mp4", video_file_slot, "video/mp4"),
        },
        data={
            "start_time": 1,
            "end_time": 2
        }
    )
    
    assert response.status_code == 400
    
def notest_post_swap_slot_not_yours(http_client: TestClient, file_session_memory):  
    
    video_file_slot = file_session_memory.get("demo.mp4","demo_slot")
      
    response = http_client.put(
        f"/edit/group/11111111-1111-1111-1111-111111111111/2/slot/2",
        headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"},
        files={
            "video_file": ("4.mp4", video_file_slot, "video/mp4"),
        },
        data={
            "start_time": 1,
            "end_time": 2
        }
    )
    
    assert response.status_code == 403
    
def notest_post_swap_slot_success(http_client: TestClient, file_session_memory):  
    
    video_file_slot = file_session_memory.get("demo.mp4","demo_slot")
      
    response = http_client.put(
        f"/edit/group/11111111-1111-1111-1111-111111111111/1/slot/1",
        headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"},
        files={
            "video_file": ("4.mp4", video_file_slot, "video/mp4"),
        },
        data={
            "start_time": 1,
            "end_time": 2
        }
    )
    
    assert response.status_code == 200
