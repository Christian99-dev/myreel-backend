from datetime import datetime, timedelta
import secrets
from sqlalchemy.orm import Session
from api.models.database.model import LoginRequest

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