from sqlalchemy.orm import Session
from api.models.database.model import Group

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
