import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from api.models.database.model import Invitation


def create(group_id: str, email: str, database_session: Session, expires_in_days: int = 7) -> Invitation:
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
    
    database_session.add(new_invitation)
    database_session.commit()
    database_session.refresh(new_invitation)
    return new_invitation

def delete(invitation_id: int, database_session: Session) -> None:
    invitation = database_session.query(Invitation).filter(Invitation.invitation_id == invitation_id).first()
    
    if invitation:
        database_session.delete(invitation)
        database_session.commit()
        
def get(invitation_id: int, db_session: Session) -> Invitation:
    return db_session.query(Invitation).filter(Invitation.invitation_id == invitation_id).one_or_none()

def delete_all_by_email(email: str, database_session: Session) -> None:
    # Finde alle Einladungen mit der angegebenen E-Mail
    invitations_to_delete = database_session.query(Invitation).filter(Invitation.email == email).all()

    for invitation in invitations_to_delete:
        database_session.delete(invitation)  # Lösche jede gefundene Einladung

    database_session.commit()  # Commit für die Löschvorgänge