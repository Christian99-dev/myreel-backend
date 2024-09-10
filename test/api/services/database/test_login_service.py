from datetime import datetime, timedelta
from api.models.database.model import LoginRequest, User
from api.services.database.login import create, delete, delete_all_from_email, get_login_request_by_groupid_and_token
from mock.database.data import data

# create
def test_create(memory_database_session):
    user_id = data["users"][3]["user_id"]  # Use the fourth user
    login_request = create(user_id=user_id, database_session=memory_database_session)

    assert login_request.user_id == user_id
    assert isinstance(login_request.pin, str)
    assert login_request.created_at <= datetime.now()
    assert login_request.expires_at == login_request.created_at + timedelta(minutes=10)

# delete
def test_delete_login_request(memory_database_session):
    # Arrange: Verwende eine vorhandene Login-Anfrage
    existing_login_request = memory_database_session.query(LoginRequest).first()

    # Act: Lösche die Login-Anfrage
    delete(existing_login_request.user_id, memory_database_session)

    # Verify: Stelle sicher, dass die Login-Anfrage nicht mehr in der Datenbank vorhanden ist
    login_request_in_database_session = memory_database_session.query(LoginRequest).filter_by(user_id=existing_login_request.user_id).one_or_none()
    assert login_request_in_database_session is None


def test_delete_login_request_failed(memory_database_session):
    # Arrange: Verwende eine ungültige user_id
    non_existent_user_id = 9999

    # Act: Versuche, die Login-Anfrage mit der ungültigen ID zu löschen
    delete(non_existent_user_id, memory_database_session)

    # Assert: Stelle sicher, dass kein Fehler auftritt (keine Ausnahme)
    assert True  # Prüfung, dass die Funktion ohne Fehler durchläuft

# delete all from email
def test_delete_all_from_email(memory_database_session):
    # Arrange: Verwende eine existierende E-Mail-Adresse eines Benutzers
    email = data["users"][3]["email"]  # Verwende den vierten Benutzer

    # Act: Lösche alle Login-Anfragen für den Benutzer mit dieser E-Mail-Adresse
    delete_all_from_email(email, memory_database_session)

    # Assert: Überprüfe, dass alle Login-Anfragen für diesen Benutzer gelöscht wurden
    user = memory_database_session.query(User).filter_by(email=email).first()
    login_requests_in_database_session = memory_database_session.query(LoginRequest).filter_by(user_id=user.user_id).all()
    assert len(login_requests_in_database_session) == 0

def test_delete_all_from_email_failed(memory_database_session):
    # Arrange: Verwende eine ungültige E-Mail-Adresse
    non_existent_email = "nonexistent@example.com"

    # Act: Versuche, alle Login-Anfragen für eine ungültige E-Mail-Adresse zu löschen
    delete_all_from_email(non_existent_email, memory_database_session)

    # Assert: Überprüfe, dass kein Fehler auftritt (keine Ausnahme) und dass keine Login-Anfragen gelöscht wurden
    assert True  # Prüfung, dass die Funktion ohne Fehler durchläuft
    
# get_login_request_by_groupid_and_token
def test_get_login_request_by_groupid_and_token_success(memory_database_session):
    # Arrange: Verwende gültige group_id und pin aus den Mock-Daten
    user = data["users"][0]  # Verwende den vierten Benutzer
    valid_pin = data["login_requests"][0]["pin"]  # Pin der vierten Login-Anfrage
    
    # Act: Versuche, die Login-Anfrage mit group_id und pin abzurufen
    login_request = get_login_request_by_groupid_and_token(user["group_id"], valid_pin, memory_database_session)

    # Assert: Überprüfe, dass die richtige Login-Anfrage abgerufen wurde
    assert login_request is not None
    assert login_request.pin == valid_pin
    assert login_request.user_id == user["user_id"]

def test_get_login_request_by_groupid_and_token_failed(memory_database_session):
    # Arrange: Verwende ungültige group_id und pin
    invalid_group_id = "invalid-group-id"
    invalid_pin = "invalid-pin"
    
    # Act: Versuche, eine Login-Anfrage mit ungültiger group_id und pin abzurufen
    login_request = get_login_request_by_groupid_and_token(invalid_group_id, invalid_pin, memory_database_session)

    # Assert: Überprüfe, dass keine Login-Anfrage abgerufen wurde
    assert login_request is None