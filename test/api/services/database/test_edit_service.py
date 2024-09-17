import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models.database.model import Edit
from api.services.database.edit import (are_all_slots_occupied, create, get,
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
    name = "New Test Edit"
    is_live = True
    video_src = "http://example.com/new_edit.mp4"
    
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

def test_create_invalid_data(memory_database_session: Session):
    # Arrange
    song_id = 9999  # Ungültige song_id (fremdschlüsselverletzung)
    created_by = 1
    group_id = "11111111-1111-1111-1111-111111111111"
    name = "New Test Edit"
    is_live = True
    video_src = "http://example.com/new_edit.mp4"
    
    # Act & Assert
    with pytest.raises(IntegrityError):
        create(song_id=song_id, created_by=created_by, group_id=group_id, name=name, is_live=is_live, video_src=video_src, database_session=memory_database_session)

def test_create_edgecase_empty_name(memory_database_session: Session):
    # Arrange
    song_id = 1
    created_by = 1
    group_id = "11111111-1111-1111-1111-111111111111"
    name = ""  # Leerer Name
    is_live = True
    video_src = "http://example.com/new_edit.mp4"
    
    # Act
    new_edit = create(song_id=song_id, created_by=created_by, group_id=group_id, name=name, is_live=is_live, video_src=video_src, database_session=memory_database_session)
    
    # Assert
    assert new_edit is not None
    assert new_edit.name == ""  # Leerer Name sollte akzeptiert werden

def test_create_edgecase_invalid_group_id(memory_database_session: Session):
    # Arrange
    song_id = 1
    created_by = 1
    group_id = "invalid-group-id"  # Ungültige group_id, die eine Fremdschlüsselverletzung auslösen sollte
    name = "New Test Edit"
    is_live = True
    video_src = "http://example.com/new_edit.mp4"
    
    # Act & Assert
    with pytest.raises(IntegrityError):
        create(song_id=song_id, created_by=created_by, group_id=group_id, name=name, is_live=is_live, video_src=video_src, database_session=memory_database_session)

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
    non_existent_edit_id = 9999
    
    # Act
    fetched_edit = get(non_existent_edit_id, memory_database_session)
    
    # Assert
    assert fetched_edit is None

def test_get_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_edit_id = 0
    
    # Act
    fetched_edit = get(zero_edit_id, memory_database_session)
    
    # Assert
    assert fetched_edit is None

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
    non_existent_edit_id = 9999
    new_name = "Non-Existent Edit Update"
    
    # Act
    updated_edit = update(edit_id=non_existent_edit_id, name=new_name, database_session=memory_database_session)
    
    # Assert
    assert updated_edit is None

def test_update_edgecase_empty_name(memory_database_session: Session):
    # Arrange
    existing_edit = data["edits"][0]
    new_name = ""  # Leerer Name
    
    # Act
    updated_edit = update(edit_id=existing_edit["edit_id"], name=new_name, database_session=memory_database_session)
    
    # Assert
    assert updated_edit is not None
    assert updated_edit.name == ""  # Leerer Name sollte akzeptiert werden

# Remove Tests
def test_remove_success(memory_database_session: Session):
    # Arrange
    existing_edit = memory_database_session.query(Edit).first()
    
    # Act
    result = remove(existing_edit.edit_id, memory_database_session)
    
    # Assert
    assert result is True
    assert memory_database_session.query(Edit).filter_by(edit_id=existing_edit.edit_id).one_or_none() is None

def test_remove_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_edit_id = 9999
    
    # Act
    result = remove(non_existent_edit_id, memory_database_session)
    
    # Assert
    assert result is False

def test_remove_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_edit_id = 0
    
    # Act
    result = remove(zero_edit_id, memory_database_session)
    
    # Assert
    assert result is False

"""Andere Operationen"""

# is_edit_creator Tests
def test_is_edit_creator_success(memory_database_session: Session):
    # Arrange
    edit = data["edits"][0]
    
    # Act
    result = is_edit_creator(edit["created_by"], edit["edit_id"], memory_database_session)
    
    # Assert
    assert result is True

def test_is_edit_creator_invalid_user(memory_database_session: Session):
    # Arrange
    edit = data["edits"][0]
    
    # Act
    result = is_edit_creator(9999, edit["edit_id"], memory_database_session)
    
    # Assert
    assert result is False

def test_is_edit_creator_edgecase_zero_user(memory_database_session: Session):
    # Arrange
    edit = data["edits"][0]
    
    # Act
    result = is_edit_creator(0, edit["edit_id"], memory_database_session)
    
    # Assert
    assert result is False

# are_all_slots_occupied Tests
def test_are_all_slots_occupied_success(memory_database_session: Session):
    # Arrange
    edit_id = 3  # Alle Slots für diesen Edit sind belegt
    
    # Act
    result = are_all_slots_occupied(edit_id, memory_database_session)
    
    # Assert
    assert result == True

def test_are_all_slots_occupied_failure(memory_database_session: Session):
    # Arrange
    edit_id = 2  # Nicht alle Slots sind belegt
    
    # Act
    result = are_all_slots_occupied(edit_id, memory_database_session)
    
    # Assert
    assert result == False

def test_are_all_slots_occupied_invalid_edit(memory_database_session: Session):
    # Arrange
    non_existent_edit_id = 9999
    
    # Act
    result = are_all_slots_occupied(non_existent_edit_id, memory_database_session)
    
    # Assert
    assert result == False

# set_is_live Tests
def test_set_is_live_success(memory_database_session: Session):
    # Arrange
    edit_id = 3  # Alle Slots für diesen Edit sind belegt
    
    # Act
    result = set_is_live(edit_id, memory_database_session)
    
    # Assert
    assert result is True
    assert memory_database_session.query(Edit).filter_by(edit_id=edit_id).one().isLive is True

def test_set_is_live_failure(memory_database_session: Session):
    # Arrange
    edit_id = 2  # Nicht alle Slots sind belegt
    
    # Act
    result = set_is_live(edit_id, memory_database_session)
    
    # Assert
    assert result is False

def test_set_is_live_invalid_edit(memory_database_session: Session):
    # Arrange
    non_existent_edit_id = 9999
    
    # Act
    result = set_is_live(non_existent_edit_id, memory_database_session)
    
    # Assert
    assert result is False

# get_edits_by_group Tests
def test_get_edits_by_group_success(memory_database_session: Session):
    # Arrange
    group_id = "11111111-1111-1111-1111-111111111111"
    
    # Act
    edits = get_edits_by_group(group_id, memory_database_session)
    
    # Assert
    assert len(edits) == 3

def test_get_edits_by_group_invalid_group(memory_database_session: Session):
    # Arrange
    group_id = "99999999-9999-9999-9999-999999999999"  # Ungültige group_id
    
    # Act
    edits = get_edits_by_group(group_id, memory_database_session)
    
    # Assert
    assert len(edits) == 0

def test_get_edits_by_group_edgecase_empty_group_id(memory_database_session: Session):
    # Arrange
    group_id = ""  # Leere group_id
    
    # Act
    edits = get_edits_by_group(group_id, memory_database_session)
    
    # Assert
    assert len(edits) == 0
