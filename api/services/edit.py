from sqlalchemy.orm import Session
from api.models.database.models import Edit

def create(
        song_id: int, 
        created_by: int, 
        group_id: int, 
        name: str, 
        is_live: bool, 
        db: Session) -> Edit:
    
    new_edit = Edit(
        song_id=song_id,
        created_by=created_by,
        group_id=group_id,
        name=name,
        isLive=is_live
    )
    db.add(new_edit)
    db.commit()
    db.refresh(new_edit)
    return new_edit

def get(edit_id: int, db: Session) -> Edit:
    return db.query(Edit).filter(Edit.edit_id == edit_id).first()
