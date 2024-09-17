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
    return database_session.query(Group).filter(Group.group_id == group_id).first()

def update(group_id: str, name: str, database_session: Session) -> Group:
    group = database_session.query(Group).filter(Group.group_id == group_id).first()
    if group:
        group.name = name
        database_session.commit()
        database_session.refresh(group)
    return group

def remove(group_id: str, database_session: Session) -> bool:
    group = database_session.query(Group).filter(Group.group_id == group_id).first()
    if group:
        database_session.delete(group)
        database_session.commit()
        return True
    return False

"""Andere Operationen"""

def is_group_member(user_id: int, group_id: str, database_session: Session) -> bool:
    user = database_session.query(User).filter(User.user_id == user_id, User.group_id == group_id).first()
    return user is not None

def is_group_creator(user_id: int, group_id: str, database_session: Session) -> bool:
    user = database_session.query(User).filter(User.user_id == user_id, User.group_id == group_id).first()
    return user is not None and user.role == "creator"

def list_members(group_id: str, database_session: Session):
    return database_session.query(User).filter(User.group_id == group_id).all()

def get_group_by_edit_id(edit_id: str, database_session: Session) -> Group:
    return database_session.query(Group).join(Edit).filter(Edit.edit_id == edit_id).first()

def get_group_by_user_id(user_id: int, database_session: Session) -> Group:
    user = database_session.query(User).filter(User.user_id == user_id).first()
    if user:
        return database_session.query(Group).filter(Group.group_id == user.group_id).first()
    return None
