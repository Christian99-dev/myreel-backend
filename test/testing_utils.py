from api.auth.role import Role, RoleEnum


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
    assert role_instance.hasAccess(RoleEnum.ADMIN,         include_sub_roles=True) == expected_with_sub_roles[RoleEnum.ADMIN]
    assert role_instance.hasAccess(RoleEnum.GROUP_CREATOR, include_sub_roles=True) == expected_with_sub_roles[RoleEnum.GROUP_CREATOR]
    assert role_instance.hasAccess(RoleEnum.EDIT_CREATOR,  include_sub_roles=True) == expected_with_sub_roles[RoleEnum.EDIT_CREATOR]
    assert role_instance.hasAccess(RoleEnum.GROUP_MEMBER,  include_sub_roles=True) == expected_with_sub_roles[RoleEnum.GROUP_MEMBER]
    assert role_instance.hasAccess(RoleEnum.EXTERNAL,      include_sub_roles=True) == expected_with_sub_roles[RoleEnum.EXTERNAL]

    # Teste ohne Sub-Rollen
    assert role_instance.hasAccess(RoleEnum.ADMIN,         include_sub_roles=False) == expected_without_sub_roles[RoleEnum.ADMIN]
    assert role_instance.hasAccess(RoleEnum.GROUP_CREATOR, include_sub_roles=False) == expected_without_sub_roles[RoleEnum.GROUP_CREATOR]
    assert role_instance.hasAccess(RoleEnum.EDIT_CREATOR,  include_sub_roles=False) == expected_without_sub_roles[RoleEnum.EDIT_CREATOR]
    assert role_instance.hasAccess(RoleEnum.GROUP_MEMBER,  include_sub_roles=False) == expected_without_sub_roles[RoleEnum.GROUP_MEMBER]
    assert role_instance.hasAccess(RoleEnum.EXTERNAL,      include_sub_roles=False) == expected_without_sub_roles[RoleEnum.EXTERNAL]