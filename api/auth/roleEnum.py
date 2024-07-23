from enum import Enum

class RoleEnum(Enum):
    ADMIN           = 0
    GROUP_CREATOR   = 1
    EDIT_CREATOR    = 2
    GROUP_MEMBER    = 3
    EXTERNAL        = 4