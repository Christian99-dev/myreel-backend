from datetime import datetime, timedelta
from api.models.database.model import LoginRequest
from api.services.database.login import create, delete
from api.mock.database.model import model

# create
def test_create(db_memory):
    user_id = model.users[3].user_id  # Use the fourth user
    login_request = create(user_id=user_id, db=db_memory)

    assert login_request.user_id == user_id
    assert isinstance(login_request.pin, str)
    assert login_request.created_at <= datetime.now()
    assert login_request.expires_at == login_request.created_at + timedelta(minutes=10)

# delete
def test_delete_login_request(db_memory):
    # Arrange: Verwende eine vorhandene Login-Anfrage
    existing_login_request = db_memory.query(LoginRequest).first()

    # Act: Lösche die Login-Anfrage
    delete(existing_login_request.user_id, db_memory)

    # Verify: Stelle sicher, dass die Login-Anfrage nicht mehr in der Datenbank vorhanden ist
    login_request_in_db = db_memory.query(LoginRequest).filter_by(user_id=existing_login_request.user_id).one_or_none()
    assert login_request_in_db is None


def test_delete_login_request_failed(db_memory):
    # Arrange: Verwende eine ungültige user_id
    non_existent_user_id = 9999

    # Act: Versuche, die Login-Anfrage mit der ungültigen ID zu löschen
    delete(non_existent_user_id, db_memory)

    # Assert: Stelle sicher, dass kein Fehler auftritt (keine Ausnahme)
    assert True  # Prüfung, dass die Funktion ohne Fehler durchläuft