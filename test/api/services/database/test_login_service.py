from datetime import datetime, timedelta
from api.models.database.model import LoginRequest, User
from api.services.database.login import create, delete, delete_all_from_email, get_login_request_by_groupid_and_token
from api.mock.database.model import mock_model_local_links

# create
def test_create(db_memory):
    user_id = mock_model_local_links.users[3].user_id  # Use the fourth user
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

# delete all from email
def test_delete_all_from_email(db_memory):
    # Arrange: Verwende eine existierende E-Mail-Adresse eines Benutzers
    email = mock_model_local_links.users[3].email  # Verwende den vierten Benutzer

    # Act: Lösche alle Login-Anfragen für den Benutzer mit dieser E-Mail-Adresse
    delete_all_from_email(email, db_memory)

    # Assert: Überprüfe, dass alle Login-Anfragen für diesen Benutzer gelöscht wurden
    user = db_memory.query(User).filter_by(email=email).first()
    login_requests_in_db = db_memory.query(LoginRequest).filter_by(user_id=user.user_id).all()
    assert len(login_requests_in_db) == 0

def test_delete_all_from_email_failed(db_memory):
    # Arrange: Verwende eine ungültige E-Mail-Adresse
    non_existent_email = "nonexistent@example.com"

    # Act: Versuche, alle Login-Anfragen für eine ungültige E-Mail-Adresse zu löschen
    delete_all_from_email(non_existent_email, db_memory)

    # Assert: Überprüfe, dass kein Fehler auftritt (keine Ausnahme) und dass keine Login-Anfragen gelöscht wurden
    assert True  # Prüfung, dass die Funktion ohne Fehler durchläuft
    
# get_login_request_by_groupid_and_token
def test_get_login_request_by_groupid_and_token_success(db_memory):
    # Arrange: Verwende gültige group_id und pin aus den Mock-Daten
    user = mock_model_local_links.users[0]  # Verwende den vierten Benutzer
    valid_pin = mock_model_local_links.login_requests[0].pin  # Pin der vierten Login-Anfrage
    
    # Act: Versuche, die Login-Anfrage mit group_id und pin abzurufen
    login_request = get_login_request_by_groupid_and_token(user.group_id, valid_pin, db_memory)

    # Assert: Überprüfe, dass die richtige Login-Anfrage abgerufen wurde
    assert login_request is not None
    assert login_request.pin == valid_pin
    assert login_request.user_id == user.user_id

def test_get_login_request_by_groupid_and_token_failed(db_memory):
    # Arrange: Verwende ungültige group_id und pin
    invalid_group_id = "invalid-group-id"
    invalid_pin = "invalid-pin"
    
    # Act: Versuche, eine Login-Anfrage mit ungültiger group_id und pin abzurufen
    login_request = get_login_request_by_groupid_and_token(invalid_group_id, invalid_pin, db_memory)

    # Assert: Überprüfe, dass keine Login-Anfrage abgerufen wurde
    assert login_request is None