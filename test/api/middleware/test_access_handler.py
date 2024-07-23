import json
import os
import pytest
from typing import Dict
from fastapi import FastAPI
from api.auth import jwt
from api.auth.role import Role, RoleEnum, RoleInfos
from api.config.database import get_db
from fastapi.testclient import TestClient
from api.config.path_roles import PathInfo
from api.middleware.access_handler import AccessHandlerMiddleware
from api.utils.database.test_model import group_id_1
from api.utils.routes.extract_role_credentials_from_request import extract_role_credentials_from_request
from test.utils import role_tester_has_access

# Testconfig für routen
path_roles: Dict[str, PathInfo] = {
    '/admin_no_subrole':            PathInfo(role = RoleEnum.ADMIN,         has_subroles=False),
    '/group_creator_no_subrole':    PathInfo(role = RoleEnum.GROUP_CREATOR, has_subroles=False),
    '/edit_creator_no_subrole':     PathInfo(role = RoleEnum.EDIT_CREATOR,  has_subroles=False),
    '/group_member_no_subrole':     PathInfo(role = RoleEnum.GROUP_MEMBER,  has_subroles=False),
    '/external_no_subrole':         PathInfo(role = RoleEnum.EXTERNAL,      has_subroles=False),
    
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

@pytest.fixture(scope="function")
def app_client_role_routes(db_session_filled):
    
    # simulating prod api
    app = FastAPI()
    app.add_middleware(AccessHandlerMiddleware, path_roles=path_roles)
    
    # every possible endpoint
    @app.get("/admin_no_subrole")
    async def admin_no_subrole(): return {"status": "success"}

    @app.get("/group_creator_no_subrole")
    async def group_creator_no_subrole(): return {"status": "success"}

    @app.get("/edit_creator_no_subrole")
    async def edit_creator_no_subrole(): return {"status": "success"}

    @app.get("/group_member_no_subrole")
    async def group_member_no_subrole(): return {"status": "success"}

    @app.get("/external_no_subrole")
    async def external_no_subrole(): return {"status": "success"}

    @app.get("/admin_subroles")
    async def admin_subroles(): return {"status": "success"}

    @app.get("/group_creator_subroles")
    async def group_creator_subroles(): return {"status": "success"}

    @app.get("/edit_creator_subroles")
    async def edit_creator_subroles(): return {"status": "success"}

    @app.get("/group_member_subroles")
    async def group_member_subroles(): return {"status": "success"}

    @app.get("/external_subroles")
    async def external_subroles(): return {"status": "success"}

    
    def override_get_db():
        yield db_session_filled

    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    app.dependency_overrides.pop(get_db, None)

def test_setup_routes(app_client_role_routes):
    assert app_client_role_routes.get("/admin_no_subrole").status_code          == 403
    assert app_client_role_routes.get("/group_creator_no_subrole").status_code  == 403
    assert app_client_role_routes.get("/edit_creator_no_subrole").status_code   == 403
    assert app_client_role_routes.get("/group_member_no_subrole").status_code   == 403
    assert app_client_role_routes.get("/external_no_subrole").status_code       == 403
    assert app_client_role_routes.get("/admin_subroles").status_code            == 403
    assert app_client_role_routes.get("/group_creator_subroles").status_code    == 403
    assert app_client_role_routes.get("/edit_creator_subroles").status_code     == 403
    assert app_client_role_routes.get("/group_member_subroles").status_code     == 403
    assert app_client_role_routes.get("/external_subroles").status_code         == 403
    
def test_setup_roles(db_session_filled):
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_req_creds["headers"]["admintoken"], userid=None, groupid=None, editid=None), db_session=db_session_filled),  RoleEnum.ADMIN)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=user_1_encoded, groupid=group_creator_req_creds["params"]["groupid"], editid=None), db_session=db_session_filled),  RoleEnum.GROUP_CREATOR)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=user_1_encoded, groupid=None, editid=edit_creator_req_creds["params"]["editid"]), db_session=db_session_filled),  RoleEnum.EDIT_CREATOR)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=user_2_encoded, groupid=group_member_req_creds["params"]["groupid"], editid=None), db_session=db_session_filled),  RoleEnum.GROUP_MEMBER)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=None, groupid=None, editid=None), db_session=db_session_filled),  RoleEnum.EXTERNAL)

def test_endpoints(app_client_role_routes):
    pass
    # import logging
    # for path in path_roles.keys():
        # response = app_client_role_routes.get(path, json={admin_body})
        
    # assert test_client.get("group_creator_no_subrole",   json={role_body}).status_code  == 403
    # assert test_client.get("edit_creator_no_subrole",    json={role_body}).status_code  == 403
    # assert test_client.get("group_member_no_subrole",    json={role_body}).status_code  == 403
    # assert test_client.get("external_no_subrole",        json={role_body}).status_code  == 403
    
    # assert test_client.get("admin_subroles",             json={role_body}).status_code  == 403
    # assert test_client.get("group_creator_subroles",     json={role_body}).status_code  == 403
    # assert test_client.get("edit_creator_subroles",      json={role_body}).status_code  == 403
    # assert test_client.get("group_member_subroles",      json={role_body}).status_code  == 403
    # assert test_client.get("external_subroles",          json={role_body}).status_code  == 403