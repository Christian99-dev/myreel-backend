import pytest
from sqlalchemy.exc import IntegrityError
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
    invalid_song_id = 9999
    start_time = 0.0
    end_time = 1.0

    # Act & Assert
    with pytest.raises(IntegrityError):
        create(song_id=invalid_song_id, start_time=start_time, end_time=end_time, database_session=memory_database_session)

def test_create_edgecase_zero_duration(memory_database_session: Session):
    # Arrange
    song_id = 1
    start_time = 0.0
    end_time = 0.0  # Startzeit und Endzeit sind gleich (null Dauer)

    # Act
    new_slot = create(song_id=song_id, start_time=start_time, end_time=end_time, database_session=memory_database_session)

    # Assert
    assert new_slot is not None
    assert new_slot.start_time == 0.0
    assert new_slot.end_time == 0.0

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

    # Act
    fetched_slot = get(invalid_slot_id, memory_database_session)

    # Assert
    assert fetched_slot is None

def test_get_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_slot_id = 0

    # Act
    fetched_slot = get(zero_slot_id, memory_database_session)

    # Assert
    assert fetched_slot is None

# Update Tests
def test_update_success(memory_database_session: Session):
    # Arrange
    existing_slot = data["slots"][0]
    new_start_time = 1.5
    new_end_time = 2.0

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

    # Act
    updated_slot = update(slot_id=invalid_slot_id, start_time=new_start_time, database_session=memory_database_session)

    # Assert
    assert updated_slot is None

def test_update_edgecase_no_changes(memory_database_session: Session):
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
    result = remove(existing_slot.slot_id, memory_database_session)

    # Assert
    assert result is True
    assert memory_database_session.query(Slot).filter_by(slot_id=existing_slot.slot_id).one_or_none() is None

def test_remove_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_slot_id = 9999

    # Act
    result = remove(invalid_slot_id, memory_database_session)

    # Assert
    assert result is False

def test_remove_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_slot_id = 0

    # Act
    result = remove(zero_slot_id, memory_database_session)

    # Assert
    assert result is False

"""Andere Operationen"""

# get_slots_for_edit Tests
def test_get_slots_for_edit_success(memory_database_session: Session):
    # Arrange
    edit_id = 1  # Ein gültiger Edit mit Slots

    # Act
    slots = get_slots_for_edit(edit_id=edit_id, database_session=memory_database_session)

    # Assert
    assert len(slots) > 0

def test_get_slots_for_edit_invalid_edit(memory_database_session: Session):
    # Arrange
    invalid_edit_id = 9999

    # Act
    slots = get_slots_for_edit(edit_id=invalid_edit_id, database_session=memory_database_session)

    # Assert
    assert len(slots) == 0

# get_slot_by_occupied_slot_id Tests
def test_get_slot_by_occupied_slot_id_success(memory_database_session: Session):
    # Arrange
    occupied_slot_id = 1  # Ein gültiger OccupiedSlot

    # Act
    slot = get_slot_by_occupied_slot_id(occupied_slot_id=occupied_slot_id, database_session=memory_database_session)

    # Assert
    assert slot is not None

def test_get_slot_by_occupied_slot_id_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_occupied_slot_id = 9999

    # Act
    slot = get_slot_by_occupied_slot_id(occupied_slot_id=invalid_occupied_slot_id, database_session=memory_database_session)

    # Assert
    assert slot is None

def test_get_slot_by_occupied_slot_id_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_occupied_slot_id = 0

    # Act
    slot = get_slot_by_occupied_slot_id(occupied_slot_id=zero_occupied_slot_id, database_session=memory_database_session)

    # Assert
    assert slot is None

"""Integration"""

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
    result = remove(slot_id, memory_database_session)
    
    # Assert: Überprüfe, ob der Slot erfolgreich gelöscht wurde
    assert result is True
    slot = memory_database_session.query(Slot).filter_by(slot_id=slot_id).one_or_none()
    assert slot is None

    # Überprüfen, dass alle zugehörigen OccupiedSlots gelöscht wurden
    occupied_slots = memory_database_session.query(OccupiedSlot).filter_by(slot_id=slot_id).all()
    assert len(occupied_slots) == 0