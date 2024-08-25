import logging
import os
from sqlalchemy.orm import Session
from api.auth.role import Role, RoleInfos
from api.auth.role_enum import RoleEnum
from dotenv import load_dotenv
from api.mock.database.model import group_id_1
from test.utils.role_tester_has_acccess import role_tester_has_access

logger = logging.getLogger("testing")
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

def test_role_external(db_memory: Session):
    # just wrong inputs
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None,       userid=None,    groupid=None,   editid=None),    db_session=db_memory),  RoleEnum.EXTERNAL)    
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken="wrong",    userid=-99,     groupid="-99",    editid=-99),     db_session=db_memory),  RoleEnum.EXTERNAL)

    # no user given
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken="wrong",    userid=-99,     groupid=group_id_1,      editid=1),        db_session=db_memory),  RoleEnum.EXTERNAL)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken="wrong",    userid=None,    groupid=group_id_1,      editid=1),        db_session=db_memory),  RoleEnum.EXTERNAL)
    
    # wrong group    
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken="wrong",    userid=4,     groupid=group_id_1,    editid=1),        db_session=db_memory),  RoleEnum.EXTERNAL)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken="wrong",    userid=4,     groupid=group_id_1,    editid=None),     db_session=db_memory),  RoleEnum.EXTERNAL)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken="wrong",    userid=5,     groupid=group_id_1,    editid=None),     db_session=db_memory),  RoleEnum.EXTERNAL)
    
    # wrong edit    
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken="wrong",    userid=3,     groupid=None,    editid=7),        db_session=db_memory),  RoleEnum.EXTERNAL)
    
def test_role_admin(db_memory: Session):
    admin_token = os.getenv("ADMIN_TOKEN")    
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_token, userid=None,   groupid=None,   editid=None),    db_session=db_memory),   RoleEnum.ADMIN)

def test_role_group_creator(db_memory: Session):
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None,   userid=1,   groupid=group_id_1,  editid=None), db_session=db_memory), RoleEnum.GROUP_CREATOR)
    
def test_role_edit_creator(db_memory: Session):
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None,   userid=1,   groupid=None,  editid=1), db_session=db_memory), RoleEnum.EDIT_CREATOR)

def test_role_group_member(db_memory: Session):
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None,   userid=2,   groupid=group_id_1,  editid=None), db_session=db_memory), RoleEnum.GROUP_MEMBER)   

def test_role_always_highest(db_memory: Session):  
    admin_token = os.getenv("ADMIN_TOKEN")    
    
    # ADMIN 
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_token,   userid=1,        groupid=group_id_1,      editid=None), db_session=db_memory), RoleEnum.ADMIN)  # ALSO GROUP_CREATOR
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_token,   userid=1,        groupid=None,   editid=1),    db_session=db_memory), RoleEnum.ADMIN)  # ALSO EDIT_CREATOR
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_token,   userid=2,        groupid=group_id_1,      editid=None), db_session=db_memory), RoleEnum.ADMIN)  # ALSO GROUP_MEMBER
    
    # GROUP_CREATOR 
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None,           userid=1,        groupid=group_id_1,     editid=1),    db_session=db_memory), RoleEnum.GROUP_CREATOR)  # ALSO EDIT_CREATOR


