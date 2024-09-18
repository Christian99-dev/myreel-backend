

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.exceptions.files import (DirectoryNotFoundError,
                                           FileDeleteError, FileExistsInSessionError,
                                           FileNotFoundInSessionError)
from api.models.database.model import (Edit, Group, Invitation, LoginRequest,
                                       OccupiedSlot, Slot, Song, User)
from api.sessions.files import BaseFileSessionManager
from main import app
from mock.database.data import data

"""Database"""
def test_memory_database_session_isolation(memory_database_session: Session):
    """Test to ensure that each test function gets a separate session."""
    
    # Check if the database is empty at the beginning of the test
    assert memory_database_session.query(Song).count() == len(data["songs"]), "Database should be empty at the beginning of this test."

    # Add a song to the database in this session
    song = Song(name="Test Song", author="Test Author", times_used=0, cover_src="http://example.com/cover.jpg", audio_src="http://example.com/audio.mp3")
    memory_database_session.add(song)
    memory_database_session.commit()
    
    # Check if the song is in the database
    result = memory_database_session.query(Song).filter_by(name="Test Song").first()
    assert result is not None, "The song should be present in the database in this session."

def test_memory_database_session_isolation_other(memory_database_session: Session):
    """Test to ensure that changes in one session do not affect another session."""
    
    # Check if the database is empty at the beginning of the test
    assert memory_database_session.query(Song).count() == len(data["songs"]), "Database should be empty at the beginning of this test."

    # Check that the previous test did not affect this session
    result = memory_database_session.query(Song).filter_by(name="Test Song").first()
    assert result is None, "The song should not be present in this session if isolation is correct."

def test_memory_database_session_data_test(memory_database_session: Session):
    # Daten aus der Datenbank abrufen
    groups_from_database_session = memory_database_session.query(Group).all()
    songs_from_database_session = memory_database_session.query(Song).all()
    users_from_database_session = memory_database_session.query(User).all()
    edits_from_database_session = memory_database_session.query(Edit).all()
    slots_from_database_session = memory_database_session.query(Slot).all()
    invitations_from_database_session = memory_database_session.query(Invitation).all()
    login_requests_from_database_session = memory_database_session.query(LoginRequest).all()
    occupied_slots_from_database_session = memory_database_session.query(OccupiedSlot).all()

    # Überprüfen, ob die Anzahl der Einträge stimmt
    assert len(groups_from_database_session) == len(data["groups"])
    assert len(songs_from_database_session) == len(data["songs"])
    assert len(users_from_database_session) == len(data["users"])
    assert len(edits_from_database_session) == len(data["edits"])
    assert len(slots_from_database_session) == len(data["slots"])
    assert len(invitations_from_database_session) == len(data["invitations"])
    assert len(login_requests_from_database_session) == len(data["login_requests"])
    assert len(occupied_slots_from_database_session) == len(data["occupied_slots"])

    # Überprüfen, ob die Daten inhaltlich übereinstimmen
    for expected_group, actual_group in zip(data["groups"], groups_from_database_session):
        assert expected_group["group_id"] == actual_group.group_id
        assert expected_group["name"] == actual_group.name

    for expected_song, actual_song in zip(data["songs"], songs_from_database_session):
        assert expected_song["song_id"] == actual_song.song_id
        assert expected_song["name"] == actual_song.name
        assert expected_song["author"] == actual_song.author
        assert expected_song["times_used"] == actual_song.times_used
        assert expected_song["cover_src"] == actual_song.cover_src
        assert expected_song["audio_src"] == actual_song.audio_src

    for expected_user, actual_user in zip(data["users"], users_from_database_session):
        assert expected_user["user_id"] == actual_user.user_id
        assert expected_user["group_id"] == actual_user.group_id
        assert expected_user["role"] == actual_user.role
        assert expected_user["name"] == actual_user.name
        assert expected_user["email"] == actual_user.email

    for expected_edit, actual_edit in zip(data["edits"], edits_from_database_session):
        assert expected_edit["edit_id"] == actual_edit.edit_id
        assert expected_edit["song_id"] == actual_edit.song_id
        assert expected_edit["created_by"] == actual_edit.created_by
        assert expected_edit["group_id"] == actual_edit.group_id
        assert expected_edit["name"] == actual_edit.name
        assert expected_edit["isLive"] == actual_edit.isLive
        assert expected_edit["video_src"] == actual_edit.video_src

    for expected_slot, actual_slot in zip(data["slots"], slots_from_database_session):
        assert expected_slot["slot_id"] == actual_slot.slot_id
        assert expected_slot["song_id"] == actual_slot.song_id
        assert expected_slot["start_time"] == actual_slot.start_time
        assert expected_slot["end_time"] == actual_slot.end_time

    for expected_invitation, actual_invitation in zip(data["invitations"], invitations_from_database_session):
        assert expected_invitation["invitation_id"] == actual_invitation.invitation_id
        assert expected_invitation["group_id"] == actual_invitation.group_id
        assert expected_invitation["token"] == actual_invitation.token
        assert expected_invitation["email"] == actual_invitation.email
        assert expected_invitation["created_at"] == actual_invitation.created_at
        assert expected_invitation["expires_at"] == actual_invitation.expires_at

    for expected_login_request, actual_login_request in zip(data["login_requests"], login_requests_from_database_session):
        assert expected_login_request["user_id"] == actual_login_request.user_id
        assert expected_login_request["pin"] == actual_login_request.pin
        assert expected_login_request["created_at"] == actual_login_request.created_at
        assert expected_login_request["expires_at"] == actual_login_request.expires_at

    for expected_occupied_slot, actual_occupied_slot in zip(data["occupied_slots"], occupied_slots_from_database_session):
        assert expected_occupied_slot["occupied_slot_id"] == actual_occupied_slot.occupied_slot_id
        assert expected_occupied_slot["user_id"] == actual_occupied_slot.user_id
        assert expected_occupied_slot["slot_id"] == actual_occupied_slot.slot_id
        assert expected_occupied_slot["edit_id"] == actual_occupied_slot.edit_id
        assert expected_occupied_slot["video_src"] == actual_occupied_slot.video_src

"""Files"""
def test_file_session_memory_isolation(memory_file_session: BaseFileSessionManager):
    """Testet die Isolation von MediaAccess."""
    
    # Überprüfen, ob der Speicher zu Beginn leer ist
    with pytest.raises(DirectoryNotFoundError):
        memory_file_session.list('test_dir')

    # Füge eine Datei zum Speicher hinzu
    memory_file_session.create('test_file', 'txt', b'Test content', 'test_dir')

    # Überprüfen, ob die Datei im Speicher vorhanden ist
    assert 'test_file.txt' in memory_file_session.list('test_dir')
    assert memory_file_session.get('test_file', 'test_dir') == b'Test content'

    # Versuche, dieselbe Datei erneut zu erstellen, was zu einem Fehler führen sollte
    with pytest.raises(FileExistsInSessionError):
        memory_file_session.create('test_file', 'txt', b'Test content', 'test_dir')

def test_file_session_memory_isolation_other(memory_file_session: BaseFileSessionManager):
    """Testet die Isolation, um sicherzustellen, dass ein anderer Test nicht die Daten beeinflusst."""
    
    # Überprüfen, ob der Speicher zu Beginn leer ist
    with pytest.raises(DirectoryNotFoundError):
        memory_file_session.list('test_dir')

    # Überprüfen, ob die vorherige Testdatei nicht vorhanden ist
    with pytest.raises(DirectoryNotFoundError):
        memory_file_session.get('test_file', 'test_dir')

    # Füge eine neue Datei hinzu
    memory_file_session.create('another_test_file', 'txt', b'Another Test content', 'test_dir')

    # Überprüfen, ob die neue Datei vorhanden ist
    assert 'another_test_file.txt' in memory_file_session.list('test_dir')
    assert memory_file_session.get('another_test_file', 'test_dir') == b'Another Test content'

    # Versuche, eine Datei zu entfernen, die nicht existiert, was zu einem Fehler führen sollte
    with pytest.raises(FileDeleteError):
        memory_file_session.remove('non_existent_file', 'test_dir')

def test_file_session_memory_files_as_valid_name_check(memory_file_session: BaseFileSessionManager, memory_database_session: Session):
    
    # songs
    db_songs = memory_database_session.query(Song).all()
    db_song_ids = {song.song_id for song in db_songs}
    songs_in_database_session = {f"{song_id}.wav" for song_id in db_song_ids}
    
    songs_in_folder = set(memory_file_session.list("songs"))
    
    songs_difference = len(songs_in_folder.difference(songs_in_database_session))
    
    assert songs_difference == 0, f"Missing song files in media access: {songs_difference}"
    
    # covers
    db_covers = memory_database_session.query(Song).all()  # Assuming covers are linked to songs
    db_cover_ids = {song.song_id for song in db_covers}  # Adjust based on your model
    covers_in_database_session = {f"{cover_id}.png" for cover_id in db_cover_ids}  # Assuming covers are .png files

    covers_in_folder = set(memory_file_session.list("covers"))

    covers_difference = covers_in_folder.difference(covers_in_database_session)

    assert len(covers_difference) == 0, f"Missing cover files in media access: {covers_difference}"
    
    # edits 
    db_edits = memory_database_session.query(Edit).all()  # Query for edits
    db_edit_ids = {edit.edit_id for edit in db_edits}  # Get all edit IDs
    edits_in_database_session = {f"{edit_id}.mp4" for edit_id in db_edit_ids}  # Assuming edits are stored with .mp4 extension

    edits_in_folder = set(memory_file_session.list("edits"))

    edits_difference = edits_in_folder.difference(edits_in_database_session)

    assert len(edits_difference) == 0, f"Missing edit files in media access: {edits_difference}"

    # occupied slots 
    db_slots = memory_database_session.query(OccupiedSlot).all()  # Query for occupied slots
    db_slot_ids = {slot.occupied_slot_id for slot in db_slots}  # Get all occupied slot IDs
    slots_in_database_session = {f"{slot_id}.mp4" for slot_id in db_slot_ids}  # Assuming slots are stored with .mp4 extension

    slots_in_folder = set(memory_file_session.list("occupied_slots"))

    slots_difference = slots_in_folder.difference(slots_in_database_session)

    assert len(slots_difference) == 0, f"Missing occupied slot files in media access: {slots_difference}"

    # demovideo
    demo_videos = memory_file_session.list("demo_slot")
    assert len(demo_videos) == 1

"""Email"""
def test_email_session_does_something(memory_email_session):
    memory_email_session.send("to","subject","body")

"""Instagram"""
def test_instagram_session_does_something(memory_instagram_session):
    memory_instagram_session.upload(b"A", "mp4", "hi")
   
"""HTTP Client"""
def test_http_client_has_prod_routes(http_client: TestClient):
    
    IGNORED_ROUTES_IN_PROD = [
        '/openapi.json', 
        '/docs', 
        '/docs/oauth2-redirect', 
        '/redoc', 
        '/',
        '/files/covers/{filename}',
        '/files/demo_slot/{filename}',
        '/files/edits/{filename}',
        '/files/occupied_slots/{filename}',
        '/files/songs/{filename}',
        '/testing/1',
        '/testing/2',
        '/testing/3',
        '/testing/4'
        
    ]
    
    """Test to ensure that the app has the correct routes."""
    # Get the list of routes from the production app
    prod_routes         = [route.path for route in app.router.routes]
    filtered_prod_routes = [route for route in prod_routes if route not in IGNORED_ROUTES_IN_PROD]
    
    # Get the list of routes from the test client
    response = http_client.get("/openapi.json")
    test_client_routes  = [path for path in response.json()["paths"].keys()]
    assert response.status_code == 200
    
    # Compare routes
    for route in filtered_prod_routes:
        assert route in test_client_routes, f"Expected route {route} not found in the test client app."

    for route in test_client_routes:
        assert route in filtered_prod_routes, f"Unexpected route {route} found in the test client app."

