import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from api.utils.routes.extract_role_credentials_from_request import extract_role_credentials_from_request

@pytest.fixture(scope="function")
def app_client():
    app = FastAPI()

    @app.middleware("http")
    async def add_role_credentials(request: Request, call_next):
        credentials = extract_role_credentials_from_request(request)
        request.state.credentials = credentials
        response = await call_next(request)
        return response

    @app.get("/example")
    async def example_route(request: Request):
        return {"credentials": request.state.credentials}

    yield TestClient(app)

def test_extract_credentials_from_request(app_client):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    params = {
        "groupid": "group_id_value",
        "editid": "123"
    }
    response = app_client.get("/example", headers=headers, params=params)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "Bearer jwt_token_value",
            "groupid": "group_id_value",
            "editid": 123
        }
    }
    
def test_extract_credentials_from_request_optional_fields(app_client):
    headers = {
        "admintoken": "another_admintoken"
    }
    params = {
        "groupid": "group_xyz"
    }
    response = app_client.get("/example", headers=headers, params=params)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "another_admintoken",
            "jwt": None,
            "groupid": "group_xyz",
            "editid": None
        }
    }

def test_extract_credentials_from_request_no_fields(app_client):
    response = app_client.get("/example")
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": None,
            "jwt": None,
            "groupid": None,
            "editid": None
        }
    }
    
def test_extract_credentials_from_request_more_fields(app_client):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value",
        "some other": "field"
    }
    params = {
        "groupid": "group_id_value",
        "editid": "123",
        "some": "other field"
    }
    response = app_client.get("/example", headers=headers, params=params)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "Bearer jwt_token_value",
            "groupid": "group_id_value",
            "editid": 123
        }
    }