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
def test_delete_invitation(db_memory):
    # Arrange: Verwende eine vorhandene Einladung
    existing_invitation = db_memory.query(Invitation).first()

    # Act: Lösche die Einladung
    delete(existing_invitation.invitation_id, db_memory)

    # Verify: Stelle sicher, dass die Einladung nicht mehr in der Datenbank vorhanden ist
    invitation_in_db = db_memory.query(Invitation).filter_by(invitation_id=existing_invitation.invitation_id).one_or_none()
    assert invitation_in_db is None


def test_delete_invitation_failed(db_memory):
    # Arrange: Verwende eine ungültige invitation_id
    non_existent_invitation_id = 9999

    # Act: Versuche, die Einladung mit der ungültigen ID zu löschen
    delete(non_existent_invitation_id, db_memory)

    # Assert: Stelle sicher, dass kein Fehler auftritt (keine Ausnahme)
    assert True  # Prüfung, dass die Funktion ohne Fehler durchläuft
    

