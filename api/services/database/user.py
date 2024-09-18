from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from api.models.database.model import User

"""CRUD Operationen"""

def create(group_id: str, role: str, name: str, email: str, database_session: Session) -> User:
    new_user = User(
        group_id=group_id,
        role=role,
        name=name,
        email=email
    )
    database_session.add(new_user)
    database_session.commit()
    database_session.refresh(new_user)
    return new_user

def get(user_id: int, database_session: Session) -> User:
    user = database_session.query(User).filter(User.user_id == user_id).one_or_none()
    if not user:
        raise NoResultFound(f"User with ID {user_id} not found.")
    return user

def update(user_id: int, group_id: str = None, role: str = None, name: str = None, email: str = None, database_session: Session = None) -> User:
    user = database_session.query(User).filter(User.user_id == user_id).one_or_none()
    if not user:
        raise NoResultFound(f"User with ID {user_id} not found.")
    if group_id is not None:
        user.group_id = group_id
    if role is not None:
        user.role = role
    if name is not None:
        user.name = name
    if email is not None:
        user.email = email
    database_session.commit()
    database_session.refresh(user)
    return user

def remove(user_id: int, database_session: Session) -> None:
    user = database_session.query(User).filter(User.user_id == user_id).one_or_none()
    if not user:
        raise NoResultFound(f"User with ID {user_id} not found.")
    database_session.delete(user)
    database_session.commit()

"""Andere Operationen"""

def get_user_by_email(email: str, database_session: Session) -> User:
    user = database_session.query(User).filter(User.email == email).one_or_none()
    if not user:
        raise NoResultFound(f"User with email {email} not found.")
    return user
