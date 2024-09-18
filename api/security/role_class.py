import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from api.config.endpoints import EndpointInfo
from api.security.role_enum import RoleEnum
from api.services.database.edit import is_edit_creator
from api.services.database.group import (get_group_by_edit_id,
                                         is_group_creator, is_group_member)

load_dotenv()

class RoleInfos(BaseModel):
    admintoken: Optional[str]
    userid:     Optional[int]
    groupid:    Optional[str]
    editid:     Optional[int]

class Role:
    def __init__(self, 
                 role_infos: RoleInfos,
                 database_session: Optional[Session] = None
    ):  
        roles = [RoleEnum.EXTERNAL]
        admintoken = role_infos.admintoken
        userid = role_infos.userid
        groupid = role_infos.groupid
        editid = role_infos.editid
        
        # ADMIN
        if admintoken is not None and admintoken == os.getenv("ADMIN_TOKEN"):
            roles.append(RoleEnum.ADMIN)
        
        # GROUP MEMBER ODER CREATOR
        if userid is not None and groupid is not None and database_session is not None:
            try:
                if is_group_member(userid, groupid, database_session):
                    roles.append(RoleEnum.GROUP_MEMBER)
            except NoResultFound:  # Abfangen der NoResultFound Exception
                pass  # Ignoriere den Fehler, falls kein Gruppenmitglied gefunden wird
            
            try:
                if is_group_creator(userid, groupid, database_session):
                    roles.append(RoleEnum.GROUP_CREATOR)
            except NoResultFound:
                pass  # Ignoriere den Fehler, falls kein Gruppenersteller gefunden wird
        
        # Prüfen, ob die Edit-ID zu einer Gruppe gehört (falls noch keine Gruppenmitgliedschaft/Erstellung existiert)
        if (RoleEnum.GROUP_MEMBER not in roles and 
            RoleEnum.GROUP_CREATOR not in roles and 
            editid is not None and 
            groupid is None and 
            userid is not None and 
            database_session is not None):
            try:
                group_found_via_editid = get_group_by_edit_id(editid, database_session)
                
                # Wenn eine Gruppe gefunden wurde, prüfen, ob der Nutzer Mitglied oder Ersteller ist
                try:
                    if is_group_member(userid, group_found_via_editid.group_id, database_session):
                        roles.append(RoleEnum.GROUP_MEMBER)
                except NoResultFound:
                    pass  # Ignoriere den Fehler, falls kein Gruppenmitglied gefunden wird
                
                try:
                    if is_group_creator(userid, group_found_via_editid.group_id, database_session):
                        roles.append(RoleEnum.GROUP_CREATOR)
                except NoResultFound:
                    pass  # Ignoriere den Fehler, falls kein Gruppenersteller gefunden wird
            except NoResultFound:
                pass  # Ignoriere den Fehler, falls keine Gruppe für die Edit-ID gefunden wird
        
        # GROUP EDIT CREATOR
        if userid is not None and editid is not None and database_session is not None:
            try:
                if is_edit_creator(userid, editid, database_session):
                    roles.append(RoleEnum.EDIT_CREATOR)
            except NoResultFound:
                pass  # Ignoriere den Fehler, falls kein Edit-Ersteller gefunden wird
        
        # Setze die minimale Rolle basierend auf den hinzugefügten Rollen
        self._role = min(roles, key=lambda role: role.value)    

    def hasAccess(self, pathInfo: EndpointInfo) -> bool:
        has_subroles = pathInfo.has_subroles
        role         = pathInfo.role
        
        if has_subroles:
            if self._role.value <= role.value:
                return True
            else:
                return False
        else:   
            return self._role.value == role.value