from sqlalchemy.orm import Session
from api.models.database.model import Group, User

def create(
        name: str, 
        db: Session) -> Group:
    
    new_group = Group(
        name=name
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

def get(group_id: int, db: Session) -> Group:
    return db.query(Group).filter(Group.group_id == group_id).first()

def is_group_creator(user_id: int, group_id: int, db: Session) -> bool:
    user = db.query(User).filter(User.user_id == user_id, User.group_id == group_id).first()
    if user and user.role == "creator":
        return True
    return False
