import pytest
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from api.models.database.model import Edit, OccupiedSlot
from api.services.database.edit import (are_all_slots_occupied, create, get, get_earliest_slot_start_time_by_edit,
                                        get_edits_by_group, is_edit_creator,
                                        remove, set_is_live, update)
from mock.database.data import data

"""CRUD Operationen"""

# Create Tests
def test_create_success(memory_database_session: Session):
    # Arrange
    song_id = 1
    created_by = 1
    group_id = "11111111-1111-1111-1111-111111111111"
    name = "Test Edit"
    is_live = False
    video_src = "http://example.com/video.mp4"

    # Act
    new_edit = create(song_id=song_id, created_by=created_by, group_id=group_id, name=name, is_live=is_live, video_src=video_src, database_session=memory_database_session)

    # Assert
    assert new_edit is not None
    assert new_edit.song_id == song_id
    assert new_edit.created_by == created_by
    assert new_edit.group_id == group_id
    assert new_edit.name == name
    assert new_edit.isLive == is_live
    assert new_edit.video_src == video_src

def test_create_invalid_song_id(memory_database_session: Session):
    # Arrange
    invalid_song_id = 9999  # Invalid song ID
    created_by = 1
    group_id = "11111111-1111-1111-1111-111111111111"
    name = "Invalid Edit"
    is_live = False
    video_src = "http://example.com/video.mp4"

    # Act & Assert
    with pytest.raises(IntegrityError):
        create(song_id=invalid_song_id, created_by=created_by, group_id=group_id, name=name, is_live=is_live, video_src=video_src, database_session=memory_database_session)

def test_create_edgecase_empty_name(memory_database_session: Session):
    # Arrange
    song_id = 1
    created_by = 1
    group_id = "11111111-1111-1111-1111-111111111111"
    name = ""  # Empty name should be allowed
    is_live = False
    video_src = "http://example.com/video.mp4"

    # Act
    new_edit = create(song_id=song_id, created_by=created_by, group_id=group_id, name=name, is_live=is_live, video_src=video_src, database_session=memory_database_session)

    # Assert
    assert new_edit is not None
    assert new_edit.name == ""

# Get Tests
def test_get_success(memory_database_session: Session):
    # Arrange
    existing_edit = data["edits"][0]

    # Act
    fetched_edit = get(existing_edit["edit_id"], memory_database_session)

    # Assert
    assert fetched_edit is not None
    assert fetched_edit.edit_id == existing_edit["edit_id"]

def test_get_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_edit_id = 9999

    # Act & Assert
    with pytest.raises(NoResultFound):
        get(invalid_edit_id, memory_database_session)

def test_get_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_edit_id = 0

    # Act & Assert
    with pytest.raises(NoResultFound):
        get(zero_edit_id, memory_database_session)

# Update Tests
def test_update_success(memory_database_session: Session):
    # Arrange
    existing_edit = data["edits"][0]
    new_name = "Updated Edit Name"

    # Act
    updated_edit = update(edit_id=existing_edit["edit_id"], name=new_name, database_session=memory_database_session)

    # Assert
    assert updated_edit is not None
    assert updated_edit.name == new_name

def test_update_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_edit_id = 9999
    new_name = "Non-Existent Edit Update"

    # Act & Assert
    with pytest.raises(NoResultFound):
        update(edit_id=invalid_edit_id, name=new_name, database_session=memory_database_session)

def test_update_edgecase_empty_name(memory_database_session: Session):
    # Arrange
    existing_edit = data["edits"][0]
    new_name = ""  # Empty name

    # Act
    updated_edit = update(edit_id=existing_edit["edit_id"], name=new_name, database_session=memory_database_session)

    # Assert
    assert updated_edit is not None
    assert updated_edit.name == ""  # Empty name should be accepted

# Remove Tests
def test_remove_success(memory_database_session: Session):
    # Arrange
    existing_edit = memory_database_session.query(Edit).first()

    # Act
    remove(existing_edit.edit_id, memory_database_session)

    # Assert
    with pytest.raises(NoResultFound):
        get(existing_edit.edit_id, memory_database_session)

def test_remove_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_edit_id = 9999

    # Act & Assert
    with pytest.raises(NoResultFound):
        remove(invalid_edit_id, memory_database_session)

def test_remove_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_edit_id = 0

    # Act & Assert
    with pytest.raises(NoResultFound):
        remove(zero_edit_id, memory_database_session)

"""Andere Operationen"""

# is_edit_creator Tests
def test_is_edit_creator_success(memory_database_session: Session):
    # Arrange
    edit = data["edits"][0]

    # Act
    result = is_edit_creator(edit["created_by"], edit["edit_id"], memory_database_session)

    # Assert
    assert result is True

def test_is_edit_creator_invalid_edit(memory_database_session: Session):
    # Arrange
    invalid_edit_id = 9999

    # Act & Assert
    with pytest.raises(NoResultFound):
        is_edit_creator(user_id=1, edit_id=invalid_edit_id, database_session=memory_database_session)

def test_is_edit_creator_edgecase_wrong_user(memory_database_session: Session):
    # Arrange
    edit = data["edits"][0]
    wrong_user_id = 9999  # User not the creator

    # Act
    result = is_edit_creator(wrong_user_id, edit["edit_id"], memory_database_session)

    # Assert
    assert result is False

# are_all_slots_occupied Tests
def test_are_all_slots_occupied_success(memory_database_session: Session):
    # Arrange
    edit_id = 3  # All slots are occupied for this Edit

    # Act
    result = are_all_slots_occupied(edit_id=edit_id, database_session=memory_database_session)

    # Assert
    assert result is True

def test_are_all_slots_occupied_failure(memory_database_session: Session):
    # Arrange
    edit_id = 2  # Not all slots are occupied

    # Act
    result = are_all_slots_occupied(edit_id=edit_id, database_session=memory_database_session)

    # Assert
    assert result is False

def test_are_all_slots_occupied_invalid_edit(memory_database_session: Session):
    # Arrange
    invalid_edit_id = 9999

    # Act & Assert
    with pytest.raises(NoResultFound):
        are_all_slots_occupied(edit_id=invalid_edit_id, database_session=memory_database_session)

# set_is_live Tests
def test_set_is_live_success(memory_database_session: Session):
    # Arrange
    edit_id = 3  # All slots are occupied

    # Act
    set_is_live(edit_id, memory_database_session)

    # Assert
    assert memory_database_session.query(Edit).filter_by(edit_id=edit_id).one().isLive is True

def test_set_is_live_failure(memory_database_session: Session):
    # Arrange
    edit_id = 2  # Not all slots are occupied

    # Act & Assert
    with pytest.raises(Exception):
        set_is_live(edit_id, memory_database_session)

def test_set_is_live_invalid_edit(memory_database_session: Session):
    # Arrange
    invalid_edit_id = 9999

    # Act & Assert
    with pytest.raises(NoResultFound):
        set_is_live(edit_id=invalid_edit_id, database_session=memory_database_session)

# get_edits_by_group Tests
def test_get_edits_by_group_success(memory_database_session: Session):
    # Arrange
    group_id = "11111111-1111-1111-1111-111111111111"

    # Act
    edits = get_edits_by_group(group_id, memory_database_session)

    # Assert
    assert len(edits) > 0

def test_get_edits_by_group_invalid_group(memory_database_session: Session):
    # Arrange
    invalid_group_id = "99999999-9999-9999-9999-999999999999"

    # Act & Assert
    with pytest.raises(NoResultFound):
        get_edits_by_group(group_id=invalid_group_id, database_session=memory_database_session)

def test_get_edits_by_group_edgecase_empty_group(memory_database_session: Session):
    # Arrange
    empty_group_id = ""  # Invalid group ID

    # Act & Assert
    with pytest.raises(NoResultFound):
        get_edits_by_group(group_id=empty_group_id, database_session=memory_database_session)

# get_earliest_slot_start_time_by_edit
def test_get_earliest_slot_start_time_by_edit(memory_database_session: Session):
    assert get_earliest_slot_start_time_by_edit(1, memory_database_session) == 0
    assert get_earliest_slot_start_time_by_edit(2, memory_database_session) == 0
    assert get_earliest_slot_start_time_by_edit(3, memory_database_session) == 0.5

def test_get_earliest_slot_start_time_by_edit_not_found(memory_database_session: Session):
    with pytest.raises(NoResultFound):
        get_earliest_slot_start_time_by_edit(99, memory_database_session)

"""Integration - CRUD"""

def test_integration_crud_edit(memory_database_session: Session):
    # Create an edit
    new_edit = create(song_id=1, created_by=1, group_id="11111111-1111-1111-1111-111111111111", name="Test Edit", is_live=False, video_src="http://example.com/video.mp4", database_session=memory_database_session)
    assert new_edit is not None

    # Update the edit
    updated_edit = update(edit_id=new_edit.edit_id, name="Updated Test Edit", database_session=memory_database_session)
    assert updated_edit is not None
    assert updated_edit.name == "Updated Test Edit"

    # Fetch the edit and check the updated name
    fetched_edit = get(edit_id=new_edit.edit_id, database_session=memory_database_session)
    assert fetched_edit is not None
    assert fetched_edit.name == "Updated Test Edit"

    # Remove the edit
    remove(new_edit.edit_id, memory_database_session)

    # Ensure the edit no longer exists
    with pytest.raises(NoResultFound):
        get(new_edit.edit_id, memory_database_session)

"""Integration - Cascading"""

def test_cascade_delete_edit_with_occupied_slots(memory_database_session: Session):
    # Arrange: We delete an Edit and expect all associated OccupiedSlots to be deleted
    edit_id = 1  # Edit 1 has associated OccupiedSlots

    # Ensure the Edit exists
    edit = memory_database_session.query(Edit).filter_by(edit_id=edit_id).one_or_none()
    assert edit is not None

    # Ensure OccupiedSlots exist
    occupied_slots = memory_database_session.query(OccupiedSlot).filter_by(edit_id=edit_id).all()
    assert len(occupied_slots) > 0

    # Act: Delete the Edit
    remove(edit_id, memory_database_session)

    # Ensure the Edit is deleted
    with pytest.raises(NoResultFound):
        get(edit_id, memory_database_session)

    # Ensure all associated OccupiedSlots are deleted
    occupied_slots = memory_database_session.query(OccupiedSlot).filter_by(edit_id=edit_id).all()
    assert len(occupied_slots) == 0
