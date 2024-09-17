from sqlalchemy.orm import Session

from api.models.database.model import LoginRequest, OccupiedSlot, User
from api.services.database.user import create, get, get_user_by_email, remove
from api.utils.database.create_uuid import create_uuid
from mock.database.data import data


# create
def test_create(memory_database_session: Session):
    # Define user data
    group_id = "11111111-1111-1111-1111-111111111111"
    role = "admin"
    name = "Test User"
    email = "testuser@example.com"
    
    # Create a new user
    new_user = create(group_id, role, name, email, memory_database_session)
    
    # Verify the user is created and has the correct data
    assert new_user is not None
    assert new_user.name == name
    assert new_user.email == email
    assert new_user.role == role
    assert new_user.group_id == group_id
    
    # Verify: Ensure the user was actually added to the database
    user_in_database_session = memory_database_session.query(User).filter_by(user_id=new_user.user_id).one_or_none()
    assert user_in_database_session is not None
    assert user_in_database_session.group_id == group_id
    assert user_in_database_session.role == role
    assert user_in_database_session.name == name
    assert user_in_database_session.email == email

# get
def test_get(memory_database_session: Session):
    # Assume the first user from the test data is used
    user_id = data["users"][0]["user_id"]
    retrieved_user = get(user_id, memory_database_session)
    
    assert retrieved_user is not None
    assert retrieved_user.user_id == user_id
    assert retrieved_user.name == data["users"][0]["name"]
    assert retrieved_user.email == data["users"][0]["email"]
    assert retrieved_user.role == data["users"][0]["role"]
    assert retrieved_user.group_id == data["users"][0]["group_id"]
    
def test_get_user_failed(memory_database_session: Session):
    # Define a non-existent user ID
    non_existent_user_id = 9999
    
    # Try to fetch the user by the non-existent ID
    fetched_user = get(non_existent_user_id, memory_database_session)
    
    # Verify that no user is found
    assert fetched_user is None
    
# remove
def test_remove_user(memory_database_session: Session):
    # Arrange: Verwende einen vorhandenen User
    existing_user = memory_database_session.query(User).first()

    # Act: Lösche den User
    result = remove(existing_user.user_id, memory_database_session)

    # Assert: Überprüfe, dass der User erfolgreich gelöscht wurde
    assert result is True

    # Verify: Stelle sicher, dass der User nicht mehr in der Datenbank vorhanden ist
    user_in_database_session = memory_database_session.query(User).filter_by(user_id=existing_user.user_id).one_or_none()
    assert user_in_database_session is None

    # cascading: User -> OccupiedSlot, LoginRequest
    occupied_slots_in_database_session = memory_database_session.query(OccupiedSlot).filter_by(user_id=existing_user.user_id).all()
    login_requests_in_database_session = memory_database_session.query(LoginRequest).filter_by(user_id=existing_user.user_id).all()
    assert len(occupied_slots_in_database_session) == 0
    assert len(login_requests_in_database_session) == 0

def test_remove_user_failed(memory_database_session: Session):
    # Arrange: Verwende eine ungültige user_id
    non_existent_user_id = 9999

    # Act: Versuche, den User mit der ungültigen ID zu löschen
    result = remove(non_existent_user_id, memory_database_session)

    # Assert: Stelle sicher, dass kein User gelöscht wird
    assert result is False
    
# get user by email
def test_get_user_by_email_success(memory_database_session: Session):
    # Arrange: Verwende eine existierende E-Mail-Adresse aus den Testdaten
    test_email = data["users"][0]["email"]
    
    # Act: Versuche, den Benutzer anhand der E-Mail-Adresse abzurufen
    retrieved_user = get_user_by_email(test_email, memory_database_session)
    
    # Assert: Überprüfe, dass der Benutzer korrekt abgerufen wurde
    assert retrieved_user is not None
    assert retrieved_user.email == test_email
    assert retrieved_user.name == data["users"][0]["name"]
    assert retrieved_user.user_id == data["users"][0]["user_id"]
    assert retrieved_user.group_id == data["users"][0]["group_id"]
    assert retrieved_user.role == data["users"][0]["role"]

def test_get_user_by_email_not_found(memory_database_session: Session):
    # Arrange: Verwende eine E-Mail-Adresse, die nicht existiert
    non_existent_email = "nonexistent@example.com"
    
    # Act: Versuche, den Benutzer anhand der nicht existierenden E-Mail-Adresse abzurufen
    retrieved_user = get_user_by_email(non_existent_email, memory_database_session)
    
    # Assert: Überprüfe, dass kein Benutzer abgerufen wurde
    assert retrieved_user is None