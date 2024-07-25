import logging
from sqlalchemy.orm import Session
from api.auth.role import Role, RoleInfos
from api.auth.role_enum import RoleEnum
from api.models.database.model import Song
from test.utils.role_tester_has_acccess import role_tester_has_access
from test.utils.mock_roles_creds import admin_req_creds, group_creator_req_creds, group_member_req_creds, external_req_creds, edit_creator_req_creds
from test.utils.test_model import test_model
from fastapi.testclient import TestClient
from main import app
logger = logging.getLogger("testing")
#TODO SONG
# -- DB SESSIONS -- #

# isolation db session 
def test_db_session_isolation(db_session_empty: Session):
    """Test to ensure that each test function gets a separate session."""
    
    # Check if the database is empty at the beginning of the test
    assert db_session_empty.query(Song).count() == 0, "Database should be empty at the beginning of this test."

    # Add a song to the database in this session
    song = Song(name="Test Song", author="Test Author", times_used=0, cover_src="http://example.com/cover.jpg", audio_src="http://example.com/audio.mp3")
    db_session_empty.add(song)
    db_session_empty.commit()
    
    # Check if the song is in the database
    result = db_session_empty.query(Song).filter_by(name="Test Song").first()
    assert result is not None, "The song should be present in the database in this session."

def test_db_session_isolation_other(db_session_empty: Session):
    """Test to ensure that changes in one session do not affect another session."""
    
    # Check if the database is empty at the beginning of the test
    assert db_session_empty.query(Song).count() == 0, "Database should be empty at the beginning of this test."

    # Check that the previous test did not affect this session
    result = db_session_empty.query(Song).filter_by(name="Test Song").first()
    assert result is None, "The song should not be present in this session if isolation is correct."
    
# isolation db session filled
def test_db_session_isolation_filled(db_session_filled: Session):
    """Test to ensure that each test function gets a separate session."""
    
    # Check if the database is empty at the beginning of the test
    assert db_session_filled.query(Song).count() == len(test_model.songs), "Database should be empty at the beginning of this test."

    # Add a song to the database in this session
    song = Song(name="Test Song", author="Test Author", times_used=0, cover_src="http://example.com/cover.jpg", audio_src="http://example.com/audio.mp3")
    db_session_filled.add(song)
    db_session_filled.commit()
    
    # Check if the song is in the database
    result = db_session_filled.query(Song).filter_by(name="Test Song").first()
    assert result is not None, "The song should be present in the database in this session."

def test_db_session_isolation_other_filled(db_session_filled: Session):
    """Test to ensure that changes in one session do not affect another session."""
    
    # Check if the database is empty at the beginning of the test
    assert db_session_filled.query(Song).count() == len(test_model.songs), "Database should be empty at the beginning of this test."

    # Check that the previous test did not affect this session
    result = db_session_filled.query(Song).filter_by(name="Test Song").first()
    assert result is None, "The song should not be present in this session if isolation is correct."

# -- HTTP CLIENTS -- #

# app client routes empty and not empty
def test_app_client_empty_has_no_routes(app_client_empty: TestClient):
    """Test to ensure that each test function gets a separate client session with no routes."""
    
    response = app_client_empty.get("/songs")
    assert response.status_code == 404, "Route should not exist in this client."

# app client PROD routes are mirrored
def test_app_client_filled_has_prod_routes(app_client_prod_routes: TestClient):
    """Test to ensure that the app has the correct routes."""
    # Get the list of routes from the production app
    prod_routes         = [route.path for route in app.router.routes]
    filtered_prod_routes = [route for route in prod_routes if route not in ['/openapi.json', '/docs', '/docs/oauth2-redirect', '/redoc']]

    # Get the list of routes from the test client
    response = app_client_prod_routes.get("/openapi.json")
    test_client_routes  = [path for path in response.json()["paths"].keys()]
    assert response.status_code == 200
    
    # Compare routes
    for route in filtered_prod_routes:
        assert route in test_client_routes, f"Expected route {route} not found in the test client app."

    for route in test_client_routes:
        assert route in filtered_prod_routes, f"Unexpected route {route} found in the test client app."

# app client PROD
def notest_app_client_isolation_filled(app_client_prod_routes: TestClient):
    """Test to ensure that each test function gets a separate client session with filled database."""
    
    response = app_client_prod_routes.get("/song/list")
    assert response.status_code == 200
    response = response.json()
    songs = response.get("songs")
    assert len(songs) == len(test_model.songs), "Database should be filled with test data at the beginning of this test."

    # Add a song using the client
    create_response = app_client_prod_routes.post("/song/create", json={
        "name": "Das ist ein song",
        "author": "Hallo",
        "cover_src": "http://example.com/cover.jpg",
        "audio_src": "http://example.com/audio.mp3"
    })
    assert create_response.status_code == 200

    create_response_data = create_response.json()
    song_id = create_response_data.get("song_id")

    get_response = app_client_prod_routes.get(f"/song/get/{song_id}")
    assert get_response.status_code == 200
    
    list_response = app_client_prod_routes.get("/song/list")
    assert list_response.status_code == 200
    new_songs = list_response.json().get("songs")
    assert len(new_songs) == len(test_model.songs) + 1

def notest_app_client_isolation_other_filled(app_client_prod_routes: TestClient):
    """Test to ensure that changes in one client session do not affect another session."""
    
    response = app_client_prod_routes.get("/song/list")
    assert response.status_code == 200
    songs = response.json().get("songs")
    assert len(songs) == len(test_model.songs), "Database should be filled with test data at the beginning of this test."
    assert not any(song["name"] == "Test Song" for song in songs), "The song should not be present in this session if isolation is correct."

# app client MOCK_ROUTES are there with middleware
def test_setup_routes(app_client_mock_routes_middleware):
    assert app_client_mock_routes_middleware.get("/admin_no_subroles").status_code          == 403
    assert app_client_mock_routes_middleware.get("/group_creator_no_subroles").status_code  == 403
    assert app_client_mock_routes_middleware.get("/edit_creator_no_subroles").status_code   == 403
    assert app_client_mock_routes_middleware.get("/group_member_no_subroles").status_code   == 403
    assert app_client_mock_routes_middleware.get("/external_no_subroles").status_code       == 200
    
    assert app_client_mock_routes_middleware.get("/admin_subroles").status_code            == 403
    assert app_client_mock_routes_middleware.get("/group_creator_subroles").status_code    == 403
    assert app_client_mock_routes_middleware.get("/edit_creator_subroles").status_code     == 403
    assert app_client_mock_routes_middleware.get("/group_member_subroles").status_code     == 403
    assert app_client_mock_routes_middleware.get("/external_subroles").status_code         == 200

# -- UTILS -- #

# testing mock roles are configured corretly
def test_setup_roles(db_session_filled):
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_req_creds["req"]["headers"]["admintoken"], userid=None, groupid=None, editid=None), db_session=db_session_filled), RoleEnum.ADMIN)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=1, groupid=group_creator_req_creds["req"]["params"]["groupid"], editid=None), db_session=db_session_filled), RoleEnum.GROUP_CREATOR)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=1, groupid=None, editid=edit_creator_req_creds["req"]["params"]["editid"]), db_session=db_session_filled), RoleEnum.EDIT_CREATOR)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=2, groupid=group_member_req_creds["req"]["params"]["groupid"], editid=None), db_session=db_session_filled), RoleEnum.GROUP_MEMBER)
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=None, groupid=None, editid=None), db_session=db_session_filled), RoleEnum.EXTERNAL)    

    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=admin_req_creds["req"]["headers"]["admintoken"], userid=None, groupid=None, editid=None), db_session=db_session_filled), admin_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=1, groupid=group_creator_req_creds["req"]["params"]["groupid"], editid=None), db_session=db_session_filled), group_creator_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=1, groupid=None, editid=edit_creator_req_creds["req"]["params"]["editid"]), db_session=db_session_filled), edit_creator_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=2, groupid=group_member_req_creds["req"]["params"]["groupid"], editid=None), db_session=db_session_filled), group_member_req_creds["role"])
    role_tester_has_access(Role(role_infos=RoleInfos(admintoken=None, userid=None, groupid=None, editid=None), db_session=db_session_filled), external_req_creds["role"])
