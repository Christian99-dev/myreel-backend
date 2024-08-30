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

def get_occupied_slots_for_edit(edit_id: int, db: Session):
    return db.query(OccupiedSlot).filter(OccupiedSlot.edit_id == edit_id).all()

def is_slot_occupied(slot_id: int, edit_id: int, db: Session):
    # Abrufen aller belegten Slots für die gegebene edit_id
    occupied_slots = db.query(OccupiedSlot).filter(OccupiedSlot.edit_id == edit_id).all()
    
    # Überprüfen, ob der angegebene slot_id belegt ist
    return any(slot.slot_id == slot_id for slot in occupied_slots)

def update(
        db: Session,
        occupied_slot_id: int, 
        user_id: int = None, 
        slot_id: int = None, 
        edit_id: int = None, 
        video_src: str = None, 
) -> OccupiedSlot:
    
    # Suche nach dem zu aktualisierenden OccupiedSlot
    occupied_slot = db.query(OccupiedSlot).filter(OccupiedSlot.occupied_slot_id == occupied_slot_id).first()

    # Falls der OccupiedSlot existiert, aktualisiere die Felder
    if occupied_slot:
        if user_id is not None:
            occupied_slot.user_id = user_id
        if slot_id is not None:
            occupied_slot.slot_id = slot_id
        if edit_id is not None:
            occupied_slot.edit_id = edit_id
        if video_src is not None:
            occupied_slot.video_src = video_src

        # Änderungen in der Datenbank speichern
        db.commit()
        db.refresh(occupied_slot)
    
    return occupied_slot