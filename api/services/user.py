from sqlalchemy.orm import Session
from api.models.database.model import User

def create(
        group_id: str, 
        role: str, 
        name: str, 
        email: str, 
        db: Session) -> User:
    
    new_user = User(
        group_id=group_id,
        role=role,
        name=name,
        email=email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get(user_id: int, db: Session) -> User:
    return db.query(User).filter(User.user_id == user_id).first()