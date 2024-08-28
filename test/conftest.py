import pytest
import logging
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from api.config.media_access import MemoryMediaAccess
from api.middleware.access_handler import AccessHandlerMiddleware
from api.mock.path_config.mock_path_config import mock_path_config
from api.models.database.model import Song
from api.mock.database.fill import fill as fill_db
from api.mock.database.model import mock_model_memory_links
from api.mock.media.fill import fill as fill_media
from api.utils.middleware.get_all_routes import get_all_routes
from api.utils.routes.extract_role_credentials_from_request import extract_role_credentials_from_request
from logging_config import setup_logging_testing
from api.routes.song import router as song_router
from api.config.database import get_db, get_db_memory

# setup logging
setup_logging_testing()
logger = logging.getLogger("testing")

## -- MAIN FIXTURES -- ## 

# Database   : Test_Data 
# Media      : None
# Routes     : None
# Middleware : None
@pytest.fixture(scope="function")
def db_memory():
    session_generator = get_db_memory()  
    session = next(session_generator)
    fill_db(session, mock_model_memory_links)   
    yield session
    
# Database   : None
# Media      : Mock Media
# Routes     : None
# Middleware : None
@pytest.fixture
def media_access_memory():
    media_access_memory = MemoryMediaAccess()
    fill_media(media_access_memory)
    return media_access_memory


# Database   : Test_Data
# Media      : None 
# Routes     : Prod
# Middleware : None 
@pytest.fixture(scope="function")
def http_client(db_memory: Session):
    
    # adding prod routes
    app = FastAPI()
    app.include_router(song_router)
    
    def get_db_override():
        yield db_memory

    # Überschreibe die get_db-Abhängigkeit
    app.dependency_overrides[get_db] = get_db_override

    with TestClient(app) as test_client:
        yield test_client

    # Entferne die Überschreibung nach dem Test
    del app.dependency_overrides[get_db]

## -- SPECIFIC FIXTURES -- ## 

# Database   : Test_Data 
# Media      : None
# Routes     : add and list
# Middleware : None  
# Description : 
# 
# This is mainly for testing the behavoiur of a roundtrip from route to service to database, 
# if no routes in prod are available. so we are just mocking crud operations.
@pytest.fixture(scope="function")
def http_client_mocked_path_crud(db_memory: Session):
    # fresh client
    app = FastAPI()
    
    # CRUD routes for songs
    @app.post("/add/{name}/{author}")
    async def add(name: str, author: str, db: Session = Depends(lambda: db_memory)):
        new_song = Song(name=name, author=author, times_used=0, cover_src="cover_src", audio_src="audio_src")
        db.add(new_song)
        db.commit()
        db.refresh(new_song)
        return new_song

    @app.get("/list")
    async def list(db: Session = Depends(lambda: db_memory)):
        return db.query(Song).all()
    
    # yield client with routes
    with TestClient(app) as test_client:
        yield test_client
        
# Database   : Test_Data 
# Media      : None
# Routes     : for every mocked path one
# Middleware : Access_Handler  
# Description : 
# 
# A fixture where every possible role is has a dedicated path, to test out security access in a non prod env
@pytest.fixture(scope="function")
def http_client_mocked_path_config(db_memory: Session):
    
    # simulating prod api
    app = FastAPI()
    
    # session
    def get_db_override(): 
        yield db_memory
    
    # middleware for access testing 
    app.add_middleware(AccessHandlerMiddleware, path_config=mock_path_config, get_db=get_db_override)
    
    # every endpoints based on testconfig file
    def create_endpoint(m_name: str):
        async def endpoint(request: Request):
            return f"You called {m_name}"
        return endpoint

    for path, method in mock_path_config.get_all_paths_and_methods():
        app.add_api_route(f"{path}", create_endpoint(path), methods=[method])
    
    # yield client with routes
    with TestClient(app) as test_client:
        yield test_client
        
# Database   : Test_Data 
# Media      : None
# Routes     : for body and path params
# Middleware : extracing credentials  
# Description : 
# 
# A client where i can test putting in credetials in routes (params, body, path) and extracing them in the middleware
@pytest.fixture(scope="function")
def http_client_mocked_path_for_extracting_creds():
    app = FastAPI()

    @app.middleware("http")
    async def add_role_credentials(request: Request, call_next):
        credentials = await extract_role_credentials_from_request(request)
        request.state.credentials = credentials
        response = await call_next(request)
        return response

    # from body / query
    @app.get("/example")
    async def example_route(request: Request):
        return {"credentials": request.state.credentials}
    
    @app.post("/example")
    async def example_route(request: Request):
        return {"credentials": request.state.credentials}

    # from path
    @app.post("/group/{groupid}")
    async def group_route(request: Request, groupid: str):
        return {"credentials": request.state.credentials}

    @app.post("/edit/{editid}")
    async def edit_route(request: Request, editid: int):
        return {"credentials": request.state.credentials}
    
    @app.post("/example/group/{groupid}/example")
    async def nested_group_route(request: Request, groupid: str):
        return {"credentials": request.state.credentials}

    @app.post("/example/edit/{editid}/example")
    async def nested_edit_route(request: Request, editid: int):
        return {"credentials": request.state.credentials}
    
    # yield client with routes
    with TestClient(app) as test_client:
        yield test_client