from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from api.models.schema.user import (AcceptInviteRequest, AcceptInviteResponse,
                                    InviteRequest, InviteResponse,
                                    LoginRequest, LoginRequestRequest,
                                    LoginRequestResponse, LoginResponse)
from api.services.database.invite import create as create_invite_service
from api.services.database.invite import remove as delete_invite_service
from api.services.database.invite import \
    remove_all_by_email as remove_all_by_email_invite_service
from api.services.database.invite import get as get_invite_service
from api.services.database.login import create as create_loging_service
from api.services.database.login import remove as remove_loging_service
from api.services.database.login import get_login_request_by_groupid_and_token
from api.services.database.user import create as create_user_service
from api.services.database.user import get as get_user_service
from api.services.database.user import get_user_by_email
from api.services.email.invite import invite as email_invite_service
from api.services.email.login import login as email_login_service
from api.sessions.database import get_database_session
from api.sessions.email import BaseEmailSessionManager, get_email_session
from api.utils.jwt.jwt import create_jwt

router = APIRouter(
    prefix="/user",
)    

         
@router.post("/invite", response_model=InviteResponse, tags=["user"])
async def invite(request: InviteRequest = Body(...), database_session: Session = Depends(get_database_session), email_session: BaseEmailSessionManager = Depends(get_email_session)): 
    try: 
        # erstelle einen invite mit dem service 
        new_invite = create_invite_service(request.groupid, request.email, database_session=database_session)
        
        # sende eine email raus mit dem servi
        if email_invite_service(request.email, new_invite.token, new_invite.invitation_id, request.groupid, email_session): 
            return {"message" : "Invite successfull"}
        else:
            raise HTTPException(status_code=400, detail="Email konnte nicht gesendet werden")    
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))    
         
         
@router.post("/acceptInvite", response_model=AcceptInviteResponse,   tags=["user"])
async def acceptInvite(request: AcceptInviteRequest = Body(...), database_session: Session = Depends(get_database_session)):
    
    invite = get_invite_service(request.invitationid, database_session=database_session)
    
    # checke ob invite da ist 
    if invite is None: 
        raise HTTPException(status_code=400, detail="Keine Einlandung vorhanden")    
        
    if invite.token != request.token:
        raise HTTPException(status_code=400, detail="Einlandungstoken falsch")    

    if invite.expires_at < datetime.now():  # Überprüfe, ob das Ablaufdatum in der Vergangenheit liegt
        raise HTTPException(status_code=400, detail="Einladungstoken abgelaufen")
        
    # erstelle user für diese gruppe
    new_user = create_user_service(request.groupid, "member", request.name, email=invite.email, database_session=database_session)
    
    jwt = create_jwt(new_user.user_id, 30)
    
    # lösche invite
    delete_invite_service(invitation_id=invite.invitation_id, database_session=database_session)
    
    # lösche alle die noch da sind mit diesem user
    remove_all_by_email_invite_service(email=invite.email, database_session=database_session)
    
    return {"jwt": jwt}
    
    
@router.post("/loginRequest", response_model=LoginRequestResponse,tags=["user"])
async def loginRequest(request: LoginRequestRequest = Body(...), database_session: Session = Depends(get_database_session), email_session: BaseEmailSessionManager = Depends(get_email_session)):
    
    user = get_user_by_email(request.email, database_session=database_session)
    if user is None:
        raise HTTPException(status_code=400, detail="User gibt es nicht") 

    if user.group_id != request.groupid:
        raise HTTPException(status_code=400, detail="Gruppe nicht Nutzer angehörig")  
        
        
    remove_loging_service(user.user_id, database_session=database_session)
    new_login_request = create_loging_service(user.user_id, expires_in_minutes=10, database_session=database_session)

    email_login_service(user.email, new_login_request.pin, email_session)
    
    return {"message": "email wurde versendet"}

        
@router.post("/login", response_model=LoginResponse, tags=["user"])
async def login(request: LoginRequest = Body(...), database_session: Session = Depends(get_database_session)):
    # Verwende den Service, um die LoginRequest basierend auf groupid und token zu finden
    login_request = get_login_request_by_groupid_and_token(request.groupid, request.token, database_session)
    
    if login_request is None:
        raise HTTPException(status_code=400, detail="Ungültiger Token oder Gruppe")

    if login_request.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Login-Anfrage ist abgelaufen")

    user = get_user_service(login_request.user_id, database_session=database_session)

    if user is None:
        raise HTTPException(status_code=400, detail="Benutzer nicht gefunden")

    jwt = create_jwt(user.user_id, 30)
    remove_loging_service(user.user_id, database_session=database_session)

    return {"jwt": jwt, "user_id": user.user_id, "name":user.name }

