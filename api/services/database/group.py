from sqlalchemy.orm import Session
from api.models.database.model import Group, User, Edit
from api.utils.database.create_uuid import create_uuid

def create(
        name: str, 
        db: Session) -> Group:
    
    new_group = Group(
        group_id=create_uuid(),
        name=name
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

def get(group_id: str, db: Session) -> Group:
    return db.query(Group).filter(Group.group_id == group_id).first()

def is_group_member(user_id: int, group_id: str, db: Session) -> bool:
    user = db.query(User).filter(User.user_id == user_id, User.group_id == group_id).first()
    return user is not None

def is_group_creator(user_id: int, group_id: str, db: Session) -> bool:
    user = db.query(User).filter(User.user_id == user_id, User.group_id == group_id).first()
    if user and user.role == "creator":
        return True
    return False

def remove(group_id: str, db: Session) -> bool:
    group = db.query(Group).filter(Group.group_id == group_id).first()
    if group:
        db.delete(group)
        db.commit()
        return True
    return False

def list_members(group_id: str, db: Session):
    return db.query(User).filter(User.group_id == group_id).all()

def get_group_by_edit_id(edit_id: str, db: Session) -> Group:
    return db.query(Group).join(Edit).filter(Edit.edit_id == edit_id).first()

def get_group_by_user_id(user_id: int, db: Session) -> Group:
    # Retrieve the user based on the user_id
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if user:
        # If the user exists, fetch the group associated with that user
        return db.query(Group).filter(Group.group_id == user.group_id).first()
    
    return None  # Return None if the user does not exist