import pytest
import logging
from api.auth.role import Role, RoleEnum
from typing import Optional

logger = logging.getLogger(__name__)

def test_role_has_access_with_include_sub_roles():
    role_instance = Role() 
    
    role_instance._role = RoleEnum.ADMIN
    assert role_instance.hasAccess(RoleEnum.ADMIN)          == True
    assert role_instance.hasAccess(RoleEnum.GROUP_CREATOR)  == True
    assert role_instance.hasAccess(RoleEnum.EDIT_CREATOR)   == True
    assert role_instance.hasAccess(RoleEnum.GROUP_MEMBER)   == True
    assert role_instance.hasAccess(RoleEnum.EXTERNAL)       == True
    
    role_instance._role = RoleEnum.GROUP_CREATOR
    assert role_instance.hasAccess(RoleEnum.ADMIN)          == False
    assert role_instance.hasAccess(RoleEnum.GROUP_CREATOR)  == True
    assert role_instance.hasAccess(RoleEnum.EDIT_CREATOR)   == True
    assert role_instance.hasAccess(RoleEnum.GROUP_MEMBER)   == True
    assert role_instance.hasAccess(RoleEnum.EXTERNAL)       == True
    
    role_instance._role = RoleEnum.EDIT_CREATOR
    assert role_instance.hasAccess(RoleEnum.ADMIN)          == False
    assert role_instance.hasAccess(RoleEnum.GROUP_CREATOR)  == False
    assert role_instance.hasAccess(RoleEnum.EDIT_CREATOR)   == True
    assert role_instance.hasAccess(RoleEnum.GROUP_MEMBER)   == True
    assert role_instance.hasAccess(RoleEnum.EXTERNAL)       == True
    
    role_instance._role = RoleEnum.GROUP_MEMBER
    assert role_instance.hasAccess(RoleEnum.ADMIN)          == False
    assert role_instance.hasAccess(RoleEnum.GROUP_CREATOR)  == False
    assert role_instance.hasAccess(RoleEnum.EDIT_CREATOR)   == False
    assert role_instance.hasAccess(RoleEnum.GROUP_MEMBER)   == True
    assert role_instance.hasAccess(RoleEnum.EXTERNAL)       == True
    
    role_instance._role = RoleEnum.EXTERNAL
    assert role_instance.hasAccess(RoleEnum.ADMIN)          == False
    assert role_instance.hasAccess(RoleEnum.GROUP_CREATOR)  == False
    assert role_instance.hasAccess(RoleEnum.EDIT_CREATOR)   == False
    assert role_instance.hasAccess(RoleEnum.GROUP_MEMBER)   == False
    assert role_instance.hasAccess(RoleEnum.EXTERNAL)       == True
    
def test_role_has_access_without_include_sub_roles():
    role_instance = Role() 
    
    role_instance._role = RoleEnum.ADMIN
    assert role_instance.hasAccess(RoleEnum.ADMIN, include_sub_roles=False)          == True
    assert role_instance.hasAccess(RoleEnum.GROUP_CREATOR, include_sub_roles=False)  == False
    assert role_instance.hasAccess(RoleEnum.EDIT_CREATOR, include_sub_roles=False)   == False
    assert role_instance.hasAccess(RoleEnum.GROUP_MEMBER, include_sub_roles=False)   == False
    assert role_instance.hasAccess(RoleEnum.EXTERNAL, include_sub_roles=False)       == False
    
    role_instance._role = RoleEnum.GROUP_CREATOR
    assert role_instance.hasAccess(RoleEnum.ADMIN, include_sub_roles=False)          == False
    assert role_instance.hasAccess(RoleEnum.GROUP_CREATOR, include_sub_roles=False)  == True
    assert role_instance.hasAccess(RoleEnum.EDIT_CREATOR, include_sub_roles=False)   == False
    assert role_instance.hasAccess(RoleEnum.GROUP_MEMBER, include_sub_roles=False)   == False
    assert role_instance.hasAccess(RoleEnum.EXTERNAL, include_sub_roles=False)       == False
    
    role_instance._role = RoleEnum.EDIT_CREATOR
    assert role_instance.hasAccess(RoleEnum.ADMIN, include_sub_roles=False)          == False
    assert role_instance.hasAccess(RoleEnum.GROUP_CREATOR, include_sub_roles=False)  == False
    assert role_instance.hasAccess(RoleEnum.EDIT_CREATOR, include_sub_roles=False)   == True
    assert role_instance.hasAccess(RoleEnum.GROUP_MEMBER, include_sub_roles=False)   == False
    assert role_instance.hasAccess(RoleEnum.EXTERNAL, include_sub_roles=False)       == False
    
    role_instance._role = RoleEnum.GROUP_MEMBER
    assert role_instance.hasAccess(RoleEnum.ADMIN, include_sub_roles=False)          == False
    assert role_instance.hasAccess(RoleEnum.GROUP_CREATOR, include_sub_roles=False)  == False
    assert role_instance.hasAccess(RoleEnum.EDIT_CREATOR, include_sub_roles=False)   == False
    assert role_instance.hasAccess(RoleEnum.GROUP_MEMBER, include_sub_roles=False)   == True
    assert role_instance.hasAccess(RoleEnum.EXTERNAL, include_sub_roles=False)       == False
    
    role_instance._role = RoleEnum.EXTERNAL
    assert role_instance.hasAccess(RoleEnum.ADMIN, include_sub_roles=False)          == False
    assert role_instance.hasAccess(RoleEnum.GROUP_CREATOR, include_sub_roles=False)  == False
    assert role_instance.hasAccess(RoleEnum.EDIT_CREATOR, include_sub_roles=False)   == False
    assert role_instance.hasAccess(RoleEnum.GROUP_MEMBER, include_sub_roles=False)   == False
    assert role_instance.hasAccess(RoleEnum.EXTERNAL, include_sub_roles=False)       == True