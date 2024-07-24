from datetime import datetime, timedelta
import secrets
from sqlalchemy.orm import Session
from api.models.database.model import Invitation

def create(group_id: str, email: str, db: Session, expires_in_days: int = 7) -> Invitation:
    token = secrets.token_urlsafe(16)
    created_at = datetime.now()
    expires_at = created_at + timedelta(days=expires_in_days)
    
    new_invitation = Invitation(
        group_id=group_id,
        token=token,
        email=email,
        created_at=created_at,
        expires_at=expires_at
    )
    
    db.add(new_invitation)
    db.commit()
    db.refresh(new_invitation)
    return new_invitation

def delete(invitation_id: int, db: Session) -> None:
    invitation = db.query(Invitation).filter(Invitation.invitation_id == invitation_id).first()
    
    if invitation:
        db.delete(invitation)
        db.commit()
