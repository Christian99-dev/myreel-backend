import logging
from datetime import datetime

from click import group
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from api.models.schema.user import (AcceptInviteRequest, AcceptInviteResponse,
                                    InviteRequest, InviteResponse,
                                    LoginRequest, LoginRequestRequest,
                                    LoginRequestResponse, LoginResponse)
from api.services.database.group import get as get_group_database
from api.services.database.invite import create as create_invite_database
from api.services.database.invite import get as get_invite_database
from api.services.database.invite import \
    remove_all_by_email_and_group_id as \
    remove_all_by_email_and_group_id_invite_database
from api.services.database.login import \
    create_or_update as create_or_update_login_database
from api.services.database.login import \
    get_login_request_by_groupid_and_email as \
    get_login_request_by_groupid_and_email_database
from api.services.database.login import remove as remove_login_database
from api.services.database.user import create as create_user_database
from api.services.database.user import get as get_user_database
from api.services.database.user import \
    get_user_by_email_and_group_id as get_user_by_email_and_group_id_database
from api.services.email.invite import invite as invite_email
from api.services.email.login import login as login_email
from api.sessions.database import get_database_session
from api.sessions.email import BaseEmailSessionManager, get_email_session
from api.utils.jwt.jwt import create_jwt

logger = logging.getLogger("routes.user")

router = APIRouter(
    prefix="/user",
)    
         
@router.post("/invite", response_model=InviteResponse, tags=["user"])
async def invite(request: InviteRequest = Body(...), database_session: Session = Depends(get_database_session), email_session: BaseEmailSessionManager = Depends(get_email_session)): 
    # erstelle einen invite mit dem service 
    new_invite = create_invite_database(request.groupid, request.email, database_session=database_session)
    
    # sende eine email raus mit dem servi
    invite_email(request.email, new_invite.token, new_invite.invitation_id, request.groupid, email_session)
        
    return {"message" : "Invite successfull"}
         
         
@router.post("/acceptInvite", response_model=AcceptInviteResponse,   tags=["user"])
async def acceptInvite(request: AcceptInviteRequest = Body(...), database_session: Session = Depends(get_database_session)):
    
    # sollte einen fehler feuern, wenn es die gruppe nicht gibt
    get_group_database(request.groupid, database_session=database_session)

    # hole invite
    invite = get_invite_database(request.invitationid, database_session=database_session)
         
    if invite.token != request.token:
        raise HTTPException(status_code=400, detail="Einlandungstoken falsch")    

    if invite.expires_at < datetime.now():  # Überprüfe, ob das Ablaufdatum in der Vergangenheit liegt
        raise HTTPException(status_code=400, detail="Einladungstoken abgelaufen")
        
    # erstelle user für diese gruppe
    new_user = create_user_database(request.groupid, "member", request.name, email=invite.email, database_session=database_session)
    
    # jwt für den nutzer, nutzer kann sich aber auch über login einen token holen
    jwt = create_jwt(new_user.user_id, 130)
    
    # lösche alle die noch da sind mit diesem user
    remove_all_by_email_and_group_id_invite_database(email=invite.email, group_id=request.groupid, database_session=database_session)
    
    return {"jwt": jwt}
    
    
@router.post("/loginRequest", response_model=LoginRequestResponse,tags=["user"])
async def loginRequest(request: LoginRequestRequest = Body(...), database_session: Session = Depends(get_database_session), email_session: BaseEmailSessionManager = Depends(get_email_session)):
    
    # hole user
    user = get_user_by_email_and_group_id_database(request.email, request.groupid, database_session=database_session)
    
    # create or update
    new_login_request = create_or_update_login_database(user.user_id, expires_in_minutes=10, database_session=database_session)
    
    # email raussenden
    login_email(user.email, new_login_request.pin, email_session)
    
    return {"message": "email wurde versendet"}

        
@router.post("/login", response_model=LoginResponse, tags=["user"])
async def login(request: LoginRequest = Body(...), database_session: Session = Depends(get_database_session)):
    
    # Verwende den Service, um die LoginRequest basierend auf groupid und token zu finden
    login_request = get_login_request_by_groupid_and_email_database(request.groupid, request.email, database_session)
    
    # user holen
    user = get_user_database(login_request.user_id, database_session=database_session)
    
    # checks
    if login_request.pin != request.pin:
        raise HTTPException(status_code=400, detail="Ungültiger Token")

    if login_request.expires_at < datetime.now():
        remove_login_database(user.user_id, database_session=database_session)
        raise HTTPException(status_code=400, detail="Login-Anfrage ist abgelaufen")

    # jwt für user
    jwt = create_jwt(user.user_id, 130)
    
    # login request löschen
    remove_login_database(user.user_id, database_session=database_session)

    return {"jwt": jwt, "user_id": user.user_id, "name":user.name }

