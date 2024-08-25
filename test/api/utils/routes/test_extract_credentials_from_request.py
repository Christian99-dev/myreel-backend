from fastapi.testclient import TestClient

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