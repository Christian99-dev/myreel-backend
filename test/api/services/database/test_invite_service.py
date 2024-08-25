from datetime import datetime, timedelta
from api.models.database.model import Invitation
from api.services.database.invite import create, delete
from api.mock.database.model import model

# create
def test_create(db_memory):
    group_id = model.groups[0].group_id
    email = "test@example.com"
    invitation = create(group_id=group_id, email=email, db=db_memory)

    assert invitation.group_id == group_id
    assert invitation.email == email
    assert isinstance(invitation.token, str)
    assert invitation.created_at <= datetime.now()
    assert invitation.expires_at == invitation.created_at + timedelta(days=7)

# delete
def test_delete(db_memory):
    group_id = model.groups[0].group_id
    email = "test@example.com"
    invitation = create(group_id=group_id, email=email, db=db_memory)
    invitation_id = invitation.invitation_id

    # Ensure the invitation exists
    assert db_memory.query(Invitation).filter(Invitation.invitation_id == invitation_id).first() is not None

    # Delete the invitation
    delete(invitation_id=invitation_id, db=db_memory)

    # Ensure the invitation no longer exists
    assert db_memory.query(Invitation).filter(Invitation.invitation_id == invitation_id).first() is None
