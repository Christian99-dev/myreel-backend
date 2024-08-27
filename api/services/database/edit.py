from sqlalchemy.orm import Session
from api.models.database.model import Edit

def create(
        song_id: int, 
        created_by: int, 
        group_id: str, 
        name: str, 
        is_live: bool, 
        video_src: str,
        db: Session) -> Edit:
    
    new_edit = Edit(
        song_id=song_id,
        created_by=created_by,
        group_id=group_id,
        name=name,
        isLive=is_live,
        video_src=video_src
    )
    db.add(new_edit)
    db.commit()
    db.refresh(new_edit)
    return new_edit

def get(edit_id: int, db: Session) -> Edit:
    return db.query(Edit).filter(Edit.edit_id == edit_id).first()

def is_edit_creator(user_id: int, edit_id: int, db: Session) -> bool:
    edit = db.query(Edit).filter(Edit.edit_id == edit_id).first()
    if edit and edit.created_by == user_id:
        return True
    return False

def remove(edit_id: int, db: Session) -> bool:
    edit = db.query(Edit).filter(Edit.edit_id == edit_id).first()
    if edit:
        db.delete(edit)
        db.commit()
        return True
    return False