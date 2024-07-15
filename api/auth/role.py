import os
from enum import Enum
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class RoleEnum(Enum):
    ADMIN           = "admin"
    GROUP_CREATOR   = "GroupCreator"
    EDIT_CREATOR    = "EditCreator"
    GROUP_MEMBER    = "GroupMember"
    EXTERNAL        = "External"
    
role_hierarchy = {
    RoleEnum.ADMIN:         [RoleEnum.GROUP_CREATOR, RoleEnum.EDIT_CREATOR, RoleEnum.GROUP_MEMBER, RoleEnum.EXTERNAL],
    RoleEnum.GROUP_CREATOR: [                        RoleEnum.EDIT_CREATOR, RoleEnum.GROUP_MEMBER, RoleEnum.EXTERNAL],
    RoleEnum.EDIT_CREATOR:  [                                               RoleEnum.GROUP_MEMBER, RoleEnum.EXTERNAL],
    RoleEnum.GROUP_MEMBER:  [                                                                      RoleEnum.EXTERNAL],
    RoleEnum.EXTERNAL:      []
}

class Role:
    def __init__(self, 
                 admintoken:    Optional[str] = None, 
                 userid:        Optional[str] = None, 
                 groupid:       Optional[str] = None, 
                 editid:        Optional[str] = None
    ):        
        if admintoken is not None and admintoken is os.getenv("ADMIN_TOKEN"):
            self._role = RoleEnum.ADMIN
            return
        
        self._role = RoleEnum.EXTERNAL
    

    def hasAccess(self, role: RoleEnum, include_sub_roles: bool = True) -> bool:
        if include_sub_roles:
            if self._role == role:
                return True
            elif role in role_hierarchy.get(self._role, []):
                return True
            return False
        else:
            return self._role == role