import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from api.models.database.model import LoginRequest, User


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

def delete(user_id: int, database_session: Session) -> None:
    login_request = database_session.query(LoginRequest).filter(LoginRequest.user_id == user_id).first()
    
    if login_request:
        database_session.delete(login_request)
        database_session.commit()
        
def delete_all_from_email(email: str, database_session: Session) -> None:
    # Suche den Benutzer anhand der E-Mail-Adresse
    user = database_session.query(User).filter(User.email == email).first()

    if user:
        # Lösche alle LoginRequests für diesen Benutzer
        database_session.query(LoginRequest).filter(LoginRequest.user_id == user.user_id).delete()
        database_session.commit()
        
def get_login_request_by_groupid_and_token(groupid: str, token: str, database_session: Session) -> LoginRequest:
    return database_session.query(LoginRequest).join(User).filter(
        User.group_id == groupid,
        LoginRequest.pin == token
    ).first()