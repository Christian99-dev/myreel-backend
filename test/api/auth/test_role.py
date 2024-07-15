import pytest
import logging
from api.auth.role import Role

logger = logging.getLogger(__name__)

def test_role_access_with_sub_roles():
    role_instance = Role()
    logger.info("Testing access with sub-roles included")

    assert role_instance.hasAccess("admin")
    assert role_instance.hasAccess("GroupCreator")
    assert role_instance.hasAccess("EditCreator")
    assert role_instance.hasAccess("GroupMember")
    assert role_instance.hasAccess("External")
    assert not role_instance.hasAccess("UnknownRole")

def test_role_access_without_sub_roles():
    role_instance = Role()
    logger.info("Testing access without sub-roles included")

    assert role_instance.hasAccess("admin", include_sub_roles=False)
    assert not role_instance.hasAccess("GroupCreator", include_sub_roles=False)
    assert not role_instance.hasAccess("EditCreator", include_sub_roles=False)
    assert not role_instance.hasAccess("GroupMember", include_sub_roles=False)
    assert not role_instance.hasAccess("External", include_sub_roles=False)
    assert not role_instance.hasAccess("UnknownRole", include_sub_roles=False)