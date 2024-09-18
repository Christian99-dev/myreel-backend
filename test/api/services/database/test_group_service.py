import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models.database.model import Edit, Group, User
from api.services.database.group import (create, get, get_group_by_edit_id,
                                         get_group_by_user_id,
                                         is_group_creator, is_group_member,
                                         list_members, remove, update)
from mock.database.data import data

"""CRUD Operationen"""

# Create Tests
def test_create_success(memory_database_session: Session):
    # Arrange
    group_name = "New Test Group"
    
    # Act
    new_group = create(name=group_name, database_session=memory_database_session)
    
    # Assert
    assert new_group is not None
    assert new_group.name == group_name
    assert isinstance(new_group.group_id, str)

def test_create_invalid_data(memory_database_session: Session):
    # Arrange: Name ist None, was zu einem Fehler führen sollte
    group_name = None
    
    # Act & Assert
    with pytest.raises(IntegrityError):
        create(name=group_name, database_session=memory_database_session)

# Get Tests
def test_get_success(memory_database_session: Session):
    # Arrange
    existing_group = data["groups"][0]
    
    # Act
    fetched_group = get(group_id=existing_group["group_id"], database_session=memory_database_session)
    
    # Assert
    assert fetched_group is not None
    assert fetched_group.group_id == existing_group["group_id"]

def test_get_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_group_id = "invalid-group-id"
    
    # Act
    fetched_group = get(group_id=non_existent_group_id, database_session=memory_database_session)
    
    # Assert
    assert fetched_group is None

def test_get_edgecase_empty_group_id(memory_database_session: Session):
    # Arrange
    empty_group_id = ""
    
    # Act
    fetched_group = get(group_id=empty_group_id, database_session=memory_database_session)
    
    # Assert
    assert fetched_group is None

# Update Tests
def test_update_success(memory_database_session: Session):
    # Arrange
    existing_group = data["groups"][0]
    new_name = "Updated Group Name"
    
    # Act
    updated_group = update(group_id=existing_group["group_id"], name=new_name, database_session=memory_database_session)
    
    # Assert
    assert updated_group is not None
    assert updated_group.name == new_name

def test_update_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_group_id = "non-existent-id"
    new_name = "Non-existent Group Update"
    
    # Act
    updated_group = update(group_id=non_existent_group_id, name=new_name, database_session=memory_database_session)
    
    # Assert
    assert updated_group is None

def test_update_edgecase_empty_name(memory_database_session: Session):
    # Arrange
    existing_group = data["groups"][0]
    new_name = ""  # Leerer Name
    
    # Act
    updated_group = update(group_id=existing_group["group_id"], name=new_name, database_session=memory_database_session)
    
    # Assert
    assert updated_group is not None
    assert updated_group.name == ""  # Leerer Name sollte akzeptiert werden

# Remove Tests
def test_remove_success(memory_database_session: Session):
    # Arrange
    existing_group = memory_database_session.query(Group).first()
    
    # Act
    result = remove(group_id=existing_group.group_id, database_session=memory_database_session)
    
    # Assert
    assert result is True
    assert memory_database_session.query(Group).filter_by(group_id=existing_group.group_id).one_or_none() is None

def test_remove_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_group_id = "invalid-group-id"
    
    # Act
    result = remove(group_id=non_existent_group_id, database_session=memory_database_session)
    
    # Assert
    assert result is False

def test_remove_edgecase_empty_group_id(memory_database_session: Session):
    # Arrange
    empty_group_id = ""
    
    # Act
    result = remove(group_id=empty_group_id, database_session=memory_database_session)
    
    # Assert
    assert result is False

"""Andere Operationen"""

# is_group_member Tests
def test_is_group_member_success(memory_database_session: Session):
    # Arrange
    user = data["users"][0]  # Der erste User in der Gruppe
    
    # Act
    result = is_group_member(user_id=user["user_id"], group_id=user["group_id"], database_session=memory_database_session)
    
    # Assert
    assert result is True

def test_is_group_member_invalid_user(memory_database_session: Session):
    # Arrange
    invalid_user_id = 9999  # Ungültige user_id
    group_id = data["groups"][0]["group_id"]
    
    # Act
    result = is_group_member(user_id=invalid_user_id, group_id=group_id, database_session=memory_database_session)
    
    # Assert
    assert result is False

def test_is_group_member_edgecase_empty_group_id(memory_database_session: Session):
    # Arrange
    user_id = data["users"][0]["user_id"]
    empty_group_id = ""
    
    # Act
    result = is_group_member(user_id=user_id, group_id=empty_group_id, database_session=memory_database_session)
    
    # Assert
    assert result is False

# is_group_creator Tests
def test_is_group_creator_success(memory_database_session: Session):
    # Arrange
    creator = data["users"][0]  # Creator der Gruppe
    
    # Act
    result = is_group_creator(user_id=creator["user_id"], group_id=creator["group_id"], database_session=memory_database_session)
    
    # Assert
    assert result is True

def test_is_group_creator_invalid_user(memory_database_session: Session):
    # Arrange
    invalid_user_id = 9999  # Ungültige user_id
    group_id = data["groups"][0]["group_id"]
    
    # Act
    result = is_group_creator(user_id=invalid_user_id, group_id=group_id, database_session=memory_database_session)
    
    # Assert
    assert result is False

def test_is_group_creator_edgecase_empty_group_id(memory_database_session: Session):
    # Arrange
    user_id = data["users"][0]["user_id"]
    empty_group_id = ""
    
    # Act
    result = is_group_creator(user_id=user_id, group_id=empty_group_id, database_session=memory_database_session)
    
    # Assert
    assert result is False

# list_members Tests
def test_list_members_success(memory_database_session: Session):
    # Arrange
    group_id = data["groups"][0]["group_id"]
    
    # Act
    members = list_members(group_id=group_id, database_session=memory_database_session)
    
    # Assert
    assert len(members) > 0  # Es gibt Mitglieder in der Gruppe

def test_list_members_invalid_group(memory_database_session: Session):
    # Arrange
    invalid_group_id = "invalid-group-id"
    
    # Act
    members = list_members(group_id=invalid_group_id, database_session=memory_database_session)
    
    # Assert
    assert len(members) == 0

def test_list_members_edgecase_empty_group_id(memory_database_session: Session):
    # Arrange
    empty_group_id = ""
    
    # Act
    members = list_members(group_id=empty_group_id, database_session=memory_database_session)
    
    # Assert
    assert len(members) == 0

# get_group_by_edit_id Tests
def test_get_group_by_edit_id_success(memory_database_session: Session):
    # Arrange
    edit_id = data["edits"][0]["edit_id"]
    
    # Act
    group = get_group_by_edit_id(edit_id=edit_id, database_session=memory_database_session)
    
    # Assert
    assert group is not None
    assert group.group_id == data["edits"][0]["group_id"]

def test_get_group_by_edit_id_invalid_edit(memory_database_session: Session):
    # Arrange
    invalid_edit_id = 9999
    
    # Act
    group = get_group_by_edit_id(edit_id=invalid_edit_id, database_session=memory_database_session)
    
    # Assert
    assert group is None

# get_group_by_user_id Tests
def test_get_group_by_user_id_success(memory_database_session: Session):
    # Arrange
    user_id = data["users"][0]["user_id"]
    
    # Act
    group = get_group_by_user_id(user_id=user_id, database_session=memory_database_session)
    
    # Assert
    assert group is not None
    assert group.group_id == data["users"][0]["group_id"]

def test_get_group_by_user_id_invalid_user(memory_database_session: Session):
    # Arrange
    invalid_user_id = 9999
    
    # Act
    group = get_group_by_user_id(user_id=invalid_user_id, database_session=memory_database_session)
    
    # Assert
    assert group is None

"""Integration"""

def test_cascade_delete_group_with_edits_and_users(memory_database_session: Session):
    # Arrange: Wir löschen eine Gruppe und erwarten, dass alle zugehörigen Edits und Users gelöscht werden.
    group_id = "11111111-1111-1111-1111-111111111111"  # Gruppe 1 hat Edits und Users
    
    # Überprüfen, dass die Gruppe existiert
    group = memory_database_session.query(Group).filter_by(group_id=group_id).one_or_none()
    assert group is not None
    
    # Überprüfen, dass zugehörige Edits und Users existieren
    edits = memory_database_session.query(Edit).filter_by(group_id=group_id).all()
    users = memory_database_session.query(User).filter_by(group_id=group_id).all()
    assert len(edits) > 0
    assert len(users) > 0
    
    # Act: Lösche die Gruppe
    result = remove(group_id=group_id, database_session=memory_database_session)
    
    # Assert: Überprüfe, ob die Gruppe erfolgreich gelöscht wurde
    assert result is True
    group = memory_database_session.query(Group).filter_by(group_id=group_id).one_or_none()
    assert group is None

    # Überprüfen, dass alle zugehörigen Edits und Users gelöscht wurden
    edits = memory_database_session.query(Edit).filter_by(group_id=group_id).all()
    users = memory_database_session.query(User).filter_by(group_id=group_id).all()
    assert len(edits) == 0
    assert len(users) == 0
