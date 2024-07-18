import os
from enum import Enum
from typing import Optional
from dotenv import load_dotenv
from pytest import Session
from api.services.edit import is_edit_creator
from api.services.group import is_group_creator, is_group_member

load_dotenv()

class RoleEnum(Enum):
    ADMIN           = 0
    GROUP_CREATOR   = 1
    EDIT_CREATOR    = 2
    GROUP_MEMBER    = 3
    EXTERNAL        = 4

class Role:
    def __init__(self, 
                 admintoken:    Optional[str]     = None, 
                 userid:        Optional[int]     = None, 
                 groupid:       Optional[int]     = None, 
                 editid:        Optional[int]     = None,
                 db_session:    Optional[Session] = None
    ):  
        roles = [RoleEnum.EXTERNAL]

        #ADMIN
        if admintoken is not None and admintoken is os.getenv("ADMIN_TOKEN"):
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
    

    def hasAccess(self, role: RoleEnum, include_sub_roles: bool = True) -> bool:
        if include_sub_roles:
            if self._role.value <= role.value:
                return True
            else:
                return False
        else:   
            return self._role.value == role.value