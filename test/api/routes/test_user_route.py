from fastapi.testclient import TestClient

from api.utils.jwt import jwt


# invite
def notest_invite_success(http_client: TestClient):
    request_data = {
        "groupid": "11111111-1111-1111-1111-111111111111",
        "email": "abc@example.de"
    }
    response = http_client.post("/user/invite", json=request_data, headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"} )
    assert response.status_code == 200
    assert response.json() == {"message": "Invite successfull"}

def notest_invite_no_success(http_client: TestClient):
    request_data = {
        "groupid": "asd",
        "email": "abc@example.de"
    }
    response = http_client.post("/user/invite", json=request_data, headers={"Authorization": f"Bearer {jwt.create_jwt(1, 10)}"} )
    assert response.status_code == 403


# accept invite
def notest_accept_invite_success(http_client: TestClient):
    request_data = {
        "invitationid": "1",
        "token": "token1",
        "groupid": "11111111-1111-1111-1111-111111111111",
        "name": "New User"
    }
    response = http_client.post("/user/acceptInvite", json=request_data)
    assert response.status_code == 200
    assert "jwt" in response.json()

def notest_accept_invite_invalid_token(http_client: TestClient):
    request_data = {
        "invitationid": "1",
        "token": "wrong_token",
        "groupid": "11111111-1111-1111-1111-111111111111",
        "name": "New User"
    }
    response = http_client.post("/user/acceptInvite", json=request_data)
    assert response.status_code == 400

def notest_accept_invite_nonexistent_invitation(http_client: TestClient):
    request_data = {
        "invitationid": "999",
        "token": "token1",
        "groupid": "11111111-1111-1111-1111-111111111111",
        "name": "New User"
    }
    response = http_client.post("/user/acceptInvite", json=request_data)
    assert response.status_code == 400

# login request
def notest_login_request_success(http_client: TestClient):
    request_data = {
        "groupid": "11111111-1111-1111-1111-111111111111",
        "email": "creator1@example.com"
    }
    response = http_client.post("/user/loginRequest", json=request_data)
    assert response.status_code == 200
    assert response.json() == {"message": "email wurde versendet"}

def notest_login_request_nonexistent_user(http_client: TestClient):
    request_data = {
        "groupid": "11111111-1111-1111-1111-111111111111",
        "email": "nonexistent@example.com"
    }
    response = http_client.post("/user/loginRequest", json=request_data)
    assert response.status_code == 400
    
    
# login request
def notest_login_success(http_client: TestClient):
    
    request_data = {
        "groupid": "11111111-1111-1111-1111-111111111111",
        "token": "1234"  # Angenommener Token für den Test
    }
    response = http_client.post("/user/login", json=request_data)

    assert response.status_code == 200
    assert "jwt" in response.json()

def notest_login_request_invalid_token(http_client: TestClient):
    request_data = {
        "groupid": "11111111-1111-1111-1111-111111111111",
        "token": "invalid_token"
    }
    response = http_client.post("/user/login", json=request_data)
    assert response.status_code == 400

def notest_login_request_nonexistent_user(http_client: TestClient):
    request_data = {
        "groupid": "none_existend_group_id",
        "token": "1234"  # Angenommener Token für den Test
    }
    response = http_client.post("/user/login", json=request_data)
    assert response.status_code == 400