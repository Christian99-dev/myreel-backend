import asyncio
from typing import List
from fastapi import WebSocketDisconnect
from fastapi.testclient import TestClient
import pytest
import time
from api.sessions.files import MemoryFileSessionManager
from mock.database.data import data


"""Auth"""
@pytest.mark.asyncio
async def test_websocket_blank_access(http_client: TestClient):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with http_client.websocket_connect("/ws/updates/11111111-1111-1111-1111-111111111111"):
            pass
    # Überprüfe, ob der Code für fehlende Authentifizierung korrekt ist (1008)
    assert exc_info.value.code == 1008

@pytest.mark.asyncio
async def test_websocket_wrong_jwt(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Extrahiere das JWT aus den Headern
    authorization_header = bearer_headers[0]["Authorization"]
    jwt_token = authorization_header.replace("Bearer ", "")

    # Füge das falsche JWT als Query-Parameter hinzu
    ws_url = f"/ws/updates/22222222-2222-2222-2222-222222222222?token=Bearer%20{jwt_token}"

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with http_client.websocket_connect(ws_url):
            pass
    # Überprüfe, ob der Code für falsches JWT korrekt ist (4001 oder 1008)
    assert exc_info.value.code == 4001  # Da der JWT ungültig ist, sollte der Code 1008 sein

"""Success"""        
@pytest.mark.asyncio
async def test_websocket_edit_success(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    song_id = data["songs"][0]["song_id"]  # Song 1
    group_id = data["groups"][1]["group_id"]  # Group 1

    # Extrahiere das JWT aus den Headern
    authorization_header = bearer_headers[3]["Authorization"]
    jwt_token = authorization_header.replace("Bearer ", "")
    jwt_token_encoded = jwt_token

    # Füge das JWT als Query-Parameter hinzu
    ws_url = f"/ws/updates/{group_id}?token=Bearer%20{jwt_token_encoded}"

    # Verbinde dich über WebSocket
    with http_client.websocket_connect(ws_url) as websocket:
        # Act: Erstelle einen neuen Edit
        response = http_client.post(
            "/edit/",
            headers=bearer_headers[3],
            json={
                "song_id": song_id,
                "groupid": group_id,
                "edit_name": "New Edit for Group 1"
            }
        )

        assert response.status_code == 200

        # Warte auf die Nachricht über den WebSocket
        message = websocket.receive_text()
        assert message == "EDIT"
        
@pytest.mark.asyncio
async def test_websocket_user_success(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    group_id = data["groups"][0]["group_id"]
    
    # Extrahiere das JWT aus den Headern
    authorization_header = bearer_headers[0]["Authorization"]
    jwt_token = authorization_header.replace("Bearer ", "")
    jwt_token_encoded = jwt_token

    # Füge das JWT als Query-Parameter hinzu
    ws_url = f"/ws/updates/{group_id}?token=Bearer%20{jwt_token_encoded}"

    with http_client.websocket_connect(ws_url) as websocket:
        response = http_client.post(
            "/user/acceptInvite",
            json={
                "invitationid": "1",
                "token": "token1",
                "groupid": "11111111-1111-1111-1111-111111111111",
                "name": "New User"
            }
        )

        # Assert
        assert response.status_code == 200

        # Warte auf die Nachricht über den WebSocket
        message = websocket.receive_text()
        assert message == "USER"

@pytest.mark.asyncio
async def test_websocket_occupied_slot_post_put_delete(http_client: TestClient, memory_file_session: MemoryFileSessionManager, bearer_headers: List[dict[str, str]]):
    group_id = data["groups"][0]["group_id"]
    free_slot_id = data["slots"][1]["slot_id"]  # Slot 1
    new_occupied_slot_id = len(data["occupied_slots"]) + 1
    video_file_bytes = memory_file_session.get("1", "occupied_slots")
    
    # Extrahiere das JWT aus den Headern
    authorization_header = bearer_headers[0]["Authorization"]
    jwt_token = authorization_header.replace("Bearer ", "")
    jwt_token_encoded = jwt_token

    # Füge das JWT als Query-Parameter hinzu
    ws_url = f"/ws/updates/{group_id}?token=Bearer%20{jwt_token_encoded}"
    

    # Verbinde dich über WebSocket
    with http_client.websocket_connect(ws_url) as websocket:

        # POST
        response = http_client.post(
            f"/edit/1/slot/{free_slot_id}",
            headers=bearer_headers[0],
            files={
                "video_file": ("test_video.mp4", video_file_bytes, "video/mp4")
            },
            data={
                "start_time": 0.0,
                "end_time": 0.5
            }
        )
        assert response.status_code == 200
        assert websocket.receive_text() == "OCCUPIEDSLOT"

        # # PUT
        response = http_client.put(
            f"/edit/1/slot/{new_occupied_slot_id}",
            headers=bearer_headers[0],
            files={
                "video_file": ("updated_test_video.mp4", video_file_bytes, "video/mp4")
            },
            data={
                "start_time": 0.0,
                "end_time": 0.5
            }
        )
        assert response.status_code == 200
        assert websocket.receive_text() == "OCCUPIEDSLOT"

        # DELETE
        response = http_client.delete(f"/edit/1/slot/{new_occupied_slot_id}", headers=bearer_headers[0])
        assert response.status_code == 200
        assert websocket.receive_text() == "OCCUPIEDSLOT"

"""Multiple Connections"""
@pytest.mark.asyncio
async def test_websocket_multiple_connections_check_queue(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    group_1_id = data["groups"][0]["group_id"]  # Group 1
    group_2_id = data["groups"][1]["group_id"]  # Group 2
    
    # Extrahiere das JWT aus den Headern
    authorization_header_user_1 = bearer_headers[0]["Authorization"]
    jwt_token_user_1 = authorization_header_user_1.replace("Bearer ", "")
    jwt_token_encoded_user_1 = jwt_token_user_1
    ws_url_user_1 = f"/ws/updates/{group_1_id}?token=Bearer%20{jwt_token_encoded_user_1}"

    # Füge das JWT als Query-Parameter hinzu
    authorization_header_user_2 = bearer_headers[1]["Authorization"]
    jwt_token_user_2 = authorization_header_user_2.replace("Bearer ", "")
    jwt_token_encoded_user_2 = jwt_token_user_2
    ws_url_user_2 = f"/ws/updates/{group_1_id}?token=Bearer%20{jwt_token_encoded_user_2}"
    
    authorization_header_user_3 = bearer_headers[3]["Authorization"]
    jwt_token_user_3 = authorization_header_user_3.replace("Bearer ", "")
    jwt_token_encoded_user_3 = jwt_token_user_3
    ws_url_user_3 = f"/ws/updates/{group_2_id}?token=Bearer%20{jwt_token_encoded_user_3}"


    # Verbinde drei WebSocket-Verbindungen:
    with http_client.websocket_connect(ws_url_user_1) as websocket_user_0:
        with http_client.websocket_connect(ws_url_user_2) as websocket_user_1:
            with http_client.websocket_connect(ws_url_user_3) as websocket_user_2:

                # # Act: Aktualisiere einen Benutzer in Gruppe 1
                response_user_group_1 = http_client.post(
                    "/user/acceptInvite",
                    json={
                        "invitationid": "1",
                        "token": "token1",
                        "groupid": group_1_id,
                        "name": "New User"
                    }
                )
                assert response_user_group_1.status_code == 200
                
                # Act: Erstelle einen neuen Edit
                response_edit_group_2 = http_client.post(
                    "/edit/",
                    headers=bearer_headers[3],
                    json={
                        "song_id": 1,
                        "groupid": group_2_id,
                        "edit_name": "New Edit for Group 1"
                    }
                )

                assert response_edit_group_2.status_code == 200


                # Assert: Benutzer 0 und 1 sollten eine "USER"-Nachricht erhalten haben
                assert "USER" == websocket_user_0.receive_text()
                assert "USER" == websocket_user_1.receive_text()
                assert "EDIT" == websocket_user_2.receive_text()

