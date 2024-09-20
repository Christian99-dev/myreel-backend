from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from api.models.database.model import Edit, Group, User
from api.utils.database.create_uuid import create_uuid

"""CRUD Operationen"""

def create(name: str, database_session: Session) -> Group:
    new_group = Group(
        group_id=create_uuid(),
        name=name
    )
    database_session.add(new_group)
    database_session.commit()
    database_session.refresh(new_group)
    return new_group

def get(group_id: str, database_session: Session) -> Group:
    group = database_session.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        raise NoResultFound(f"Group with ID {group_id} not found")
    return group

def update(group_id: str, name: str, database_session: Session) -> Group:
    group = database_session.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        raise NoResultFound(f"Group with ID {group_id} not found")
    group.name = name
    database_session.commit()
    database_session.refresh(group)
    return group

def remove(group_id: str, database_session: Session) -> None:
    group = database_session.query(Group).filter(Group.group_id == group_id).first()
    if not group:
        raise NoResultFound(f"Group with ID {group_id} not found")
    database_session.delete(group)
    database_session.commit()

"""Andere Operationen"""

def is_group_member(user_id: int, group_id: str, database_session: Session) -> bool:
    return database_session.query(User).filter(User.user_id == user_id, User.group_id == group_id).count() > 0

def is_group_creator(user_id: int, group_id: str, database_session: Session) -> bool:
    user = database_session.query(User).filter(User.user_id == user_id, User.group_id == group_id).first()
    if not user:
        raise NoResultFound(f"User with ID {user_id} not found in group {group_id}")
    return user.role == "creator"

def list_members(group_id: str, database_session: Session):
    members = database_session.query(User).filter(User.group_id == group_id).all()
    if not members:
        raise NoResultFound(f"No members found for group ID {group_id}")
    return members

def get_group_by_edit_id(edit_id: str, database_session: Session) -> Group:
    group = database_session.query(Group).join(Edit).filter(Edit.edit_id == edit_id).first()
    if not group:
        raise NoResultFound(f"Group for edit ID {edit_id} not found")
    return group

def get_group_by_user_id(user_id: int, database_session: Session) -> Group:
    user = database_session.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise NoResultFound(f"Group for user ID {user_id} not found")
    return database_session.query(Group).filter(Group.group_id == user.group_id).first()

def get_group_creator(group_id: str, database_session: Session) -> User:
    # Suche den ersten Edit in der Gruppe, um den Ersteller zu finden
    creator = (
        database_session.query(User)
        .join(Edit, Edit.created_by == User.user_id)
        .filter(Edit.group_id == group_id)
        .first()
    )
    
    if not creator:
        raise NoResultFound(f"No creator found for group ID {group_id}")
    
    return creator