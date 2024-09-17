from sqlalchemy.orm import Session

from api.models.database.model import OccupiedSlot

"""CRUD Operationen"""

def create(user_id: int, slot_id: int, edit_id: int, video_src: str, database_session: Session) -> OccupiedSlot:
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

def update(occupied_slot_id: int, database_session: Session, user_id: int = None, slot_id: int = None, edit_id: int = None, video_src: str = None) -> OccupiedSlot:
    occupied_slot = database_session.query(OccupiedSlot).filter(OccupiedSlot.occupied_slot_id == occupied_slot_id).first()
    if occupied_slot:
        if user_id is not None:
            occupied_slot.user_id = user_id
        if slot_id is not None:
            occupied_slot.slot_id = slot_id
        if edit_id is not None:
            occupied_slot.edit_id = edit_id
        if video_src is not None:
            occupied_slot.video_src = video_src
        database_session.commit()
        database_session.refresh(occupied_slot)
    return occupied_slot

def remove(occupied_slot_id: int, database_session: Session) -> bool:
    occupied_slot = database_session.query(OccupiedSlot).filter(OccupiedSlot.occupied_slot_id == occupied_slot_id).first()
    if occupied_slot:
        database_session.delete(occupied_slot)
        database_session.commit()
        return True
    return False

"""Andere Operationen"""

def get_occupied_slots_for_edit(edit_id: int, database_session: Session):
    return database_session.query(OccupiedSlot).filter(OccupiedSlot.edit_id == edit_id).all()

def is_slot_occupied(slot_id: int, edit_id: int, database_session: Session):
    occupied_slots = database_session.query(OccupiedSlot).filter(OccupiedSlot.edit_id == edit_id).all()
    return any(slot.slot_id == slot_id for slot in occupied_slots)
