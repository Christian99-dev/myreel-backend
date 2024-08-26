from sqlalchemy.orm import Session
from api.models.database.model import Slot

def create(
        song_id: int, 
        start_time: float, 
        end_time: float, 
        db: Session) -> Slot:
    
    new_slot = Slot(
        song_id=song_id,
        start_time=start_time,
        end_time=end_time
    )
    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)
    return new_slot

def get(slot_id: int, db: Session) -> Slot:
    return db.query(Slot).filter(Slot.slot_id == slot_id).first()