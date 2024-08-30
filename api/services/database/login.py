from datetime import datetime, timedelta
import secrets
from sqlalchemy.orm import Session
from api.models.database.model import LoginRequest, User

def create(user_id: int, db: Session, expires_in_minutes: int = 10) -> LoginRequest:
    pin = secrets.token_urlsafe(4)
    created_at = datetime.now()
    expires_at = created_at + timedelta(minutes=expires_in_minutes)
    
    new_login_request = LoginRequest(
        user_id=user_id,
        pin=pin,
        created_at=created_at,
        expires_at=expires_at
    )
    
    db.add(new_login_request)
    db.commit()
    db.refresh(new_login_request)
    return new_login_request

def delete(user_id: int, db: Session) -> None:
    login_request = db.query(LoginRequest).filter(LoginRequest.user_id == user_id).first()
    
    if login_request:
        db.delete(login_request)
        db.commit()
        
def delete_all_from_email(email: str, db: Session) -> None:
    # Suche den Benutzer anhand der E-Mail-Adresse
    user = db.query(User).filter(User.email == email).first()

    if user:
        # Lösche alle LoginRequests für diesen Benutzer
        db.query(LoginRequest).filter(LoginRequest.user_id == user.user_id).delete()
        db.commit()
        
def get_login_request_by_groupid_and_token(groupid: str, token: str, db: Session) -> LoginRequest:
    return db.query(LoginRequest).join(User).filter(
        User.group_id == groupid,
        LoginRequest.pin == token
    ).first()