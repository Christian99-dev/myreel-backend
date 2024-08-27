from api.auth.path_config import PathConfig, PathInfo
from api.auth.role_enum import RoleEnum

mock_path_config = PathConfig({
    '/admin_no_subroles': {
        "GET": PathInfo(role=RoleEnum.ADMIN, has_subroles=False),
    },
    '/group_creator_no_subroles': {
        "GET": PathInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=False),
    },
    '/edit_creator_no_subroles': {
        "GET": PathInfo(role=RoleEnum.EDIT_CREATOR, has_subroles=False),
    },
    '/group_member_no_subroles': {
        "GET": PathInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=False),
    },
    '/external_no_subroles': {
        "GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=False),
    },
    '/admin_subroles': {
        "GET": PathInfo(role=RoleEnum.ADMIN, has_subroles=True),
    },
    '/group_creator_subroles': {
        "GET": PathInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=True),
    },
    '/edit_creator_subroles': {
        "GET": PathInfo(role=RoleEnum.EDIT_CREATOR, has_subroles=True),
    },
    '/group_member_subroles': {
        "GET": PathInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True),
    },
    '/external_subroles': {
        "GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True),
    },
})