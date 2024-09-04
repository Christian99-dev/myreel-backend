import os
import logging
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy.orm import Session
from api.config.endpoints import EndpointInfo
from api.security.role_enum import RoleEnum
from api.services.database.edit import is_edit_creator
from api.services.database.group import get_group_by_edit_id, is_group_creator, is_group_member
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
        
        # There is still a chance that the edit id is pointing to a group. 
        if RoleEnum.GROUP_MEMBER not in roles and RoleEnum.GROUP_CREATOR not in roles and editid is not None and groupid is None and userid is not None:
            group_found_via_editid = get_group_by_edit_id(editid, db_session)
            
            if group_found_via_editid is not None:
                if is_group_member(userid, group_found_via_editid.group_id, db_session):
                    roles.append(RoleEnum.GROUP_MEMBER)
                
                if is_group_creator(userid, group_found_via_editid.group_id, db_session):
                    roles.append(RoleEnum.GROUP_CREATOR)

            
            
        
        #GROUP EDIT CREATOR
        if userid is not None and editid is not None and db_session is not None:
            if is_edit_creator(userid, editid, db_session):
                roles.append(RoleEnum.EDIT_CREATOR)
            
        self._role = min(roles, key=lambda role: role.value)
    

    def hasAccess(self, pathInfo: EndpointInfo) -> bool:
        has_subroles = pathInfo.has_subroles
        role         = pathInfo.role
        
        if has_subroles:
            if self._role.value <= role.value:
                return True
            else:
                return False
        else:   
            return self._role.value == role.value