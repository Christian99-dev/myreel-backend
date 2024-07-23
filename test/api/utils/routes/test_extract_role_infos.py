import logging
from fastapi import Request, FastAPI
from fastapi.testclient import TestClient
from api.utils.routes.ectract_role_infos import extract_role_infos, RoleCredentials
logger = logging.getLogger("testing")

app = FastAPI()

# @app.post("/test")
# async def role_infos_test_point(request: Request): 
#     body = await request.json()
#     roleInfos = extract_role_infos(body)
#     return roleInfos
    
client = TestClient(app)


def _extract_role_infos():
    response = client.post("/test", json={
        "admintoken": "some_admintoken",
        "userid": "123",
        "groupid": "group_abc",
        "editid": "456"
    })
    assert response.status_code == 200
    role_infos = RoleInfos(**response.json())
    logger.info(role_infos)
    assert role_infos.admintoken == "some_admintoken"
    assert role_infos.userid == 123
    assert role_infos.groupid == "group_abc"
    assert role_infos.editid == 456

def _extract_role_infos_optional_fields():

    response = client.post("/test", json={
        "admintoken": "another_admintoken",
        "groupid": "group_xyz"
    })
    
    assert response.status_code == 200
    role_infos = RoleInfos(**response.json())
    logger.info(role_infos)
    assert role_infos.admintoken == "another_admintoken"
    assert role_infos.userid is None
    assert role_infos.groupid == "group_xyz"
    assert role_infos.editid is None
    
def _extract_role_infos_no_fields():

    response = client.post("/test", json={})
    
    assert response.status_code == 200
    role_infos = RoleInfos(**response.json())
    logger.info(role_infos)
    assert role_infos.admintoken is None
    assert role_infos.userid is None
    assert role_infos.groupid is None
    assert role_infos.editid is None
