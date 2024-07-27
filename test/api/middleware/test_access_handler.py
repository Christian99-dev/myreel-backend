from typing import Dict
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import pytest
from api.auth.role_enum import RoleEnum
from api.config.database import get_db
from api.config.path_roles import PathInfo
from api.middleware.access_handler import AccessHandlerMiddleware
from test.utils.mock_path_roles import mock_path_roles
from test.utils.mock_roles_creds import admin_req_creds, group_creator_req_creds, group_member_req_creds, external_req_creds, edit_creator_req_creds
import logging
logger = logging.getLogger("testing")

# routes        = mock_path_roles mirrored
# database      = test_model
# middleware    yes
@pytest.fixture(scope="function")
def app_client_mock_routes_middleware(db_session_filled):
    
    
    def override_get_db():
        yield db_session_filled
        
    mock_path_roles: Dict[str, PathInfo] = {
        '/admin_no_subroles':            PathInfo(role = RoleEnum.ADMIN,         has_subroles=False),
        '/group_creator_no_subroles':    PathInfo(role = RoleEnum.GROUP_CREATOR, has_subroles=False),
        '/edit_creator_no_subroles':     PathInfo(role = RoleEnum.EDIT_CREATOR,  has_subroles=False),
        '/group_member_no_subroles':     PathInfo(role = RoleEnum.GROUP_MEMBER,  has_subroles=False),
        '/external_no_subroles':         PathInfo(role = RoleEnum.EXTERNAL,      has_subroles=False),
        
        '/admin_subroles':              PathInfo(role = RoleEnum.ADMIN,         has_subroles=True),
        '/group_creator_subroles':      PathInfo(role = RoleEnum.GROUP_CREATOR, has_subroles=True),
        '/edit_creator_subroles':       PathInfo(role = RoleEnum.EDIT_CREATOR,  has_subroles=True),
        '/group_member_subroles':       PathInfo(role = RoleEnum.GROUP_MEMBER,  has_subroles=True),
        '/external_subroles':           PathInfo(role = RoleEnum.EXTERNAL,      has_subroles=True),
    }

    # simulating prod api
    app = FastAPI()
    
    # middleware for access testing 
    app.add_middleware(AccessHandlerMiddleware, path_roles=mock_path_roles, get_db=override_get_db)
    
    # every endpoints based on testconfig file
    def create_endpoint(m_name: str):
        async def endpoint(request: Request):
            return f"You called {m_name}"
        return endpoint

    for path in mock_path_roles.keys():    
        app.add_api_route(f"{path}", create_endpoint(path), methods=["GET"])
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    app.dependency_overrides.pop(get_db, None)
 
 # app client MOCK_ROUTES are there with middleware

def test_setup(app_client_mock_routes_middleware):
    assert app_client_mock_routes_middleware.get("/admin_no_subroles").status_code          == 403
    assert app_client_mock_routes_middleware.get("/group_creator_no_subroles").status_code  == 403
    assert app_client_mock_routes_middleware.get("/edit_creator_no_subroles").status_code   == 403
    assert app_client_mock_routes_middleware.get("/group_member_no_subroles").status_code   == 403
    assert app_client_mock_routes_middleware.get("/external_no_subroles").status_code       == 200
    
    assert app_client_mock_routes_middleware.get("/admin_subroles").status_code            == 403
    assert app_client_mock_routes_middleware.get("/group_creator_subroles").status_code    == 403
    assert app_client_mock_routes_middleware.get("/edit_creator_subroles").status_code     == 403
    assert app_client_mock_routes_middleware.get("/group_member_subroles").status_code     == 403
    assert app_client_mock_routes_middleware.get("/external_subroles").status_code         == 200
    
# maintest
def test_endpoints(app_client_mock_routes_middleware):     
    for path in mock_path_roles.keys():
        # logger.debug("\n")
        for current_creds in [admin_req_creds, group_creator_req_creds, edit_creator_req_creds,group_member_req_creds, external_req_creds]: 
            
            # Extrahiere die erforderlichen Details für die Anfrage
            headers = current_creds["req"]["headers"]
            params  = current_creds["req"].get("params", {})
            
            with_subroles = mock_path_roles.get(path).has_subroles
            
            required_role = mock_path_roles.get(path).role
            current_role  = current_creds["role"]

            # Sende die Anfrage an den Endpoint
            response = app_client_mock_routes_middleware.get(path, headers=headers, params=params)

            # Bestimme den erwarteten Statuscode
            if not with_subroles:
                expected_status = 200 if required_role.value == current_role.value else 403
                assert response.status_code == expected_status
            else:
                expected_status = 200 if required_role.value <= current_role.value else 403
            
        