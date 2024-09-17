import os
from test.utils.role_tester_has_acccess import role_tester_has_access

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.middleware.access_handler import AccessHandlerMiddleware
from api.security.endpoints_class import EndpointConfig, EndpointInfo
from api.security.role_class import Role, RoleInfos
from api.security.role_enum import RoleEnum
from api.utils.jwt import jwt

"""Setup"""

mock_path_config = EndpointConfig({
    '/admin_no_subroles': {
        "GET": EndpointInfo(role=RoleEnum.ADMIN, has_subroles=False),
    },
    '/group_creator_no_subroles': {
        "GET": EndpointInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=False),
    },
    '/edit_creator_no_subroles': {
        "GET": EndpointInfo(role=RoleEnum.EDIT_CREATOR, has_subroles=False),
    },
    '/group_member_no_subroles': {
        "GET": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=False),
    },
    '/external_no_subroles': {
        "GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=False),
    },
    '/admin_subroles': {
        "GET": EndpointInfo(role=RoleEnum.ADMIN, has_subroles=True),
    },
    '/group_creator_subroles': {
        "GET": EndpointInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=True),
    },
    '/edit_creator_subroles': {
        "GET": EndpointInfo(role=RoleEnum.EDIT_CREATOR, has_subroles=True),
    },
    '/group_member_subroles': {
        "GET": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True),
    },
    '/external_subroles': {
        "GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True),
    },
})

admin_req_creds = {
    "req": {    
        "headers": {
            "admintoken": str(os.getenv("ADMIN_TOKEN"))
        }
    }, 
    "role": RoleEnum.ADMIN,
    "userid": 1
}

group_creator_req_creds = {
    "req": {    
        "headers": {
            "Authorization": f"Bearer {jwt.create_jwt(1, 30)}"
        },
        "params": {
            "groupid": "11111111-1111-1111-1111-111111111111"
        }
    }, 
    "role": RoleEnum.GROUP_CREATOR,
    "userid": 1
}

edit_creator_req_creds = {
    "req": {    
        "headers": {
            "Authorization": f"Bearer {jwt.create_jwt(2, 30)}"
        },
        "params": {
            "editid": "3"
        }
    }, 
    "role": RoleEnum.EDIT_CREATOR,
    "userid": 2
}

group_member_req_creds = {
    "req": {    
        "headers": {
            "Authorization": f"Bearer {jwt.create_jwt(2, 30)}"
        },
        "params": {
            "groupid": "11111111-1111-1111-1111-111111111111"
        }
    }, 
    "role": RoleEnum.GROUP_MEMBER,
    "userid": 2
}

external_req_creds = {
    "req": {
        "headers": {},
        "params": {}
    }, 
    "role": RoleEnum.EXTERNAL,
    "userid": 1
}

group_creator_with_edit_id_req_creds = {
    "req": {    
        "headers": {
            "Authorization": f"Bearer {jwt.create_jwt(1, 30)}"
        },
        "params": {
            "editid": "1"
        }
    }, 
    "role": RoleEnum.GROUP_CREATOR,
    "userid": 1
}

group_member_with_edit_id_req_creds = {
    "req": {    
        "headers": {
            "Authorization": f"Bearer {jwt.create_jwt(3, 30)}"
        },
        "params": {
            "editid": "1"
        }
    }, 
    "role": RoleEnum.GROUP_MEMBER,
    "userid": 2
}


@pytest.fixture(scope="function")
def http_client_mocked_paths(memory_database_session: Session):
    
    # simulating prod api
    app = FastAPI()
    
    # session
    def get_database_session_override(): 
        yield memory_database_session
    
    # middleware for access testing 
    app.add_middleware(AccessHandlerMiddleware, path_config=mock_path_config, get_database_session=get_database_session_override)
    
    # every endpoints based on testconfig file
    def create_endpoint(m_name: str):
        async def endpoint(request: Request):
            return f"You called {m_name}"
        return endpoint

    for path, method in mock_path_config.get_all_paths_and_methods():
        app.add_api_route(f"{path}", create_endpoint(path), methods=[method])
    
    # yield client with routes
    with TestClient(app) as test_client:
        yield test_client

"""Testing Setup"""
def test_http_client_mocked_paths(http_client_mocked_paths: TestClient):
    assert http_client_mocked_paths.get("/admin_no_subroles").status_code          == 403
    assert http_client_mocked_paths.get("/group_creator_no_subroles").status_code  == 403
    assert http_client_mocked_paths.get("/edit_creator_no_subroles").status_code   == 403
    assert http_client_mocked_paths.get("/group_member_no_subroles").status_code   == 403
    assert http_client_mocked_paths.get("/external_no_subroles").status_code       == 200
    
    assert http_client_mocked_paths.get("/admin_subroles").status_code            == 403
    assert http_client_mocked_paths.get("/group_creator_subroles").status_code    == 403
    assert http_client_mocked_paths.get("/edit_creator_subroles").status_code     == 403
    assert http_client_mocked_paths.get("/group_member_subroles").status_code     == 403
    assert http_client_mocked_paths.get("/external_subroles").status_code         == 200   

def test_mock_data_user_creds(memory_database_session: Session):
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_req_creds["req"]["headers"]["admintoken"], userid=None, groupid=None, editid=None), db_session=memory_database_session), RoleEnum.ADMIN)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=group_creator_req_creds["userid"], groupid=group_creator_req_creds["req"]["params"]["groupid"], editid=None), db_session=memory_database_session), RoleEnum.GROUP_CREATOR)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=group_creator_with_edit_id_req_creds["userid"], groupid=None, editid=group_creator_with_edit_id_req_creds["req"]["params"]["editid"]), db_session=memory_database_session), RoleEnum.GROUP_CREATOR)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=group_member_with_edit_id_req_creds["userid"], groupid=None, editid=group_member_with_edit_id_req_creds["req"]["params"]["editid"]), db_session=memory_database_session), RoleEnum.GROUP_MEMBER)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=edit_creator_req_creds["userid"], groupid=None, editid=edit_creator_req_creds["req"]["params"]["editid"]), db_session=memory_database_session), RoleEnum.EDIT_CREATOR)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=group_member_req_creds["userid"], groupid=group_member_req_creds["req"]["params"]["groupid"], editid=None), db_session=memory_database_session), RoleEnum.GROUP_MEMBER)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=None, groupid=None, editid=None), db_session=memory_database_session), RoleEnum.EXTERNAL)    

    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_req_creds["req"]["headers"]["admintoken"], userid=None, groupid=None, editid=None), db_session=memory_database_session), admin_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=group_creator_req_creds["userid"], groupid=group_creator_req_creds["req"]["params"]["groupid"], editid=None), db_session=memory_database_session), group_creator_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=group_creator_with_edit_id_req_creds["userid"], groupid=None, editid=group_creator_with_edit_id_req_creds["req"]["params"]["editid"]), db_session=memory_database_session), group_creator_with_edit_id_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=group_member_with_edit_id_req_creds["userid"], groupid=None, editid=group_member_with_edit_id_req_creds["req"]["params"]["editid"]), db_session=memory_database_session), group_member_with_edit_id_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=edit_creator_req_creds["userid"], groupid=None, editid=edit_creator_req_creds["req"]["params"]["editid"]), db_session=memory_database_session), edit_creator_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=group_member_req_creds["userid"], groupid=group_member_req_creds["req"]["params"]["groupid"], editid=None), db_session=memory_database_session), group_member_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=None, groupid=None, editid=None), db_session=memory_database_session), external_req_creds["role"])


"""Main test"""
def test_access_handler_with_subroles(http_client_mocked_paths: TestClient):     
    for path, method in mock_path_config.get_all_paths_and_methods():
        path_info = mock_path_config.get_path_info(path, method)
        
        # Beispiel für Subrollen (angenommen, es gibt Subrollen für ADMIN)
        for current_creds in [
            admin_req_creds, 
            group_creator_req_creds, 
            edit_creator_req_creds, 
            group_member_req_creds, 
            external_req_creds,
            group_creator_with_edit_id_req_creds,
            group_member_with_edit_id_req_creds
        ]: 
            headers = current_creds["req"]["headers"]
            params  = current_creds["req"].get("params", {})
            with_subroles = path_info.has_subroles
            required_role = path_info.role
            current_role  = current_creds["role"]

            response = http_client_mocked_paths.get(path, headers=headers, params=params)


            if not with_subroles:
                expected_status = 200 if required_role.value == current_role.value else 403
            else:
                expected_status = 200 if required_role.value >= current_role.value else 403
                
            assert response.status_code == expected_status
            
            