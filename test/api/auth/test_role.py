import logging
import os
from sqlalchemy.orm import Session
from api.auth.role import Role, RoleEnum
from dotenv import load_dotenv
from api.utils.database.test_model import group_id_1

logger = logging.getLogger("testing")
load_dotenv()

# util
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
    

def test_role_has_access_methode_with_include_sub_roles():
    role_instance = Role()
    
    role_instance._role = RoleEnum.ADMIN
    role_tester_has_access(role_instance,  RoleEnum.ADMIN)
    
    role_instance._role = RoleEnum.GROUP_CREATOR
    role_tester_has_access(role_instance,  RoleEnum.GROUP_CREATOR)
    
    role_instance._role = RoleEnum.EDIT_CREATOR
    role_tester_has_access(role_instance,  RoleEnum.EDIT_CREATOR)
    
    role_instance._role = RoleEnum.GROUP_MEMBER
    role_tester_has_access(role_instance,  RoleEnum.GROUP_MEMBER)
    
    role_instance._role = RoleEnum.EXTERNAL
    role_tester_has_access(role_instance,  RoleEnum.EXTERNAL)

def test_role_has_access_methode_without_include_sub_roles():
    role_instance = Role()
    
    role_instance._role = RoleEnum.ADMIN
    role_tester_has_access(role_instance,  RoleEnum.ADMIN)
    
    role_instance._role = RoleEnum.GROUP_CREATOR
    role_tester_has_access(role_instance,  RoleEnum.GROUP_CREATOR)
    
    role_instance._role = RoleEnum.EDIT_CREATOR
    role_tester_has_access(role_instance,  RoleEnum.EDIT_CREATOR)
    
    role_instance._role = RoleEnum.GROUP_MEMBER
    role_tester_has_access(role_instance,  RoleEnum.GROUP_MEMBER)
    
    role_instance._role = RoleEnum.EXTERNAL
    role_tester_has_access(role_instance,  RoleEnum.EXTERNAL)

def test_role_external(db_session_filled: Session):
    # just wrong inputs
    role_tester_has_access(Role(admintoken=None,       userid=None,    groupid=None,   editid=None,    db_session=db_session_filled),  RoleEnum.EXTERNAL)    
    role_tester_has_access(Role(admintoken="wrong",    userid=-99,     groupid=-99,    editid=-99,     db_session=db_session_filled),  RoleEnum.EXTERNAL)

    # no user given
    role_tester_has_access(Role(admintoken="wrong",    userid=-99,     groupid=group_id_1,      editid=1,        db_session=db_session_filled),  RoleEnum.EXTERNAL)
    role_tester_has_access(Role(admintoken="wrong",    userid=None,    groupid=group_id_1,      editid=1,        db_session=db_session_filled),  RoleEnum.EXTERNAL)
    
    # wrong group    
    role_tester_has_access(Role(admintoken="wrong",    userid=4,     groupid=group_id_1,    editid=1,        db_session=db_session_filled),  RoleEnum.EXTERNAL)
    role_tester_has_access(Role(admintoken="wrong",    userid=4,     groupid=group_id_1,    editid=None,     db_session=db_session_filled),  RoleEnum.EXTERNAL)
    role_tester_has_access(Role(admintoken="wrong",    userid=5,     groupid=group_id_1,    editid=None,     db_session=db_session_filled),  RoleEnum.EXTERNAL)
    
    # wrong edit    
    role_tester_has_access(Role(admintoken="wrong",    userid=3,     groupid=None,    editid=7,        db_session=db_session_filled),  RoleEnum.EXTERNAL)
    
def test_role_admin(db_session_filled: Session):
    admin_token = os.getenv("ADMIN_TOKEN")    
    role_tester_has_access(Role(admintoken=admin_token, userid=None,   groupid=None,   editid=None,    db_session=db_session_filled),   RoleEnum.ADMIN)

def test_role_group_creator(db_session_filled: Session):
    role_tester_has_access(Role(admintoken=None,   userid=1,   groupid=group_id_1,  editid=None, db_session=db_session_filled), RoleEnum.GROUP_CREATOR)
    
def test_role_edit_creator(db_session_filled: Session):
    role_tester_has_access(Role(admintoken=None,   userid=1,   groupid=None,  editid=1, db_session=db_session_filled), RoleEnum.EDIT_CREATOR)

def test_role_group_member(db_session_filled: Session):
    role_tester_has_access(Role(admintoken=None,   userid=2,   groupid=group_id_1,  editid=None, db_session=db_session_filled), RoleEnum.GROUP_MEMBER)   

def test_role_always_highest(db_session_filled: Session):  
    admin_token = os.getenv("ADMIN_TOKEN")    
    
    # ADMIN 
    role_tester_has_access(Role(admintoken=admin_token,   userid=1,        groupid=group_id_1,      editid=None, db_session=db_session_filled), RoleEnum.ADMIN)  # ALSO GROUP_CREATOR
    role_tester_has_access(Role(admintoken=admin_token,   userid=1,        groupid=None,   editid=1,    db_session=db_session_filled), RoleEnum.ADMIN)  # ALSO EDIT_CREATOR
    role_tester_has_access(Role(admintoken=admin_token,   userid=2,        groupid=group_id_1,      editid=None, db_session=db_session_filled), RoleEnum.ADMIN)  # ALSO GROUP_MEMBER
    
    # GROUP_CREATOR 
    role_tester_has_access(Role(admintoken=None,           userid=1,        groupid=group_id_1,     editid=1,    db_session=db_session_filled), RoleEnum.GROUP_CREATOR)  # ALSO EDIT_CREATOR


