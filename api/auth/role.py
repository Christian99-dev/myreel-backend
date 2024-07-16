import os
from enum import Enum
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class RoleEnum(Enum):
    ADMIN           = 0
    GROUP_CREATOR   = 1
    EDIT_CREATOR    = 2
    GROUP_MEMBER    = 3
    EXTERNAL        = 4

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
        print(role)
        if include_sub_roles:
            if self._role.value <= role.value:
                return True
            else:
                return False
        else:
            return self._role.value == role.value