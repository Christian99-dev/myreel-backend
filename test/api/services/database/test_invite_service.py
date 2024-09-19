from datetime import timedelta

import pytest
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from api.models.database.model import Invitation
from api.services.database.invite import (create, get, remove,
                                          remove_all_by_email_and_group_id, update)
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

def test_create_edgcase_double(memory_database_session: Session):
    # Arrange
    group_id = "11111111-1111-1111-1111-111111111111"
    email = "new_invitee@example.com"
    expires_in_days = 7
    
    # Act
    first_invitation = create(group_id=group_id, email=email, expires_in_days=expires_in_days, database_session=memory_database_session)
    
    # Assert
    assert first_invitation is not None
    assert first_invitation.group_id == group_id
    assert first_invitation.email == email
    assert first_invitation.expires_at == first_invitation.created_at + timedelta(days=expires_in_days)


    # Arrange
    group_id = "11111111-1111-1111-1111-111111111111"
    email = "new_invitee@example.com"
    expires_in_days = 7
    
    # Act
    secound_invitation = create(group_id=group_id, email=email, expires_in_days=expires_in_days, database_session=memory_database_session)
    
    # Assert
    assert secound_invitation is not None
    assert secound_invitation.group_id == group_id
    assert secound_invitation.email == email
    assert secound_invitation.expires_at == secound_invitation.created_at + timedelta(days=expires_in_days)

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
def test_remove_all_by_email_and_group_success(memory_database_session: Session):
    # Arrange
    email = "invitee1@example.com"
    group_id = "11111111-1111-1111-1111-111111111111"
    
    # Act
    remove_all_by_email_and_group_id(email=email, group_id=group_id, database_session=memory_database_session)
    
    # Assert: Ensure only invitations for the specified group are deleted
    remaining_invitations = memory_database_session.query(Invitation).filter_by(email=email, group_id=group_id).all()
    assert len(remaining_invitations) == 0

def test_remove_all_by_email_and_group_invalid_email(memory_database_session: Session):
    # Arrange
    non_existent_email = "nonexistent@example.com"
    group_id = "11111111-1111-1111-1111-111111111111"
    
    # Act & Assert: Ensure NoResultFound is raised for invalid email
    with pytest.raises(NoResultFound):
        remove_all_by_email_and_group_id(email=non_existent_email, group_id=group_id, database_session=memory_database_session)

def test_remove_all_by_email_and_group_edgecase_empty_email(memory_database_session: Session):
    # Arrange
    empty_email = ""
    group_id = "11111111-1111-1111-1111-111111111111"
    
    # Act & Assert: Ensure NoResultFound is raised for empty email
    with pytest.raises(NoResultFound):
        remove_all_by_email_and_group_id(email=empty_email, group_id=group_id, database_session=memory_database_session)


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

def test_integration_create_multiple_invites_same_email(memory_database_session: Session):

    # Arrange
    group_id_1 = "11111111-1111-1111-1111-111111111111"
    group_id_2 = "22222222-2222-2222-2222-222222222222"
    email = "hallo@example.com"

    # Act: Create two invites for the same email and group
    invite_1 = create(group_id=group_id_1, email=email, expires_in_days=7, database_session=memory_database_session)
    invite_2 = create(group_id=group_id_1, email=email, expires_in_days=7, database_session=memory_database_session)

    # Act: Create another invite for the same email but a different group
    invite_3 = create(group_id=group_id_2, email=email, expires_in_days=7, database_session=memory_database_session)

    # Assert: All three invites should be created
    assert invite_1 is not None
    assert invite_2 is not None
    assert invite_3 is not None

    # Check that all three invites exist in the database
    invites_in_db = memory_database_session.query(Invitation).filter_by(email=email).all()
    assert len(invites_in_db) == 3

    # Ensure that invites 1 and 2 are for the same group and have unique IDs
    assert invites_in_db[0].group_id == group_id_1
    assert invites_in_db[1].group_id == group_id_1
    assert invites_in_db[0].invitation_id != invites_in_db[1].invitation_id != invites_in_db[2].invitation_id

    # Ensure that invite 3 is for the other group
    assert invites_in_db[2].group_id == group_id_2

    # Ensure all invitations are for the same email
    assert all(invite.email == email for invite in invites_in_db)

    # Ensure that all invites are unique
    invite_ids = [invite.invitation_id for invite in invites_in_db]
    assert len(invite_ids) == len(set(invite_ids))  # No duplicates in IDs

def test_integration_remove_by_email_and_group_id(memory_database_session: Session):
    # Arrange
    group_id_1 = "11111111-1111-1111-1111-111111111111"
    group_id_2 = "22222222-2222-2222-2222-222222222222"
    email = "integration_test@example.com"

    # Act: Create two invites for the same email and group 1
    invite_1 = create(group_id=group_id_1, email=email, expires_in_days=7, database_session=memory_database_session)
    invite_2 = create(group_id=group_id_1, email=email, expires_in_days=7, database_session=memory_database_session)

    # Act: Create another invite for the same email but group 2
    invite_3 = create(group_id=group_id_2, email=email, expires_in_days=7, database_session=memory_database_session)

    # Assert: All three invites should be created
    assert invite_1 is not None
    assert invite_2 is not None
    assert invite_3 is not None

    # Step 1: Verify that all three invitations exist in the database
    invites_in_db = memory_database_session.query(Invitation).filter_by(email=email).all()
    assert len(invites_in_db) == 3

    # Step 2: Remove invitations for group 1
    remove_all_by_email_and_group_id(email=email, group_id=group_id_1, database_session=memory_database_session)

    # Step 3: Verify that only the invitation for group 2 remains
    remaining_invitations = memory_database_session.query(Invitation).filter_by(email=email).all()
    assert len(remaining_invitations) == 1
    assert remaining_invitations[0].group_id == group_id_2
