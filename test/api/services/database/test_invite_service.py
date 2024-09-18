from datetime import timedelta

import pytest
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from api.models.database.model import Invitation
from api.services.database.invite import (create, get, remove,
                                          remove_all_by_email, update)
from mock.database.data import data

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
    assert new_invitation.expires_at == new_invitation.created_at + timedelta(days=expires_in_days)

def test_create_invalid_group(memory_database_session: Session):
    # Arrange
    invalid_group_id = "invalid-group-id"
    email = "invitee@example.com"
    
    # Act & Assert
    with pytest.raises(IntegrityError):
        create(group_id=invalid_group_id, email=email, expires_in_days=7, database_session=memory_database_session)

def test_create_edgecase_no_expiry(memory_database_session: Session):
    # Arrange
    group_id = "11111111-1111-1111-1111-111111111111"
    email = "invitee@example.com"
    
    # Act
    new_invitation = create(group_id=group_id, email=email, expires_in_days=0, database_session=memory_database_session)
    
    # Assert
    assert new_invitation.expires_at == new_invitation.created_at

# Get Tests
def test_get_success(memory_database_session: Session):
    # Arrange
    existing_invitation = data["invitations"][0]
    
    # Act
    fetched_invitation = get(invitation_id=existing_invitation["invitation_id"], database_session=memory_database_session)
    
    # Assert
    assert fetched_invitation is not None
    assert fetched_invitation.invitation_id == existing_invitation["invitation_id"]

def test_get_invalid_id(memory_database_session: Session):
    # Arrange
    non_existent_invitation_id = 9999
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get(invitation_id=non_existent_invitation_id, database_session=memory_database_session)

def test_get_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_invitation_id = 0
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        get(invitation_id=zero_invitation_id, database_session=memory_database_session)

# Update Tests
def test_update_success(memory_database_session: Session):
    # Arrange
    existing_invitation = data["invitations"][0]
    new_email = "updated_invitee@example.com"
    expires_in_days = 10
    
    # Act
    updated_invitation = update(invitation_id=existing_invitation["invitation_id"], email=new_email, expires_in_days=expires_in_days, database_session=memory_database_session)
    
    # Assert
    assert updated_invitation is not None
    assert updated_invitation.email == new_email
    assert updated_invitation.expires_at > updated_invitation.created_at

def test_update_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_invitation_id = 9999
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        update(invitation_id=invalid_invitation_id, email="updated@example.com", expires_in_days=7, database_session=memory_database_session)

def test_update_edgecase_empty_email(memory_database_session: Session):
    # Arrange
    existing_invitation = data["invitations"][0]
    new_email = ""  # Empty email should be accepted
    
    # Act
    updated_invitation = update(invitation_id=existing_invitation["invitation_id"], email=new_email, database_session=memory_database_session)
    
    # Assert
    assert updated_invitation.email == ""

# remove Tests
def test_remove_success(memory_database_session: Session):
    # Arrange
    existing_invitation = data["invitations"][0]
    
    # Act
    remove(invitation_id=existing_invitation["invitation_id"], database_session=memory_database_session)
    
    # Assert
    with pytest.raises(NoResultFound):
        get(invitation_id=existing_invitation["invitation_id"], database_session=memory_database_session)

def test_remove_invalid_id(memory_database_session: Session):
    # Arrange
    invalid_invitation_id = 9999
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        remove(invitation_id=invalid_invitation_id, database_session=memory_database_session)

def test_remove_edgecase_zero_id(memory_database_session: Session):
    # Arrange
    zero_invitation_id = 0
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        remove(invitation_id=zero_invitation_id, database_session=memory_database_session)

"""Andere Operationen"""

# remove_all_by_email Tests
def test_remove_all_by_email_success(memory_database_session: Session):
    # Arrange
    email = "invitee1@example.com"
    
    # Act
    remove_all_by_email(email=email, database_session=memory_database_session)
    
    # Assert
    remaining_invitations = memory_database_session.query(Invitation).filter_by(email=email).all()
    assert len(remaining_invitations) == 0

def test_remove_all_by_email_invalid_email(memory_database_session: Session):
    # Arrange
    non_existent_email = "nonexistent@example.com"
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        remove_all_by_email(email=non_existent_email, database_session=memory_database_session)

def test_remove_all_by_email_edgecase_empty_email(memory_database_session: Session):
    # Arrange
    empty_email = ""
    
    # Act & Assert
    with pytest.raises(NoResultFound):
        remove_all_by_email(email=empty_email, database_session=memory_database_session)

"""Integration - CRUD"""

def test_integration_crud_invitation(memory_database_session: Session):
    # Create an invitation
    new_invitation = create(group_id="11111111-1111-1111-1111-111111111111", email="new@example.com", expires_in_days=7, database_session=memory_database_session)
    assert new_invitation is not None

    # Update the invitation
    updated_invitation = update(invitation_id=new_invitation.invitation_id, email="updated@example.com", expires_in_days=10, database_session=memory_database_session)
    assert updated_invitation is not None
    assert updated_invitation.email == "updated@example.com"

    # Fetch the invitation and check the updated email
    fetched_invitation = get(invitation_id=new_invitation.invitation_id, database_session=memory_database_session)
    assert fetched_invitation is not None
    assert fetched_invitation.email == "updated@example.com"

    # remove the invitation
    remove(new_invitation.invitation_id, memory_database_session)

    # Ensure the invitation no longer exists
    with pytest.raises(NoResultFound):
        get(new_invitation.invitation_id, memory_database_session)
