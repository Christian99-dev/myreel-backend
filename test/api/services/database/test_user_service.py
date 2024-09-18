import pytest
from sqlalchemy.exc import IntegrityError, NoResultFound
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
    name = "Test User"
    email = "test@example.com"
    
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

def test_create_invalid_group_id(memory_database_session: Session):
    # Arrange
    group_id = None  # Ungültige Group ID
    role = "member"
    name = "Invalid User"
    email = "invalid@example.com"
    
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
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get(non_existent_user_id, memory_database_session)

def test_get_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_user_id = 0
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get(zero_user_id, memory_database_session)

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
    new_name = "Non-Existent User"
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        update(user_id=non_existent_user_id, name=new_name, database_session=memory_database_session)

def test_update_no_changes(memory_database_session: Session):
    # Arrange
    existing_user = data["users"][0]
    
    # Act
    updated_user = update(user_id=existing_user["user_id"], database_session=memory_database_session)  # Keine Änderungen
    
    # Assert
    assert updated_user is not None
    assert updated_user.name == existing_user["name"]

# Remove Tests
def test_remove_success(memory_database_session: Session):
    # Arrange
    existing_user = memory_database_session.query(User).first()
    
    # Act
    remove(existing_user.user_id, memory_database_session)
    
    # Assert
    with pytest.raises(NoResultFound):
        get(existing_user.user_id, memory_database_session)

def test_remove_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_user_id = 9999
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        remove(non_existent_user_id, memory_database_session)

def test_remove_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_user_id = 0
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        remove(zero_user_id, memory_database_session)


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
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get_user_by_email(non_existent_email, memory_database_session)

def test_get_user_by_email_edgecase_empty_email(memory_database_session: Session):
    # Arrange
    empty_email = ""
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get_user_by_email(empty_email, memory_database_session)


"""Integration - CRUD"""

def test_integration_crud_user(memory_database_session: Session):
    # Create a user
    new_user = create(group_id="11111111-1111-1111-1111-111111111111", role="member", name="Test User", email="test@example.com", database_session=memory_database_session)
    assert new_user is not None

    # Update the user
    updated_user = update(user_id=new_user.user_id, name="Updated Test User", database_session=memory_database_session)
    assert updated_user is not None
    assert updated_user.name == "Updated Test User"

    # Fetch the user and check the updated name
    fetched_user = get(user_id=new_user.user_id, database_session=memory_database_session)
    assert fetched_user is not None
    assert fetched_user.name == "Updated Test User"

    # Remove the user
    remove(new_user.user_id, memory_database_session)

    # Ensure the user no longer exists
    with pytest.raises(NoResultFound):
        get(new_user.user_id, memory_database_session)


"""Integration - Cascading"""

def test_cascade_delete_user_with_related_entities(memory_database_session: Session):
    # Arrange: Lösche einen Benutzer und erwarte, dass alle zugehörigen LoginRequests, OccupiedSlots und Edits gelöscht werden.
    user_id = 1  # Ein Benutzer mit zugehörigen LoginRequests, OccupiedSlots und Edits
    
    # Überprüfe, dass der Benutzer existiert
    user = memory_database_session.query(User).filter_by(user_id=user_id).one_or_none()
    assert user is not None

    # Überprüfe, dass zugehörige LoginRequests existieren
    login_requests = memory_database_session.query(LoginRequest).filter_by(user_id=user_id).all()
    assert len(login_requests) > 0

    # Überprüfe, dass zugehörige OccupiedSlots existieren
    occupied_slots = memory_database_session.query(OccupiedSlot).filter_by(user_id=user_id).all()
    assert len(occupied_slots) > 0

    # Überprüfe, dass zugehörige Edits existieren
    edits = memory_database_session.query(Edit).filter_by(created_by=user_id).all()
    assert len(edits) > 0

    # Act: Lösche den Benutzer
    remove(user_id, memory_database_session)

    # Assert: Überprüfe, ob der Benutzer erfolgreich gelöscht wurde
    with pytest.raises(NoResultFound):
        get(user_id, memory_database_session)

    # Überprüfe, dass alle zugehörigen LoginRequests gelöscht wurden
    login_requests = memory_database_session.query(LoginRequest).filter_by(user_id=user_id).all()
    assert len(login_requests) == 0

    # Überprüfe, dass alle zugehörigen OccupiedSlots gelöscht wurden
    occupied_slots = memory_database_session.query(OccupiedSlot).filter_by(user_id=user_id).all()
    assert len(occupied_slots) == 0

    # Überprüfe, dass alle zugehörigen Edits gelöscht wurden
    edits = memory_database_session.query(Edit).filter_by(created_by=user_id).all()
    assert len(edits) == 0
