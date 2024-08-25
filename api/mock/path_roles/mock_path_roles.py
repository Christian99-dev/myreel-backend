from typing import Dict
from api.auth.role_enum import RoleEnum
from api.config.path_roles import PathInfo

mock_path_roles: Dict[str, PathInfo] = {
    '/admin_no_subroles':            PathInfo(role = RoleEnum.ADMIN,         has_subroles=False),
    '/group_creator_no_subroles':    PathInfo(role = RoleEnum.GROUP_CREATOR, has_subroles=False),
    '/edit_creator_no_subroles':     PathInfo(role = RoleEnum.EDIT_CREATOR,  has_subroles=False),
    '/group_member_no_subroles':     PathInfo(role = RoleEnum.GROUP_MEMBER,  has_subroles=False),
    '/external_no_subroles':         PathInfo(role = RoleEnum.EXTERNAL,      has_subroles=False),
    
    '/admin_subroles':              PathInfo(role = RoleEnum.ADMIN,         has_subroles=True),
    '/group_creator_subroles':      PathInfo(role = RoleEnum.GROUP_CREATOR, has_subroles=True),
    '/edit_creator_subroles':       PathInfo(role = RoleEnum.EDIT_CREATOR,  has_subroles=True),
    '/group_member_subroles':       PathInfo(role = RoleEnum.GROUP_MEMBER,  has_subroles=True),
    '/external_subroles':           PathInfo(role = RoleEnum.EXTERNAL,      has_subroles=True),
}