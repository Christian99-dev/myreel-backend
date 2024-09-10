from sqlalchemy.orm import Session
from api.models.database.model import Slot, OccupiedSlot

def create(
        song_id: int, 
        start_time: float, 
        end_time: float, 
        database_session: Session) -> Slot:
    
    new_slot = Slot(
        song_id=song_id,
        start_time=start_time,
        end_time=end_time
    )
    database_session.add(new_slot)
    database_session.commit()
    database_session.refresh(new_slot)
    return new_slot

def get(slot_id: int, database_session: Session) -> Slot:
    return database_session.query(Slot).filter(Slot.slot_id == slot_id).first()

def remove(slot_id: int, database_session: Session) -> bool:
    slot = database_session.query(Slot).filter(Slot.slot_id == slot_id).first()
    if slot:
        database_session.delete(slot)
        database_session.commit()
        return True
    return False

def get_slots_for_edit(edit_id: int, database_session: Session):
    return database_session.query(Slot).filter(Slot.song_id == edit_id).all()

def get_slot_by_occupied_slot_id(occupied_slot_id: int, database_session: Session) -> Slot:
    # Suche nach dem OccupiedSlot mit der angegebenen occupied_slot_id
    occupied_slot = database_session.query(OccupiedSlot).filter(OccupiedSlot.occupied_slot_id == occupied_slot_id).first()
    
    # Falls ein OccupiedSlot gefunden wurde, den zugehörigen Slot abrufen
    if occupied_slot:
        return database_session.query(Slot).filter(Slot.slot_id == occupied_slot.slot_id).first()
    
    # Falls kein entsprechender Slot gefunden wurde, None zurückgeben
    return None