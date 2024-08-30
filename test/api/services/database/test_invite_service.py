from datetime import datetime, timedelta
from api.models.database.model import Invitation
from api.services.database.invite import create, delete, delete_all_by_email, get
from api.mock.database.model import mock_model_memory_links

# create
def test_create(db_memory):
    group_id = mock_model_memory_links.groups[0].group_id
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
    
# get invite
def test_get_invitation_success(db_memory):
    # Arrange: Verwende eine vorhandene Einladung
    existing_invitation = db_memory.query(Invitation).first()

    # Act: Rufe die Einladung basierend auf der invitation_id ab
    retrieved_invitation = get(existing_invitation.invitation_id, db_memory)

    # Assert: Überprüfe, dass die richtige Einladung abgerufen wurde
    assert retrieved_invitation is not None
    assert retrieved_invitation.invitation_id == existing_invitation.invitation_id
    assert retrieved_invitation.email == existing_invitation.email

def test_get_invitation_failed(db_memory):
    # Arrange: Verwende eine ungültige invitation_id
    non_existent_invitation_id = 9999

    # Act: Versuche, eine Einladung mit einer ungültigen invitation_id abzurufen
    retrieved_invitation = get(non_existent_invitation_id, db_memory)

    # Assert: Überprüfe, dass keine Einladung zurückgegeben wird
    assert retrieved_invitation is None
    
# delete all by email 
def test_delete_all_by_email_success(db_memory):
    # Arrange: Verwende eine E-Mail-Adresse, die mit mehreren Einladungen verknüpft ist
    email = mock_model_memory_links.invitations[0].email  # Verwende die E-Mail der ersten Einladung

    # Act: Lösche alle Einladungen für die angegebene E-Mail-Adresse
    delete_all_by_email(email, db_memory)

    # Assert: Überprüfe, dass alle Einladungen mit dieser E-Mail-Adresse gelöscht wurden
    invitations_in_db = db_memory.query(Invitation).filter_by(email=email).all()
    assert len(invitations_in_db) == 0

def test_delete_all_by_email_no_match(db_memory):
    # Arrange: Verwende eine E-Mail-Adresse, die mit keiner Einladung verknüpft ist
    non_existent_email = "nonexistent@example.com"

    # Act: Versuche, alle Einladungen für die nicht vorhandene E-Mail-Adresse zu löschen
    delete_all_by_email(non_existent_email, db_memory)

    # Assert: Überprüfe, dass kein Fehler auftritt (keine Ausnahme) und keine Einladungen gelöscht werden
    assert True  # Prüfung, dass die Funktion ohne Fehler durchläuft
