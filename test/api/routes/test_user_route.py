import logging
from datetime import datetime, timedelta
from typing import List

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.models.database.model import Invitation, LoginRequest
from mock.database.data import data

logger = logging.getLogger("test.unittest")


# Test for invite route
def test_invite_blank_access(http_client: TestClient):
    response = http_client.post("/user/invite")
    assert response.status_code == 403

def test_invite_success(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    group_id = data["groups"][0]["group_id"]
    email = "invitee@example.com"

    # Act
    response = http_client.post(
        "/user/invite",
        headers=bearer_headers[0],
        json={
            "groupid": group_id,
            "email": email
        }
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Invite successfull"

def test_empty_email(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    group_id = data["groups"][0]["group_id"]
    email = ""

    # Act
    response = http_client.post(
        "/user/invite",
        headers=bearer_headers[0],
        json={
            "groupid": group_id,
            "email": email
        }
    )

    # Assert
    assert response.status_code == 500
    assert response.json()["detail"] == "Recipient email address is missing."

def test_invite_wrong_group(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    group_id = data["groups"][1]["group_id"]
    email = "invitee@example.com"

    # Act
    response = http_client.post(
        "/user/invite",
        headers=bearer_headers[0],
        json={
            "groupid": group_id,
            "email": email
        }
    )

    # Assert
    assert response.status_code == 403

def test_invite_wrong_user_bearer(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    group_id = data["groups"][1]["group_id"]
    email = "invitee@example.com"

    # Act
    response = http_client.post(
        "/user/invite",
        headers=bearer_headers[0],
        json={
            "groupid": group_id,
            "email": email
        }
    )

    # Assert
    assert response.status_code == 403

# Test for acceptInvite route
def test_accept_invite_blank_access(http_client: TestClient):
    response = http_client.post("/user/acceptInvite")
    assert response.status_code == 422

def test_accept_invite_success(http_client: TestClient):
    # Arrange & Act
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
    assert "jwt" in response.json()

def test_accept_invite_wrong_token(http_client: TestClient):
    # Arrange & Act
    response = http_client.post(
        "/user/acceptInvite",
        json={
            "invitationid": "1",
            "token": "token2",
            "groupid": "11111111-1111-1111-1111-111111111111",
            "name": "New User"
        }
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Einlandungstoken falsch"

def test_accept_invite_wrong_group(http_client: TestClient):
    # Arrange & Act
    response = http_client.post(
        "/user/acceptInvite",
        json={
            "invitationid": "1",
            "token": "token1",
            "groupid": "11112111-1111-1111-1111-111111111111",
            "name": "New User"
        }
    )

    # Assert
    assert response.json()["detail"] == "Group with ID 11112111-1111-1111-1111-111111111111 not found"
    assert response.status_code == 404

def test_accept_invite_expired_token(http_client: TestClient, memory_database_session: Session):
    # Arrange: Eine abgelaufene Einladung in der Datenbank erstellen
    expired_invitation = Invitation(
        group_id="11111111-1111-1111-1111-111111111111",
        token="expiredtoken",
        email="invitee@example.com",
        created_at=datetime.now() - timedelta(days=2),  # Erstellt vor 2 Tagen
        expires_at=datetime.now() - timedelta(days=1),  # Abgelaufen vor 1 Tag
    )
    memory_database_session.add(expired_invitation)
    memory_database_session.commit()

    # Act: Versuche, die abgelaufene Einladung anzunehmen
    response = http_client.post(
        "/user/acceptInvite",
        json={
            "invitationid": str(expired_invitation.invitation_id),
            "token": "expiredtoken",
            "groupid": "11111111-1111-1111-1111-111111111111",
            "name": "New User"
        }
    )

    # Assert: Überprüfe, dass die Einladung abgelaufen ist
    assert response.status_code == 400
    assert response.json()["detail"] == "Einladungstoken abgelaufen"

# Test for loginRequest route
def test_login_request_blank_access(http_client: TestClient):
    response = http_client.post("/user/loginRequest")
    assert response.status_code == 422

def test_login_request_success(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    group_id = data["groups"][0]["group_id"]
    email = data["users"][0]["email"]

    # Act
    response = http_client.post(
        "/user/loginRequest",
        headers=bearer_headers[0],
        json={
            "groupid": group_id,
            "email": email
        }
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "email wurde versendet"

def test_login_request_wrong_group(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    group_id = "123"
    email = data["users"][0]["email"]

    # Act
    response = http_client.post(
        "/user/loginRequest",
        headers=bearer_headers[0],
        json={
            "groupid": group_id,
            "email": email
        }
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "User with email creator1@example.com in group 123 not found."

def test_login_request_wrong_email(http_client: TestClient, bearer_headers: List[dict[str, str]]):
    # Arrange
    group_id = data["groups"][0]["group_id"]
    email = "wrong@email.de"

    # Act
    response = http_client.post(
        "/user/loginRequest",
        headers=bearer_headers[0],
        json={
            "groupid": group_id,
            "email": email
        }
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == f"User with email wrong@email.de in group {group_id} not found."

# Test for login route
def test_login_blank_access(http_client: TestClient):
    response = http_client.post("/user/login")
    assert response.status_code == 422

def test_login_success(http_client: TestClient):

    # Act
    response = http_client.post(
        "/user/login",
        json={
            "groupid": "11111111-1111-1111-1111-111111111111",
            "pin": "1234",
            "email": "creator1@example.com"
        }
    )

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert "jwt" in response_data
    assert response_data["user_id"] == data["users"][0]["user_id"]
    assert response_data["name"] == data["users"][0]["name"]

def test_login_wrong_group(http_client: TestClient):

    # Act
    response = http_client.post(
        "/user/login",
        json={
            "groupid": "11111111-1211-1111-1111-111111111111",
            "pin": "1234",
            "email": "creator1@example.com"
        }
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == f"Login request with group ID 11111111-1211-1111-1111-111111111111 and email creator1@example.com not found"

def test_login_wrong_pin(http_client: TestClient):

    # Act
    response = http_client.post(
        "/user/login",
        json={
            "groupid": "11111111-1111-1111-1111-111111111111",
            "pin": "1134",
            "email": "creator1@example.com"
        }
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == f"Ungültiger Token"

def test_login_wrong_email(http_client: TestClient):

    # Act
    response = http_client.post(
        "/user/login",
        json={
            "groupid": "11111111-1111-1111-1111-111111111111",
            "pin": "1234",
            "email": "creator2@example.com"
        }
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == f"Login request with group ID 11111111-1111-1111-1111-111111111111 and email creator2@example.com not found"

def test_login_expired_token(http_client: TestClient, memory_database_session: Session):
    
    # Arrange: Lösche vorherige Login-Requests für den Benutzer
    memory_database_session.query(LoginRequest).filter_by(user_id=1).delete()
    memory_database_session.commit()

    # Arrange: Ein abgelaufenes Login-Request in der Datenbank erstellen
    expired_login_request = LoginRequest(
        user_id=1,  # Assuming user ID 1 exists in the test data
        pin="1234",
        created_at=datetime.now() - timedelta(minutes=20),  # Erstellt vor 20 Minuten
        expires_at=datetime.now() - timedelta(minutes=10)  # Abgelaufen vor 10 Minuten
    )
    memory_database_session.add(expired_login_request)
    memory_database_session.commit()

    # Act: Versuche, mit dem abgelaufenen Token einzuloggen
    response = http_client.post(
        "/user/login",
        json={
            "groupid": "11111111-1111-1111-1111-111111111111",
            "pin": "1234",
            "email": "creator1@example.com"
        }
    )

    # Assert: Überprüfe, dass der Token abgelaufen ist
    assert response.status_code == 400
    assert response.json()["detail"] == "Login-Anfrage ist abgelaufen"


"""Integration"""
def test_integration_login_requests(http_client: TestClient, memory_database_session: Session):
    # Arrange: Lösche vorherige Login-Requests für den Benutzer
    memory_database_session.query(LoginRequest).filter_by(user_id=1).delete()
    memory_database_session.commit()

    # Step 1: Sende die erste Login-Anfrage
    response_1 = http_client.post(
        "/user/loginRequest",
        json={
            "groupid": "11111111-1111-1111-1111-111111111111",
            "email": "creator1@example.com"
        }
    )
    assert response_1.status_code == 200
    assert response_1.json()["message"] == "email wurde versendet"

    # Step 2: Sende die zweite Login-Anfrage
    response_2 = http_client.post(
        "/user/loginRequest",
        json={
            "groupid": "11111111-1111-1111-1111-111111111111",
            "email": "creator1@example.com"
        }
    )
    assert response_2.status_code == 200
    assert response_2.json()["message"] == "email wurde versendet"

    # Step 3: Überprüfe, dass nur eine aktive Login-Anfrage in der Datenbank existiert
    active_login_requests = memory_database_session.query(LoginRequest).filter_by(user_id=1).all()
    assert len(active_login_requests) == 1, "Es sollte nur eine aktive Login-Anfrage in der Datenbank sein."

    latest_login_request = active_login_requests[0]
    first_pin = "1234"  # Assuming the first PIN is 1234 from the test data
    second_pin = latest_login_request.pin

    # Step 4: Versuche, dich mit dem ersten (veralteten) PIN einzuloggen (sollte fehlschlagen)
    response_invalid_login = http_client.post(
        "/user/login",
        json={
            "groupid": "11111111-1111-1111-1111-111111111111",
            "pin": first_pin,
            "email": "creator1@example.com"
        }
    )
    assert response_invalid_login.status_code == 400
    assert response_invalid_login.json()["detail"] == "Ungültiger Token", "Die erste Login-Anfrage sollte fehlschlagen."

    # Step 5: Versuche, dich mit dem PIN der zweiten (aktuellen) Login-Anfrage einzuloggen (sollte erfolgreich sein)
    response_valid_login = http_client.post(
        "/user/login",
        json={
            "groupid": "11111111-1111-1111-1111-111111111111",
            "pin": second_pin,
            "email": "creator1@example.com"
        }
    )
    assert response_valid_login.status_code == 200
    response_data = response_valid_login.json()
    assert "jwt" in response_data, "Die zweite Login-Anfrage sollte erfolgreich sein."
    assert response_data["user_id"] == 1, "Die Benutzer-ID sollte korrekt sein."
    assert response_data["name"] == "Creator of Group 1"