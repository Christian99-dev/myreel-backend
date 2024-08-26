from sqlalchemy.orm import Session
from api.models.database.model import OccupiedSlot

def create(
        user_id: int, 
        slot_id: int, 
        edit_id: int, 
        video_src: str, 
        db: Session) -> OccupiedSlot:
    
    new_occupied_slot = OccupiedSlot(
        user_id=user_id,
        slot_id=slot_id,
        edit_id=edit_id,
        video_src=video_src
    )
    db.add(new_occupied_slot)
    db.commit()
    db.refresh(new_occupied_slot)
    return new_occupied_slot

def get(occupied_slot_id: int, db: Session) -> OccupiedSlot:
    return db.query(OccupiedSlot).filter(OccupiedSlot.occupied_slot_id == occupied_slot_id).first()

def remove(occupied_slot_id: int, db: Session) -> bool:
    occupied_slot = db.query(OccupiedSlot).filter(OccupiedSlot.occupied_slot_id == occupied_slot_id).first()
    if occupied_slot:
        db.delete(occupied_slot)
        db.commit()
        return True
    return False
