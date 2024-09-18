import pytest
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from api.models.database.model import Group, Invitation, User
from api.services.database.group import (create, get, get_group_by_edit_id,
                                         get_group_by_user_id,
                                         is_group_creator, is_group_member,
                                         list_members, remove, update)
from mock.database.data import data

"""CRUD Operationen"""

# Create Tests
def test_create_success(memory_database_session: Session):
    # Arrange
    group_name = "New Group"
    
    # Act
    new_group = create(name=group_name, database_session=memory_database_session)
    
    # Assert
    assert new_group is not None
    assert new_group.name == group_name

def test_create_invalid_data(memory_database_session: Session):
    # Arrange
    invalid_name = None  # Name cannot be None

    # Act & Assert
    with pytest.raises(IntegrityError):
        create(name=invalid_name, database_session=memory_database_session)

def test_create_edgecase_empty_name(memory_database_session: Session):
    # Arrange
    empty_name = ""  # Empty name should be allowed
    
    # Act
    new_group = create(name=empty_name, database_session=memory_database_session)
    
    # Assert
    assert new_group is not None
    assert new_group.name == ""

# Get Tests
def test_get_success(memory_database_session: Session):
    # Arrange
    existing_group = data["groups"][0]
    
    # Act
    fetched_group = get(existing_group["group_id"], memory_database_session)
    
    # Assert
    assert fetched_group is not None
    assert fetched_group.group_id == existing_group["group_id"]

def test_get_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_group_id = "99999999-9999-9999-9999-999999999999"
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get(non_existent_group_id, memory_database_session)

def test_get_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_group_id = "00000000-0000-0000-0000-000000000000"
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get(zero_group_id, memory_database_session)

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
    non_existent_group_id = "99999999-9999-9999-9999-999999999999"
    new_name = "Non-Existent Group Update"
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        update(group_id=non_existent_group_id, name=new_name, database_session=memory_database_session)

def test_update_edgecase_empty_name(memory_database_session: Session):
    # Arrange
    existing_group = data["groups"][0]
    new_name = ""  # Empty name
    
    # Act
    updated_group = update(group_id=existing_group["group_id"], name=new_name, database_session=memory_database_session)
    
    # Assert
    assert updated_group is not None
    assert updated_group.name == ""  # Empty name should be accepted

# Remove Tests
def test_remove_success(memory_database_session: Session):
    # Arrange
    existing_group = memory_database_session.query(Group).first()
    
    # Act
    remove(existing_group.group_id, memory_database_session)
    
    # Assert
    with pytest.raises(NoResultFound):
        get(existing_group.group_id, memory_database_session)

def test_remove_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_group_id = "99999999-9999-9999-9999-999999999999"
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        remove(non_existent_group_id, memory_database_session)

def test_remove_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_group_id = "00000000-0000-0000-0000-000000000000"
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        remove(zero_group_id, memory_database_session)

"""Andere Operationen"""

# is_group_member Tests
def test_is_group_member_success(memory_database_session: Session):
    # Arrange
    user = data["users"][0]
    
    # Act
    result = is_group_member(user_id=user["user_id"], group_id=user["group_id"], database_session=memory_database_session)
    
    # Assert
    assert result is True

def test_is_group_member_invalid_user(memory_database_session: Session):
    # Arrange
    non_existent_user_id = 9999
    group_id = data["groups"][0]["group_id"]
    
    # Act
    result = is_group_member(user_id=non_existent_user_id, group_id=group_id, database_session=memory_database_session)
    
    # Assert
    assert result is False

def test_is_group_member_invalid_group(memory_database_session: Session):
    # Arrange
    user_id = data["users"][0]["user_id"]
    non_existent_group_id = "99999999-9999-9999-9999-999999999999"
    
    # Act
    result = is_group_member(user_id=user_id, group_id=non_existent_group_id, database_session=memory_database_session)
    
    # Assert
    assert result is False

# is_group_creator Tests
def test_is_group_creator_success(memory_database_session: Session):
    # Arrange
    user = data["users"][0]
    
    # Act
    result = is_group_creator(user_id=user["user_id"], group_id=user["group_id"], database_session=memory_database_session)
    
    # Assert
    assert result is True

def test_is_group_creator_invalid_user(memory_database_session: Session):
    # Arrange
    non_existent_user_id = 9999
    group_id = data["groups"][0]["group_id"]
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        is_group_creator(user_id=non_existent_user_id, group_id=group_id, database_session=memory_database_session)

def test_is_group_creator_invalid_group(memory_database_session: Session):
    # Arrange
    user_id = data["users"][0]["user_id"]
    non_existent_group_id = "99999999-9999-9999-9999-999999999999"
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        is_group_creator(user_id=user_id, group_id=non_existent_group_id, database_session=memory_database_session)

# list_members Tests
def test_list_members_success(memory_database_session: Session):
    # Arrange
    group_id = data["groups"][0]["group_id"]
    
    # Act
    members = list_members(group_id=group_id, database_session=memory_database_session)
    
    # Assert
    assert len(members) > 0

def test_list_members_invalid_group(memory_database_session: Session):
    # Arrange
    non_existent_group_id = "99999999-9999-9999-9999-999999999999"
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        list_members(non_existent_group_id, memory_database_session)

# get_group_by_edit_id Tests
def test_get_group_by_edit_id_success(memory_database_session: Session):
    # Arrange
    edit = data["edits"][0]
    
    # Act
    group = get_group_by_edit_id(edit_id=edit["edit_id"], database_session=memory_database_session)
    
    # Assert
    assert group is not None

def test_get_group_by_edit_id_invalid_edit(memory_database_session: Session):
    # Arrange
    invalid_edit_id = 9999
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get_group_by_edit_id(edit_id=invalid_edit_id, database_session=memory_database_session)

# get_group_by_user_id Tests
def test_get_group_by_user_id_success(memory_database_session: Session):
    # Arrange
    user = data["users"][0]
    
    # Act
    group = get_group_by_user_id(user_id=user["user_id"], database_session=memory_database_session)
    
    # Assert
    assert group is not None

def test_get_group_by_user_id_invalid_user(memory_database_session: Session):
    # Arrange
    non_existent_user_id = 9999
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get_group_by_user_id(user_id=non_existent_user_id, database_session=memory_database_session)

"""Integration - CRUD"""

def test_integration_crud_group(memory_database_session: Session):
    # Create a group
    new_group = create(name="New Group", database_session=memory_database_session)
    assert new_group is not None

    # Update the group
    updated_group = update(group_id=new_group.group_id, name="Updated Group", database_session=memory_database_session)
    assert updated_group is not None
    assert updated_group.name == "Updated Group"

    # Fetch the group and check the updated name
    fetched_group = get(group_id=new_group.group_id, database_session=memory_database_session)
    assert fetched_group is not None
    assert fetched_group.name == "Updated Group"

    # Remove the group
    remove(new_group.group_id, memory_database_session)

    # Ensure the group no longer exists
    with pytest.raises(NoResultFound):
        get(new_group.group_id, memory_database_session)

"""Integration - Cascading"""

def test_cascade_delete_group_with_users_and_invitations(memory_database_session: Session):
    # Arrange: We delete a Group and expect all associated Users and Invitations to be deleted
    group_id = data["groups"][0]["group_id"]

    # Ensure the Group exists
    group = memory_database_session.query(Group).filter_by(group_id=group_id).one_or_none()
    assert group is not None

    # Ensure Users exist
    users = memory_database_session.query(User).filter_by(group_id=group_id).all()
    assert len(users) > 0

    # Ensure Invitations exist
    invitations = memory_database_session.query(Invitation).filter_by(group_id=group_id).all()
    assert len(invitations) > 0

    # Act: Delete the Group
    remove(group_id, memory_database_session)

    # Ensure the Group is deleted
    with pytest.raises(NoResultFound):
        get(group_id, memory_database_session)

    # Ensure all associated Users are deleted
    users = memory_database_session.query(User).filter_by(group_id=group_id).all()
    assert len(users) == 0

    # Ensure all associated Invitations are deleted
    invitations = memory_database_session.query(Invitation).filter_by(group_id=group_id).all()
    assert len(invitations) == 0
