from typing import List

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from api.models.database.model import OccupiedSlot

"""CRUD Operationen"""

def create(user_id: int, slot_id: int, edit_id: int, video_src: str, start_time: float, end_time: float, database_session: Session) -> OccupiedSlot:
    new_occupied_slot = OccupiedSlot(
        user_id=user_id,
        slot_id=slot_id,
        edit_id=edit_id,
        video_src=video_src,
        start_time=start_time,
        end_time=end_time
    )
    database_session.add(new_occupied_slot)
    database_session.commit()
    database_session.refresh(new_occupied_slot)
    return new_occupied_slot

def get(occupied_slot_id: int, database_session: Session) -> OccupiedSlot:
    occupied_slot = database_session.query(OccupiedSlot).filter(OccupiedSlot.occupied_slot_id == occupied_slot_id).one_or_none()
    if not occupied_slot:
        raise NoResultFound(f"Occupied slot with ID {occupied_slot_id} not found.")
    return occupied_slot

def update(occupied_slot_id: int, database_session: Session, user_id: int = None, slot_id: int = None, edit_id: int = None, video_src: str = None, start_time: float = None, end_time: float = None) -> OccupiedSlot:
    occupied_slot = database_session.query(OccupiedSlot).filter(OccupiedSlot.occupied_slot_id == occupied_slot_id).one_or_none()
    if not occupied_slot:
        raise NoResultFound(f"Occupied slot with ID {occupied_slot_id} not found.")

    if user_id is not None:
        occupied_slot.user_id = user_id
    if slot_id is not None:
        occupied_slot.slot_id = slot_id
    if edit_id is not None:
        occupied_slot.edit_id = edit_id
    if video_src is not None:
        occupied_slot.video_src = video_src
    if start_time is not None:
        occupied_slot.start_time = start_time
    if end_time is not None:
        occupied_slot.end_time = end_time
    database_session.commit()
    database_session.refresh(occupied_slot)
    return occupied_slot

def remove(occupied_slot_id: int, database_session: Session) -> None:
    occupied_slot = database_session.query(OccupiedSlot).filter(OccupiedSlot.occupied_slot_id == occupied_slot_id).one_or_none()
    if not occupied_slot:
        raise NoResultFound(f"Occupied slot with ID {occupied_slot_id} not found.")
    database_session.delete(occupied_slot)
    database_session.commit()

"""Andere Operationen"""

def get_occupied_slots_for_edit(edit_id: int, database_session: Session)-> List[OccupiedSlot]:
    occupied_slots = database_session.query(OccupiedSlot).filter(OccupiedSlot.edit_id == edit_id).all()
    
    if not occupied_slots:
        raise NoResultFound(f"No occupied slots found for edit ID {edit_id}")
    
    return occupied_slots

def is_slot_occupied(slot_id: int, edit_id: int, database_session: Session) -> bool:
    occupied_slots = database_session.query(OccupiedSlot).filter(OccupiedSlot.edit_id == edit_id).all()
    
    if not occupied_slots:
        raise NoResultFound(f"No occupied slots found for edit ID {edit_id}")
    
    return any(slot.slot_id == slot_id for slot in occupied_slots)