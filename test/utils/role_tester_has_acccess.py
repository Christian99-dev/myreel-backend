from api.config.endpoints import EndpointInfo
from api.security.role_enum import RoleEnum
from api.security.role_class import Role

# this methode is testing, if the role_instance is the expected role.
def role_tester_has_access(role_instance: Role, role_to_test: RoleEnum):
    if role_to_test == RoleEnum.ADMIN:
        expected_with_sub_roles = {
            RoleEnum.ADMIN:         True,
            RoleEnum.GROUP_CREATOR: True,
            RoleEnum.EDIT_CREATOR:  True,
            RoleEnum.GROUP_MEMBER:  True,
            RoleEnum.EXTERNAL:      True
        }
        expected_without_sub_roles = {
            RoleEnum.ADMIN:         True,
            RoleEnum.GROUP_CREATOR: False,
            RoleEnum.EDIT_CREATOR:  False,
            RoleEnum.GROUP_MEMBER:  False,
            RoleEnum.EXTERNAL:      False
        }
    elif role_to_test == RoleEnum.GROUP_CREATOR:
        expected_with_sub_roles = {
            RoleEnum.ADMIN:         False,
            RoleEnum.GROUP_CREATOR: True,
            RoleEnum.EDIT_CREATOR:  True,
            RoleEnum.GROUP_MEMBER:  True,
            RoleEnum.EXTERNAL:      True
        }
        expected_without_sub_roles = {
            RoleEnum.GROUP_CREATOR: True,
            RoleEnum.ADMIN:         False,
            RoleEnum.EDIT_CREATOR:  False,
            RoleEnum.GROUP_MEMBER:  False,
            RoleEnum.EXTERNAL:      False
        }
    elif role_to_test == RoleEnum.EDIT_CREATOR:
        expected_with_sub_roles = {
            RoleEnum.ADMIN:         False,
            RoleEnum.GROUP_CREATOR: False,
            RoleEnum.EDIT_CREATOR:  True,
            RoleEnum.GROUP_MEMBER:  True,
            RoleEnum.EXTERNAL:      True
        }
        expected_without_sub_roles = {
            RoleEnum.ADMIN:         False,
            RoleEnum.GROUP_CREATOR: False,
            RoleEnum.EDIT_CREATOR:  True,
            RoleEnum.GROUP_MEMBER:  False,
            RoleEnum.EXTERNAL:      False
        }
    elif role_to_test == RoleEnum.GROUP_MEMBER:
        expected_with_sub_roles = {
            RoleEnum.ADMIN:         False,
            RoleEnum.GROUP_CREATOR: False,
            RoleEnum.EDIT_CREATOR:  False,
            RoleEnum.GROUP_MEMBER:  True,
            RoleEnum.EXTERNAL:      True
        }
        expected_without_sub_roles = {
            RoleEnum.ADMIN:         False,
            RoleEnum.GROUP_CREATOR: False,
            RoleEnum.EDIT_CREATOR:  False,
            RoleEnum.GROUP_MEMBER:  True,
            RoleEnum.EXTERNAL:      False
        }
    elif role_to_test == RoleEnum.EXTERNAL:
        expected_with_sub_roles = {
            RoleEnum.ADMIN:         False,
            RoleEnum.GROUP_CREATOR: False,
            RoleEnum.EDIT_CREATOR:  False,
            RoleEnum.GROUP_MEMBER:  False,
            RoleEnum.EXTERNAL:      True
        }
        expected_without_sub_roles = {
            RoleEnum.ADMIN:         False,
            RoleEnum.GROUP_CREATOR: False,
            RoleEnum.EDIT_CREATOR:  False,
            RoleEnum.GROUP_MEMBER:  False,
            RoleEnum.EXTERNAL:      True
        }

    # Teste mit Sub-Rollen
    assert role_instance.hasAccess(EndpointInfo(role=RoleEnum.ADMIN,         has_subroles=True)) == expected_with_sub_roles[RoleEnum.ADMIN]
    assert role_instance.hasAccess(EndpointInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=True)) == expected_with_sub_roles[RoleEnum.GROUP_CREATOR]
    assert role_instance.hasAccess(EndpointInfo(role=RoleEnum.EDIT_CREATOR,  has_subroles=True)) == expected_with_sub_roles[RoleEnum.EDIT_CREATOR]
    assert role_instance.hasAccess(EndpointInfo(role=RoleEnum.GROUP_MEMBER,  has_subroles=True)) == expected_with_sub_roles[RoleEnum.GROUP_MEMBER]
    assert role_instance.hasAccess(EndpointInfo(role=RoleEnum.EXTERNAL,      has_subroles=True)) == expected_with_sub_roles[RoleEnum.EXTERNAL]

    # Teste ohne Sub-Rollen
    assert role_instance.hasAccess(EndpointInfo(role=RoleEnum.ADMIN,         has_subroles=False)) == expected_without_sub_roles[RoleEnum.ADMIN]
    assert role_instance.hasAccess(EndpointInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=False)) == expected_without_sub_roles[RoleEnum.GROUP_CREATOR]
    assert role_instance.hasAccess(EndpointInfo(role=RoleEnum.EDIT_CREATOR,  has_subroles=False)) == expected_without_sub_roles[RoleEnum.EDIT_CREATOR]
    assert role_instance.hasAccess(EndpointInfo(role=RoleEnum.GROUP_MEMBER,  has_subroles=False)) == expected_without_sub_roles[RoleEnum.GROUP_MEMBER]
    assert role_instance.hasAccess(EndpointInfo(role=RoleEnum.EXTERNAL,      has_subroles=False)) == expected_without_sub_roles[RoleEnum.EXTERNAL]
