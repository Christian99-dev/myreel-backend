from typing import Optional
from pydantic import BaseModel

class RoleInfos(BaseModel):
    admintoken: Optional[str]
    userid:     Optional[int]
    groupid:    Optional[str]
    editid:     Optional[int]

def extract_role_infos(body: dict) -> RoleInfos:
    # Extrahiere die relevanten Informationen aus dem Body
    admintoken  = body.get('admintoken')
    userid      = body.get('userid')
    groupid     = body.get('groupid')
    editid      = body.get('editid')
    
    userid = int(userid) if userid is not None else None
    editid = int(editid) if editid is not None else None

    return RoleInfos(admintoken=admintoken, userid=userid, groupid=groupid, editid=editid)
