from typing import Optional
from pydantic import BaseModel

class RoleCredentials(BaseModel):
    admintoken: Optional[str]
    jwt:        Optional[str]
    groupid:    Optional[str]
    editid:     Optional[int]

def extract_role_infos(body: dict) -> RoleCredentials:
    # Extrahiere die relevanten Informationen aus dem Body
    admintoken  = body.get('admintoken')
    jwt         = body.get('jwt')
    groupid     = body.get('groupid')
    editid      = body.get('editid')
    
    editid = int(editid) if editid is not None else None

    return RoleCredentials(admintoken=admintoken, jwt=jwt, groupid=groupid, editid=editid)
