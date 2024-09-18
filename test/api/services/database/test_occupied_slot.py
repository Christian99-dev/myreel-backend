import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models.database.model import OccupiedSlot, Slot
from api.services.database.occupied_slot import (create, get,
                                                 get_occupied_slots_for_edit,
                                                 is_slot_occupied, remove,
                                                 update)
from mock.database.data import data

"""CRUD Operationen"""

# Create Tests
def test_create_success(memory_database_session: Session):
    # Arrange
    user_id = 1
    slot_id = 1
    edit_id = 1
    video_src = "http://example.com/new_video.mp4"

    # Act
    new_occupied_slot = create(user_id=user_id, slot_id=slot_id, edit_id=edit_id, video_src=video_src, database_session=memory_database_session)

    # Assert
    assert new_occupied_slot is not None
    assert new_occupied_slot.user_id == user_id
    assert new_occupied_slot.slot_id == slot_id
    assert new_occupied_slot.edit_id == edit_id
    assert new_occupied_slot.video_src == video_src

def test_create_invalid_user(memory_database_session: Session):
    # Arrange
    invalid_user_id = 9999
    slot_id = 1
    edit_id = 1
    video_src = "http://example.com/new_video.mp4"

    # Act & Assert
    with pytest.raises(IntegrityError):
        create(user_id=invalid_user_id, slot_id=slot_id, edit_id=edit_id, video_src=video_src, database_session=memory_database_session)

def test_create_edgecase_empty_video_src(memory_database_session: Session):
    # Arrange
    user_id = 1
    slot_id = 1
    edit_id = 1
    video_src = ""  # Leerer video_src

    # Act
    new_occupied_slot = create(user_id=user_id, slot_id=slot_id, edit_id=edit_id, video_src=video_src, database_session=memory_database_session)

    # Assert
    assert new_occupied_slot is not None
    assert new_occupied_slot.video_src == ""  # Leerer video_src sollte akzeptiert werden

# Get Tests
def test_get_success(memory_database_session: Session):
    # Arrange
    existing_occupied_slot = data["occupied_slots"][0]

    # Act
    fetched_occupied_slot = get(existing_occupied_slot["occupied_slot_id"], memory_database_session)

    # Assert
    assert fetched_occupied_slot is not None
    assert fetched_occupied_slot.occupied_slot_id == existing_occupied_slot["occupied_slot_id"]

def test_get_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_occupied_slot_id = 9999

    # Act
    fetched_occupied_slot = get(invalid_occupied_slot_id, memory_database_session)

    # Assert
    assert fetched_occupied_slot is None

def test_get_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_occupied_slot_id = 0

    # Act
    fetched_occupied_slot = get(zero_occupied_slot_id, memory_database_session)

    # Assert
    assert fetched_occupied_slot is None

# Update Tests
def test_update_success(memory_database_session: Session):
    # Arrange
    existing_occupied_slot = data["occupied_slots"][0]
    new_video_src = "http://example.com/updated_video.mp4"

    # Act
    updated_occupied_slot = update(occupied_slot_id=existing_occupied_slot["occupied_slot_id"], video_src=new_video_src, database_session=memory_database_session)

    # Assert
    assert updated_occupied_slot is not None
    assert updated_occupied_slot.video_src == new_video_src

def test_update_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_occupied_slot_id = 9999
    new_video_src = "http://example.com/updated_video.mp4"

    # Act
    updated_occupied_slot = update(occupied_slot_id=invalid_occupied_slot_id, video_src=new_video_src, database_session=memory_database_session)

    # Assert
    assert updated_occupied_slot is None

def test_update_edgecase_empty_video_src(memory_database_session: Session):
    # Arrange
    existing_occupied_slot = data["occupied_slots"][0]
    new_video_src = ""  # Leerer video_src

    # Act
    updated_occupied_slot = update(occupied_slot_id=existing_occupied_slot["occupied_slot_id"], video_src=new_video_src, database_session=memory_database_session)

    # Assert
    assert updated_occupied_slot is not None
    assert updated_occupied_slot.video_src == ""  # Leerer video_src sollte akzeptiert werden

# Remove Tests
def test_remove_success(memory_database_session: Session):
    # Arrange
    existing_occupied_slot = memory_database_session.query(OccupiedSlot).first()

    # Act
    result = remove(existing_occupied_slot.occupied_slot_id, memory_database_session)

    # Assert
    assert result is True
    assert memory_database_session.query(OccupiedSlot).filter_by(occupied_slot_id=existing_occupied_slot.occupied_slot_id).one_or_none() is None

def test_remove_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_occupied_slot_id = 9999

    # Act
    result = remove(invalid_occupied_slot_id, memory_database_session)

    # Assert
    assert result is False

def test_remove_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_occupied_slot_id = 0

    # Act
    result = remove(zero_occupied_slot_id, memory_database_session)

    # Assert
    assert result is False

"""Andere Operationen"""

# get_occupied_slots_for_edit Tests
def test_get_occupied_slots_for_edit_success(memory_database_session: Session):
    # Arrange
    edit_id = 1  # Ein gültiger Edit mit OccupiedSlots

    # Act
    occupied_slots = get_occupied_slots_for_edit(edit_id=edit_id, database_session=memory_database_session)

    # Assert
    assert len(occupied_slots) > 0

def test_get_occupied_slots_for_edit_invalid_edit(memory_database_session: Session):
    # Arrange
    invalid_edit_id = 9999

    # Act
    occupied_slots = get_occupied_slots_for_edit(edit_id=invalid_edit_id, database_session=memory_database_session)

    # Assert
    assert len(occupied_slots) == 0

# is_slot_occupied Tests
def test_is_slot_occupied_success(memory_database_session: Session):
    # Arrange
    slot_id = 1
    edit_id = 1  # Ein gültiger Edit, der den Slot belegt

    # Act
    result = is_slot_occupied(slot_id=slot_id, edit_id=edit_id, database_session=memory_database_session)

    # Assert
    assert result is True

def test_is_slot_occupied_failure(memory_database_session: Session):
    # Arrange
    slot_id = 1
    invalid_edit_id = 9999  # Ungültiger Edit

    # Act
    result = is_slot_occupied(slot_id=slot_id, edit_id=invalid_edit_id, database_session=memory_database_session)

    # Assert
    assert result is False

def test_is_slot_occupied_edgecase_no_occupied_slots(memory_database_session: Session):
    # Arrange
    slot_id = 1
    edit_id = 2  # Edit hat keine belegten Slots

    # Act
    result = is_slot_occupied(slot_id=slot_id, edit_id=edit_id, database_session=memory_database_session)

    # Assert
    assert result is False
