from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from api.models.schema.group import (DeleteResponse, GetMembersResponse,
                                     GetResponse, GetRoleResponse,
                                     GroupExistsResponse, PostRequest,
                                     PostResponse)
from api.services.database.group import create as create_group_service
from api.services.database.group import get as get_group_service
from api.services.database.group import \
    is_group_member as is_group_member_group_service
from api.services.database.group import \
    list_members as list_members_groud_service
from api.services.database.group import remove as remove_group_service
from api.services.database.user import create as create_user_service
from api.services.database.user import get as get_user_service
from api.sessions.database import get_database_session
from api.utils.jwt.jwt import create_jwt, read_jwt

router = APIRouter(
    prefix="/group",
)    

@router.post("/", response_model=PostResponse, tags=["group"])
async def create(request: PostRequest = Body(...), database_session: Session = Depends(get_database_session)): 
    # Erstelle die Gruppe
    new_group = create_group_service(name=request.groupname, database_session=database_session)

    if not new_group:
        raise HTTPException(status_code=400, detail="Group creation failed")

    # Erstelle einen neuen Benutzer mit den übergebenen Daten
    new_user = create_user_service(
        group_id=new_group.group_id,  # group_id der neu erstellten Gruppe verwenden
        role="creator",  # Standardrolle für neue Benutzer
        name=request.username,
        email=request.email,
        database_session=database_session
    )

    # Erstelle ein JWT mit der Benutzer-ID
    jwt_token = create_jwt(user_id=new_user.user_id, expires_in_minutes=30)

    # Rückgabe der Antwort mit der neuen Gruppen-ID, dem Namen und dem JWT-Token
    return PostResponse(group_id=new_group.group_id, name=new_group.name, jwt=jwt_token)   
 
@router.delete("/{group_id}", response_model=DeleteResponse, tags=["group"])
async def delete(group_id: str, database_session: Session = Depends(get_database_session)):
    # Überprüfen, ob die Gruppe existiert und entfernen
    success = remove_group_service(group_id, database_session)

    if not success:
        raise HTTPException(status_code=404, detail="Group not found or could not be deleted")
    
    return DeleteResponse(message="Group successfully deleted")

@router.get("/{group_id}", response_model=GetResponse, tags=["group"])
async def get(group_id: str, database_session: Session = Depends(get_database_session)):
    group = get_group_service(group_id=group_id, database_session=database_session)
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return group

# Hole die Rolle des Benutzers in der Gruppe
@router.get("/{group_id}/role", response_model=GetRoleResponse, tags=["group"])
async def get_role(group_id: str, request: Request, database_session: Session = Depends(get_database_session)):
    # Extrahiere den JWT-Token aus den Headern
    jwt_token = request.headers.get('Authorization').replace("Bearer ", "")
    
    # Lese die Benutzer-ID aus dem JWT-Token
    user_id = read_jwt(jwt_token)

    if is_group_member_group_service(user_id=user_id, group_id=group_id, database_session=database_session):
        user = get_user_service(user_id, database_session)
        return {"role": user.role}
    else:
        raise HTTPException(status_code=404, detail="User not a member of this group")
        
@router.get("/{group_id}/groupExists", response_model=GroupExistsResponse, tags=["group"])
async def group_exist(group_id: str, database_session: Session = Depends(get_database_session)):
    # Überprüfen, ob die Gruppe existiert
    group = get_group_service(group_id=group_id, database_session=database_session)
    
    if group:
        return {"exists":True}
    
    return {"exists":False}

@router.get("/{group_id}/listMembers", response_model=GetMembersResponse, tags=["group"])
async def list_members(group_id: str, database_session: Session = Depends(get_database_session)):
    # Liste der Mitglieder der Gruppe abrufen
    members = list_members_groud_service(group_id=group_id, database_session=database_session)
    
    if not members:
        raise HTTPException(status_code=404, detail="No members found for this group")

    return {"members":members}
    
    
