import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from api.utils.routes.extract_role_credentials_from_request import extract_role_credentials_from_request

@pytest.fixture(scope="function")
def app_client():
    app = FastAPI()

    @app.middleware("http")
    async def add_role_credentials(request: Request, call_next):
        credentials = await extract_role_credentials_from_request(request)
        request.state.credentials = credentials
        response = await call_next(request)
        return response

    # BODY  / QUERY
    @app.get("/example")
    async def example_route(request: Request):
        return {"credentials": request.state.credentials}
    
    @app.post("/example")
    async def example_route(request: Request):
        return {"credentials": request.state.credentials}

    # PATH 
    @app.post("/group/{groupid}")
    async def group_route(request: Request, groupid: str):
        return {"credentials": request.state.credentials}

    @app.post("/edit/{editid}")
    async def edit_route(request: Request, editid: int):
        return {"credentials": request.state.credentials}
    
    @app.post("/example/group/{groupid}/example")
    async def nested_group_route(request: Request, groupid: str):
        return {"credentials": request.state.credentials}

    @app.post("/example/edit/{editid}/example")
    async def nested_edit_route(request: Request, editid: int):
        return {"credentials": request.state.credentials}
    
    yield TestClient(app)

# QUERY
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
            "jwt": "jwt_token_value",
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
            "jwt": "jwt_token_value",
            "groupid": "group_id_value",
            "editid": 123
        }
    }
    
# BODY 
def test_extract_credentials_from_body(app_client):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    body = {
        "groupid": "body_group_id_value",
        "editid": 456
    }
    response = app_client.post("/example", headers=headers, json=body)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": "body_group_id_value",
            "editid": 456
        }
    }

def test_extract_credentials_with_body_and_query(app_client):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    params = {
        "groupid": "query_group_id_value",
        "editid": "123"
    }
    body = {
        "groupid": "body_group_id_value",
        "editid": 456
    }
    response = app_client.post("/example", headers=headers, params=params, json=body)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": "query_group_id_value",  # Query-Parameter hat Vorrang vor Body
            "editid": 123  # Query-Parameter hat Vorrang vor Body
        }
    }
    
# PATH 
def test_extract_credentials_from_path_group(app_client):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    response = app_client.post("/group/group_id_value", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": "group_id_value",
            "editid": None
        }
    }

def test_extract_credentials_from_path_edit(app_client):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    response = app_client.post("/edit/123", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": None,
            "editid": 123
        }
    }

def test_extract_credentials_with_body_and_path(app_client):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    body = {
        "groupid": "body_group_id_value",
        "editid": 456
    }
    response = app_client.post("/edit/123", headers=headers, json=body)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": "body_group_id_value",  # Body-Wert wird übernommen, da kein Query-Parameter vorhanden
            "editid": 123  # Path-Wert hat Vorrang vor Body
        }
    }
    
def test_extract_credentials_from_nested_path_group(app_client):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    response = app_client.post("/example/group/group_id_value/example", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": "group_id_value",
            "editid": None
        }
    }

def test_extract_credentials_from_nested_path_edit(app_client):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    response = app_client.post("/example/edit/123/example", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": None,
            "editid": 123
        }
    }
    
def test_extract_credentials_from_invalid_path_editid(app_client):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    response = app_client.post("/example/edit/invalid_editid/example", headers=headers)
    assert response.status_code == 422
    
    
# Noting
def test_extract_credentials_no_information(app_client):
    # Kein Header, Query-Parameter, Body oder Path-Parameter
    response = app_client.post("/example", headers={})
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": None,
            "jwt": None,
            "groupid": None,
            "editid": None
        }
    }