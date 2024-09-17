from sqlalchemy.orm import Session

from api.models.database.model import User


def create(
        group_id: str, 
        role: str, 
        name: str, 
        email: str, 
        database_session: Session) -> User:
    
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
    return database_session.query(User).filter(User.user_id == user_id).first()

def remove(user_id: int, database_session: Session) -> bool:
    user = database_session.query(User).filter(User.user_id == user_id).first()
    if user:
        database_session.delete(user)
        database_session.commit()
        return True
    return False

def get_user_by_email(email: str, database_session: Session) -> User:
    # Suche den Benutzer anhand der E-Mail-Adresse
    return database_session.query(User).filter(User.email == email).first()