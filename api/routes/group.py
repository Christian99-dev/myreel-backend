import logging

from fastapi import APIRouter, Body, Depends, Header
from sqlalchemy.orm import Session

from api.models.schema.group import (DeleteResponse, GetResponse,
                                     GroupNameResponse, PostRequest,
                                     PostResponse)
from api.services.database.edit import get_edits_by_group
from api.services.database.group import create as create_group_service
from api.services.database.group import get as get_group_service
from api.services.database.group import \
    list_members as list_members_groud_service
from api.services.database.group import remove as remove_group_service
from api.services.database.user import create as create_user_service
from api.services.database.user import get as get_user_service
from api.sessions.database import get_database_session
from api.utils.jwt.jwt import create_jwt, read_jwt

logger = logging.getLogger("routes.group")

router = APIRouter(
    prefix="/group",
)    

@router.post("/", response_model=PostResponse, tags=["group"])
async def create(request: PostRequest = Body(...), database_session: Session = Depends(get_database_session)): 
    # Erstelle die Gruppe
    new_group = create_group_service(name=request.groupname, database_session=database_session)

    # Erstelle einen neuen Benutzer mit den übergebenen Daten
    new_user = create_user_service(
        group_id=new_group.group_id,  # group_id der neu erstellten Gruppe verwenden
        role="creator",
        name=request.username,
        email=request.email,
        database_session=database_session
    )

    # Erstelle ein JWT mit der Benutzer-ID
    jwt_token = create_jwt(user_id=new_user.user_id, expires_in_minutes=30)

    # Rückgabe der Antwort mit der neuen Gruppen-ID, dem Namen und dem JWT-Token 
    return {
        "group_id":new_group.group_id,
        "jwt":jwt_token
    }   
 
@router.delete("/{group_id}", response_model=DeleteResponse, tags=["group"])
async def delete(group_id: str, database_session: Session = Depends(get_database_session)):
    # Überprüfen, ob die Gruppe existiert und entfernen
    remove_group_service(group_id, database_session)

    return {"message" : "Group successfully deleted"}

@router.get("/{group_id}/name", response_model=GroupNameResponse, tags=["group"])
async def group_name(group_id: str, database_session: Session = Depends(get_database_session)):
    group = get_group_service(group_id=group_id, database_session=database_session)

    return {"name":group.name}

@router.get("/{group_id}", response_model=GetResponse, tags=["group"])
async def get(group_id: str, authorization: str = Header(None), database_session: Session = Depends(get_database_session)):
    
    # group infos
    group = get_group_service(group_id=group_id, database_session=database_session)
    
    # user infos
    user_id = read_jwt(authorization.replace("Bearer ", ""))
    user = get_user_service(user_id, database_session=database_session)

    # get edits 
    edits = get_edits_by_group(group_id, database_session=database_session)
    
    # get members
    members = list_members_groud_service(group_id, database_session=database_session)

    return {
        "user" : {
            "id": user.user_id,
            "name": user.name,
            "role": user.role,
            "email" : user.email
        }, 
        "members" : [
            {
                "user_id" : member.user_id,
                "role" : member.role,
                "name" : member.name,
            }
            for member in members
        ], 
        "edits" : [
            {
                "edit_id" : edit.edit_id,
                "created_by" : edit.created_by,
                "name" : edit.name,
                "isLive" : edit.isLive
            }
            for edit in edits
        ], 
        "group_id" : group.group_id, 
        "group_name" : group.name
    }

        



    
