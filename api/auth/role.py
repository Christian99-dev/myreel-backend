import os
import logging
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy.orm import Session
from api.auth.path_config import PathInfo
from api.auth.role_enum import RoleEnum
from api.services.database.edit import is_edit_creator
from api.services.database.group import is_group_creator, is_group_member
logger = logging.getLogger("testing")

load_dotenv()

class RoleInfos(BaseModel):
    admintoken: Optional[str]
    userid:     Optional[int]
    groupid:    Optional[str]
    editid:     Optional[int]

class Role:
    def __init__(self, 
                 role_infos:    RoleInfos,
                 db_session:    Optional[Session] = None
    ):  
        roles = [RoleEnum.EXTERNAL]
        admintoken = role_infos.admintoken
        userid = role_infos.userid
        groupid = role_infos.groupid
        editid = role_infos.editid
            
        #ADMIN
        if admintoken is not None and admintoken == os.getenv("ADMIN_TOKEN"):
            roles.append(RoleEnum.ADMIN)
        
        #GROUP MEMBER ODER CREATOR
        if userid is not None and groupid is not None and db_session is not None:
            
            if is_group_member(userid, groupid, db_session):
                roles.append(RoleEnum.GROUP_MEMBER)
                
            if is_group_creator(userid, groupid, db_session):
                roles.append(RoleEnum.GROUP_CREATOR)
        
        #GROUP MEMBER ODER CREATOR
        if userid is not None and editid is not None and db_session is not None:
            if is_edit_creator(userid, editid, db_session):
                roles.append(RoleEnum.EDIT_CREATOR)
            
        self._role = min(roles, key=lambda role: role.value)
    

    def hasAccess(self, pathInfo: PathInfo) -> bool:
        has_subroles = pathInfo.has_subroles
        role         = pathInfo.role
        
        if has_subroles:
            if self._role.value <= role.value:
                return True
            else:
                return False
        else:   
            return self._role.value == role.value