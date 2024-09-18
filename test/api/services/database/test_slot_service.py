import pytest
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from api.models.database.model import OccupiedSlot, Slot
from api.services.database.slot import (create, get,
                                        get_slot_by_occupied_slot_id,
                                        get_slots_for_edit, remove, update)
from mock.database.data import data

"""CRUD Operationen"""

# Create Tests
def test_create_success(memory_database_session: Session):
    # Arrange
    song_id = 1
    start_time = 0.0
    end_time = 1.0
    
    # Act
    new_slot = create(song_id=song_id, start_time=start_time, end_time=end_time, database_session=memory_database_session)
    
    # Assert
    assert new_slot is not None
    assert new_slot.song_id == song_id
    assert new_slot.start_time == start_time
    assert new_slot.end_time == end_time

def test_create_invalid_song(memory_database_session: Session):
    # Arrange
    invalid_song_id = 9999  # Song ID doesn't exist
    start_time = 0.0
    end_time = 1.0
    
    # Act & Assert
    with pytest.raises(IntegrityError):
        create(song_id=invalid_song_id, start_time=start_time, end_time=end_time, database_session=memory_database_session)

def test_create_edgecase_zero_duration(memory_database_session: Session):
    # Arrange
    song_id = 1
    start_time = 1.0
    end_time = 1.0  # Startzeit und Endzeit sind gleich
    
    # Act
    new_slot = create(song_id=song_id, start_time=start_time, end_time=end_time, database_session=memory_database_session)
    
    # Assert
    assert new_slot is not None
    assert new_slot.start_time == 1.0
    assert new_slot.end_time == 1.0  # Null-Dauer sollte akzeptiert werden

# Get Tests
def test_get_success(memory_database_session: Session):
    # Arrange
    existing_slot = data["slots"][0]
    
    # Act
    fetched_slot = get(existing_slot["slot_id"], memory_database_session)
    
    # Assert
    assert fetched_slot is not None
    assert fetched_slot.slot_id == existing_slot["slot_id"]

def test_get_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_slot_id = 9999
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get(invalid_slot_id, memory_database_session)

def test_get_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_slot_id = 0
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get(zero_slot_id, memory_database_session)

# Update Tests
def test_update_success(memory_database_session: Session):
    # Arrange
    existing_slot = data["slots"][0]
    new_start_time = 1.5
    new_end_time = 2.5
    
    # Act
    updated_slot = update(slot_id=existing_slot["slot_id"], start_time=new_start_time, end_time=new_end_time, database_session=memory_database_session)
    
    # Assert
    assert updated_slot is not None
    assert updated_slot.start_time == new_start_time
    assert updated_slot.end_time == new_end_time

def test_update_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_slot_id = 9999
    new_start_time = 1.5
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        update(slot_id=invalid_slot_id, start_time=new_start_time, database_session=memory_database_session)

def test_update_no_changes(memory_database_session: Session):
    # Arrange
    existing_slot = data["slots"][0]
    
    # Act
    updated_slot = update(slot_id=existing_slot["slot_id"], database_session=memory_database_session)  # Keine Änderungen
    
    # Assert
    assert updated_slot is not None
    assert updated_slot.start_time == existing_slot["start_time"]
    assert updated_slot.end_time == existing_slot["end_time"]

# Remove Tests
def test_remove_success(memory_database_session: Session):
    # Arrange
    existing_slot = memory_database_session.query(Slot).first()
    
    # Act
    remove(existing_slot.slot_id, memory_database_session)
    
    # Assert
    with pytest.raises(NoResultFound):
        get(existing_slot.slot_id, memory_database_session)

def test_remove_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_slot_id = 9999
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        remove(invalid_slot_id, memory_database_session)

def test_remove_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_slot_id = 0
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        remove(zero_slot_id, memory_database_session)


"""Andere Operationen"""

# get_slots_for_edit Tests
def test_get_slots_for_edit_success(memory_database_session: Session):
    # Arrange
    edit_id = 1  # Song ID is the same as edit ID for mock data purposes
    
    # Act
    slots = get_slots_for_edit(edit_id, memory_database_session)
    
    # Assert
    assert len(slots) > 0

def test_get_slots_for_edit_no_slots(memory_database_session: Session):
    # Arrange
    edit_id = 9999  # No slots associated with this edit
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get_slots_for_edit(edit_id, memory_database_session)

def test_get_slots_for_edit_invalid_edit(memory_database_session: Session):
    # Arrange
    invalid_edit_id = 9999
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get_slots_for_edit(invalid_edit_id, memory_database_session)

# get_slot_by_occupied_slot_id Tests
def test_get_slot_by_occupied_slot_id_success(memory_database_session: Session):
    # Arrange
    occupied_slot_id = 1  # Ein gültiger occupied_slot
    
    # Act
    slot = get_slot_by_occupied_slot_id(occupied_slot_id, memory_database_session)
    
    # Assert
    assert slot is not None

def test_get_slot_by_occupied_slot_id_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_occupied_slot_id = 9999
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get_slot_by_occupied_slot_id(invalid_occupied_slot_id, memory_database_session)

def test_get_slot_by_occupied_slot_id_no_occupied_slot(memory_database_session: Session):
    # Arrange
    occupied_slot_id = 9999  # Invalid OccupiedSlot ID
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get_slot_by_occupied_slot_id(occupied_slot_id, memory_database_session)


"""Integration - CRUD"""

def test_integration_crud_slot(memory_database_session: Session):
    # Create a slot
    new_slot = create(song_id=1, start_time=0.0, end_time=1.0, database_session=memory_database_session)
    assert new_slot is not None

    # Update the slot
    updated_slot = update(slot_id=new_slot.slot_id, start_time=0.5, end_time=1.5, database_session=memory_database_session)
    assert updated_slot is not None
    assert updated_slot.start_time == 0.5
    assert updated_slot.end_time == 1.5

    # Fetch the slot and check the updated times
    fetched_slot = get(slot_id=new_slot.slot_id, database_session=memory_database_session)
    assert fetched_slot is not None
    assert fetched_slot.start_time == 0.5
    assert fetched_slot.end_time == 1.5

    # Remove the slot
    remove(new_slot.slot_id, memory_database_session)

    # Ensure the slot no longer exists
    with pytest.raises(NoResultFound):
        get(new_slot.slot_id, memory_database_session)


"""Integration - Cascading"""

def test_cascade_delete_slot_with_occupied_slots(memory_database_session: Session):
    # Arrange: Wir löschen einen Slot und erwarten, dass alle zugehörigen OccupiedSlots gelöscht werden.
    slot_id = 1  # Dieser Slot hat zugehörige OccupiedSlots
    
    # Überprüfen, dass der Slot existiert
    slot = memory_database_session.query(Slot).filter_by(slot_id=slot_id).one_or_none()
    assert slot is not None
    
    # Überprüfen, dass zugehörige OccupiedSlots existieren
    occupied_slots = memory_database_session.query(OccupiedSlot).filter_by(slot_id=slot_id).all()
    assert len(occupied_slots) > 0
    
    # Act: Lösche den Slot
    remove(slot_id, memory_database_session)
    
    # Assert: Überprüfe, ob der Slot erfolgreich gelöscht wurde
    with pytest.raises(NoResultFound):
        get(slot_id, memory_database_session)

    # Überprüfen, dass alle zugehörigen OccupiedSlots gelöscht wurden
    occupied_slots = memory_database_session.query(OccupiedSlot).filter_by(slot_id=slot_id).all()
    assert len(occupied_slots) == 0
