import os
from sqlalchemy.orm import Session
from api.security.role_class import Role, RoleInfos
from api.security.role_enum import RoleEnum
from dotenv import load_dotenv
from test.utils.role_tester_has_acccess import role_tester_has_access
load_dotenv()

def test_role_has_access_methode_with_include_sub_roles():
    role_instance = Role(RoleInfos(admintoken=None,       userid=None,    groupid=None,   editid=None))
    
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
    role_instance = Role(RoleInfos(admintoken=None,       userid=None,    groupid=None,   editid=None))
    
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

def test_role_external(memory_database_session: Session):
    # just wrong inputs
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None,       userid=None,    groupid=None,   editid=None),    db_session=memory_database_session),  RoleEnum.EXTERNAL)    
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken="wrong",    userid=-99,     groupid="-99",    editid=-99),     db_session=memory_database_session),  RoleEnum.EXTERNAL)

    # no user given
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken="wrong",    userid=-99,     groupid="11111111-1111-1111-1111-111111111111",      editid=1),        db_session=memory_database_session),  RoleEnum.EXTERNAL)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken="wrong",    userid=None,    groupid="11111111-1111-1111-1111-111111111111",      editid=1),        db_session=memory_database_session),  RoleEnum.EXTERNAL)
    
    # wrong group    
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken="wrong",    userid=4,     groupid="11111111-1111-1111-1111-111111111111",    editid=1),        db_session=memory_database_session),  RoleEnum.EXTERNAL)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken="wrong",    userid=4,     groupid="11111111-1111-1111-1111-111111111111",    editid=None),     db_session=memory_database_session),  RoleEnum.EXTERNAL)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken="wrong",    userid=5,     groupid="11111111-1111-1111-1111-111111111111",    editid=None),     db_session=memory_database_session),  RoleEnum.EXTERNAL)
    
    # wrong edit    
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken="wrong",    userid=3,     groupid=None,    editid=7),        db_session=memory_database_session),  RoleEnum.EXTERNAL)
    
def test_role_admin(memory_database_session: Session):
    admin_token = os.getenv("ADMIN_TOKEN")    
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_token, userid=None,   groupid=None,   editid=None),    db_session=memory_database_session),   RoleEnum.ADMIN)

def test_role_group_creator(memory_database_session: Session):
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None,   userid=1,   groupid="11111111-1111-1111-1111-111111111111",  editid=None), db_session=memory_database_session), RoleEnum.GROUP_CREATOR)
    
def test_role_edit_creator(memory_database_session: Session):
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None,   userid=2,   groupid=None,  editid=3), db_session=memory_database_session), RoleEnum.EDIT_CREATOR)

def test_role_group_member(memory_database_session: Session):
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None,   userid=2,   groupid="11111111-1111-1111-1111-111111111111",  editid=None), db_session=memory_database_session), RoleEnum.GROUP_MEMBER)   

def test_role_always_highest(memory_database_session: Session):  
    admin_token = os.getenv("ADMIN_TOKEN")    
    
    # ADMIN 
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_token,   userid=1,        groupid="11111111-1111-1111-1111-111111111111",      editid=None), db_session=memory_database_session), RoleEnum.ADMIN)  # ALSO GROUP_CREATOR
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_token,   userid=1,        groupid=None,   editid=1),    db_session=memory_database_session), RoleEnum.ADMIN)  # ALSO EDIT_CREATOR
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_token,   userid=2,        groupid="11111111-1111-1111-1111-111111111111",      editid=None), db_session=memory_database_session), RoleEnum.ADMIN)  # ALSO GROUP_MEMBER
    
    # GROUP_CREATOR 
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None,           userid=1,        groupid="11111111-1111-1111-1111-111111111111",     editid=1),    db_session=memory_database_session), RoleEnum.GROUP_CREATOR)  # ALSO EDIT_CREATOR


