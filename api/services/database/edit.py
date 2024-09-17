from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from api.models.database.model import Edit, OccupiedSlot, Slot

"""CRUD Operationen"""

def create(
        song_id: int, 
        created_by: int, 
        group_id: str, 
        name: str, 
        is_live: bool, 
        video_src: str,
        database_session: Session) -> Edit:
    
    new_edit = Edit(
        song_id=song_id,
        created_by=created_by,
        group_id=group_id,
        name=name,
        isLive=is_live,
        video_src=video_src
    )
    database_session.add(new_edit)
    database_session.commit()
    database_session.refresh(new_edit)
    return new_edit

def get(edit_id: int, database_session: Session) -> Edit:
    return database_session.query(Edit).filter(Edit.edit_id == edit_id).first()

def update(
        edit_id: int, 
        name: str = None, 
        is_live: bool = None, 
        video_src: str = None, 
        database_session: Session = None) -> Edit:
    
    edit = database_session.query(Edit).filter(Edit.edit_id == edit_id).first()
    
    if not edit:
        return None
    
    if name is not None:
        edit.name = name
    if is_live is not None:
        edit.isLive = is_live
    if video_src is not None:
        edit.video_src = video_src
    
    database_session.commit()
    database_session.refresh(edit)
    
    return edit

def remove(edit_id: int, database_session: Session) -> bool:
    edit = database_session.query(Edit).filter(Edit.edit_id == edit_id).first()
    if edit:
        database_session.delete(edit)
        database_session.commit()
        return True
    return False

"""Andere Operationen"""

def is_edit_creator(user_id: int, edit_id: int, database_session: Session) -> bool:
    edit = database_session.query(Edit).filter(Edit.edit_id == edit_id).first()
    if edit and edit.created_by == user_id:
        return True
    return False

def are_all_slots_occupied(edit_id: int, database_session: Session) -> bool:
    edit = database_session.query(Edit).filter(Edit.edit_id == edit_id).first()
    if not edit:
        return False

    total_slots = database_session.query(Slot).filter(Slot.song_id == edit.song_id).count()

    occupied_slots_count = database_session.query(func.count(OccupiedSlot.slot_id)).filter(OccupiedSlot.edit_id == edit_id).scalar()

    return total_slots == occupied_slots_count

def set_is_live(edit_id: int, database_session: Session) -> bool:
    edit = database_session.query(Edit).filter(Edit.edit_id == edit_id).first()
    
    if not edit:
        return False
    
    slots = database_session.query(Slot).filter(Slot.song_id == edit.song_id).all()
    
    occupied_slots = database_session.query(OccupiedSlot).filter(OccupiedSlot.edit_id == edit_id).all()
    
    occupied_slot_ids = {occupied.slot_id for occupied in occupied_slots}
    all_slots_occupied = all(slot.slot_id in occupied_slot_ids for slot in slots)
    
    if all_slots_occupied:
        edit.isLive = True
        database_session.commit()
        return True
    
    return False

def get_edits_by_group(group_id: str, database_session: Session) -> List[Edit]:
    edits = database_session.query(Edit).filter(Edit.group_id == group_id).all()
    return edits
