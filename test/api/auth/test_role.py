import logging
import os
from sqlalchemy.orm import Session
from api.auth.role import Role, RoleEnum
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

def test_role_has_access_methode_with_include_sub_roles():
    role_instance = Role()
    
    role_instance._role = RoleEnum.ADMIN
    roleTesterHasAccess(role_instance,  RoleEnum.ADMIN)
    
    role_instance._role = RoleEnum.GROUP_CREATOR
    roleTesterHasAccess(role_instance,  RoleEnum.GROUP_CREATOR)
    
    role_instance._role = RoleEnum.EDIT_CREATOR
    roleTesterHasAccess(role_instance,  RoleEnum.EDIT_CREATOR)
    
    role_instance._role = RoleEnum.GROUP_MEMBER
    roleTesterHasAccess(role_instance,  RoleEnum.GROUP_MEMBER)
    
    role_instance._role = RoleEnum.EXTERNAL
    roleTesterHasAccess(role_instance,  RoleEnum.EXTERNAL)

def test_role_has_access_methode_without_include_sub_roles():
    role_instance = Role()
    
    role_instance._role = RoleEnum.ADMIN
    roleTesterHasAccess(role_instance,  RoleEnum.ADMIN)
    
    role_instance._role = RoleEnum.GROUP_CREATOR
    roleTesterHasAccess(role_instance,  RoleEnum.GROUP_CREATOR)
    
    role_instance._role = RoleEnum.EDIT_CREATOR
    roleTesterHasAccess(role_instance,  RoleEnum.EDIT_CREATOR)
    
    role_instance._role = RoleEnum.GROUP_MEMBER
    roleTesterHasAccess(role_instance,  RoleEnum.GROUP_MEMBER)
    
    role_instance._role = RoleEnum.EXTERNAL
    roleTesterHasAccess(role_instance,  RoleEnum.EXTERNAL)

def test_role_external(db_session_filled: Session):
    # just wrong inputs
    roleTesterHasAccess(Role(admintoken=None,       userid=None,    groupid=None,   editid=None,    db_session=db_session_filled),  RoleEnum.EXTERNAL)    
    roleTesterHasAccess(Role(admintoken="wrong",    userid=-99,     groupid=-99,    editid=-99,     db_session=db_session_filled),  RoleEnum.EXTERNAL)

    # no user given
    roleTesterHasAccess(Role(admintoken="wrong",    userid=-99,     groupid=1,      editid=1,        db_session=db_session_filled),  RoleEnum.EXTERNAL)
    roleTesterHasAccess(Role(admintoken="wrong",    userid=None,    groupid=1,      editid=1,        db_session=db_session_filled),  RoleEnum.EXTERNAL)
    
    # wrong group    
    roleTesterHasAccess(Role(admintoken="wrong",    userid=4,     groupid=1,    editid=1,        db_session=db_session_filled),  RoleEnum.EXTERNAL)
    roleTesterHasAccess(Role(admintoken="wrong",    userid=4,     groupid=1,    editid=None,     db_session=db_session_filled),  RoleEnum.EXTERNAL)
    roleTesterHasAccess(Role(admintoken="wrong",    userid=5,     groupid=1,    editid=None,     db_session=db_session_filled),  RoleEnum.EXTERNAL)
    
    # wrong edit    
    roleTesterHasAccess(Role(admintoken="wrong",    userid=3,     groupid=None,    editid=7,        db_session=db_session_filled),  RoleEnum.EXTERNAL)
    
    
def test_role_admin(db_session_filled: Session):
    admin_token = os.getenv("ADMIN_TOKEN")    
    roleTesterHasAccess(Role(admintoken=admin_token, userid=None,   groupid=None,   editid=None,    db_session=db_session_filled),   RoleEnum.ADMIN)

def test_role_group_creator(db_session_filled: Session):
    roleTesterHasAccess(Role(admintoken=None,   userid=1,   groupid=1,  editid=None, db_session=db_session_filled), RoleEnum.GROUP_CREATOR)
    
def test_role_edit_creator(db_session_filled: Session):
    roleTesterHasAccess(Role(admintoken=None,   userid=1,   groupid=None,  editid=1, db_session=db_session_filled), RoleEnum.EDIT_CREATOR)

def test_role_group_member(db_session_filled: Session):
    roleTesterHasAccess(Role(admintoken=None,   userid=2,   groupid=1,  editid=None, db_session=db_session_filled), RoleEnum.GROUP_MEMBER)   

def test_role_always_highest(db_session_filled: Session):  
    admin_token = os.getenv("ADMIN_TOKEN")    
    
    # ADMIN 
    roleTesterHasAccess(Role(admintoken=admin_token,   userid=1,        groupid=1,      editid=None, db_session=db_session_filled), RoleEnum.ADMIN)  # ALSO GROUP_CREATOR
    roleTesterHasAccess(Role(admintoken=admin_token,   userid=1,        groupid=None,   editid=1,    db_session=db_session_filled), RoleEnum.ADMIN)  # ALSO EDIT_CREATOR
    roleTesterHasAccess(Role(admintoken=admin_token,   userid=2,        groupid=1,      editid=None, db_session=db_session_filled), RoleEnum.ADMIN)  # ALSO GROUP_MEMBER
    
    # GROUP_CREATOR 
    roleTesterHasAccess(Role(admintoken=None,           userid=1,        groupid=1,     editid=1,    db_session=db_session_filled), RoleEnum.GROUP_CREATOR)  # ALSO EDIT_CREATOR



# util
def roleTesterHasAccess(role_instance: Role, role_to_test: RoleEnum):
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