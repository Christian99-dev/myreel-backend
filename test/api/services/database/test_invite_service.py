import logging
from datetime import datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models.database.model import Invitation
from api.services.database.invite import (create, delete, delete_all_by_email,
                                          get, update)
from mock.database.data import data

logger = logging.getLogger("test.unittest")

"""CRUD Operationen"""

# Create Tests
def test_create_success(memory_database_session: Session):
    # Arrange
    group_id = "11111111-1111-1111-1111-111111111111"
    email = "new_invitee@example.com"
    expires_in_days = 7
    
    # Act
    new_invitation = create(group_id=group_id, email=email, expires_in_days=expires_in_days, database_session=memory_database_session)
    
    # Assert
    assert new_invitation is not None
    assert new_invitation.group_id == group_id
    assert new_invitation.email == email
    assert isinstance(new_invitation.created_at, datetime)
    assert new_invitation.expires_at == new_invitation.created_at + timedelta(days=expires_in_days)

def test_create_invalid_group_id(memory_database_session: Session):
    # Arrange
    group_id = "invalid_group_id"  # Ungültige group_id
    email = "new_invitee@example.com"
    expires_in_days = 7
    
    # Act & Assert
    with pytest.raises(IntegrityError):
        create(group_id=group_id, email=email, expires_in_days=expires_in_days, database_session=memory_database_session)

def test_create_edgecase_no_email(memory_database_session: Session):
    # Arrange
    group_id = "11111111-1111-1111-1111-111111111111"
    email = ""  # Leere E-Mail
    expires_in_days = 7
    
    # Act
    new_invitation = create(group_id=group_id, email=email, expires_in_days=expires_in_days, database_session=memory_database_session)
    
    # Assert
    assert new_invitation is not None
    assert new_invitation.email == ""  # Leere E-Mail sollte akzeptiert werden

# Get Tests
def test_get_success(memory_database_session: Session):
    # Arrange
    existing_invitation = data["invitations"][0]
    
    # Act
    fetched_invitation = get(existing_invitation["invitation_id"], memory_database_session)
    
    # Assert
    assert fetched_invitation is not None
    assert fetched_invitation.invitation_id == existing_invitation["invitation_id"]

def test_get_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_invitation_id = 9999
    
    # Act
    fetched_invitation = get(non_existent_invitation_id, memory_database_session)
    
    # Assert
    assert fetched_invitation is None

def test_get_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_invitation_id = 0
    
    # Act
    fetched_invitation = get(zero_invitation_id, memory_database_session)
    
    # Assert
    assert fetched_invitation is None

# Update Tests
def test_update_success(memory_database_session: Session):
    # Arrange
    existing_invitation = data["invitations"][0]
    new_email = "updated_invitee@example.com"
    expires_in_days = 14
    
    # Act
    updated_invitation = update(invitation_id=existing_invitation["invitation_id"], email=new_email, expires_in_days=expires_in_days, database_session=memory_database_session)
    
    # Assert
    assert updated_invitation is not None
    assert updated_invitation.email == new_email

    expires_at_expected = datetime.now() + timedelta(days=expires_in_days)

    # Erlaube eine kleine Toleranz 
    tolerance = timedelta(seconds=3)
    assert abs(updated_invitation.expires_at - expires_at_expected) < tolerance

def test_update_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_invitation_id = 9999
    new_email = "updated_invitee@example.com"
    
    # Act
    updated_invitation = update(invitation_id=non_existent_invitation_id, email=new_email, database_session=memory_database_session)
    
    # Assert
    assert updated_invitation is None

def test_update_edgecase_empty_email(memory_database_session: Session):
    # Arrange
    existing_invitation = data["invitations"][0]
    new_email = ""  # Leere E-Mail
    
    # Act
    updated_invitation = update(invitation_id=existing_invitation["invitation_id"], email=new_email, database_session=memory_database_session)
    
    # Assert
    assert updated_invitation is not None
    assert updated_invitation.email == ""  # Leere E-Mail sollte akzeptiert werden

# Delete Tests
def test_delete_success(memory_database_session: Session):
    # Arrange
    existing_invitation = data["invitations"][0]
    
    # Act
    result = delete(existing_invitation["invitation_id"], memory_database_session)
    
    # Assert
    assert result is True
    deleted_invitation = memory_database_session.query(Invitation).filter_by(invitation_id=existing_invitation["invitation_id"]).one_or_none()
    assert deleted_invitation is None

def test_delete_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_invitation_id = 9999
    
    # Act
    result = delete(non_existent_invitation_id, memory_database_session)
    
    # Assert
    assert result is False

def test_delete_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_invitation_id = 0
    
    # Act
    result = delete(zero_invitation_id, memory_database_session)
    
    # Assert
    assert result is False

"""Andere Operationen"""

def test_delete_all_by_email_success(memory_database_session: Session):
    # Arrange
    email = "invitee1@example.com"
    
    # Act
    delete_all_by_email(email, memory_database_session)
    
    # Assert
    deleted_invitations = memory_database_session.query(Invitation).filter_by(email=email).all()
    assert len(deleted_invitations) == 0

def test_delete_all_by_email_no_match(memory_database_session: Session):
    # Arrange
    non_existent_email = "nonexistent_email@example.com"
    
    # Act
    delete_all_by_email(non_existent_email, memory_database_session)
    
    # Assert
    # Überprüfen, dass keine Einladungen gelöscht wurden, da es keine Übereinstimmung gab
    all_invitations = memory_database_session.query(Invitation).all()
    assert len(all_invitations) == len(data["invitations"])  # Die Anzahl der Einladungen sollte unverändert bleiben
