from datetime import datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models.database.model import LoginRequest, User
from api.services.database.login import (
    create, create_or_update, delete_all_from_email, get,
    get_login_request_by_groupid_and_token, remove, update)
from mock.database.data import data

"""CRUD Operationen"""

# Create Tests
def test_create_success(memory_database_session: Session):
    # Arrange
    user_id = 4  # Ein gültiger Benutzer aus der Mock-Datenbank
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
    invalid_user_id = 9999  # Ein ungültiger Benutzer
    expires_in_minutes = 10

    # Act & Assert
    with pytest.raises(IntegrityError):
        create(user_id=invalid_user_id, expires_in_minutes=expires_in_minutes, database_session=memory_database_session)

# Get Tests
def test_get_success(memory_database_session: Session):
    # Arrange
    user_id = 1  # Gültiger Benutzer mit vorhandenem LoginRequest

    # Act
    fetched_login_request = get(user_id=user_id, database_session=memory_database_session)

    # Assert
    assert fetched_login_request is not None
    assert fetched_login_request.user_id == user_id

def test_get_invalid_user(memory_database_session: Session):
    # Arrange
    non_existent_user_id = 9999

    # Act
    fetched_login_request = get(user_id=non_existent_user_id, database_session=memory_database_session)

    # Assert
    assert fetched_login_request is None

# Update Tests
def test_update_success(memory_database_session: Session):
    # Arrange
    user_id = 1  # Ein gültiger Benutzer
    new_pin = "new_pin_1234"
    new_expires_in_minutes = 20

    # Act
    updated_login_request = update(user_id=user_id, pin=new_pin, expires_in_minutes=new_expires_in_minutes, database_session=memory_database_session)

    # Assert
    assert updated_login_request is not None
    assert updated_login_request.pin == new_pin
    assert updated_login_request.expires_at > datetime.now()

def test_update_invalid_user(memory_database_session: Session):
    # Arrange
    non_existent_user_id = 9999
    new_pin = "new_pin_1234"
    new_expires_in_minutes = 20

    # Act
    updated_login_request = update(user_id=non_existent_user_id, pin=new_pin, expires_in_minutes=new_expires_in_minutes, database_session=memory_database_session)

    # Assert
    assert updated_login_request is None

# Remove Tests
def test_remove_success(memory_database_session: Session):
    # Arrange
    user_id = 1  # Ein gültiger Benutzer

    # Act
    result = remove(user_id=user_id, database_session=memory_database_session)

    # Assert
    assert result is True
    assert memory_database_session.query(LoginRequest).filter_by(user_id=user_id).one_or_none() is None

def test_remove_invalid_user(memory_database_session: Session):
    # Arrange
    non_existent_user_id = 9999

    # Act
    result = remove(user_id=non_existent_user_id, database_session=memory_database_session)

    # Assert
    assert result is False

"""Andere Operationen"""

# delete_all_from_email Tests
def test_delete_all_from_email_success(memory_database_session: Session):
    # Arrange
    email = "creator1@example.com"  # Benutzer mit einem LoginRequest

    # Act
    delete_all_from_email(email=email, database_session=memory_database_session)

    # Assert
    user = memory_database_session.query(User).filter_by(email=email).first()
    assert memory_database_session.query(LoginRequest).filter_by(user_id=user.user_id).one_or_none() is None

def test_delete_all_from_email_no_login_request(memory_database_session: Session):
    # Arrange
    email = "creator3@example.com"  # Benutzer ohne LoginRequest

    # Act
    delete_all_from_email(email=email, database_session=memory_database_session)

    # Assert
    user = memory_database_session.query(User).filter_by(email=email).first()
    assert memory_database_session.query(LoginRequest).filter_by(user_id=user.user_id).one_or_none() is None

# get_login_request_by_groupid_and_token Tests
def test_get_login_request_by_groupid_and_token_success(memory_database_session: Session):
    # Arrange
    group_id = "11111111-1111-1111-1111-111111111111"
    token = "1234"

    # Act
    login_request = get_login_request_by_groupid_and_token(groupid=group_id, token=token, database_session=memory_database_session)

    # Assert
    assert login_request is not None
    assert login_request.pin == token

def test_get_login_request_by_groupid_and_token_invalid_token(memory_database_session: Session):
    # Arrange
    group_id = "11111111-1111-1111-1111-111111111111"
    invalid_token = "invalid_token"

    # Act
    login_request = get_login_request_by_groupid_and_token(groupid=group_id, token=invalid_token, database_session=memory_database_session)

    # Assert
    assert login_request is None

# create_or_update Tests
def test_create_or_update_creates_new_request(memory_database_session: Session):
    # Arrange
    user_id = 4  # Ein gültiger Benutzer, der noch keine LoginRequest hat
    expires_in_minutes = 10

    # Act
    new_login_request = create_or_update(user_id=user_id, expires_in_minutes=expires_in_minutes, database_session=memory_database_session)

    # Assert
    assert new_login_request is not None
    assert new_login_request.user_id == user_id
    assert new_login_request.expires_at > datetime.now()

def test_create_or_update_updates_existing_request(memory_database_session: Session):
    # Arrange
    user_id = 1  # Ein gültiger Benutzer mit existierendem LoginRequest
    expires_in_minutes = 20

    # Act
    updated_login_request = create_or_update(user_id=user_id, expires_in_minutes=expires_in_minutes, database_session=memory_database_session)

    # Assert
    assert updated_login_request is not None
    assert updated_login_request.user_id == user_id
    assert updated_login_request.expires_at > datetime.now()

"""Integration"""

def test_integration_create_and_delete_login_request(memory_database_session: Session):
    # Arrange
    user_id = 4  # Ein gültiger Benutzer
    expires_in_minutes = 10

    # Act: Erstelle ein LoginRequest
    new_login_request = create_or_update(user_id=user_id, expires_in_minutes=expires_in_minutes, database_session=memory_database_session)
    assert new_login_request is not None

    # Assert: Überprüfe, ob der LoginRequest existiert
    fetched_login_request = get(user_id=user_id, database_session=memory_database_session)
    assert fetched_login_request is not None

    # Act: Lösche den LoginRequest
    result = remove(user_id=user_id, database_session=memory_database_session)
    assert result is True

    # Assert: Überprüfe, ob der LoginRequest gelöscht wurde
    fetched_login_request = get(user_id=user_id, database_session=memory_database_session)
    assert fetched_login_request is None
