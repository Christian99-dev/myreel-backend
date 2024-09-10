from sqlalchemy.orm import Session
from api.models.database.model import OccupiedSlot

def create(
        user_id: int, 
        slot_id: int, 
        edit_id: int, 
        video_src: str, 
        database_session: Session) -> OccupiedSlot:
    
    new_occupied_slot = OccupiedSlot(
        user_id=user_id,
        slot_id=slot_id,
        edit_id=edit_id,
        video_src=video_src
    )
    database_session.add(new_occupied_slot)
    database_session.commit()
    database_session.refresh(new_occupied_slot)
    return new_occupied_slot

def get(occupied_slot_id: int, database_session: Session) -> OccupiedSlot:
    return database_session.query(OccupiedSlot).filter(OccupiedSlot.occupied_slot_id == occupied_slot_id).first()

def remove(occupied_slot_id: int, database_session: Session) -> bool:
    occupied_slot = database_session.query(OccupiedSlot).filter(OccupiedSlot.occupied_slot_id == occupied_slot_id).first()
    if occupied_slot:
        database_session.delete(occupied_slot)
        database_session.commit()
        return True
    return False

def get_occupied_slots_for_edit(edit_id: int, database_session: Session):
    return database_session.query(OccupiedSlot).filter(OccupiedSlot.edit_id == edit_id).all()

def is_slot_occupied(slot_id: int, edit_id: int, database_session: Session):
    # Abrufen aller belegten Slots für die gegebene edit_id
    occupied_slots = database_session.query(OccupiedSlot).filter(OccupiedSlot.edit_id == edit_id).all()
    
    # Überprüfen, ob der angegebene slot_id belegt ist
    return any(slot.slot_id == slot_id for slot in occupied_slots)

def update(
        database_session: Session,
        occupied_slot_id: int, 
        user_id: int = None, 
        slot_id: int = None, 
        edit_id: int = None, 
        video_src: str = None, 
) -> OccupiedSlot:
    
    # Suche nach dem zu aktualisierenden OccupiedSlot
    occupied_slot = database_session.query(OccupiedSlot).filter(OccupiedSlot.occupied_slot_id == occupied_slot_id).first()

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
        database_session.commit()
        database_session.refresh(occupied_slot)
    
    return occupied_slot