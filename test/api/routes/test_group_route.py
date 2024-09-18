import os

from dotenv import load_dotenv
from fastapi.testclient import TestClient

from api.utils.jwt import jwt
from api.utils.jwt.jwt import read_jwt


# create
def notest_create_group_status(http_client: TestClient): 
    assert http_client.post("/group").status_code == 422
    
def notest_create_group_success(http_client: TestClient):
    # Definiere die Anfrage-Daten für die Gruppencreation
    request_data = {
        "groupname": "New Group",
        "username": "Test User",
        "email": "test@example.com"
    }

    # Sende die POST-Anfrage zur Erstellung der Gruppe
    response = http_client.post("/group/", json=request_data)

    # Überprüfe den Statuscode und die Struktur der Antwort
    assert response.status_code == 200  # OK (200) für erfolgreiche Erstellung
    response_data = response.json()
    assert "jwt" in response_data  # Stelle sicher, dass das JWT in der Antwort enthalten ist
    assert 10 is read_jwt(response_data.get("jwt"))  # Stelle sicher, dass das JWT in der Antwort enthalten ist
    assert response_data["group_id"] is not None  # Überprüfe, ob die group_id vorhanden ist

def notest_create_group_missing_fields(http_client: TestClient):
    # Definiere die Anfrage-Daten ohne erforderliche Felder
    request_data = {
        "groupname": "New Group"  # Fehlt: username, email
    }

    # Sende die POST-Anfrage zur Erstellung der Gruppe
    response = http_client.post("/group/", json=request_data)

    # Überprüfe den Statuscode und die Fehlerstruktur
    assert response.status_code == 422  # Unprocessable Entity (422) für fehlende Felder
    assert "detail" in response.json()  # Stelle sicher, dass Fehlerdetails vorhanden sind

# delete
def notest_delete_group_status(http_client: TestClient): 
    assert http_client.delete("/group/1").status_code == 403

def notest_delete_group_success(http_client: TestClient):
    # Zuerst eine Gruppe erstellen, um sicherzustellen, dass sie existiert
    create_response = http_client.post("/group/", json={
        "groupname": "Test Group for Deletion",
        "username": "Test User",
        "email": "test@example.com"
    })

    assert create_response.status_code == 200  # Gruppe sollte erfolgreich erstellt werden
    group_id = create_response.json()["group_id"]
    jwt = create_response.json()["jwt"]

    # Jetzt die Gruppe löschen
    delete_response = http_client.delete(f"/group/{group_id}", headers={"Authorization" : f"Bearer {jwt}"})

    # Überprüfen des Statuscodes und der Antwort
    assert delete_response.status_code == 200  # Erfolgreiche Löschung sollte 200 zurückgeben
    assert delete_response.json() == {"message": "Group successfully deleted"}  # Erfolgsnachricht

# get
def notest_get_group_success(http_client: TestClient):
    
    # Zuerst eine Gruppe erstellen, um sicherzustellen, dass sie existiert
    create_response = http_client.post("/group/", json={
        "groupname": "Test Group for Deletion",
        "username": "Test User",
        "email": "test@example.com"
    })

    assert create_response.status_code == 200  # Gruppe sollte erfolgreich erstellt werden
    
    group_id = create_response.json()["group_id"]
    jwt = create_response.json()["jwt"]

    # Sende die GET-Anfrage zur Gruppe
    get_response = http_client.get(f'/group/{group_id}', headers={"Authorization" : f'Bearer {jwt}'})

    # Überprüfe den Statuscode und die Struktur der Antwort
    assert get_response.status_code == 200  # OK (200) für erfolgreiche Abfrage
    response_data = get_response.json()
    assert response_data["group_id"] == group_id  # Überprüfe die group_id
    assert response_data["name"] == "Test Group for Deletion"  # Überprüfe den Gruppennamen

def notest_get_group_not_found(http_client: TestClient):
    admintoken = os.getenv("ADMIN_TOKEN")
    
    # Sende die GET-Anfrage für eine nicht existierende Gruppe
    response = http_client.get("/group/non-existent-group-id", headers={"admintoken" : admintoken})

    # Überprüfe den Statuscode und die Fehlermeldung
    assert response.status_code == 404  # Not Found (403) für nicht keinen zugriff
    

# get_role
def notest_get_group_role(http_client: TestClient): 
    response1 = http_client.get(f"/group/11111111-1111-1111-1111-111111111111/role", headers={"Authorization" : f"Bearer {jwt.create_jwt(1, 30)}"})
    response2 = http_client.get(f"/group/11111111-1111-1111-1111-111111111111/role", headers={"Authorization" : f"Bearer {jwt.create_jwt(2, 30)}"})
    response3 = http_client.get(f"/group/11111111-1111-1111-1111-111111111111/role", headers={"Authorization" : f"Bearer {jwt.create_jwt(5, 30)}"})
    
    assert response1.json().get("role") == "creator"
    assert response2.json().get("role") == "member"
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 404
    
# group_exist
def notest_group_exists_status(http_client: TestClient): 

    # Sende die GET-Anfrage zur Überprüfung, ob die Gruppe existiert
    response = http_client.get(f"/group/11111111-1111-1111-1111-111111111111/groupExists")

    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get("exists") == True
    
    # Sende die GET-Anfrage zur Überprüfung, ob die Gruppe existiert
    response_not_there = http_client.get(f"/group/123/groupExists")

    assert response_not_there.status_code == 200
    response_data_not_there = response_not_there.json()
    assert response_data_not_there.get("exists") == False

# list_members
def notest_list_group_members_status(http_client: TestClient): 
     # Sende die GET-Anfrage zur Abrufung der Mitglieder
    response = http_client.get(f"/group/11111111-1111-1111-1111-111111111111/listMembers", headers={"Authorization" : f"Bearer {jwt.create_jwt(2, 30)}"})

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["members"] == [
        {"user_id": 1, "group_id": "11111111-1111-1111-1111-111111111111", "role": "creator", "name": "Creator of Group 1", "email": "creator1@example.com"},
        {"user_id": 2, "group_id": "11111111-1111-1111-1111-111111111111", "role": "member", "name": "Member 1 of Group 1", "email": "member1_1@example.com"},
        {"user_id": 3, "group_id": "11111111-1111-1111-1111-111111111111", "role": "member", "name": "Member 2 of Group 1", "email": "member2_1@example.com"},
    ]

def notest_list_group_members_no_groupe(http_client: TestClient): 
    assert http_client.get("/group/123/listMembers", headers={"Authorization" : f"Bearer {jwt.create_jwt(2, 30)}"}).status_code == 403





