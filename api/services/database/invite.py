import secrets
from datetime import datetime, timedelta

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from api.models.database.model import Invitation

"""CRUD Operationen"""

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

def get(invitation_id: int, database_session: Session) -> Invitation:
    invitation = database_session.query(Invitation).filter(Invitation.invitation_id == invitation_id).one_or_none()
    if not invitation:
        raise NoResultFound(f"Invitation with ID {invitation_id} not found")
    return invitation

def update(invitation_id: int, email: str = None, expires_in_days: int = None, database_session: Session = None) -> Invitation:
    invitation = database_session.query(Invitation).filter(Invitation.invitation_id == invitation_id).first()
    if not invitation:
        raise NoResultFound(f"Invitation with ID {invitation_id} not found")

    if email is not None:
        invitation.email = email
    
    if expires_in_days is not None:
        invitation.expires_at = datetime.now() + timedelta(days=expires_in_days)

    database_session.commit()
    database_session.refresh(invitation)
    return invitation

def remove(invitation_id: int, database_session: Session) -> None:
    invitation = database_session.query(Invitation).filter(Invitation.invitation_id == invitation_id).first()
    if not invitation:
        raise NoResultFound(f"Invitation with ID {invitation_id} not found")

    database_session.delete(invitation)
    database_session.commit()

"""Andere Operationen"""

def remove_all_by_email_and_group_id(email: str, group_id: str, database_session: Session) -> None:
    invitations_to_delete = database_session.query(Invitation).filter(
        Invitation.email == email,
        Invitation.group_id == group_id
    ).all()
    
    if not invitations_to_delete:
        raise NoResultFound(f"No invitations found with email {email} in group {group_id}")

    for invitation in invitations_to_delete:
        database_session.delete(invitation)
    
    database_session.commit()
