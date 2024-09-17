import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from api.utils.routes.extract_role_credentials_from_request import \
    extract_role_credentials_from_request

"""Setup"""
@pytest.fixture(scope="function")
def http_client_mocked_path_for_extracting_creds():
    app = FastAPI()

    @app.middleware("http")
    async def add_role_credentials(request: Request, call_next):
        credentials = await extract_role_credentials_from_request(request)
        request.state.credentials = credentials
        response = await call_next(request)
        return response

    # from body / query
    @app.get("/example")
    async def example_route(request: Request):
        return {"credentials": request.state.credentials}
    
    @app.post("/example")
    async def example_route(request: Request):
        return {"credentials": request.state.credentials}

    # from path
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
    
    # yield client with routes
    with TestClient(app) as test_client:
        yield test_client

"""Test Setup"""
def test_http_client_mocked_path_for_extracting_creds_config(http_client_mocked_path_for_extracting_creds: TestClient):
    assert http_client_mocked_path_for_extracting_creds.get("/example").status_code                                 == 200
    assert http_client_mocked_path_for_extracting_creds.post("/example", json={"key": "value"}).status_code         == 200
    assert http_client_mocked_path_for_extracting_creds.post("/group/test-group-id").status_code                    == 200
    assert http_client_mocked_path_for_extracting_creds.post("/edit/123").status_code                               == 200
    assert http_client_mocked_path_for_extracting_creds.post("/example/group/test-group-id/example").status_code    == 200
    assert http_client_mocked_path_for_extracting_creds.post("/example/edit/456/example").status_code               == 200

"""Main test"""
# from query
def test_extract_credentials_from_request(http_client_mocked_path_for_extracting_creds: TestClient):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    params = {
        "groupid": "group_id_value",
        "editid": "123"
    }
    response = http_client_mocked_path_for_extracting_creds.get("/example", headers=headers, params=params)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": "group_id_value",
            "editid": 123
        }
    }
    
def test_extract_credentials_from_request_optional_fields(http_client_mocked_path_for_extracting_creds: TestClient):
    headers = {
        "admintoken": "another_admintoken"
    }
    params = {
        "groupid": "group_xyz"
    }
    response = http_client_mocked_path_for_extracting_creds.get("/example", headers=headers, params=params)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "another_admintoken",
            "jwt": None,
            "groupid": "group_xyz",
            "editid": None
        }
    }

def test_extract_credentials_from_request_no_fields(http_client_mocked_path_for_extracting_creds: TestClient):
    response = http_client_mocked_path_for_extracting_creds.get("/example")
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": None,
            "jwt": None,
            "groupid": None,
            "editid": None
        }
    }
    
def test_extract_credentials_from_request_more_fields(http_client_mocked_path_for_extracting_creds: TestClient):
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
    response = http_client_mocked_path_for_extracting_creds.get("/example", headers=headers, params=params)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": "group_id_value",
            "editid": 123
        }
    }
    
# from body 
def test_extract_credentials_from_body(http_client_mocked_path_for_extracting_creds: TestClient):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    body = {
        "groupid": "body_group_id_value",
        "editid": 456
    }
    response = http_client_mocked_path_for_extracting_creds.post("/example", headers=headers, json=body)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": "body_group_id_value",
            "editid": 456
        }
    }

def test_extract_credentials_with_body_and_query(http_client_mocked_path_for_extracting_creds: TestClient):
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
    response = http_client_mocked_path_for_extracting_creds.post("/example", headers=headers, params=params, json=body)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": "query_group_id_value",  # Query-Parameter hat Vorrang vor Body
            "editid": 123  # Query-Parameter hat Vorrang vor Body
        }
    }
    
# from path
def test_extract_credentials_from_path_group(http_client_mocked_path_for_extracting_creds: TestClient):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    response = http_client_mocked_path_for_extracting_creds.post("/group/group_id_value", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": "group_id_value",
            "editid": None
        }
    }

def test_extract_credentials_from_path_edit(http_client_mocked_path_for_extracting_creds: TestClient):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    response = http_client_mocked_path_for_extracting_creds.post("/edit/123", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": None,
            "editid": 123
        }
    }

def test_extract_credentials_with_body_and_path(http_client_mocked_path_for_extracting_creds: TestClient):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    body = {
        "groupid": "body_group_id_value",
        "editid": 456
    }
    response = http_client_mocked_path_for_extracting_creds.post("/edit/123", headers=headers, json=body)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": "body_group_id_value",  # Body-Wert wird übernommen, da kein Query-Parameter vorhanden
            "editid": 123  # Path-Wert hat Vorrang vor Body
        }
    }
    
def test_extract_credentials_from_nested_path_group(http_client_mocked_path_for_extracting_creds: TestClient):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    response = http_client_mocked_path_for_extracting_creds.post("/example/group/group_id_value/example", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": "group_id_value",
            "editid": None
        }
    }

def test_extract_credentials_from_nested_path_edit(http_client_mocked_path_for_extracting_creds: TestClient):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    response = http_client_mocked_path_for_extracting_creds.post("/example/edit/123/example", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": "admin_token_value",
            "jwt": "jwt_token_value",
            "groupid": None,
            "editid": 123
        }
    }
    
def test_extract_credentials_from_invalid_path_editid(http_client_mocked_path_for_extracting_creds: TestClient):
    headers = {
        "admintoken": "admin_token_value",
        "Authorization": "Bearer jwt_token_value"
    }
    response = http_client_mocked_path_for_extracting_creds.post("/example/edit/invalid_editid/example", headers=headers)
    assert response.status_code == 422
    
# empty
def test_extract_credentials_no_information(http_client_mocked_path_for_extracting_creds: TestClient):
    # Kein Header, Query-Parameter, Body oder Path-Parameter
    response = http_client_mocked_path_for_extracting_creds.post("/example", headers={})
    assert response.status_code == 200
    assert response.json() == {
        "credentials": {
            "admintoken": None,
            "jwt": None,
            "groupid": None,
            "editid": None
        }
    }