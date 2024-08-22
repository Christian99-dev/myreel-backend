from datetime import datetime, timedelta
from api.models.database.model import Invitation
from api.services.database.invite import create, delete
from test.utils.testing_data.db.model import group_id_1

def test_create(db_session_filled):
    email = "test@example.com"
    invitation = create(group_id=group_id_1, email=email, db=db_session_filled)

    assert invitation.group_id == group_id_1
    assert invitation.email == email
    assert isinstance(invitation.token, str)
    assert invitation.created_at <= datetime.now()
    assert invitation.expires_at == invitation.created_at + timedelta(days=7)

def test_delete(db_session_filled):
    
    email = "test@example.com"
    invitation = create(group_id=group_id_1, email=email, db=db_session_filled)
    invitation_id = invitation.invitation_id

    # Ensure the invitation exists
    assert db_session_filled.query(Invitation).filter(Invitation.invitation_id == invitation_id).first() is not None

    # Delete the invitation
    delete(invitation_id=invitation_id, db=db_session_filled)

    # Ensure the invitation no longer exists
    assert db_session_filled.query(Invitation).filter(Invitation.invitation_id == invitation_id).first() is None