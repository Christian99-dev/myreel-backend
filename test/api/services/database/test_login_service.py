from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from api.models.database.model import LoginRequest, User
from api.services.database.login import (
    create, create_or_update, delete_all_from_email, get,
    get_login_request_by_groupid_and_email, remove, update)
from mock.database.data import data

"""CRUD Operationen"""

# Create Tests
def test_create_success(memory_database_session: Session):
    # Arrange
    user_id = 4  # Ein gültiger Benutzer aus den Mockdaten
    expires_in_minutes = 10

    # Act
    new_login_request = create(user_id=user_id, expires_in_minutes=expires_in_minutes, database_session=memory_database_session)

    # Assert
    assert new_login_request is not None
    assert new_login_request.user_id == user_id
    assert isinstance(new_login_request.pin, str)
    assert new_login_request.expires_at > datetime.now()

def test_create_invalid_user(memory_database_session: Session):
    # Arrange
    invalid_user_id = 9999  # Ungültiger Benutzer
    
    # Act & Assert
    with pytest.raises(IntegrityError):
        create(user_id=invalid_user_id, expires_in_minutes=10, database_session=memory_database_session)

def test_create_edgecase_expires_now(memory_database_session: Session):
    # Arrange
    user_id = 4  # Ein gültiger Benutzer
    expires_in_minutes = 0  # LoginRequest läuft sofort ab

    # Act
    new_login_request = create(user_id=user_id, expires_in_minutes=expires_in_minutes, database_session=memory_database_session)

    # Assert
    assert new_login_request.expires_at == new_login_request.created_at

def test_create_duplicate_login_request(memory_database_session: Session):
    # Arrange
    user_id = 4  # Ein gültiger Benutzer
    expires_in_minutes = 10

    # Act: Erstelle die erste Login-Anfrage
    first_login_request = create(user_id=user_id, expires_in_minutes=expires_in_minutes, database_session=memory_database_session)

    # Assert: Die erste Login-Anfrage sollte erfolgreich erstellt werden
    assert first_login_request is not None
    assert first_login_request.user_id == user_id

    # Act & Assert: Versuche, eine zweite Login-Anfrage für denselben Benutzer zu erstellen
    with pytest.raises(IntegrityError):
        create(user_id=user_id, expires_in_minutes=expires_in_minutes, database_session=memory_database_session)
        
# Get Tests
def test_get_success(memory_database_session: Session):
    # Arrange
    existing_login_request = data["login_requests"][0]

    # Act
    fetched_login_request = get(existing_login_request["user_id"], memory_database_session)

    # Assert
    assert fetched_login_request is not None
    assert fetched_login_request.user_id == existing_login_request["user_id"]

def test_get_invalid_user(memory_database_session: Session):
    # Arrange
    non_existent_user_id = 9999

    # Act & Assert
    with pytest.raises(NoResultFound):
        get(user_id=non_existent_user_id, database_session=memory_database_session)

def test_get_edgecase_zero_user_id(memory_database_session: Session):
    # Arrange
    zero_user_id = 0

    # Act & Assert
    with pytest.raises(NoResultFound):
        get(user_id=zero_user_id, database_session=memory_database_session)

# Update Tests
def test_update_success(memory_database_session: Session):
    # Arrange
    existing_login_request = data["login_requests"][0]
    new_pin = "updated_pin"
    expires_in_minutes = 15

    # Act
    updated_login_request = update(user_id=existing_login_request["user_id"], pin=new_pin, expires_in_minutes=expires_in_minutes, database_session=memory_database_session)

    # Assert
    assert updated_login_request is not None
    assert updated_login_request.pin == new_pin
    assert updated_login_request.expires_at > datetime.now()

def test_update_invalid_user(memory_database_session: Session):
    # Arrange
    non_existent_user_id = 9999

    # Act & Assert
    with pytest.raises(NoResultFound):
        update(user_id=non_existent_user_id, pin="new_pin", expires_in_minutes=10, database_session=memory_database_session)

def test_update_edgecase_empty_pin(memory_database_session: Session):
    # Arrange
    existing_login_request = data["login_requests"][0]
    empty_pin = ""  # Leerer PIN

    # Act
    updated_login_request = update(user_id=existing_login_request["user_id"], pin=empty_pin, expires_in_minutes=10, database_session=memory_database_session)

    # Assert
    assert updated_login_request.pin == empty_pin

# Remove Tests
def test_remove_success(memory_database_session: Session):
    # Arrange
    existing_login_request = memory_database_session.query(LoginRequest).first()

    # Act
    remove(user_id=existing_login_request.user_id, database_session=memory_database_session)

    # Assert
    with pytest.raises(NoResultFound):
        get(existing_login_request.user_id, memory_database_session)

def test_remove_invalid_user(memory_database_session: Session):
    # Arrange
    non_existent_user_id = 9999

    # Act & Assert
    with pytest.raises(NoResultFound):
        remove(user_id=non_existent_user_id, database_session=memory_database_session)

def test_remove_edgecase_zero_user_id(memory_database_session: Session):
    # Arrange
    zero_user_id = 0

    # Act & Assert
    with pytest.raises(NoResultFound):
        remove(user_id=zero_user_id, database_session=memory_database_session)

"""Andere Operationen"""

# delete_all_from_email Tests
def test_delete_all_from_email_success(memory_database_session: Session):
    # Arrange
    email = "creator1@example.com"

    # Act
    delete_all_from_email(email=email, database_session=memory_database_session)

    # Assert
    user = memory_database_session.query(User).filter_by(email=email).first()
    assert memory_database_session.query(LoginRequest).filter_by(user_id=user.user_id).one_or_none() is None

def test_delete_all_from_email_invalid_email(memory_database_session: Session):
    # Arrange
    non_existent_email = "nonexistent@example.com"

    # Act & Assert
    with pytest.raises(NoResultFound):
        delete_all_from_email(email=non_existent_email, database_session=memory_database_session)

def test_delete_all_from_email_edgecase_empty_email(memory_database_session: Session):
    # Arrange
    empty_email = ""

    # Act & Assert
    with pytest.raises(NoResultFound):
        delete_all_from_email(email=empty_email, database_session=memory_database_session)

# get_login_request_by_groupid_and_email Tests
def test_get_login_request_by_groupid_and_email_success(memory_database_session: Session):
    # Arrange
    group_id = "11111111-1111-1111-1111-111111111111"
    email = data["users"][0]["email"]

    # Act
    login_request = get_login_request_by_groupid_and_email(groupid=group_id, email=email, database_session=memory_database_session)

    # Assert
    assert login_request is not None
    assert login_request.user.email == email

def test_get_login_request_by_groupid_and_email_invalid_group(memory_database_session: Session):
    # Arrange
    invalid_group_id = "invalid-group-id"
    email = data["users"][0]["email"]

    # Act & Assert
    with pytest.raises(NoResultFound):
        get_login_request_by_groupid_and_email(groupid=invalid_group_id, email=email, database_session=memory_database_session)

def test_get_login_request_by_groupid_and_email_invalid_email(memory_database_session: Session):
    # Arrange
    group_id = "11111111-1111-1111-1111-111111111111"
    invalid_email = "invalid_email@example.com"

    # Act & Assert
    with pytest.raises(NoResultFound):
        get_login_request_by_groupid_and_email(groupid=group_id, email=invalid_email, database_session=memory_database_session)
        
# create_or_update Tests
def test_create_or_update_creates_new_request(memory_database_session: Session):
    # Arrange
    user_id = 4  # Ein gültiger Benutzer, der noch keine LoginRequest hat

    # Act
    new_login_request = create_or_update(user_id=user_id, database_session=memory_database_session)

    # Assert
    assert new_login_request is not None
    assert new_login_request.user_id == user_id

def test_create_or_update_updates_existing_request(memory_database_session: Session):
    # Arrange
    existing_login_request = data["login_requests"][0]

    # Act
    updated_login_request = create_or_update(user_id=existing_login_request["user_id"], database_session=memory_database_session)

    # Assert
    assert updated_login_request is not None
    assert updated_login_request.user_id == existing_login_request["user_id"]

def test_create_or_update_invalid_user(memory_database_session: Session):
    # Arrange
    invalid_user_id = 9999

    # Act & Assert
    with pytest.raises(NoResultFound):
        create_or_update(user_id=invalid_user_id, database_session=memory_database_session)

"""Integration - CRUD"""

def test_integration_crud_login_request(memory_database_session: Session):
    # Create a login request
    new_login_request = create(user_id=4, expires_in_minutes=10, database_session=memory_database_session)
    assert new_login_request is not None

    # Update the login request
    updated_login_request = update(user_id=new_login_request.user_id, pin="new_pin", expires_in_minutes=15, database_session=memory_database_session)
    assert updated_login_request is not None
    assert updated_login_request.pin == "new_pin"

    # Fetch the login request and check the updated pin
    fetched_login_request = get(user_id=new_login_request.user_id, database_session=memory_database_session)
    assert fetched_login_request is not None
    assert fetched_login_request.pin == "new_pin"

    # Remove the login request
    remove(new_login_request.user_id, memory_database_session)

    # Ensure the login request no longer exists
    with pytest.raises(NoResultFound):
        get(new_login_request.user_id, memory_database_session)
