from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from api.models.database.model import OccupiedSlot, Slot

"""CRUD Operationen"""

def create(song_id: int, start_time: float, end_time: float, database_session: Session) -> Slot:
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
    slot = database_session.query(Slot).filter(Slot.slot_id == slot_id).one_or_none()
    if not slot:
        raise NoResultFound(f"Slot with ID {slot_id} not found.")
    return slot

def update(slot_id: int, start_time: float = None, end_time: float = None, database_session: Session = None) -> Slot:
    slot = database_session.query(Slot).filter(Slot.slot_id == slot_id).one_or_none()
    if not slot:
        raise NoResultFound(f"Slot with ID {slot_id} not found.")
    
    if start_time is not None:
        slot.start_time = start_time
    if end_time is not None:
        slot.end_time = end_time
    database_session.commit()
    database_session.refresh(slot)
    return slot

def remove(slot_id: int, database_session: Session) -> None:
    slot = database_session.query(Slot).filter(Slot.slot_id == slot_id).one_or_none()
    if not slot:
        raise NoResultFound(f"Slot with ID {slot_id} not found.")
    database_session.delete(slot)
    database_session.commit()

"""Andere Operationen"""

def get_slots_for_edit(edit_id: int, database_session: Session):
    """
    Gibt die Liste der Slots zurück, die mit der angegebenen edit_id verknüpft sind.
    Wenn keine Slots gefunden werden, wird eine NoResultFound Exception geworfen.
    """
    slots = database_session.query(Slot).filter(Slot.song_id == edit_id).all()
    
    if not slots:
        raise NoResultFound(f"No slots found for edit ID {edit_id}")
    
    return slots

def get_slot_by_occupied_slot_id(occupied_slot_id: int, database_session: Session) -> Slot:
    """
    Gibt den Slot zurück, der mit der angegebenen occupied_slot_id verknüpft ist.
    Wenn kein Slot oder keine OccupiedSlot gefunden wird, wird eine NoResultFound Exception geworfen.
    """
    # Finde den OccupiedSlot
    occupied_slot = database_session.query(OccupiedSlot).filter(OccupiedSlot.occupied_slot_id == occupied_slot_id).one_or_none()
    
    if not occupied_slot:
        raise NoResultFound(f"OccupiedSlot with ID {occupied_slot_id} not found.")
    
    # Finde den zugehörigen Slot
    slot = database_session.query(Slot).filter(Slot.slot_id == occupied_slot.slot_id).one_or_none()
    
    if not slot:
        raise NoResultFound(f"Slot linked to OccupiedSlot ID {occupied_slot_id} not found.")
    
    return slot

