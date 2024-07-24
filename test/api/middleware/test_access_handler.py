import os
import pytest
from fastapi import FastAPI, Request
from api.auth import jwt
from api.auth.role import Role, RoleInfos
from api.auth.role_enum import RoleEnum
from api.config.database import get_db
from fastapi.testclient import TestClient
from api.middleware.access_handler import AccessHandlerMiddleware
from test.utils.mock_path_roles import mock_path_roles
from test.utils.test_model import group_id_1
from test.utils.role_tester_has_acccess import role_tester_has_access
import logging
logger = logging.getLogger("testing")

# setup roles
jwt_user_1 = jwt.create_jwt(1, 30)
jwt_user_2 = jwt.create_jwt(2, 30)
user_1_encoded = jwt.read_jwt(jwt_user_1)
user_2_encoded = jwt.read_jwt(jwt_user_2)
    
admin_req_creds = {
    "req": {    
        "headers": {
            "admintoken": str(os.getenv("ADMIN_TOKEN"))
        }
    }, 
    "role": RoleEnum.ADMIN
}

group_creator_req_creds = {
    "req": {    
        "headers": {
            "Authorization": f"Bearer {jwt_user_1}"
        },
        "params": {
            "groupid": group_id_1
        }
    }, 
    "role": RoleEnum.GROUP_CREATOR
}

edit_creator_req_creds = {
    "req": {    
        "headers": {
            "Authorization": f"Bearer {jwt_user_1}"
        },
        "params": {
            "editid": "1"
        }
    }, 
    "role": RoleEnum.EDIT_CREATOR
}

group_member_req_creds = {
    "req": {    
        "headers": {
            "Authorization": f"Bearer {jwt_user_2}"
        },
        "params": {
            "groupid": group_id_1
        }
    }, 
    "role": RoleEnum.GROUP_MEMBER
}

external_req_creds = {
    "req": {
        "headers": {},
        "params": {}
    }, 
    "role": RoleEnum.EXTERNAL
}

# prepare app with all routes
@pytest.fixture(scope="function")
def app_client_test_routes_middleware(db_session_filled):
    def override_get_db():
        yield db_session_filled

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

# test config
def notest_setup_routes(app_client_test_routes_middleware):
    assert app_client_test_routes_middleware.get("/admin_no_subroles").status_code          == 403
    assert app_client_test_routes_middleware.get("/group_creator_no_subroles").status_code  == 403
    assert app_client_test_routes_middleware.get("/edit_creator_no_subroles").status_code   == 403
    assert app_client_test_routes_middleware.get("/group_member_no_subroles").status_code   == 403
    assert app_client_test_routes_middleware.get("/external_no_subroles").status_code       == 200
    
    assert app_client_test_routes_middleware.get("/admin_subroles").status_code            == 403
    assert app_client_test_routes_middleware.get("/group_creator_subroles").status_code    == 403
    assert app_client_test_routes_middleware.get("/edit_creator_subroles").status_code     == 403
    assert app_client_test_routes_middleware.get("/group_member_subroles").status_code     == 403
    assert app_client_test_routes_middleware.get("/external_subroles").status_code         == 200
    
def test_setup_roles(db_session_filled):
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_req_creds["req"]["headers"]["admintoken"], userid=None, groupid=None, editid=None), db_session=db_session_filled), RoleEnum.ADMIN)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=user_1_encoded, groupid=group_creator_req_creds["req"]["params"]["groupid"], editid=None), db_session=db_session_filled), RoleEnum.GROUP_CREATOR)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=user_1_encoded, groupid=None, editid=edit_creator_req_creds["req"]["params"]["editid"]), db_session=db_session_filled), RoleEnum.EDIT_CREATOR)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=user_2_encoded, groupid=group_member_req_creds["req"]["params"]["groupid"], editid=None), db_session=db_session_filled), RoleEnum.GROUP_MEMBER)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=None, groupid=None, editid=None), db_session=db_session_filled), RoleEnum.EXTERNAL)    

def test_setup_roles_with_creds(db_session_filled):
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_req_creds["req"]["headers"]["admintoken"], userid=None, groupid=None, editid=None), db_session=db_session_filled), admin_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=user_1_encoded, groupid=group_creator_req_creds["req"]["params"]["groupid"], editid=None), db_session=db_session_filled), group_creator_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=user_1_encoded, groupid=None, editid=edit_creator_req_creds["req"]["params"]["editid"]), db_session=db_session_filled), edit_creator_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=user_2_encoded, groupid=group_member_req_creds["req"]["params"]["groupid"], editid=None), db_session=db_session_filled), group_member_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=None, groupid=None, editid=None), db_session=db_session_filled), external_req_creds["role"])

# maintest
def test_endpoints(app_client_test_routes_middleware):     
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
            response = app_client_test_routes_middleware.get(path, headers=headers, params=params)

            # Bestimme den erwarteten Statuscode
            if not with_subroles:
                expected_status = 200 if required_role.value == current_role.value else 403
                assert response.status_code == expected_status
            else:
                expected_status = 200 if required_role.value <= current_role.value else 403
            
        