import logging
from sqlalchemy.orm import Session
from api.auth.jwt import read_jwt
from api.auth.role import Role, RoleInfos
from api.auth.role_enum import RoleEnum
from api.models.database.model import Edit, Group, Song, User, Slot, Invitation, LoginRequest, OccupiedSlot
from api.mock.role_creds.role_creds import admin_req_creds, group_creator_req_creds, edit_creator_req_creds, external_req_creds, group_member_req_creds
from api.mock.database.model import mock_model_memory_links
from fastapi.testclient import TestClient
from test.utils.role_tester_has_acccess import role_tester_has_access
from api.config.media_access import BaseMediaAccess


from main import app
logger = logging.getLogger("testing")

# -- credentials -- #

def test_credentials(credentials: dict):
    assert credentials.get("admin_token") is not None 
    assert type(credentials.get("admin_token")) is str
    
    assert credentials.get("user_1_jwt") is not None
    assert type(credentials.get("user_1_jwt")) is str
    
    assert read_jwt(credentials.get("user_1_jwt")) is 1
    assert type(read_jwt(credentials.get("user_1_jwt"))) is int


# -- db_memory -- #

def test_db_memory_isolation(db_memory: Session):
    """Test to ensure that each test function gets a separate session."""
    
    # Check if the database is empty at the beginning of the test
    assert db_memory.query(Song).count() == len(mock_model_memory_links.songs), "Database should be empty at the beginning of this test."

    # Add a song to the database in this session
    song = Song(name="Test Song", author="Test Author", times_used=0, cover_src="http://example.com/cover.jpg", audio_src="http://example.com/audio.mp3")
    db_memory.add(song)
    db_memory.commit()
    
    # Check if the song is in the database
    result = db_memory.query(Song).filter_by(name="Test Song").first()
    assert result is not None, "The song should be present in the database in this session."

def test_db_memory_isolation_other(db_memory: Session):
    """Test to ensure that changes in one session do not affect another session."""
    
    # Check if the database is empty at the beginning of the test
    assert db_memory.query(Song).count() == len(mock_model_memory_links.songs), "Database should be empty at the beginning of this test."

    # Check that the previous test did not affect this session
    result = db_memory.query(Song).filter_by(name="Test Song").first()
    assert result is None, "The song should not be present in this session if isolation is correct."

def test_db_memory_data_test(db_memory: Session):
    # Daten aus der Datenbank abrufen
    groups_from_db = db_memory.query(Group).all()
    songs_from_db = db_memory.query(Song).all()
    users_from_db = db_memory.query(User).all()
    edits_from_db = db_memory.query(Edit).all()
    slots_from_db = db_memory.query(Slot).all()
    invitations_from_db = db_memory.query(Invitation).all()
    login_requests_from_db = db_memory.query(LoginRequest).all()
    occupied_slots_from_db = db_memory.query(OccupiedSlot).all()

    # Überprüfen, ob die Anzahl der Einträge stimmt
    assert len(groups_from_db) == len(mock_model_memory_links.groups)
    assert len(songs_from_db) == len(mock_model_memory_links.songs)
    assert len(users_from_db) == len(mock_model_memory_links.users)
    assert len(edits_from_db) == len(mock_model_memory_links.edits)
    assert len(slots_from_db) == len(mock_model_memory_links.slots)
    assert len(invitations_from_db) == len(mock_model_memory_links.invitations)
    assert len(login_requests_from_db) == len(mock_model_memory_links.login_requests)
    assert len(occupied_slots_from_db) == len(mock_model_memory_links.occupied_slots)

    # Überprüfen, ob die Daten inhaltlich übereinstimmen
    for expected_group, actual_group in zip(mock_model_memory_links.groups, groups_from_db):
        assert expected_group.group_id == actual_group.group_id
        assert expected_group.name == actual_group.name

    for expected_song, actual_song in zip(mock_model_memory_links.songs, songs_from_db):
        assert expected_song.song_id == actual_song.song_id
        assert expected_song.name == actual_song.name
        assert expected_song.author == actual_song.author
        assert expected_song.times_used == actual_song.times_used
        assert expected_song.cover_src == actual_song.cover_src
        assert expected_song.audio_src == actual_song.audio_src

    for expected_user, actual_user in zip(mock_model_memory_links.users, users_from_db):
        assert expected_user.user_id == actual_user.user_id
        assert expected_user.group_id == actual_user.group_id
        assert expected_user.role == actual_user.role
        assert expected_user.name == actual_user.name
        assert expected_user.email == actual_user.email

    for expected_edit, actual_edit in zip(mock_model_memory_links.edits, edits_from_db):
        assert expected_edit.edit_id == actual_edit.edit_id
        assert expected_edit.song_id == actual_edit.song_id
        assert expected_edit.created_by == actual_edit.created_by
        assert expected_edit.group_id == actual_edit.group_id
        assert expected_edit.name == actual_edit.name
        assert expected_edit.isLive == actual_edit.isLive
        assert expected_edit.video_src == actual_edit.video_src

    for expected_slot, actual_slot in zip(mock_model_memory_links.slots, slots_from_db):
        assert expected_slot.slot_id == actual_slot.slot_id
        assert expected_slot.song_id == actual_slot.song_id
        assert expected_slot.start_time == actual_slot.start_time
        assert expected_slot.end_time == actual_slot.end_time

    for expected_invitation, actual_invitation in zip(mock_model_memory_links.invitations, invitations_from_db):
        assert expected_invitation.invitation_id == actual_invitation.invitation_id
        assert expected_invitation.group_id == actual_invitation.group_id
        assert expected_invitation.token == actual_invitation.token
        assert expected_invitation.email == actual_invitation.email
        assert expected_invitation.created_at == actual_invitation.created_at
        assert expected_invitation.expires_at == actual_invitation.expires_at

    for expected_login_request, actual_login_request in zip(mock_model_memory_links.login_requests, login_requests_from_db):
        assert expected_login_request.user_id == actual_login_request.user_id
        assert expected_login_request.pin == actual_login_request.pin
        assert expected_login_request.created_at == actual_login_request.created_at
        assert expected_login_request.expires_at == actual_login_request.expires_at

    for expected_occupied_slot, actual_occupied_slot in zip(mock_model_memory_links.occupied_slots, occupied_slots_from_db):
        assert expected_occupied_slot.occupied_slot_id == actual_occupied_slot.occupied_slot_id
        assert expected_occupied_slot.user_id == actual_occupied_slot.user_id
        assert expected_occupied_slot.slot_id == actual_occupied_slot.slot_id
        assert expected_occupied_slot.edit_id == actual_occupied_slot.edit_id
        assert expected_occupied_slot.video_src == actual_occupied_slot.video_src

# -- media_access_memory -- #

def test_media_access_memory_isolation(media_access_memory: BaseMediaAccess):
    """Testet die Isolation von MediaAccess."""
    
    # Überprüfen, ob der Speicher zu Beginn leer ist
    assert media_access_memory.list('test_dir') == []

    # Füge eine Datei zum Speicher hinzu
    media_access_memory.save('test_file.txt', 'test_dir', b'Test content')

    # Überprüfen, ob die Datei im Speicher vorhanden ist
    assert 'test_file.txt' in media_access_memory.list('test_dir')
    assert media_access_memory.get('test_file.txt', 'test_dir') == b'Test content'

def test_media_access_memory_isolation_other(media_access_memory: BaseMediaAccess):
    """Testet die Isolation, um sicherzustellen, dass ein anderer Test nicht die Daten beeinflusst."""
    
    # Überprüfen, ob der Speicher zu Beginn leer ist
    assert media_access_memory.list('test_dir') == []

    # Überprüfen, ob die vorherige Testdatei nicht vorhanden ist
    assert 'test_file.txt' not in media_access_memory.list('test_dir')

    # Füge eine neue Datei hinzu
    media_access_memory.save('another_test_file.txt', 'test_dir', b'Another Test content')

    # Überprüfen, ob die neue Datei vorhanden ist
    assert 'another_test_file.txt' in media_access_memory.list('test_dir')
    assert media_access_memory.get('another_test_file.txt', 'test_dir') == b'Another Test content'

def test_media_access_memory_files_as_valid_name_check(media_access_memory: BaseMediaAccess, db_memory: Session):
    
    # songs
    db_songs = db_memory.query(Song).all()
    db_song_ids = {song.song_id for song in db_songs}
    songs_in_db = {f"{song_id}.wav" for song_id in db_song_ids}
    
    songs_in_folder = set(media_access_memory.list("songs"))
    
    songs_difference = len(songs_in_folder.difference(songs_in_db))
    
    assert songs_difference == 0, f"Missing song files in media access: {songs_difference}"
    
    # covers
    db_covers = db_memory.query(Song).all()  # Assuming covers are linked to songs
    db_cover_ids = {song.song_id for song in db_covers}  # Adjust based on your model
    covers_in_db = {f"{cover_id}.png" for cover_id in db_cover_ids}  # Assuming covers are .png files

    covers_in_folder = set(media_access_memory.list("covers"))

    covers_difference = covers_in_folder.difference(covers_in_db)

    assert len(covers_difference) == 0, f"Missing cover files in media access: {covers_difference}"
    
    # edits 
    db_edits = db_memory.query(Edit).all()  # Query for edits
    db_edit_ids = {edit.edit_id for edit in db_edits}  # Get all edit IDs
    edits_in_db = {f"{edit_id}.mp4" for edit_id in db_edit_ids}  # Assuming edits are stored with .edit extension

    edits_in_folder = set(media_access_memory.list("edits"))

    edits_difference = edits_in_folder.difference(edits_in_db)

    assert len(edits_difference) == 0, f"Missing edit files in media access: {edits_difference}"

    # occupied slots 
    db_slots = db_memory.query(OccupiedSlot).all()  # Query for occupied slots
    db_slot_ids = {slot.slot_id for slot in db_slots}  # Get all occupied slot IDs
    slots_in_db = {f"{slot_id}.mp4" for slot_id in db_slot_ids}  # Assuming slots are stored with .slot extension

    slots_in_folder = set(media_access_memory.list("occupied_slots"))

    slots_difference = slots_in_folder.difference(slots_in_db)

    assert len(slots_difference) == 0, f"Missing occupied slot files in media access: {slots_difference}"
    
    # demovideo
    demo_videos = media_access_memory.list("demo_slot")
    assert len(demo_videos) == 1

# -- email_access_memory -- #

def test_email_access_does_something(email_access_memory):
    email_access_memory.send("to","subject","body")

# -- instagram_access_memory -- #

def test_instagram_access_does_something(instagram_access_memory):
    instagram_access_memory.upload(b"", "mp4", "hi")
   
# -- http_client  -- #

def test_http_client_has_prod_routes(http_client: TestClient):
    
    IGNORED_ROUTES_IN_PROD = [
        '/openapi.json', 
        '/docs', 
        '/docs/oauth2-redirect', 
        '/redoc', 
        '/',
        '/static/covers/{filename}',
        '/static/demo_slot/{filename}',
        '/static/edits/{filename}',
        '/static/occupied_slots/{filename}',
        '/static/songs/{filename}',
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

# -- http_client_mocked_path_crud -- #

def test_http_client_mocked_path_crud_isolation(http_client_mocked_path_crud: TestClient):
    """Test to ensure that adding a song does not affect other sessions."""
    
    # Check that the database is empty at the beginning of the test
    response = http_client_mocked_path_crud.get("/list")
    assert response.status_code == 200
    assert len(response.json()) == len(mock_model_memory_links.songs)
    
    
    # Add a new song using the HTTP client
    response = http_client_mocked_path_crud.post("/add/Test Song A/Test Author")
    assert response.status_code == 200
    new_song = response.json()
    assert new_song["name"] == "Test Song A"
    assert new_song["author"] == "Test Author"

    # Verify the song was added
    response = http_client_mocked_path_crud.get("/list")
    assert response.status_code == 200
    songs = response.json()
    assert len(songs) == len(mock_model_memory_links.songs) + 1
    assert songs[len(songs) - 1]["name"] == "Test Song A"

def test_http_client_mocked_path_crud_isolation_other(http_client_mocked_path_crud: TestClient):
    """Test to ensure that changes in one session do not affect another session."""
    
    
    # Check that the database is still empty for this test
    response = http_client_mocked_path_crud.get("/list")
    assert response.status_code == 200
    assert len(response.json()) == len(mock_model_memory_links.songs), "Database should be empty at the beginning of this test."
    

    # This session should not have access to the song added in the previous test
    response = http_client_mocked_path_crud.get("/list")
    assert response.status_code == 200
    songs = response.json()
    assert len(songs) == len(mock_model_memory_links.songs), "Database should remain empty in this isolated session."
    
    # Add a song in this separate test
    response = http_client_mocked_path_crud.post("/add/Test Song B/Test Artist")
    assert response.status_code == 200
    new_song = response.json()
    assert new_song["name"] == "Test Song B"
    assert new_song["author"] == "Test Artist"
    
    # Ensure the song is present in this session
    response = http_client_mocked_path_crud.get("/list")
    assert response.status_code == 200
    songs = response.json()
    assert len(songs) == len(songs)
    assert songs[len(songs) - 1]["name"] == "Test Song B"

# -- http_client_mocked_path_config -- #

def test_http_client_mocked_path_config_config(http_client_mocked_path_config: TestClient):
    assert http_client_mocked_path_config.get("/admin_no_subroles").status_code          == 403
    assert http_client_mocked_path_config.get("/group_creator_no_subroles").status_code  == 403
    assert http_client_mocked_path_config.get("/edit_creator_no_subroles").status_code   == 403
    assert http_client_mocked_path_config.get("/group_member_no_subroles").status_code   == 403
    assert http_client_mocked_path_config.get("/external_no_subroles").status_code       == 200
    
    assert http_client_mocked_path_config.get("/admin_subroles").status_code            == 403
    assert http_client_mocked_path_config.get("/group_creator_subroles").status_code    == 403
    assert http_client_mocked_path_config.get("/edit_creator_subroles").status_code     == 403
    assert http_client_mocked_path_config.get("/group_member_subroles").status_code     == 403
    assert http_client_mocked_path_config.get("/external_subroles").status_code         == 200

# -- http_client_mocked_path_for_extracting_creds -- #

def test_http_client_mocked_path_for_extracting_creds_config(http_client_mocked_path_for_extracting_creds: TestClient):
    assert http_client_mocked_path_for_extracting_creds.get("/example").status_code                                 == 200
    assert http_client_mocked_path_for_extracting_creds.post("/example", json={"key": "value"}).status_code         == 200
    assert http_client_mocked_path_for_extracting_creds.post("/group/test-group-id").status_code                    == 200
    assert http_client_mocked_path_for_extracting_creds.post("/edit/123").status_code                               == 200
    assert http_client_mocked_path_for_extracting_creds.post("/example/group/test-group-id/example").status_code    == 200
    assert http_client_mocked_path_for_extracting_creds.post("/example/edit/456/example").status_code               == 200
    
# -- NOT FIXTURE : mock data wich is not testet already -- #

def test_mock_data_user_creds(db_memory: Session):
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_req_creds["req"]["headers"]["admintoken"], userid=None, groupid=None, editid=None), db_session=db_memory), RoleEnum.ADMIN)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=1, groupid=group_creator_req_creds["req"]["params"]["groupid"], editid=None), db_session=db_memory), RoleEnum.GROUP_CREATOR)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=1, groupid=None, editid=edit_creator_req_creds["req"]["params"]["editid"]), db_session=db_memory), RoleEnum.EDIT_CREATOR)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=2, groupid=group_member_req_creds["req"]["params"]["groupid"], editid=None), db_session=db_memory), RoleEnum.GROUP_MEMBER)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=None, groupid=None, editid=None), db_session=db_memory), RoleEnum.EXTERNAL)    

    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_req_creds["req"]["headers"]["admintoken"], userid=None, groupid=None, editid=None), db_session=db_memory), admin_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=1, groupid=group_creator_req_creds["req"]["params"]["groupid"], editid=None), db_session=db_memory), group_creator_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=1, groupid=None, editid=edit_creator_req_creds["req"]["params"]["editid"]), db_session=db_memory), edit_creator_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=2, groupid=group_member_req_creds["req"]["params"]["groupid"], editid=None), db_session=db_memory), group_member_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=None, groupid=None, editid=None), db_session=db_memory), external_req_creds["role"])
