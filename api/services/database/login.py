import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from api.models.database.model import LoginRequest, User

"""CRUD Operationen"""

def create(user_id: int, database_session: Session, expires_in_minutes: int = 10) -> LoginRequest:
    pin = secrets.token_urlsafe(4)
    created_at = datetime.now()
    expires_at = created_at + timedelta(minutes=expires_in_minutes)
    
    new_login_request = LoginRequest(
        user_id=user_id,
        pin=pin,
        created_at=created_at,
        expires_at=expires_at
    )
    database_session.add(new_login_request)
    database_session.commit()
    database_session.refresh(new_login_request)
    return new_login_request

def get(user_id: int, database_session: Session) -> LoginRequest:
    return database_session.query(LoginRequest).filter(LoginRequest.user_id == user_id).first()

def update(user_id: int, pin: str, expires_in_minutes: int, database_session: Session) -> LoginRequest:
    login_request = database_session.query(LoginRequest).filter(LoginRequest.user_id == user_id).first()
    if login_request:
        login_request.pin = pin
        login_request.expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
        database_session.commit()
        database_session.refresh(login_request)
    return login_request

def remove(user_id: int, database_session: Session) -> bool:
    login_request = database_session.query(LoginRequest).filter(LoginRequest.user_id == user_id).first()
    if login_request:
        database_session.delete(login_request)
        database_session.commit()
        return True
    return False

"""Andere Operationen"""

def delete_all_from_email(email: str, database_session: Session) -> None:
    user = database_session.query(User).filter(User.email == email).first()
    if user:
        database_session.query(LoginRequest).filter(LoginRequest.user_id == user.user_id).delete()
        database_session.commit()

def get_login_request_by_groupid_and_token(groupid: str, token: str, database_session: Session) -> LoginRequest:
    return database_session.query(LoginRequest).join(User).filter(
        User.group_id == groupid,
        LoginRequest.pin == token
    ).first()
