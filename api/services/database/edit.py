from typing import List
from sqlalchemy.orm import Session
from api.models.database.model import Edit, OccupiedSlot, Slot
from sqlalchemy import func


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

def are_all_slots_occupied(edit_id: int, db: Session) -> bool:
    # Finde den Edit
    edit = db.query(Edit).filter(Edit.edit_id == edit_id).first()
    if not edit:
        return False  # Edit existiert nicht

    # Anzahl der Slots, die zu dem Song des Edits gehören
    total_slots = db.query(Slot).filter(Slot.song_id == edit.song_id).count()

    # Anzahl der belegten Slots für diesen Edit
    occupied_slots_count = db.query(func.count(OccupiedSlot.slot_id)).filter(OccupiedSlot.edit_id == edit_id).scalar()

    # Überprüfen, ob alle Slots belegt sind
    return total_slots == occupied_slots_count

def set_is_live(edit_id: int, db: Session) -> bool:
    # Find the Edit by edit_id
    edit = db.query(Edit).filter(Edit.edit_id == edit_id).first()
    
    if not edit:
        # If the Edit does not exist, return False
        return False
    
    # Fetch all slots associated with the song_id in this edit
    slots = db.query(Slot).filter(Slot.song_id == edit.song_id).all()
    
    # Fetch all occupied slots associated with this edit_id
    occupied_slots = db.query(OccupiedSlot).filter(OccupiedSlot.edit_id == edit_id).all()
    
    # Check if all slots are occupied
    occupied_slot_ids = {occupied.slot_id for occupied in occupied_slots}
    all_slots_occupied = all(slot.slot_id in occupied_slot_ids for slot in slots)
    
    if all_slots_occupied:
        # If all slots are occupied, set the edit to live
        edit.isLive = True
        db.commit()  # Save the changes to the database
        return True
    
    return False

def update(
        edit_id: int, 
        name: str = None, 
        is_live: bool = None, 
        video_src: str = None, 
        db: Session = None) -> Edit:
    
    # Fetch the existing Edit by edit_id
    edit = db.query(Edit).filter(Edit.edit_id == edit_id).first()
    
    if not edit:
        # If the Edit does not exist, return None
        return None
    
    # Update the fields that are provided
    if name is not None:
        edit.name = name
    if is_live is not None:
        edit.isLive = is_live
    if video_src is not None:
        edit.video_src = video_src
    
    # Commit the changes to the database
    db.commit()
    db.refresh(edit)  # Refresh the instance to get the updated data
    
    return edit

def get_edits_by_group(group_id: str, db: Session) -> List[Edit]:
    edits = db.query(Edit).filter(Edit.group_id == group_id).all()
    return edits