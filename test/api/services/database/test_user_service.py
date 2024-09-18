import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models.database.model import Edit, LoginRequest, OccupiedSlot, User
from api.services.database.user import (create, get, get_user_by_email, remove,
                                        update)
from mock.database.data import data

"""CRUD Operationen"""

# Create Tests
def test_create_success(memory_database_session: Session):
    # Arrange
    group_id = "11111111-1111-1111-1111-111111111111"
    role = "member"
    name = "New User"
    email = "newuser@example.com"
    
    # Act
    new_user = create(group_id=group_id, role=role, name=name, email=email, database_session=memory_database_session)
    
    # Assert
    assert new_user is not None
    assert new_user.group_id == group_id
    assert new_user.role == role
    assert new_user.name == name
    assert new_user.email == email

def test_create_duplicate_email(memory_database_session: Session):
    # Arrange
    group_id = "11111111-1111-1111-1111-111111111111"
    role = "member"
    name = "Another User"
    email = data["users"][0]["email"]  # Bereits vorhandene E-Mail
    
    # Act & Assert
    with pytest.raises(IntegrityError):
        create(group_id=group_id, role=role, name=name, email=email, database_session=memory_database_session)

def test_create_invalid_group(memory_database_session: Session):
    # Arrange
    group_id = "invalid-group-id"  # Ungültige group_id
    role = "member"
    name = "Invalid Group User"
    email = "invalidgroup@example.com"
    
    # Act & Assert
    with pytest.raises(IntegrityError):
        create(group_id=group_id, role=role, name=name, email=email, database_session=memory_database_session)

# Get Tests
def test_get_success(memory_database_session: Session):
    # Arrange
    existing_user = data["users"][0]
    
    # Act
    fetched_user = get(existing_user["user_id"], memory_database_session)
    
    # Assert
    assert fetched_user is not None
    assert fetched_user.user_id == existing_user["user_id"]

def test_get_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_user_id = 9999
    
    # Act
    fetched_user = get(non_existent_user_id, memory_database_session)
    
    # Assert
    assert fetched_user is None

def test_get_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_user_id = 0
    
    # Act
    fetched_user = get(zero_user_id, memory_database_session)
    
    # Assert
    assert fetched_user is None

# Update Tests
def test_update_success(memory_database_session: Session):
    # Arrange
    existing_user = data["users"][0]
    new_name = "Updated User Name"
    
    # Act
    updated_user = update(user_id=existing_user["user_id"], name=new_name, database_session=memory_database_session)
    
    # Assert
    assert updated_user is not None
    assert updated_user.name == new_name

def test_update_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_user_id = 9999
    new_name = "Non-Existent User Update"
    
    # Act
    updated_user = update(user_id=non_existent_user_id, name=new_name, database_session=memory_database_session)
    
    # Assert
    assert updated_user is None

def test_update_edgecase_empty_name(memory_database_session: Session):
    # Arrange
    existing_user = data["users"][0]
    new_name = ""  # Leerer Name
    
    # Act
    updated_user = update(user_id=existing_user["user_id"], name=new_name, database_session=memory_database_session)
    
    # Assert
    assert updated_user is not None
    assert updated_user.name == ""  # Leerer Name sollte akzeptiert werden

# Remove Tests
def test_remove_success(memory_database_session: Session):
    # Arrange
    existing_user = memory_database_session.query(User).first()
    
    # Act
    result = remove(existing_user.user_id, memory_database_session)
    
    # Assert
    assert result is True
    assert memory_database_session.query(User).filter_by(user_id=existing_user.user_id).one_or_none() is None

def test_remove_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_user_id = 9999
    
    # Act
    result = remove(non_existent_user_id, memory_database_session)
    
    # Assert
    assert result is False

def test_remove_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_user_id = 0
    
    # Act
    result = remove(zero_user_id, memory_database_session)
    
    # Assert
    assert result is False

"""Andere Operationen"""

# get_user_by_email Tests
def test_get_user_by_email_success(memory_database_session: Session):
    # Arrange
    existing_user = data["users"][0]
    
    # Act
    fetched_user = get_user_by_email(existing_user["email"], memory_database_session)
    
    # Assert
    assert fetched_user is not None
    assert fetched_user.email == existing_user["email"]

def test_get_user_by_email_invalid_email(memory_database_session: Session):
    # Arrange
    non_existent_email = "nonexistent@example.com"
    
    # Act
    fetched_user = get_user_by_email(non_existent_email, memory_database_session)
    
    # Assert
    assert fetched_user is None

def test_get_user_by_email_edgecase_empty_email(memory_database_session: Session):
    # Arrange
    empty_email = ""
    
    # Act
    fetched_user = get_user_by_email(empty_email, memory_database_session)
    
    # Assert
    assert fetched_user is None

"""Integration"""

def test_cascade_delete_user_with_edits_login_requests_and_occupied_slots(memory_database_session: Session):
    # Arrange: Wir löschen einen Benutzer und erwarten, dass alle zugehörigen Edits, LoginRequests und OccupiedSlots gelöscht werden.
    user_id = 1  # Benutzer 1

    # Überprüfen, dass der Benutzer existiert
    user = memory_database_session.query(User).filter_by(user_id=user_id).one_or_none()
    assert user is not None

    # Überprüfen, dass zugehörige Edits existieren
    edits = memory_database_session.query(Edit).filter_by(created_by=user_id).all()
    assert len(edits) > 0

    # Überprüfen, dass zugehörige LoginRequests existieren
    login_requests = memory_database_session.query(LoginRequest).filter_by(user_id=user_id).all()
    assert len(login_requests) > 0

    # Überprüfen, dass zugehörige OccupiedSlots existieren
    occupied_slots = memory_database_session.query(OccupiedSlot).filter_by(user_id=user_id).all()
    assert len(occupied_slots) > 0

    # Act: Lösche den Benutzer
    result = remove(user_id, memory_database_session)

    # Assert: Überprüfe, ob der Benutzer erfolgreich gelöscht wurde
    assert result is True
    user = memory_database_session.query(User).filter_by(user_id=user_id).one_or_none()
    assert user is None

    # Überprüfen, dass alle zugehörigen Edits gelöscht wurden
    edits = memory_database_session.query(Edit).filter_by(created_by=user_id).all()
    assert len(edits) == 0

    # Überprüfen, dass alle zugehörigen LoginRequests gelöscht wurden
    login_requests = memory_database_session.query(LoginRequest).filter_by(user_id=user_id).all()
    assert len(login_requests) == 0

    # Überprüfen, dass alle zugehörigen OccupiedSlots gelöscht wurden
    occupied_slots = memory_database_session.query(OccupiedSlot).filter_by(user_id=user_id).all()
    assert len(occupied_slots) == 0