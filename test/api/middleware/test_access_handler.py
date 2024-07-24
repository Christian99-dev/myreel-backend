import os
import pytest
from typing import Dict
from fastapi import FastAPI, Request
from api.auth import jwt
from api.auth.role import Role, RoleInfos
from api.auth.role_enum import RoleEnum
from api.config.database import get_db
from fastapi.testclient import TestClient
from api.config.path_roles import PathInfo
from api.middleware.access_handler import AccessHandlerMiddleware
from api.utils.database.test_model import group_id_1
from test.utils import role_tester_has_access
import logging
logger = logging.getLogger("testing")

# Testconfig für routen
path_roles: Dict[str, PathInfo] = {
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

# setup roles
jwt_user_1 = jwt.create_jwt(1, 30)
jwt_user_2 = jwt.create_jwt(2, 30)
user_1_encoded = jwt.read_jwt(jwt_user_1)
user_2_encoded = jwt.read_jwt(jwt_user_2)
    
admin_req_creds = {    
    "headers": {
        "admintoken": str(os.getenv("ADMIN_TOKEN"))
    }
}

group_creator_req_creds = {    
    "headers": {
        "Authorization": f"Bearer {jwt_user_1}"
    },
    "params" : {
        "groupid":group_id_1
    }
}

edit_creator_req_creds = {    
    "headers": {
        "Authorization": f"Bearer {jwt_user_1}"
    },
    "params" : {
        "editid":"1"
    }
}

group_member_req_creds = {    
    "headers": {
        "Authorization": f"Bearer {jwt_user_2}"
    },
    "params" : {
        "groupid":group_id_1
    }
}

external_req_creds = {
    "headers": {},
    "params" : {}
}

# prepare app with all routes
@pytest.fixture(scope="function")
def app_client_role_routes(db_session_filled):
    def override_get_db():
        yield db_session_filled

    
    # simulating prod api
    app = FastAPI()
    
    # middleware for access testing 
    app.add_middleware(AccessHandlerMiddleware, path_roles=path_roles, get_db=override_get_db)
    
    # every endpoints based on testconfig file
    def create_endpoint(m_name: str):
        async def endpoint(request: Request):
            return f"You called {m_name}"
        return endpoint

    for path in path_roles.keys():    
        app.add_api_route(f"{path}", create_endpoint(path), methods=["GET"])
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    app.dependency_overrides.pop(get_db, None)

# test config
def notest_setup_routes(app_client_role_routes):
    assert app_client_role_routes.get("/admin_no_subroles").status_code          == 403
    assert app_client_role_routes.get("/group_creator_no_subroles").status_code  == 403
    assert app_client_role_routes.get("/edit_creator_no_subroles").status_code   == 403
    assert app_client_role_routes.get("/group_member_no_subroles").status_code   == 403
    assert app_client_role_routes.get("/external_no_subroles").status_code       == 200
    
    assert app_client_role_routes.get("/admin_subroles").status_code            == 403
    assert app_client_role_routes.get("/group_creator_subroles").status_code    == 403
    assert app_client_role_routes.get("/edit_creator_subroles").status_code     == 403
    assert app_client_role_routes.get("/group_member_subroles").status_code     == 403
    assert app_client_role_routes.get("/external_subroles").status_code         == 200
    
def test_setup_roles(db_session_filled):
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_req_creds["headers"]["admintoken"], userid=None, groupid=None, editid=None), db_session=db_session_filled),  RoleEnum.ADMIN)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=user_1_encoded, groupid=group_creator_req_creds["params"]["groupid"], editid=None), db_session=db_session_filled),  RoleEnum.GROUP_CREATOR)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=user_1_encoded, groupid=None, editid=edit_creator_req_creds["params"]["editid"]), db_session=db_session_filled),  RoleEnum.EDIT_CREATOR)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=user_2_encoded, groupid=group_member_req_creds["params"]["groupid"], editid=None), db_session=db_session_filled),  RoleEnum.GROUP_MEMBER)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=None, groupid=None, editid=None), db_session=db_session_filled),  RoleEnum.EXTERNAL)

# maintest
def test_endpoints(app_client_role_routes):
    response_1 = app_client_role_routes.get("/edit_creator_no_subroles", headers=edit_creator_req_creds["headers"], params=edit_creator_req_creds["params"])
    response_2 = app_client_role_routes.get("/edit_creator_subroles", headers=edit_creator_req_creds["headers"], params=edit_creator_req_creds["params"])
    
    response_3 = app_client_role_routes.get("/group_member_no_subroles", headers=edit_creator_req_creds["headers"], params=edit_creator_req_creds["params"])    
    response_4 = app_client_role_routes.get("/group_member_subroles", headers=edit_creator_req_creds["headers"], params=edit_creator_req_creds["params"])    
    
    assert response_1.status_code == 200
    assert response_2.status_code == 200
    assert response_3.status_code == 403
    assert response_4.status_code == 200
    
     
    # import logging
    # for path in path_roles.keys():
        # for role_creds in [admin_req_creds, group_creator_req_creds, edit_creator_req_creds,group_member_req_creds, external_req_creds]: 
            # response = app_client_role_routes.get(path)
            # subroles = path_roles.get(path).has_subroles
            
            
              
            # response.status_code == 403